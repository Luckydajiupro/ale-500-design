#!/usr/bin/env python3
"""Check a wave2 verification contract with the Python standard library only.

The checker mirrors the shape rules in ``schemas/verification-contract.schema.json``
and adds the cross-field rules that a plain JSON Schema cannot state comfortably:
oracle requirements, judge calibration, hard-gate explicitness, artifact
visibility, package-hash scope, and handoff state.

Usage:
    python3 tools/wave2/verify_contract_check.py --check tools/wave2/fixtures/c4-judge.json
    python3 tools/wave2/verify_contract_check.py --check fixtures/*.json --json
    python3 tools/wave2/verify_contract_check.py --selftest
"""

import argparse
import copy
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "docs/data/wave2-verifier-poc-results.csv"
SCHEMA_PATH = ROOT / "schemas/verification-contract.schema.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

SCHEMA_VERSION = "verification-contract-1.0"
KINDS = [
    "numeric_cases",
    "tabular_columns",
    "document_qa",
    "artifact_diff",
    "code_artifact",
]
MODES = ["deterministic", "rubric", "judge", "hybrid", "human_review"]
ROLES = [
    "oracle",
    "rubric",
    "judge_config",
    "fixture",
    "reference_render",
    "answer_key",
    "output_contract",
    "verifier",
    "sample_good",
    "sample_bad",
]
VISIBILITIES = ["agent_visible", "evaluator_only", "platform_only"]
EVALUATOR_ONLY_ROLES = {
    "oracle",
    "rubric",
    "judge_config",
    "reference_render",
    "answer_key",
    "sample_good",
    "sample_bad",
}
ORACLE_BEARING_ROLES = {"oracle", "answer_key", "reference_render"}
ORACLE_KINDS_REQUIRED = {
    "independent_oracle",
    "recomputed_oracle",
    "equivalence_class",
}
ORACLE_KINDS_UNREFERENCED = {"none", "rubric_only", "visual_reference_family"}
DIMENSIONS = [
    "correctness",
    "completeness",
    "format",
    "professional_judgment",
    "process",
]
CHECK_METHODS = ["auto_script", "artifact_diff", "llm_judge", "human_rubric"]
CHANNELS = [
    "recompute",
    "declared_output",
    "geometry",
    "render_compare",
    "judge",
    "human_rubric",
    "format",
]
DETERMINISTIC_CHANNELS = {
    "recompute",
    "declared_output",
    "geometry",
    "render_compare",
    "format",
}
TOLERANCE_TYPES = [
    "absolute",
    "relative",
    "decimal",
    "geometric",
    "structural",
    "set_exact",
    "none",
]
SCORE_TYPES = ["binary", "ratio", "weighted_sum", "rubric_levels"]
REWARDS = ["score", "passed"]
HANDOFF_STATUSES = ["draft", "exported", "accepted", "rejected", "registered"]
ENFORCED_BY = ["verifier", "packaging", "judge", "human"]
ON_FAIL = ["score_0", "reject", "task_fail"]
ANSWER_FORMATS = ["YES_NO", "LIKERT", "JSON"]
MODEL_VERSION_POLICIES = ["pinned", "rolling_with_record"]
COMPOSITIONS = ["weighted_sum", "gate_then_weighted", "sequential"]


class Problem(object):
    __slots__ = ("code", "path", "message")

    def __init__(self, code, path, message):
        self.code = code
        self.path = path
        self.message = message

    def as_dict(self):
        return {"code": self.code, "path": self.path, "message": self.message}

    def __repr__(self):
        return "%s %s: %s" % (self.code, self.path, self.message)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _pattern(value, regex):
    return isinstance(value, str) and re.match(regex, value) is not None


def _path_safety(path):
    """Return a reason when a repository-relative artifact path is unsafe."""
    if not isinstance(path, str) or not path:
        return "must be a non-empty string"
    if path != path.strip():
        return "must not have leading or trailing whitespace"
    if "\x00" in path:
        return "must not contain a null byte"
    if "\\" in path:
        return "must use forward slashes"
    if path.startswith("/"):
        return "must be repository-relative, not absolute"
    if re.match(r"^[A-Za-z]:", path):
        return "must not carry a Windows drive letter"
    core = path[:-1] if path.endswith("/") and path != "/" else path
    parts = core.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return "must not contain empty, dot, or parent segments"
    return None


def _sha256_ok(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


class ContractValidator(object):
    def __init__(self):
        self.problems = []

    def add(self, code, path, message):
        self.problems.append(Problem(code, path, message))

    def require(self, obj, key, path, code="CONTRACT_REQUIRED_MISSING"):
        if not isinstance(obj, dict) or key not in obj:
            self.add(code, path + "." + key, "required field is missing")
            return False
        return True

    def require_keys(self, obj, keys, path):
        if not isinstance(obj, dict):
            self.add("CONTRACT_REQUIRED_MISSING", path, "must be an object")
            return
        for key in keys:
            self.require(obj, key, path)

    def validate(self, contract, source="$"):
        self.problems = []
        if not isinstance(contract, dict):
            self.add("CONTRACT_REQUIRED_MISSING", source, "contract must be a JSON object")
            return self.problems

        required = [
            "schema_version",
            "contract_id",
            "task_id",
            "contract_kind",
            "mode",
            "oracle",
            "artifacts",
            "tolerance",
            "scoring",
            "handoff",
        ]
        for key in required:
            self.require(contract, key, source)

        if "schema_version" in contract and contract["schema_version"] != SCHEMA_VERSION:
            self.add(
                "CONTRACT_ENUM_INVALID",
                source + ".schema_version",
                "expected %r" % SCHEMA_VERSION,
            )
        if "contract_id" in contract and not _pattern(
            contract["contract_id"], r"^VC-[A-Za-z0-9][A-Za-z0-9._-]*$"
        ):
            self.add(
                "CONTRACT_ENUM_INVALID",
                source + ".contract_id",
                "must match VC-[A-Za-z0-9][A-Za-z0-9._-]*",
            )
        if "task_id" in contract and not _pattern(
            contract["task_id"], r"^[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)*$"
        ):
            self.add(
                "CONTRACT_ENUM_INVALID",
                source + ".task_id",
                "must be a repository task id such as domain/task",
            )

        kind = contract.get("contract_kind")
        mode = contract.get("mode")
        if "contract_kind" in contract and kind not in KINDS:
            self.add(
                "CONTRACT_ENUM_INVALID",
                source + ".contract_kind",
                "one of %s" % ", ".join(KINDS),
            )
        if "mode" in contract and mode not in MODES:
            self.add(
                "CONTRACT_ENUM_INVALID",
                source + ".mode",
                "one of %s" % ", ".join(MODES),
            )

        roles = self.validate_artifacts(contract, source)
        self.validate_oracle(contract, source, roles, kind, mode)
        self.validate_tolerance(contract, source, kind, mode)
        self.validate_scoring(contract, source, kind, mode)
        self.validate_judge(contract, source, mode, roles)
        self.validate_human_review(contract, source, mode)
        self.validate_handoff(contract, source)

        return sorted(self.problems, key=lambda p: (p.path, p.code))

    # ------------------------------------------------------------------
    # artifacts
    # ------------------------------------------------------------------
    def validate_artifacts(self, contract, source):
        artifacts = contract.get("artifacts")
        path = source + ".artifacts"
        roles = set()
        if not isinstance(artifacts, list) or not artifacts:
            self.add("CONTRACT_REQUIRED_MISSING", path, "must be a non-empty array")
            return roles

        seen_pairs = set()
        for index, item in enumerate(artifacts):
            here = "%s[%d]" % (path, index)
            if not isinstance(item, dict):
                self.add("CONTRACT_REQUIRED_MISSING", here, "artifact must be an object")
                continue
            self.require_keys(
                item,
                ["role", "path", "visibility", "in_package_hash", "required"],
                here,
            )
            role = item.get("role")
            artifact_path = item.get("path")
            visibility = item.get("visibility")

            if "role" in item:
                if role not in ROLES:
                    self.add(
                        "CONTRACT_ARTIFACT_ROLE_INVALID",
                        here + ".role",
                        "one of %s" % ", ".join(ROLES),
                    )
                else:
                    roles.add(role)

            if "path" in item:
                reason = _path_safety(artifact_path)
                if reason:
                    self.add(
                        "CONTRACT_ARTIFACT_PATH_UNSAFE",
                        here + ".path",
                        reason,
                    )
            if "visibility" in item and visibility not in VISIBILITIES:
                self.add(
                    "CONTRACT_ENUM_INVALID",
                    here + ".visibility",
                    "one of %s" % ", ".join(VISIBILITIES),
                )

            if role in EVALUATOR_ONLY_ROLES and visibility != "evaluator_only":
                self.add(
                    "CONTRACT_ARTIFACT_VISIBILITY_LEAK",
                    here + ".visibility",
                    "%s must stay evaluator_only" % role,
                )
            if role == "verifier":
                if visibility != "platform_only":
                    self.add(
                        "CONTRACT_ARTIFACT_VISIBILITY_LEAK",
                        here + ".visibility",
                        "verifier is a platform-only handoff asset",
                    )
                if item.get("in_package_hash") is not False:
                    self.add(
                        "CONTRACT_ARTIFACT_VISIBILITY_LEAK",
                        here + ".in_package_hash",
                        "verifier must not enter the ALE-data package hash",
                    )
            if (
                visibility == "agent_visible"
                and isinstance(artifact_path, str)
                and artifact_path.startswith("reference/")
            ):
                self.add(
                    "CONTRACT_ARTIFACT_VISIBILITY_LEAK",
                    here + ".path",
                    "agent_visible path must not point into reference/",
                )

            if "in_package_hash" in item and item["in_package_hash"] not in (True, False):
                self.add(
                    "CONTRACT_ENUM_INVALID",
                    here + ".in_package_hash",
                    "must be boolean",
                )
            if "required" in item and item["required"] not in (True, False):
                self.add("CONTRACT_ENUM_INVALID", here + ".required", "must be boolean")
            if "sha256" in item and not _sha256_ok(item["sha256"]):
                self.add(
                    "CONTRACT_ENUM_INVALID",
                    here + ".sha256",
                    "must be 64 lowercase hex characters",
                )
            if item.get("in_package_hash") is True and "sha256" not in item:
                self.add(
                    "CONTRACT_REQUIRED_MISSING",
                    here + ".sha256",
                    "hashable artifacts must declare sha256",
                )

            if isinstance(role, str) and isinstance(artifact_path, str):
                pair = (role, artifact_path)
                if pair in seen_pairs:
                    self.add(
                        "CONTRACT_ENUM_INVALID",
                        here,
                        "duplicate role and path pair",
                    )
                seen_pairs.add(pair)

        by_mode = {
            "deterministic": [],
            "rubric": ["rubric", "sample_good", "sample_bad"],
            "judge": [],
            "hybrid": [],
            "human_review": ["rubric", "sample_good", "sample_bad"],
        }
        for role in by_mode.get(contract.get("mode"), []):
            if role not in roles:
                self.add(
                    "CONTRACT_REQUIRED_MISSING",
                    path,
                    "mode %s requires artifact role %s"
                    % (contract.get("mode"), role),
                )

        if contract.get("mode") == "judge" and not ({"rubric", "judge_config"} & roles):
            self.add(
                "CONTRACT_JUDGE_RUBRIC_MISSING",
                path,
                "judge mode requires a rubric or judge_config artifact",
            )
        if contract.get("contract_kind") in ("numeric_cases", "document_qa"):
            if "output_contract" not in roles:
                self.add(
                    "CONTRACT_REQUIRED_MISSING",
                    path,
                    "kind %s requires an output_contract artifact"
                    % contract.get("contract_kind"),
                )
        return roles

    # ------------------------------------------------------------------
    # oracle
    # ------------------------------------------------------------------
    def validate_oracle(self, contract, source, roles, kind, mode):
        oracle = contract.get("oracle")
        path = source + ".oracle"
        if not isinstance(oracle, dict):
            return
        self.require_keys(oracle, ["required", "kind", "rationale"], path)
        required = oracle.get("required")
        oracle_kind = oracle.get("kind")

        if "required" in oracle and required not in (True, False):
            self.add("CONTRACT_ENUM_INVALID", path + ".required", "must be boolean")
        if "kind" in oracle:
            allowed = ORACLE_KINDS_REQUIRED | ORACLE_KINDS_UNREFERENCED
            if oracle_kind not in allowed:
                self.add(
                    "CONTRACT_ENUM_INVALID",
                    path + ".kind",
                    "one of %s" % ", ".join(sorted(allowed)),
                )
        if "rationale" in oracle and not _nonempty(oracle.get("rationale")):
            self.add(
                "CONTRACT_REQUIRED_MISSING",
                path + ".rationale",
                "must state why the oracle is or is not required",
            )

        if required is True:
            if oracle_kind in ORACLE_KINDS_UNREFERENCED:
                self.add(
                    "CONTRACT_ORACLE_MISSING",
                    path + ".kind",
                    "oracle.required=true cannot use %r" % oracle_kind,
                )
            if not (roles & ORACLE_BEARING_ROLES):
                self.add(
                    "CONTRACT_ORACLE_MISSING",
                    path,
                    "an oracle, answer_key, or reference_render artifact is required",
                )
            if oracle_kind == "equivalence_class":
                channels = oracle.get("channels")
                if not isinstance(channels, list) or len(channels) < 2:
                    self.add(
                        "CONTRACT_ORACLE_MISSING",
                        path + ".channels",
                        "equivalence_class requires two or more named answer channels",
                    )
                if len(roles & {"answer_key"}) < 1:
                    self.add(
                        "CONTRACT_ORACLE_MISSING",
                        path,
                        "equivalence_class requires at least one answer_key artifact",
                    )

        if required is False:
            if oracle_kind not in ORACLE_KINDS_UNREFERENCED:
                self.add(
                    "CONTRACT_ENUM_INVALID",
                    path + ".kind",
                    "oracle.required=false must use none, rubric_only, or visual_reference_family",
                )
            if oracle.get("approved_without_reference") is not True:
                self.add(
                    "CONTRACT_ORACLE_APPROVAL_MISSING",
                    path + ".approved_without_reference",
                    "must be true when no independent oracle exists",
                )
            if not _nonempty(oracle.get("approval_ref")):
                self.add(
                    "CONTRACT_ORACLE_APPROVAL_MISSING",
                    path + ".approval_ref",
                    "must name the approval record",
                )

        if mode == "deterministic" and required is not True:
            self.add(
                "CONTRACT_ORACLE_MISSING",
                path,
                "deterministic mode requires an independent or recomputed oracle",
            )

    # ------------------------------------------------------------------
    # tolerance
    # ------------------------------------------------------------------
    def validate_tolerance(self, contract, source, kind, mode):
        tolerance = contract.get("tolerance")
        path = source + ".tolerance"
        if not isinstance(tolerance, dict):
            return
        self.require(tolerance, "type", path)
        ttype = tolerance.get("type")
        if "type" in tolerance and ttype not in TOLERANCE_TYPES:
            self.add(
                "CONTRACT_ENUM_INVALID",
                path + ".type",
                "one of %s" % ", ".join(TOLERANCE_TYPES),
            )
            return
        if ttype not in ("none", "set_exact", "structural"):
            value = tolerance.get("value")
            if not _is_number(value) or value <= 0:
                self.add(
                    "CONTRACT_TOLERANCE_MISSING",
                    path + ".value",
                    "a positive numeric value is required for %r" % ttype,
                )

        allowed = {
            "numeric_cases": {"absolute", "relative", "decimal"},
            "document_qa": {"absolute", "relative", "decimal"},
            "tabular_columns": {"absolute", "relative", "decimal", "structural"},
            "artifact_diff": {"absolute", "relative", "decimal", "geometric", "structural", "none"},
            "code_artifact": {"set_exact", "structural", "none"},
        }.get(kind)
        if allowed and ttype not in allowed:
            self.add(
                "CONTRACT_TOLERANCE_MISSING",
                path + ".type",
                "kind %s accepts %s" % (kind, ", ".join(sorted(allowed))),
            )
        if kind == "artifact_diff" and mode in ("deterministic", "hybrid") and ttype == "none":
            self.add(
                "CONTRACT_TOLERANCE_MISSING",
                path + ".type",
                "deterministic or hybrid artifact_diff needs a measurable tolerance",
            )

    # ------------------------------------------------------------------
    # scoring
    # ------------------------------------------------------------------
    def validate_scoring(self, contract, source, kind, mode):
        scoring = contract.get("scoring")
        path = source + ".scoring"
        if not isinstance(scoring, dict):
            return
        self.require_keys(
            scoring,
            ["reward", "score_type", "score_range", "partial_credit", "components", "hard_gates", "passed"],
            path,
        )
        reward = scoring.get("reward")
        score_type = scoring.get("score_type")
        partial = scoring.get("partial_credit")

        if "reward" in scoring and reward not in REWARDS:
            self.add(
                "CONTRACT_REWARD_INVALID",
                path + ".reward",
                "one of %s" % ", ".join(REWARDS),
            )
        if "score_type" in scoring and score_type not in SCORE_TYPES:
            self.add(
                "CONTRACT_ENUM_INVALID",
                path + ".score_type",
                "one of %s" % ", ".join(SCORE_TYPES),
            )
        score_range = scoring.get("score_range")
        if not isinstance(score_range, list) or len(score_range) != 2:
            self.add(
                "CONTRACT_ENUM_INVALID",
                path + ".score_range",
                "must be [min, max]",
            )
        else:
            low, high = score_range
            if not (_is_number(low) and _is_number(high) and 0 <= low < high <= 1):
                self.add(
                    "CONTRACT_ENUM_INVALID",
                    path + ".score_range",
                    "must satisfy 0 <= min < max <= 1",
                )
        if "partial_credit" in scoring and partial not in (True, False):
            self.add("CONTRACT_ENUM_INVALID", path + ".partial_credit", "must be boolean")
        if partial is False and score_type != "binary":
            self.add(
                "CONTRACT_WEIGHTS_INVALID",
                path + ".score_type",
                "partial_credit=false requires binary scoring",
            )
        if partial is True and score_type == "binary":
            self.add(
                "CONTRACT_WEIGHTS_INVALID",
                path + ".score_type",
                "partial_credit=true cannot be binary",
            )

        passed = scoring.get("passed")
        if isinstance(passed, dict):
            self.require_keys(passed, ["rule", "is_reward"], path + ".passed")
            if "rule" in passed and not _nonempty(passed.get("rule")):
                self.add(
                    "CONTRACT_REWARD_INVALID",
                    path + ".passed.rule",
                    "must state the reporting rule",
                )
            if "is_reward" in passed and passed.get("is_reward") not in (True, False):
                self.add(
                    "CONTRACT_REWARD_INVALID",
                    path + ".passed.is_reward",
                    "must be boolean",
                )
            if reward in REWARDS and isinstance(passed, dict):
                expected = reward == "passed"
                if passed.get("is_reward") is not expected:
                    self.add(
                        "CONTRACT_REWARD_INVALID",
                        path + ".passed.is_reward",
                        "must be %r when reward is %r" % (expected, reward),
                    )

        components = scoring.get("components")
        component_channels = set()
        if not isinstance(components, list):
            self.add("CONTRACT_WEIGHTS_INVALID", path + ".components", "must be an array")
        else:
            total = 0
            critical_count = 0
            for index, item in enumerate(components):
                here = "%s.components[%d]" % (path, index)
                if not isinstance(item, dict):
                    self.add("CONTRACT_WEIGHTS_INVALID", here, "must be an object")
                    continue
                self.require_keys(
                    item,
                    ["criterion_id", "dimension", "check_method", "channel", "weight", "critical"],
                    here,
                )
                if not _nonempty(item.get("criterion_id")):
                    self.add(
                        "CONTRACT_WEIGHTS_INVALID",
                        here + ".criterion_id",
                        "must be non-empty",
                    )
                if item.get("dimension") not in DIMENSIONS:
                    self.add(
                        "CONTRACT_ENUM_INVALID",
                        here + ".dimension",
                        "one of %s" % ", ".join(DIMENSIONS),
                    )
                if item.get("check_method") not in CHECK_METHODS:
                    self.add(
                        "CONTRACT_ENUM_INVALID",
                        here + ".check_method",
                        "one of %s" % ", ".join(CHECK_METHODS),
                    )
                if item.get("channel") not in CHANNELS:
                    self.add(
                        "CONTRACT_ENUM_INVALID",
                        here + ".channel",
                        "one of %s" % ", ".join(CHANNELS),
                    )
                else:
                    component_channels.add(item["channel"])
                weight = item.get("weight")
                if not _is_int(weight) or weight < 1 or weight > 100:
                    self.add(
                        "CONTRACT_WEIGHTS_INVALID",
                        here + ".weight",
                        "must be an integer from 1 to 100",
                    )
                else:
                    total += weight
                if item.get("critical") not in (True, False):
                    self.add(
                        "CONTRACT_WEIGHTS_INVALID",
                        here + ".critical",
                        "must be boolean",
                    )
                elif item.get("critical") is True:
                    critical_count += 1

            weights_total = scoring.get("weights_total", 100)
            if not _is_int(weights_total) or weights_total <= 0:
                self.add(
                    "CONTRACT_WEIGHTS_INVALID",
                    path + ".weights_total",
                    "must be a positive integer",
                )
            elif partial is True and total != weights_total:
                self.add(
                    "CONTRACT_WEIGHTS_INVALID",
                    path + ".components",
                    "component weights sum to %d, expected %d" % (total, weights_total),
                )
            if partial is True and len(components) < 2:
                self.add(
                    "CONTRACT_WEIGHTS_INVALID",
                    path + ".components",
                    "partial credit needs at least two components",
                )
            if partial is True and critical_count < 1:
                self.add(
                    "CONTRACT_WEIGHTS_INVALID",
                    path + ".components",
                    "at least one component must be critical",
                )
            if partial is False and components:
                if len(components) != 1 or components[0].get("weight") != 100:
                    self.add(
                        "CONTRACT_WEIGHTS_INVALID",
                        path + ".components",
                        "binary scoring allows one component of weight 100",
                    )

        self.validate_mode_channels(contract, source, mode, component_channels)
        self.validate_hard_gates(scoring, path, mode)

    def validate_mode_channels(self, contract, source, mode, channels):
        path = source + ".scoring.components"
        if mode == "deterministic" and (channels & {"judge", "human_rubric"}):
            self.add(
                "CONTRACT_MODE_INCONSISTENT",
                path,
                "deterministic mode cannot use judge or human_rubric channels",
            )
        if mode == "rubric":
            if "human_rubric" not in channels:
                self.add(
                    "CONTRACT_MODE_INCONSISTENT",
                    path,
                    "rubric mode needs a human_rubric component",
                )
            if "judge" in channels:
                self.add(
                    "CONTRACT_MODE_INCONSISTENT",
                    path,
                    "rubric mode cannot use an automated judge channel",
                )
        if mode == "judge" and "judge" not in channels:
            self.add(
                "CONTRACT_MODE_INCONSISTENT",
                path,
                "judge mode needs at least one judge channel",
            )
        if mode == "human_review" and "human_rubric" not in channels:
            self.add(
                "CONTRACT_MODE_INCONSISTENT",
                path,
                "human_review mode needs a human_rubric component",
            )
        if mode == "hybrid":
            if len(channels) < 2:
                self.add(
                    "CONTRACT_MODE_INCONSISTENT",
                    path,
                    "hybrid mode needs at least two distinct evidence channels",
                )
            if not (channels & DETERMINISTIC_CHANNELS):
                self.add(
                    "CONTRACT_MODE_INCONSISTENT",
                    path,
                    "hybrid mode needs at least one deterministic channel",
                )
            if not (channels & {"judge", "human_rubric", "declared_output", "render_compare"}):
                self.add(
                    "CONTRACT_MODE_INCONSISTENT",
                    path,
                    "hybrid mode needs a second evidence channel beyond recompute",
                )
            if isinstance(contract.get("scoring"), dict):
                if contract["scoring"].get("composition") not in COMPOSITIONS:
                    self.add(
                        "CONTRACT_MODE_INCONSISTENT",
                        source + ".scoring.composition",
                        "hybrid mode must declare one of %s" % ", ".join(COMPOSITIONS),
                    )

    def validate_hard_gates(self, scoring, path, mode):
        gates = scoring.get("hard_gates")
        if not isinstance(gates, list):
            self.add("CONTRACT_HARD_GATE_MISSING", path + ".hard_gates", "must be an array")
            return
        if not gates:
            self.add(
                "CONTRACT_HARD_GATE_MISSING",
                path + ".hard_gates",
                "at least one explicit hard gate is required",
            )
        seen = set()
        for index, gate in enumerate(gates):
            here = "%s.hard_gates[%d]" % (path, index)
            if not isinstance(gate, dict):
                self.add("CONTRACT_HARD_GATE_MISSING", here, "must be an object")
                continue
            self.require_keys(
                gate,
                ["gate_id", "condition", "enforced_by", "on_fail", "evidence"],
                here,
            )
            gate_id = gate.get("gate_id")
            if not _nonempty(gate_id):
                self.add("CONTRACT_HARD_GATE_MISSING", here + ".gate_id", "must be non-empty")
            elif gate_id in seen:
                self.add(
                    "CONTRACT_HARD_GATE_MISSING",
                    here + ".gate_id",
                    "duplicate gate id %r" % gate_id,
                )
            seen.add(gate_id)
            if not _nonempty(gate.get("condition")):
                self.add(
                    "CONTRACT_HARD_GATE_MISSING",
                    here + ".condition",
                    "must state the failure condition",
                )
            if gate.get("enforced_by") not in ENFORCED_BY:
                self.add(
                    "CONTRACT_HARD_GATE_NOT_EXPLICIT",
                    here + ".enforced_by",
                    "must name a runtime enforcer: %s" % ", ".join(ENFORCED_BY),
                )
            if gate.get("on_fail") not in ON_FAIL:
                self.add(
                    "CONTRACT_HARD_GATE_MISSING",
                    here + ".on_fail",
                    "one of %s" % ", ".join(ON_FAIL),
                )
            if not _nonempty(gate.get("evidence")):
                self.add(
                    "CONTRACT_HARD_GATE_NOT_EXPLICIT",
                    here + ".evidence",
                    "must name the artifact or event that records enforcement",
                )

    # ------------------------------------------------------------------
    # judge
    # ------------------------------------------------------------------
    def validate_judge(self, contract, source, mode, roles):
        judge = contract.get("judge")
        path = source + ".judge"
        scoring = contract.get("scoring") if isinstance(contract.get("scoring"), dict) else {}
        components = scoring.get("components") if isinstance(scoring.get("components"), list) else []
        has_judge_channel = any(
            isinstance(item, dict) and item.get("channel") == "judge" for item in components
        )
        if not isinstance(judge, dict):
            if mode == "judge" or has_judge_channel:
                self.add(
                    "CONTRACT_JUDGE_RUBRIC_MISSING",
                    path,
                    "a judge channel requires a judge object",
                )
            return
        if not isinstance(judge, dict):
            if mode in ("deterministic", "rubric", "human_review"):
                return
            return
        if mode in ("deterministic", "rubric", "human_review"):
            self.add(
                "CONTRACT_MODE_INCONSISTENT",
                path,
                "%s mode must not carry an automated judge object" % mode,
            )
            return

        self.require(judge, "model_family", path)
        self.require(judge, "model_version_policy", path)
        self.require(judge, "answer_format", path)
        self.require(judge, "calibration", path)
        if "model_family" in judge and not _nonempty(judge.get("model_family")):
            self.add(
                "CONTRACT_JUDGE_RUBRIC_MISSING",
                path + ".model_family",
                "must name the judge model family",
            )
        if judge.get("model_version_policy") not in MODEL_VERSION_POLICIES:
            self.add(
                "CONTRACT_ENUM_INVALID",
                path + ".model_version_policy",
                "one of %s" % ", ".join(MODEL_VERSION_POLICIES),
            )
        if judge.get("answer_format") not in ANSWER_FORMATS:
            self.add(
                "CONTRACT_ENUM_INVALID",
                path + ".answer_format",
                "one of %s" % ", ".join(ANSWER_FORMATS),
            )

        questions = judge.get("questions")
        rubric_ref = judge.get("rubric_ref")
        has_questions = isinstance(questions, list) and len(questions) > 0 and all(
            _nonempty(q) for q in questions
        )
        has_rubric_ref = _nonempty(rubric_ref)
        if not has_questions and not has_rubric_ref:
            self.add(
                "CONTRACT_JUDGE_RUBRIC_MISSING",
                path,
                "judge needs inline questions or a rubric_ref",
            )
        if has_rubric_ref:
            ref = rubric_ref
            if ref.startswith("artifact:"):
                ref = ref[len("artifact:"):]
            artifacts = contract.get("artifacts") or []
            match = [
                a
                for a in artifacts
                if isinstance(a, dict)
                and a.get("path") == ref
                and a.get("role") in ("rubric", "judge_config")
            ]
            if not match:
                self.add(
                    "CONTRACT_JUDGE_RUBRIC_MISSING",
                    path + ".rubric_ref",
                    "must resolve to a rubric or judge_config artifact",
                )

        calibration = judge.get("calibration")
        if isinstance(calibration, dict):
            self.require_keys(
                calibration,
                [
                    "required",
                    "sample_set_ref",
                    "agreement_threshold",
                    "human_review_rate",
                    "repeat_runs",
                    "record_raw_response",
                ],
                path + ".calibration",
            )
            if calibration.get("required") is not True:
                self.add(
                    "CONTRACT_JUDGE_CALIBRATION_MISSING",
                    path + ".calibration.required",
                    "an uncalibrated judge is not acceptable",
                )
            if not _nonempty(calibration.get("sample_set_ref")):
                self.add(
                    "CONTRACT_JUDGE_CALIBRATION_MISSING",
                    path + ".calibration.sample_set_ref",
                    "must point at the calibration sample set",
                )
            threshold = calibration.get("agreement_threshold")
            if not _is_number(threshold) or not 0 <= threshold <= 1:
                self.add(
                    "CONTRACT_JUDGE_CALIBRATION_MISSING",
                    path + ".calibration.agreement_threshold",
                    "must be a number from 0 to 1",
                )
            rate = calibration.get("human_review_rate")
            if not _is_number(rate) or not 0 <= rate <= 1:
                self.add(
                    "CONTRACT_JUDGE_CALIBRATION_MISSING",
                    path + ".calibration.human_review_rate",
                    "must be a number from 0 to 1",
                )
            repeat_runs = calibration.get("repeat_runs")
            if not _is_int(repeat_runs) or repeat_runs < 2:
                self.add(
                    "CONTRACT_JUDGE_CALIBRATION_MISSING",
                    path + ".calibration.repeat_runs",
                    "must be at least 2 for stability",
                )
            if calibration.get("record_raw_response") is not True:
                self.add(
                    "CONTRACT_JUDGE_CALIBRATION_MISSING",
                    path + ".calibration.record_raw_response",
                    "must be true",
                )
        elif "calibration" in judge:
            self.add(
                "CONTRACT_JUDGE_CALIBRATION_MISSING",
                path + ".calibration",
                "must be an object",
            )

        if "pass_threshold" in judge:
            threshold = judge.get("pass_threshold")
            if not _is_number(threshold) or not 0 <= threshold <= 1:
                self.add(
                    "CONTRACT_JUDGE_CALIBRATION_MISSING",
                    path + ".pass_threshold",
                    "must be a number from 0 to 1",
                )

    # ------------------------------------------------------------------
    # human review
    # ------------------------------------------------------------------
    def validate_human_review(self, contract, source, mode):
        review = contract.get("human_review")
        path = source + ".human_review"
        if mode != "human_review":
            return
        if not isinstance(review, dict):
            self.add(
                "CONTRACT_REQUIRED_MISSING",
                path,
                "human_review mode requires a human_review object",
            )
            return
        self.require_keys(
            review,
            ["reviewers_min", "adjudication", "blind_review", "approval_ref"],
            path,
        )
        reviewers = review.get("reviewers_min")
        if not _is_int(reviewers) or reviewers < 2:
            self.add(
                "CONTRACT_REQUIRED_MISSING",
                path + ".reviewers_min",
                "must be at least 2",
            )
        if not _nonempty(review.get("adjudication")):
            self.add(
                "CONTRACT_REQUIRED_MISSING",
                path + ".adjudication",
                "must state the tie-break rule",
            )
        if "blind_review" in review and review.get("blind_review") not in (True, False):
            self.add("CONTRACT_ENUM_INVALID", path + ".blind_review", "must be boolean")
        if not _nonempty(review.get("approval_ref")):
            self.add(
                "CONTRACT_REQUIRED_MISSING",
                path + ".approval_ref",
                "must name the approval record",
            )

    # ------------------------------------------------------------------
    # handoff
    # ------------------------------------------------------------------
    def validate_handoff(self, contract, source):
        handoff = contract.get("handoff")
        path = source + ".handoff"
        if not isinstance(handoff, dict):
            return
        self.require_keys(
            handoff,
            ["handoff_id", "status", "exported_at", "exported_by", "verifier", "accepted_at", "rejection_reason"],
            path,
        )
        status = handoff.get("status")
        if "status" in handoff and status not in HANDOFF_STATUSES:
            self.add(
                "CONTRACT_HANDOFF_INVALID",
                path + ".status",
                "one of %s" % ", ".join(HANDOFF_STATUSES),
            )
            return
        if not _pattern(handoff.get("handoff_id"), r"^HO-[A-Za-z0-9][A-Za-z0-9._-]*$"):
            self.add(
                "CONTRACT_HANDOFF_INVALID",
                path + ".handoff_id",
                "must match HO-[A-Za-z0-9][A-Za-z0-9._-]*",
            )
        if status in ("exported", "accepted", "registered"):
            if not _nonempty(handoff.get("exported_at")):
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".exported_at",
                    "must be set after export",
                )
            if not _nonempty(handoff.get("exported_by")):
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".exported_by",
                    "must name the exporting role",
                )
        if status == "accepted" and not _nonempty(handoff.get("accepted_at")):
            self.add(
                "CONTRACT_HANDOFF_INVALID",
                path + ".accepted_at",
                "accepted state needs accepted_at",
            )
        if status == "rejected":
            if not _nonempty(handoff.get("rejection_reason")):
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".rejection_reason",
                    "rejected state needs a reason",
                )
            if handoff.get("accepted_at") not in (None, ""):
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".accepted_at",
                    "rejected state cannot be accepted",
                )

        verifier = handoff.get("verifier")
        if not isinstance(verifier, dict):
            self.add(
                "CONTRACT_HANDOFF_INVALID",
                path + ".verifier",
                "must be an object with null-or-value fields",
            )
            return
        for key in ("verifier_id", "version", "sha256", "runtime", "entrypoint", "known_limits", "sample_results"):
            self.require(verifier, key, path + ".verifier", code="CONTRACT_HANDOFF_INVALID")
        if "sha256" in verifier and verifier.get("sha256") not in (None, ""):
            if not _sha256_ok(verifier.get("sha256")):
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".verifier.sha256",
                    "must be 64 lowercase hex characters",
                )
        if "entrypoint" in verifier and verifier.get("entrypoint") not in (None, ""):
            reason = _path_safety(verifier.get("entrypoint"))
            if reason:
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".verifier.entrypoint",
                    reason,
                )
        if "runtime" in verifier and verifier.get("runtime") not in (None, ""):
            if not _pattern(verifier.get("runtime"), r"^[a-z0-9][a-z0-9._-]{1,63}$"):
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".verifier.runtime",
                    "must be a runtime id such as python3.12",
                )
        samples = verifier.get("sample_results")
        if not isinstance(samples, list):
            self.add(
                "CONTRACT_HANDOFF_INVALID",
                path + ".verifier.sample_results",
                "must be an array",
            )
        else:
            for index, sample in enumerate(samples):
                here = "%s.verifier.sample_results[%d]" % (path, index)
                if not isinstance(sample, dict):
                    self.add("CONTRACT_HANDOFF_INVALID", here, "must be an object")
                    continue
                if not _nonempty(sample.get("case")):
                    self.add(
                        "CONTRACT_HANDOFF_INVALID",
                        here + ".case",
                        "must name the sample case",
                    )
                if sample.get("passed") not in (True, False):
                    self.add(
                        "CONTRACT_HANDOFF_INVALID",
                        here + ".passed",
                        "must be boolean",
                    )

        if status == "registered":
            for key in ("verifier_id", "version", "sha256", "runtime", "entrypoint", "known_limits"):
                if not _nonempty(verifier.get(key)):
                    self.add(
                        "CONTRACT_HANDOFF_INVALID",
                        path + ".verifier." + key,
                        "registered state needs a value",
                    )
            if not isinstance(samples, list) or len(samples) < 1:
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".verifier.sample_results",
                    "registered state needs at least one sample result",
                )
            if not _nonempty(handoff.get("accepted_at")):
                self.add(
                    "CONTRACT_HANDOFF_INVALID",
                    path + ".accepted_at",
                    "registered state needs accepted_at",
                )


def validate_document(document, source="$"):
    """Validate a single contract or a bundle object with a contracts array."""
    problems = []
    if isinstance(document, dict) and "contracts" in document:
        contracts = document.get("contracts")
        if not isinstance(contracts, list) or not contracts:
            return [Problem("CONTRACT_REQUIRED_MISSING", source + ".contracts", "must be a non-empty array")]
        for index, contract in enumerate(contracts):
            problems.extend(ContractValidator().validate(contract, "%s.contracts[%d]" % (source, index)))
        return problems
    if isinstance(document, list):
        for index, contract in enumerate(document):
            problems.extend(ContractValidator().validate(contract, "%s[%d]" % (source, index)))
        return problems
    return ContractValidator().validate(document, source)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def print_report(path, problems):
    if problems:
        print("FAIL %s" % path)
        for problem in problems:
            print("  %s %s: %s" % (problem.code, problem.path, problem.message))
    else:
        print("PASS %s" % path)


def check_schema_consistency():
    """Compare schema enums with the checker constants and reject external refs."""
    problems = []
    if not SCHEMA_PATH.exists():
        return [Problem("CONTRACT_REQUIRED_MISSING", "schemas/verification-contract.schema.json", "schema file is missing")]
    try:
        schema = load_json(SCHEMA_PATH)
    except (OSError, ValueError) as exc:
        return [Problem("CONTRACT_ENUM_INVALID", "schemas/verification-contract.schema.json", "not valid JSON: %s" % exc)]

    if "2020-12" not in str(schema.get("$schema", "")):
        problems.append(
            Problem(
                "CONTRACT_ENUM_INVALID",
                "schemas/verification-contract.schema.json.$schema",
                "must declare JSON Schema 2020-12",
            )
        )

    def walk(node, at):
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and not ref.startswith("#/"):
                problems.append(
                    Problem(
                        "CONTRACT_ENUM_INVALID",
                        "schemas/verification-contract.schema.json" + at + ".$ref",
                        "external $ref is not allowed: %s" % ref,
                    )
                )
            for key, value in node.items():
                walk(value, at + "/" + str(key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, at + "/" + str(index))

    walk(schema, "")

    def enum_at(pointer):
        node = schema
        for part in pointer.strip("/").split("/"):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node.get("enum") if isinstance(node, dict) else None

    checks = [
        ("/$defs/contract/properties/contract_kind/enum", KINDS, "contract_kind"),
        ("/$defs/contract/properties/mode/enum", MODES, "mode"),
        ("/$defs/artifact/properties/role/enum", ROLES, "artifact role"),
        ("/$defs/artifact/properties/visibility/enum", VISIBILITIES, "artifact visibility"),
        ("/$defs/tolerance/properties/type/enum", TOLERANCE_TYPES, "tolerance type"),
        ("/$defs/component/properties/dimension/enum", DIMENSIONS, "component dimension"),
        ("/$defs/component/properties/check_method/enum", CHECK_METHODS, "check method"),
        ("/$defs/component/properties/channel/enum", CHANNELS, "component channel"),
        ("/$defs/handoff/properties/status/enum", HANDOFF_STATUSES, "handoff status"),
    ]
    for pointer, expected, label in checks:
        actual = enum_at(pointer)
        if actual is None:
            problems.append(
                Problem(
                    "CONTRACT_REQUIRED_MISSING",
                    "schemas/verification-contract.schema.json" + pointer,
                    "schema enum for %s is missing" % label,
                )
            )
        elif set(actual) != set(expected):
            problems.append(
                Problem(
                    "CONTRACT_ENUM_INVALID",
                    "schemas/verification-contract.schema.json" + pointer,
                    "schema %s enum does not match checker constants" % label,
                )
            )
    return problems


SELFTEST_CASES = [
    ("selftest-01-c1-tabular-deterministic", "c1-equity-deterministic.json", True, []),
    ("selftest-02-c2-numeric-main-alt", "c2-taxform-deterministic.json", True, []),
    ("selftest-03-c3-artifact-hybrid", "c3-scene2-hybrid.json", True, []),
    ("selftest-04-c4-artifact-judge", "c4-building-judge.json", True, []),
    ("selftest-05-c5-code-deterministic", "c5-chisel-deterministic.json", True, []),
    ("selftest-06-c6-document-deterministic", "c6-legal-deterministic.json", True, []),
    ("selftest-07-v7-human-rubric", "v7-human-rubric.json", True, []),
    ("selftest-08-v8-alt-oracle", "v8-alt-oracle.json", True, []),
    ("selftest-09-missing-mode", "neg-missing-mode.json", False, ["CONTRACT_REQUIRED_MISSING"]),
    ("selftest-10-bad-kind", "neg-bad-kind.json", False, ["CONTRACT_ENUM_INVALID"]),
    ("selftest-11-bad-role", "neg-bad-role.json", False, ["CONTRACT_ARTIFACT_ROLE_INVALID"]),
    ("selftest-12-absolute-path", "neg-absolute-path.json", False, ["CONTRACT_ARTIFACT_PATH_UNSAFE"]),
    ("selftest-13-traversal-path", "neg-traversal-path.json", False, ["CONTRACT_ARTIFACT_PATH_UNSAFE"]),
    ("selftest-14-deterministic-no-oracle", "neg-deterministic-no-oracle.json", False, ["CONTRACT_ORACLE_MISSING"]),
    ("selftest-15-oracle-unapproved", "neg-oracle-unapproved.json", False, ["CONTRACT_ORACLE_APPROVAL_MISSING"]),
    ("selftest-16-judge-no-rubric", "neg-judge-no-rubric.json", False, ["CONTRACT_JUDGE_RUBRIC_MISSING"]),
    ("selftest-17-judge-uncalibrated", "neg-judge-uncalibrated.json", False, ["CONTRACT_JUDGE_CALIBRATION_MISSING"]),
    ("selftest-18-hard-gate-missing", "neg-hard-gate-missing.json", False, ["CONTRACT_HARD_GATE_MISSING"]),
    ("selftest-19-hard-gate-not-explicit", "neg-hard-gate-not-explicit.json", False, ["CONTRACT_HARD_GATE_NOT_EXPLICIT"]),
    ("selftest-20-answer-leak", "neg-answer-leak.json", False, ["CONTRACT_ARTIFACT_VISIBILITY_LEAK"]),
    ("selftest-21-verifier-in-hash", "neg-verifier-in-hash.json", False, ["CONTRACT_ARTIFACT_VISIBILITY_LEAK"]),
    ("selftest-22-weights-not-100", "neg-weights-not-100.json", False, ["CONTRACT_WEIGHTS_INVALID"]),
    ("selftest-23-passed-reward-mismatch", "neg-passed-reward-mismatch.json", False, ["CONTRACT_REWARD_INVALID"]),
    ("selftest-24-handoff-registered-missing", "neg-handoff-registered-missing.json", False, ["CONTRACT_HANDOFF_INVALID"]),
    ("selftest-25-rubric-missing-sample-bad", "neg-rubric-missing-sample-bad.json", False, ["CONTRACT_REQUIRED_MISSING"]),
    ("selftest-26-numeric-no-tolerance", "neg-numeric-no-tolerance.json", False, ["CONTRACT_TOLERANCE_MISSING"]),
    ("selftest-27-judge-channel-without-judge", "neg-judge-channel-without-judge.json", False, ["CONTRACT_JUDGE_RUBRIC_MISSING"]),
    ("selftest-28-example-bundle", "schemas/verification-contract.example.json", True, []),
]


def run_selftest(results_out, verbose=True):
    rows = []
    passed = 0
    failed = 0

    schema_problems = check_schema_consistency()
    schema_ok = not schema_problems
    rows.append(
        {
            "case": "selftest-00-schema-consistency",
            "command": "python3 tools/wave2/verify_contract_check.py --selftest",
            "result": "PASS" if schema_ok else "FAIL",
            "evidence": (
                "schema enums match checker; no external $refs"
                if schema_ok
                else "; ".join("%s %s: %s" % (p.code, p.path, p.message) for p in schema_problems)
            ),
        }
    )
    if schema_ok:
        passed += 1
    else:
        failed += 1

    for case_id, fixture, expect_valid, expected_codes in SELFTEST_CASES:
        if fixture.startswith("schemas/"):
            fixture_path = (ROOT / fixture).resolve()
            display = fixture
        else:
            fixture_path = (FIXTURES / fixture).resolve()
            display = "tools/wave2/fixtures/" + fixture
        command = "python3 tools/wave2/verify_contract_check.py --check " + display
        try:
            contract = load_json(fixture_path)
        except (OSError, ValueError) as exc:
            rows.append(
                {
                    "case": case_id,
                    "command": command,
                    "result": "FAIL",
                    "evidence": "fixture could not be loaded: %s" % exc,
                }
            )
            failed += 1
            continue
        problems = validate_document(contract, "$")
        codes = sorted({p.code for p in problems})
        if expect_valid:
            ok = len(problems) == 0
            evidence = "expected=valid; got=%s" % ("valid" if ok else ",".join(codes))
        else:
            ok = bool(set(codes) & set(expected_codes))
            evidence = "expected=%s; got=%s" % (",".join(expected_codes), ",".join(codes) or "valid")
        rows.append(
            {
                "case": case_id,
                "command": command,
                "result": "PASS" if ok else "FAIL",
                "evidence": evidence,
            }
        )
        if ok:
            passed += 1
        else:
            failed += 1

    results_out.parent.mkdir(parents=True, exist_ok=True)
    with open(str(results_out), "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case", "command", "result", "evidence"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    if verbose:
        for row in rows:
            if row["result"] != "PASS":
                print("FAIL %s: %s" % (row["case"], row["evidence"]))
        print("%d cases: %d passed, %d failed" % (len(rows), passed, failed))
        print("results: %s" % results_out)
    return failed == 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate wave2 verification contracts.")
    parser.add_argument("--check", nargs="+", metavar="PATH", help="contract or bundle JSON files")
    parser.add_argument("--selftest", action="store_true", help="run the built-in positive and negative cases")
    parser.add_argument(
        "--results-out",
        default=str(DEFAULT_RESULTS),
        help="where --selftest writes the poc results CSV",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable check results")
    args = parser.parse_args(argv)

    if args.selftest:
        return 0 if run_selftest(Path(args.results_out)) else 1

    if not args.check:
        parser.print_help()
        return 2

    all_ok = True
    payload = {}
    for name in args.check:
        path = Path(name)
        if not path.is_absolute():
            path = Path.cwd() / path
        try:
            document = load_json(path)
        except (OSError, ValueError) as exc:
            all_ok = False
            print("FAIL %s: %s" % (name, exc))
            payload[name] = {"valid": False, "errors": [{"code": "CONTRACT_REQUIRED_MISSING", "path": "$", "message": str(exc)}]}
            continue
        problems = validate_document(document, "$")
        payload[name] = {"valid": not problems, "errors": [p.as_dict() for p in problems]}
        if problems:
            all_ok = False
        if not args.json:
            print_report(name, problems)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
