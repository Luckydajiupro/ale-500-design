"""Translate the HTML workbench form to the canonical task source payload."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping

from starlette.datastructures import FormData

DOMAINS = (
    "business_finance", "computing_math", "education_info", "engineering",
    "health_medicine", "legal", "life_sciences", "other", "physical_sciences",
    "psychology_neuro", "social_sciences", "transport_safety", "visual_media",
    "agriculture_env",
)
DELIVERABLE_FORMATS = ("docx", "xlsx", "pptx", "pdf", "csv", "json", "py", "md", "png", "svg", "nii", "nii.gz", "obj", "blend", "dta", "sav", "rds", "h5", "tif", "other")


def _text(form: Mapping[str, Any], key: str, default: str = "") -> str:
    value = form.get(key)
    return str(value).strip() if value is not None else default


def _lines(form: Mapping[str, Any], key: str) -> List[str]:
    raw = _text(form, key)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _bool(form: Mapping[str, Any], key: str) -> bool:
    return _text(form, key).lower() in ("1", "true", "yes", "on")


def _rows(form: FormData, prefix: str, needed: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    ids = form.getlist(needed)
    for index, identifier in enumerate(ids):
        row: Dict[str, str] = {}
        for key in form.keys():
            if key.startswith(prefix + "."):
                values = form.getlist(key)
                if index < len(values):
                    row[key[len(prefix) + 1:]] = str(values[index]).strip()
        if identifier.strip():
            row[needed.split(".")[-1]] = str(identifier).strip()
            rows.append(row)
    return rows


def payload_from_form(
    form: FormData,
    *,
    existing: Dict[str, Any],
    owner_expert_id: str,
    task_id: str,
    domain_code: str,
    subdomain_code: str,
) -> Dict[str, Any]:
    identity = {
        "task_id": task_id,
        "version": int(existing.get("identity", {}).get("version") or 1),
        "domain_code": domain_code,
        "subdomain_code": subdomain_code,
        "title_zh": _text(form, "title_zh"),
        "title_en": _text(form, "title_en"),
        "language": _text(form, "language", "en"),
        "batch_id": _text(form, "batch_id", "w1-demo"),
        "owner_expert_id": owner_expert_id,
        "difficulty_rationale": _text(form, "difficulty_rationale"),
    }
    scenario = {
        "role": _text(form, "scenario_role"),
        "organization_context": _text(form, "scenario_context"),
        "trigger": _text(form, "scenario_trigger"),
        "audience": _text(form, "scenario_audience"),
        "constraints": _lines(form, "scenario_constraints") or ["Use only the supplied files."],
        "out_of_scope": _lines(form, "scenario_out_of_scope") or ["No external data."],
        "realism_evidence": _text(form, "scenario_evidence"),
    }
    materials: List[Dict[str, Any]] = []
    for row in _rows(form, "material", "material.material_id"):
        if not row.get("material_id"):
            continue
        materials.append(
            {
                "material_id": row["material_id"],
                "kind": row.get("kind") or "document",
                "role": row.get("role") or "input",
                "path": row.get("path") or ("input/" + row["material_id"]),
                "sha256": row.get("sha256") or "0" * 64,
                "bytes": int(row.get("bytes") or 0),
                "license": {"type": row.get("license") or "synthetic", "redistribution": True},
                "pii_level": row.get("pii_level") or "none",
                "used_by": ["1"],
                "synthetic_disclosure": "合成演示资料，不含真实客户数据，用于平台验收。" if (row.get("license") or "synthetic") == "synthetic" else None,
            }
        )
    for item in materials:
        if item.get("synthetic_disclosure") is None:
            item.pop("synthetic_disclosure", None)
    operations: List[Dict[str, Any]] = []
    for row in _rows(form, "operation", "operation.step_no"):
        if not row.get("action"):
            continue
        operations.append(
            {
                "step_no": int(row.get("step_no") or len(operations) + 1),
                "actor": "human",
                "action": row.get("action") or "",
                "tool": row.get("tool") or "",
                "inputs": [value.strip() for value in (row.get("inputs") or "").split(",") if value.strip()] or [item["material_id"] for item in materials] or ["M-001"],
                "expected_state": row.get("expected_state") or "Step complete",
                "checkpoint": bool(row.get("checkpoint")),
                "time_estimate_min": int(row.get("time_estimate_min") or 10),
            }
        )
    if not operations:
        operations = [
            {
                "step_no": 1,
                "actor": "human",
                "action": "Inspect the supplied material and produce the required deliverable.",
                "tool": "text editor",
                "inputs": [item["material_id"] for item in materials] or ["M-001"],
                "expected_state": "Deliverable written to the requested path",
                "checkpoint": True,
                "time_estimate_min": 20,
            }
        ]
    deliverables: List[Dict[str, Any]] = []
    for row in _rows(form, "deliverable", "deliverable.deliverable_id"):
        if not row.get("path"):
            continue
        deliverables.append(
            {
                "deliverable_id": row.get("deliverable_id") or "D-%03d" % (len(deliverables) + 1),
                "path": row.get("path") or "output/result.json",
                "format": row.get("format") or "json",
                "description": row.get("description") or "Required deliverable",
                "produced_by_step": int(row.get("produced_by_step") or 1),
                "mandatory": True,
                "acceptance_ref": [value.strip() for value in (row.get("acceptance_ref") or "C-001").split(",") if value.strip()],
            }
        )
    if not deliverables:
        deliverables = [
            {
                "deliverable_id": "D-001",
                "path": "output/result.json",
                "format": "json",
                "description": "Required result file",
                "produced_by_step": 1,
                "mandatory": True,
                "acceptance_ref": ["C-001"],
            }
        ]
    criteria: List[Dict[str, Any]] = []
    for row in _rows(form, "criterion", "criterion.criterion_id"):
        if not row.get("threshold"):
            continue
        method = row.get("check_method") or "auto_script"
        item: Dict[str, Any] = {
            "criterion_id": row.get("criterion_id") or "C-%03d" % (len(criteria) + 1),
            "dimension": row.get("dimension") or "correctness",
            "check_method": method,
            "weight": int(row.get("weight") or 100),
            "threshold": row.get("threshold") or "Exact match",
            "evidence_required": row.get("evidence_required") or "Output file and check log",
            "critical": bool(row.get("critical")),
        }
        if method != "human_rubric":
            item["verifier_hint"] = row.get("verifier_hint") or "Compare the declared output against the acceptance rule."
        criteria.append(item)
    if not criteria:
        criteria = [
            {
                "criterion_id": "C-001",
                "dimension": "correctness",
                "check_method": "auto_script",
                "weight": 100,
                "threshold": "Exact match",
                "evidence_required": "Output file and check log",
                "verifier_hint": "Compare the declared output against the acceptance rule.",
                "critical": True,
            }
        ]
    software = []
    for line in _lines(form, "software"):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 4:
            software.append({"name": parts[0], "version": parts[1], "license_type": parts[2], "install_method": parts[3]})
    if not software:
        software = [{"name": "LibreOffice", "version": "7.6", "license_type": "MPL-2.0", "install_method": "system package"}]
    reviewers = []
    for line in _lines(form, "required_reviewers"):
        if ":" in line:
            role, count = line.split(":", 1)
            reviewers.append({"role": role.strip(), "count": int(count.strip() or 1)})
    if not reviewers:
        reviewers = [{"role": "domain_reviewer", "count": 1}, {"role": "quality_reviewer", "count": 1}]
    sources = []
    for line in _lines(form, "sources"):
        parts = [part.strip() for part in line.split("|")]
        if parts and parts[0]:
            sources.append({"source_id": parts[0], "url_or_path": parts[1] if len(parts) > 1 else "platform://synthetic"})
    if not sources:
        sources = [{"source_id": "S-001", "url_or_path": "platform://synthetic", "note": "Synthetic demo source"}]
    environment = {
        "os": _text(form, "os", "linux"),
        "os_version": _text(form, "os_version"),
        "gui_required": _text(form, "gui_required", "no"),
        "gpu": {"required": _bool(form, "gpu_required")},
        "software": software,
        "network": {"mode": _text(form, "network_mode", "none")},
        "resources": {
            "cpu": int(_text(form, "cpu", "2")),
            "ram_gb": int(_text(form, "ram_gb", "4")),
            "disk_gb": int(_text(form, "disk_gb", "20")),
            "time_limit_min": int(_text(form, "time_limit_min", "60")),
        },
        "nested_virt": _bool(form, "nested_virt"),
    }
    if environment["network"]["mode"] == "online-required":
        environment["network"]["justification"] = _text(form, "network_justification")
    review = {
        "risk_tier": _text(form, "risk_tier", "medium"),
        "tier_rationale": _text(form, "tier_rationale"),
        "required_reviewers": reviewers,
        "open_issues": [],
    }
    provenance = {
        "author_type": "human",
        "sources": sources,
        "originality": {"not_copied": True},
        "revision_history": [],
    }
    handoff = {
        "target_format": "ale_task_toml",
        "target_schema_version": "1.4+ale.1",
        "files_expected": [item["path"] for item in deliverables],
        "known_gaps": _text(form, "known_gaps"),
        "secrets_attestation": _bool(form, "secrets_attestation"),
    }
    return {
        "identity": identity,
        "scenario": scenario,
        "materials": materials,
        "operations": operations,
        "deliverables": deliverables,
        "success_criteria": criteria,
        "environment": environment,
        "review": review,
        "provenance": provenance,
        "handoff": handoff,
    }


def empty_payload(task_id: str, domain_code: str, subdomain_code: str, owner: str) -> Dict[str, Any]:
    from types import SimpleNamespace

    return payload_from_form(
        FormData([]),
        existing={},
        owner_expert_id=owner,
        task_id=task_id,
        domain_code=domain_code,
        subdomain_code=subdomain_code,
    )
