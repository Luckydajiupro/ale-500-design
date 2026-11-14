"""Canonical Task Source contract placeholder.

The expert annotation contract is owned by work line A. Until it is frozen this
module carries a deliberately small set of required keys plus the structural
rules that the platform can enforce without knowing the final schema. Routes and
services must call :func:`validate_source` instead of testing field names.

Replace ``SCHEMA_VERSION`` and the ``REQUIRED_*`` tables when v1 lands. Nothing
else in the application reads field names directly except the seed data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

# Draft marker, not a released contract. Bump when work line A publishes v1.
SCHEMA_VERSION = "canonical-draft-0"
FIELD_SOURCE = "docs/data/wave1-canonical-task-source.csv (draft subset)"

BLOCKS: Tuple[str, ...] = (
    "identity",
    "scenario",
    "materials",
    "operations",
    "deliverables",
    "success_criteria",
    "environment",
    "review",
    "provenance",
    "handoff",
)

LIST_BLOCKS: Tuple[str, ...] = ("materials", "operations", "deliverables", "success_criteria")

# Placeholder required keys. Kept short on purpose: the frozen v1 will be wider
# and the platform must not hard-code a shape it cannot yet guarantee.
REQUIRED_FIELDS: Mapping[str, Tuple[str, ...]] = {
    "identity": ("task_id", "domain_code", "subdomain_code", "title_zh", "language", "batch_id", "owner_expert_id", "difficulty_rationale"),
    "scenario": ("role", "trigger", "audience"),
    "environment": ("os", "gui_required", "gpu", "network", "resources", "nested_virt"),
    "review": ("risk_tier", "tier_rationale", "required_reviewers", "open_issues"),
    "provenance": ("author_type", "originality", "revision_history"),
    "handoff": ("target_format", "target_schema_version", "files_expected", "known_gaps", "secrets_attestation"),
}

# Fields that are platform-derived. Experts never write them; the platform fills
# them at freeze time. Present here so validation can reject expert input.
PLATFORM_DERIVED_BLOCKS: Tuple[str, ...] = ("verification", "package")

MATERIAL_ROLES: Tuple[str, ...] = ("input", "reference", "template")
MATERIAL_LAYERS: Tuple[str, ...] = ("raw", "deidentified", "work", "reference")
LICENSE_TYPES: Tuple[str, ...] = ("public_domain", "cc_by", "proprietary", "internal", "synthetic")
PII_LEVELS: Tuple[str, ...] = ("none", "low", "medium", "high")
CHECK_METHODS: Tuple[str, ...] = ("auto_script", "artifact_diff", "llm_judge", "human_rubric")

# The five groups that the wave-1 design proposes to freeze; other fields are
# versioned. Ordering here is the canonical projection order used for hashing.
CORE_FREEZE_GROUPS: Mapping[str, Tuple[str, ...]] = {
    "identity": (
        "identity.task_id",
        "identity.domain_code",
        "identity.subdomain_code",
        "identity.title_en",
        "identity.title_zh",
        "identity.language",
        "identity.batch_id",
        "identity.source_task_id",
        "identity.source_variant",
    ),
    "materials": (
        "materials.material_id",
        "materials.kind",
        "materials.role",
        "materials.path",
        "materials.sha256",
        "materials.bytes",
        "materials.license.type",
        "materials.license.redistribution",
        "materials.pii_level",
    ),
    "deliverables": (
        "deliverables.deliverable_id",
        "deliverables.path",
        "deliverables.format",
        "deliverables.mandatory",
        "deliverables.acceptance_ref",
    ),
    "success_criteria": (
        "success_criteria.criterion_id",
        "success_criteria.dimension",
        "success_criteria.check_method",
        "success_criteria.weight",
        "success_criteria.threshold",
        "success_criteria.critical",
    ),
    "environment": (
        "environment.os",
        "environment.gui_required",
        "environment.gpu.required",
        "environment.network.mode",
        "environment.resources.time_limit_min",
    ),
}


@dataclass
class Issue:
    """One structural finding, shaped like a row of ``checks``."""

    code: str
    severity: str  # blocker | warning | info
    field_path: str
    message: str

    @property
    def passed(self) -> bool:
        return False


@dataclass
class ValidationResult:
    issues: List[Issue] = field(default_factory=list)

    @property
    def blockers(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.severity == "blocker"]

    @property
    def warnings(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.blockers


def get_in(payload: Mapping[str, Any], dotted: str) -> Any:
    """Read ``a.b.c`` from nested mappings without raising."""

    node: Any = payload
    for part in dotted.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return None
        node = node[part]
    return node


def iter_materials(payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    raw = payload.get("materials")
    if isinstance(raw, Mapping):
        raw = raw.get("items")
    if not isinstance(raw, list):
        return ()
    return [item for item in raw if isinstance(item, Mapping)]


def iter_criteria(payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    raw = payload.get("success_criteria")
    if isinstance(raw, Mapping):
        raw = raw.get("items")
    if not isinstance(raw, list):
        return ()
    return [item for item in raw if isinstance(item, Mapping)]


def iter_deliverables(payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    raw = payload.get("deliverables")
    if isinstance(raw, Mapping):
        raw = raw.get("items")
    if not isinstance(raw, list):
        return ()
    return [item for item in raw if isinstance(item, Mapping)]


def _as_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def validate_source(payload: Mapping[str, Any], known_material_ids: Optional[Iterable[str]] = None) -> ValidationResult:
    """Structural validation only.

    This is the screening pass, not a quality judgement: it proves that the
    payload has the block shape, that weights add up, that every referenced
    material exists, and that licences are declared. A pass here never means the
    task is professionally sound.
    """

    result = ValidationResult()
    if not isinstance(payload, Mapping) or not payload:
        result.issues.append(Issue("SCHEMA_EMPTY", "blocker", "$", "任务源为空"))
        return result

    for block in BLOCKS:
        value = payload.get(block)
        expected = list if block in LIST_BLOCKS else Mapping
        if not isinstance(value, expected):
            result.issues.append(Issue("SCHEMA_BLOCK_MISSING", "blocker", block, f"缺少 {block} 块或类型不对"))

    for block, fields in REQUIRED_FIELDS.items():
        node = payload.get(block)
        if not isinstance(node, Mapping):
            continue
        for name in fields:
            value = node.get(name)
            if value is None or (isinstance(value, str) and not value.strip()):
                result.issues.append(
                    Issue("SCHEMA_FIELD_REQUIRED", "blocker", f"{block}.{name}", f"必填字段 {block}.{name} 为空")
                )

    for block in PLATFORM_DERIVED_BLOCKS:
        if block in payload:
            result.issues.append(
                Issue("SCHEMA_PLATFORM_OWNED", "blocker", block, f"{block} 由平台生成，专家不可写入")
            )

    identity = payload.get("identity")
    if isinstance(identity, Mapping):
        language = identity.get("language")
        if language is not None and language not in ("zh", "en", "bilingual"):
            result.issues.append(Issue("SCHEMA_ENUM", "blocker", "identity.language", "语言取值不在允许集合"))
        task_id = identity.get("task_id")
        if isinstance(task_id, str) and (" " in task_id or task_id.count("/") < 1):
            result.issues.append(
                Issue("SCHEMA_TASK_ID", "blocker", "identity.task_id", "task_id 需为 domain/slug 且不含空格")
            )

    materials = list(iter_materials(payload))
    known = set(known_material_ids or ())
    seen_material_ids = set()
    for index, item in enumerate(materials):
        path = f"materials[{index}]"
        material_id = item.get("material_id")
        if not material_id:
            result.issues.append(Issue("SCHEMA_FIELD_REQUIRED", "blocker", f"{path}.material_id", "资料缺少 material_id"))
        else:
            seen_material_ids.add(str(material_id))
            if known and str(material_id) not in known:
                result.issues.append(
                    Issue("SCHEMA_MATERIAL_UNKNOWN", "blocker", f"{path}.material_id", "引用的资料不在资料库中")
                )
        if item.get("role") not in MATERIAL_ROLES:
            result.issues.append(Issue("SCHEMA_ENUM", "blocker", f"{path}.role", "资料 role 取值非法"))
        license_node = item.get("license") if isinstance(item.get("license"), Mapping) else item
        license_type = license_node.get("type")
        if license_type not in LICENSE_TYPES:
            result.issues.append(Issue("SCHEMA_LICENSE", "blocker", f"{path}.license.type", "许可类型缺失或非法"))
        elif license_type == "proprietary" and not license_node.get("redistribution"):
            result.issues.append(
                Issue("SCHEMA_LICENSE_REDISTRIBUTION", "warning", f"{path}.license.redistribution", "专有资料不可再分发")
            )
        if item.get("pii_level") not in PII_LEVELS:
            result.issues.append(Issue("SCHEMA_PII", "blocker", f"{path}.pii_level", "PII 等级缺失或非法"))
        elif item.get("pii_level") == "high":
            result.issues.append(Issue("SCHEMA_PII_HIGH", "blocker", f"{path}.pii_level", "高危 PII 不得提交"))

    criteria = list(iter_criteria(payload))
    if not criteria:
        result.issues.append(Issue("SCHEMA_CRITERIA_EMPTY", "blocker", "success_criteria", "至少一条成功标准"))
    total_weight = 0.0
    weights_present = False
    critical = 0
    for index, item in enumerate(criteria):
        path = f"success_criteria[{index}]"
        weight = _as_number(item.get("weight"))
        if weight is not None:
            weights_present = True
            total_weight += weight
        if item.get("critical") is True:
            critical += 1
        if item.get("check_method") is not None and item.get("check_method") not in CHECK_METHODS:
            result.issues.append(Issue("SCHEMA_CHECK_METHOD", "blocker", f"{path}.check_method", "检查方式非法"))
        threshold = item.get("threshold")
        if isinstance(threshold, str) and threshold.strip() in ("", "合理", "适当", "reasonable"):
            result.issues.append(Issue("SCHEMA_THRESHOLD_VAGUE", "blocker", f"{path}.threshold", "阈值不可判定"))
    if weights_present and abs(total_weight - 100.0) > 0.01:
        result.issues.append(
            Issue("SCHEMA_WEIGHT_SUM", "blocker", "success_criteria", f"权重合计 {total_weight:g}，应为 100")
        )
    if criteria and critical == 0:
        result.issues.append(Issue("SCHEMA_CRITICAL_MISSING", "blocker", "success_criteria", "缺少 critical 标准"))

    deliverables = list(iter_deliverables(payload))
    if not deliverables:
        result.issues.append(Issue("SCHEMA_DELIVERABLE_EMPTY", "blocker", "deliverables", "至少一个交付物"))
    deliverable_paths = {
        str(item.get("path")) for item in deliverables if item.get("path")
    }
    for index, item in enumerate(deliverables):
        if not item.get("path") or not item.get("format"):
            result.issues.append(
                Issue("SCHEMA_DELIVERABLE_INCOMPLETE", "blocker", f"deliverables[{index}]", "交付物缺 path 或 format")
            )
    for criterion in criteria:
        ref = criterion.get("acceptance_ref")
        if ref and deliverable_paths and str(ref) not in deliverable_paths:
            result.issues.append(
                Issue("SCHEMA_ACCEPTANCE_REF", "blocker", "success_criteria", f"acceptance_ref {ref} 未指向交付物路径")
            )

    operations = payload.get("operations")
    if isinstance(operations, list) and len(operations) < 3:
        result.issues.append(Issue("SCHEMA_STEPS_MIN", "blocker", "operations", "至少三步且有依赖"))

    environment = payload.get("environment")
    if isinstance(environment, Mapping):
        network = environment.get("network")
        mode = network.get("mode") if isinstance(network, Mapping) else network
        if isinstance(mode, str) and mode in ("online", "any"):
            result.issues.append(Issue("SCHEMA_NETWORK", "blocker", "environment.network.mode", "默认必须离线可跑"))

    return result


def core_projection(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Return only the candidate freeze fields, in canonical order.

    The projection is what a snapshot hashes today. It is intentionally a subset:
    anything outside these five groups stays versioned and out of the freeze
    hash until the scope decision is signed.
    """

    projection: Dict[str, Any] = {}
    for group, fields in CORE_FREEZE_GROUPS.items():
        values = {}
        for name in fields:
            short = name[len(group) + 1 :] if name.startswith(group + ".") else name
            value = get_in(payload, name)
            if value is not None:
                values[short] = value
        if values:
            projection[group] = values
    return projection
