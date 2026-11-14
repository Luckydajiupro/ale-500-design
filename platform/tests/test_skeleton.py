"""Smoke tests for the platform skeleton.

The tests avoid an HTTP server and a PostgreSQL instance. They prove the seams
that the design now depends on: schema creation, the state table, canonical
structural validation, content-addressed storage and the candidate package hash.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.adapters import LocalObjectStore  # noqa: E402
from app.db import connect, initialize  # noqa: E402
from app.domain import state_machine as sm  # noqa: E402
from contracts import canonical_schema, package_contract  # noqa: E402


class SchemaTests(unittest.TestCase):
    def test_core_tables_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = connect(Path(tmp) / "platform.db")
            initialize(db, ROOT / "app" / "schema.sql")
            names = {
                row["name"]
                for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            }
            for table in (
                "tasks",
                "task_versions",
                "materials",
                "material_versions",
                "checks",
                "reviews",
                "snapshots",
                "packages",
                "ingest_records",
                "agent_suggestions",
                "audit_events",
            ):
                self.assertIn(table, names)
            db.close()

    def test_task_state_check_rejects_unknown_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = connect(Path(tmp) / "platform.db")
            initialize(db, ROOT / "app" / "schema.sql")
            db.execute(
                "INSERT INTO users (user_id, email, display_name, created_at) VALUES (?, ?, ?, ?)",
                ("u1", "u1@example.test", "U1", "2026-11-14T00:00:00Z"),
            )
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "INSERT INTO tasks (task_id, domain_code, subdomain_code, owner_expert_id, state, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("t1", "business_finance", "accounting", "u1", "bogus", "2026-11-14T00:00:00Z", "2026-11-14T00:00:00Z"),
                )
            db.close()


class StateMachineTests(unittest.TestCase):
    def test_main_path(self) -> None:
        state = sm.DRAFT
        for event, role in (
            ("submit", "expert"),
            ("auto_check_pass", "system"),
            ("start_review", "domain_reviewer"),
            ("domain_pass", "domain_reviewer"),
            ("quality_pass", "quality_reviewer"),
            ("freeze", "quality_reviewer"),
            ("package", "platform_admin"),
            ("validate_pass", "system"),
            ("ingest", "platform_admin"),
        ):
            transition = sm.assert_can(event, state, role)
            state = transition.target
        self.assertEqual(state, sm.INGESTED)

    def test_return_and_resubmit(self) -> None:
        transition = sm.assert_can("auto_check_fail", sm.SUBMITTED, "system")
        self.assertEqual(transition.target, sm.RETURNED)
        transition = sm.assert_can("submit", sm.RETURNED, "expert")
        self.assertEqual(transition.target, sm.SUBMITTED)

    def test_skipping_a_step_is_rejected(self) -> None:
        with self.assertRaises(Exception):
            sm.assert_can("freeze", sm.DRAFT, "expert")


class CanonicalValidationTests(unittest.TestCase):
    def test_empty_payload_is_a_blocker(self) -> None:
        result = canonical_schema.validate_source({})
        self.assertFalse(result.ok)
        self.assertEqual(result.blockers[0].code, "SCHEMA_EMPTY")

    def test_identity_is_required(self) -> None:
        result = canonical_schema.validate_source({"identity": {}})
        self.assertFalse(result.ok)
        self.assertTrue(any(issue.field_path.startswith("identity") for issue in result.blockers))

    def test_material_license_is_required(self) -> None:
        payload = {
            "identity": {
                "task_id": "business_finance/demo",
                "domain_code": "business_finance",
                "subdomain_code": "accounting",
                "title_zh": "示例",
                "title_en": "Demo",
                "language": "en",
            },
            "scenario": {"role": "analyst", "trigger": "close", "audience": "cfo"},
            "environment": {"os": "linux"},
            "materials": [{"material_id": "m1", "role": "input", "path": "input/a.csv"}],
        }
        result = canonical_schema.validate_source(payload)
        self.assertFalse(result.ok)
        self.assertTrue(any("license" in issue.field_path for issue in result.blockers))


class PackageContractTests(unittest.TestCase):
    def _entry(self, path: str, mode: str = "0644") -> package_contract.FileEntry:
        return package_contract.FileEntry(path=path, bytes=3, mode=mode, role="input", sha256="a" * 64)

    def test_native_hash_is_order_independent(self) -> None:
        left = package_contract.native_hash([self._entry("b.txt"), self._entry("a.txt")])
        right = package_contract.native_hash([self._entry("a.txt"), self._entry("b.txt")])
        self.assertEqual(left, right)

    def test_mode_changes_native_hash(self) -> None:
        left = package_contract.native_hash([self._entry("a.sh", "0644")])
        right = package_contract.native_hash([self._entry("a.sh", "0755")])
        self.assertNotEqual(left, right)

    def test_package_hash_ignores_its_own_field(self) -> None:
        native = "b" * 64
        sidecars = {name: "c" * 64 for name in package_contract.SIDECARS}
        base = {"task_id": "business_finance/demo", "built_at": "2026-11-14T00:00:00Z"}
        with_hash = dict(base, package_hash="d" * 64)
        self.assertEqual(
            package_contract.package_hash(native, base, sidecars),
            package_contract.package_hash(native, with_hash, sidecars),
        )

    def test_stable_field_changes_package_hash(self) -> None:
        native = "b" * 64
        sidecars = {name: "c" * 64 for name in package_contract.SIDECARS}
        left = package_contract.package_hash(native, {"task_id": "a"}, sidecars)
        right = package_contract.package_hash(native, {"task_id": "b"}, sidecars)
        self.assertNotEqual(left, right)


class ObjectStoreTests(unittest.TestCase):
    def test_same_bytes_converge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = LocalObjectStore(Path(tmp))
            first = store.put_bytes(b"same")
            second = store.put_bytes(b"same")
            self.assertEqual(first.storage_key, second.storage_key)
            self.assertEqual(store.read_bytes(first.storage_key), b"same")

    def test_key_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = LocalObjectStore(Path(tmp))
            with self.assertRaises(ValueError):
                store.path_for("../escape")


if __name__ == "__main__":
    unittest.main()
