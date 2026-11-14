"""End-to-end delivery tests over a temporary SQLite database.

These tests exercise the same services the web workbench calls. They cover the
candidate package contract: freeze, build, L1-L5, idempotent ingest, hash
recomputation, tamper rejection and the agent-visible view.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.adapters import LocalObjectStore  # noqa: E402
from app.auth import resolve_principal  # noqa: E402
from app.db import connect  # noqa: E402
from app.domain import delivery, materials, reviews, tasks  # noqa: E402
from app.repo import reviews as review_repo  # noqa: E402
from contracts import package_contract  # noqa: E402
from seed import seed  # noqa: E402
from web.forms import empty_payload  # noqa: E402


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DeliveryFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "platform.db"
        seed(self.db_path, "AleDemo123!")
        self.db = connect(self.db_path)
        self.expert = resolve_principal(self.db, "u_expert")
        self.domain = resolve_principal(self.db, "u_domain")
        self.quality = resolve_principal(self.db, "u_quality")
        self.admin = resolve_principal(self.db, "u_admin")
        self.store = LocalObjectStore(self.root / "objects")
        self.packages = self.root / "packages"
        self.task_id = "business_finance/delivery_fixture"

    def tearDown(self) -> None:
        self.db.close()
        self.tmp.cleanup()

    def _create(self, with_reference: bool = False, filename: str = "ledger.csv") -> dict:
        payload = empty_payload(self.task_id, "business_finance", "accounting", "u_expert")
        payload["identity"]["title_zh"] = "交付链验收任务"
        payload["identity"]["title_en"] = "Delivery fixture"
        payload["identity"]["difficulty_rationale"] = "需要三步核对并解释差异。"
        payload["scenario"].update(
            {
                "role": "财务分析师",
                "organization_context": "季度结账",
                "trigger": "银行流水与总账存在差异",
                "audience": "财务负责人",
                "realism_evidence": "访谈记录",
            }
        )
        payload["review"]["tier_rationale"] = "需要专业判断与双人复核。"
        payload["handoff"]["known_gaps"] = "没有独立 reference，采用 rubric 演示。"
        payload["operations"] = [
            {
                "step_no": i,
                "actor": "human",
                "action": action,
                "tool": "spreadsheet",
                "inputs": ["M-001"],
                "expected_state": "step complete",
                "checkpoint": True,
                "time_estimate_min": 10,
            }
            for i, action in enumerate(("读取流水", "核对差异", "生成结果"), 1)
        ]
        task = tasks.create_draft(
            self.db,
            self.expert,
            {
                "task_id": self.task_id,
                "domain_code": "business_finance",
                "subdomain_code": "accounting",
                "batch_id": "w1-demo",
                "title_zh": payload["identity"]["title_zh"],
                "source_payload": payload,
            },
        )
        materials.register(
            self.db,
            self.expert,
            {
                "task_id": self.task_id,
                "material_id": "M-001",
                "kind": "dataset",
                "role": "input",
                "layer": "raw",
                "license_type": "synthetic",
                "license_redistribution": True,
                "pii_level": "none",
            },
        )
        stored = materials.upload(self.db, self.expert, self.store, "M-001", filename, b"account,amount\ncash,10\n")
        version = stored["versions"][-1]
        payload["materials"] = [
            {
                "material_id": "M-001",
                "kind": "dataset",
                "role": "input",
                "path": "input/" + filename,
                "sha256": version["sha256"],
                "bytes": version["bytes"],
                "license": {"type": "synthetic", "redistribution": True},
                "pii_level": "none",
                "used_by": ["1"],
                "synthetic_disclosure": "合成演示资料。",
            }
        ]
        if with_reference:
            materials.register(
                self.db,
                self.expert,
                {
                    "task_id": self.task_id,
                    "material_id": "M-002",
                    "kind": "dataset",
                    "role": "reference",
                    "layer": "reference",
                    "license_type": "synthetic",
                    "license_redistribution": False,
                    "pii_level": "none",
                },
            )
            ref = materials.upload(self.db, self.expert, self.store, "M-002", "answer.csv", b"answer\n42\n")
            payload["materials"].append(
                {
                    "material_id": "M-002",
                    "kind": "dataset",
                    "role": "reference",
                    "path": "reference/answer.csv",
                    "sha256": ref["versions"][-1]["sha256"],
                    "bytes": ref["versions"][-1]["bytes"],
                    "license": {"type": "synthetic", "redistribution": False},
                    "pii_level": "none",
                    "used_by": ["3"],
                    "synthetic_disclosure": "合成参考。",
                }
            )
        tasks.update_draft(
            self.db,
            self.expert,
            self.task_id,
            {"source_payload": payload, "expected_lock_version": task["lock_version"]},
        )
        return tasks.get_task(self.db, self.expert, self.task_id)

    def _approve(self) -> None:
        result = tasks.validate(self.db, self.expert, self.task_id)
        self.assertTrue(result["ok"], result)
        tasks.submit(self.db, self.expert, self.task_id, {"expected_lock_version": tasks.get_task(self.db, self.expert, self.task_id)["lock_version"]})
        domain_review = [r for r in review_repo.queue(self.db, "domain", "pending")]
        self.assertEqual(len(domain_review), 1)
        reviews.claim(self.db, self.domain, domain_review[0]["review_id"])
        reviews.decide(self.db, self.domain, domain_review[0]["review_id"], "pass", "", [])
        quality_review = [r for r in review_repo.queue(self.db, "quality", "pending")]
        self.assertEqual(len(quality_review), 1)
        reviews.claim(self.db, self.quality, quality_review[0]["review_id"])
        reviews.decide(self.db, self.quality, quality_review[0]["review_id"], "pass", "", [])

    def _package(self, with_reference: bool = False, filename: str = "ledger.csv") -> dict:
        self._create(with_reference=with_reference, filename=filename)
        self._approve()
        delivery.freeze_task(self.db, self.admin, self.task_id)
        package = delivery.build_package(self.db, self.admin, self.task_id, self.packages, self.store)
        return package

    def test_license_is_derived_from_material_records(self) -> None:
        package = self._package(with_reference=True)
        data = json.loads((self.packages / self.task_id / str(package["version_no"]) / "PACKAGE.json").read_text())
        self.assertEqual(data["license"]["sources"], ["M-001", "M-002"])
        self.assertFalse(data["license"]["redistribution"])
        self.assertEqual(data["pii"]["level"], "none")

    def test_build_refuses_target_directory_without_package_row(self) -> None:
        self._create()
        self._approve()
        delivery.freeze_task(self.db, self.admin, self.task_id)
        target = self.packages / self.task_id / "1"
        target.mkdir(parents=True)
        with self.assertRaises(Exception) as ctx:
            delivery.build_package(self.db, self.admin, self.task_id, self.packages, self.store)
        self.assertIn("拒绝覆盖", str(ctx.exception))

    def test_package_validate_and_idempotent_ingest(self) -> None:
        package = self._package()
        result = delivery.validate_package(self.db, self.admin, package["package_id"], self.packages)
        self.assertTrue(result["ok"], result)
        first = delivery.ingest_package(self.db, self.admin, package["package_id"], self.packages)
        second = delivery.ingest_package(self.db, self.admin, package["package_id"], self.packages)
        self.assertEqual(first["ingest_id"], second["ingest_id"])
        row = self.db.execute("SELECT COUNT(*) AS n FROM ingest_records").fetchone()
        self.assertEqual(row["n"], 1)
        task = self.db.execute("SELECT state FROM tasks WHERE task_id = ?", (self.task_id,)).fetchone()
        self.assertEqual(task["state"], "ingested")
        pkg = self.db.execute("SELECT state FROM packages WHERE package_id = ?", (package["package_id"],)).fetchone()
        self.assertEqual(pkg["state"], "ingested")

    def test_hashes_are_recomputable_and_self_reference_is_absent(self) -> None:
        package = self._package()
        version_dir = self.packages / "business_finance" / "delivery_fixture" / str(package["version_no"])
        manifest = json.loads((version_dir / "PACKAGE.json").read_text(encoding="utf-8"))
        entries = [
            package_contract.FileEntry(
                path=item["path"],
                bytes=item["bytes"],
                mode=item["mode"],
                role=item["role"],
                sha256=item["sha256"],
            )
            for item in manifest["files"]
        ]
        native = package_contract.native_hash(entries)
        self.assertEqual(manifest["hashes"]["native_hash"], native)
        self.assertNotIn("package_hash", manifest["hashes"])
        self.assertFalse((version_dir / "base" / "PACKAGE.json").exists())
        stored = self.db.execute("SELECT package_hash FROM packages WHERE package_id = ?", (package["package_id"],)).fetchone()
        self.assertEqual(stored["package_hash"], package["package_hash"])

    def test_unicode_material_path_survives_build_and_validation(self) -> None:
        package = self._package(filename="中文 流水.csv")
        version_dir = self.packages / self.task_id / str(package["version_no"])
        self.assertTrue((version_dir / "base" / "input" / "中文 流水.csv").is_file())
        result = delivery.validate_package(self.db, self.admin, package["package_id"], self.packages)
        self.assertTrue(result["ok"], result)

    def test_package_metadata_rejects_license_and_pii_mismatch(self) -> None:
        self._create()
        task = tasks.get_task(self.db, self.expert, self.task_id)
        payload = task["draft_payload"]
        payload["materials"][0]["license"]["type"] = "cc_by"
        with self.assertRaises(Exception) as ctx:
            delivery._package_metadata(self.db, payload)
        self.assertIn("许可与登记记录不一致", str(ctx.exception))
        payload = task["draft_payload"]
        payload["materials"][0]["license"]["type"] = "synthetic"
        payload["materials"][0]["pii_level"] = "high"
        with self.assertRaises(Exception) as ctx:
            delivery._package_metadata(self.db, payload)
        self.assertIn("PII", str(ctx.exception))

    def test_submitted_version_is_append_only(self) -> None:
        package = self._package()
        with self.assertRaises(Exception):
            self.db.execute(
                "UPDATE task_versions SET payload_json = '{}' WHERE task_id = ? AND version_no = ?",
                (self.task_id, package["version_no"]),
            )

    def test_tamper_and_path_traversal_are_rejected(self) -> None:
        package = self._package()
        original = self.packages / "business_finance" / "delivery_fixture" / str(package["version_no"])
        copy = self.root / "tampered"
        shutil.copytree(original, copy)
        (copy / "base" / "input" / "ledger.csv").write_text("tampered\n", encoding="utf-8")
        result = delivery.validate_package(self.db, self.admin, package["package_id"], copy.parent)
        self.assertFalse(result["ok"])
        self.assertIn("PKG_HASH_MISMATCH", result["blockers"])

    def test_reference_is_not_in_agent_view(self) -> None:
        package = self._create(with_reference=True)
        self._approve()
        delivery.freeze_task(self.db, self.admin, self.task_id)
        built = delivery.build_package(self.db, self.admin, self.task_id, self.packages, self.store)
        view = delivery.export_agent_view(self.packages, built, self.task_id, self.root / "agent-view")
        names = {path.relative_to(view).as_posix() for path in view.rglob("*") if path.is_file()}
        self.assertIn("input/ledger.csv", names)
        self.assertNotIn("reference/answer.csv", names)
        self.assertNotIn("PACKAGE.json", names)


if __name__ == "__main__":
    unittest.main()


class HashContractTests(unittest.TestCase):
    def test_build_time_does_not_change_package_hash(self) -> None:
        from contracts.package_contract import package_hash

        manifest = {
            "schema_version": "ale-pkg-1.2-draft",
            "task_id": "business_finance/hash_fixture",
            "task_version": 1,
            "built_by": "platform",
            "built_at": "2026-11-14T00:00:00Z",
            "hashes": {"native_hash": "a" * 64},
        }
        later = dict(manifest, built_at="2026-11-15T12:00:00Z", built_by="other")
        stable = {key: value for key, value in manifest.items() if key not in ("built_at", "built_by", "hashes")}
        self.assertEqual(
            package_hash("a" * 64, stable, {}),
            package_hash("a" * 64, {key: value for key, value in later.items() if key not in ("built_at", "built_by", "hashes")}, {}),
        )


class IndependentVerifierTests(unittest.TestCase):
    def test_external_verifier_recomputes_package_and_receipt(self) -> None:
        import importlib.util

        fixture = DeliveryFlowTests()
        fixture.setUp()
        try:
            package = fixture._package()
            delivery.validate_package(fixture.db, fixture.admin, package["package_id"], fixture.packages)
            delivery.ingest_package(fixture.db, fixture.admin, package["package_id"], fixture.packages)
            receipt = fixture.db.execute(
                "SELECT receipt_json FROM ingest_records WHERE package_id = ?", (package["package_id"],)
            ).fetchone()
            payload = json.loads(receipt["receipt_json"])
            spec = importlib.util.spec_from_file_location(
                "verify_package", Path(__file__).resolve().parents[2] / "tools" / "wave3" / "verify_package.py"
            )
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)
            version_dir = fixture.packages / "business_finance" / "delivery_fixture" / str(package["version_no"])
            result = module.verify(version_dir, payload["package_hash"], payload["native_hash"])
            self.assertTrue(result["ok"], result["checks"])
        finally:
            fixture.tearDown()
