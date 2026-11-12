"""Minimal round-trip test for the ale-data <-> Harbor contract.

Run from this directory:  python3 -m unittest -v tests/test_roundtrip.py
or:                       python3 tests/test_roundtrip.py

The fixture is a structural copy of
``03_ale-data/task-data-v1.1/legal/legal_dr_fees_01``: the brief, contract,
case data, runtime manifest and answer key are the real files; the seven PDFs
are byte-identical stand-ins with the real Chinese filenames, because the test
must not carry 1 MB of licensed material.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ale_data_format as fmt  # noqa: E402

FIXTURE = HERE / "fixtures/legal_dr_fees_01/base"


class ImportValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ale-pkg-"))
        self.pkg = self.tmp / "base"
        shutil.copytree(FIXTURE, self.pkg)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def codes(self):
        return [finding["code"] for finding in fmt.errors(fmt.validate_package(self.pkg))]

    def test_valid_package_passes(self):
        findings = fmt.validate_package(self.pkg)
        self.assertEqual(fmt.errors(findings), [], findings)

    def test_missing_output_contract_is_rejected(self):
        (self.pkg / "input/output_contract.json").unlink()
        self.assertIn("IMPORT_MISSING_FILE", self.codes())

    def test_missing_answer_key_is_rejected(self):
        (self.pkg / "reference/answer_key.json").unlink()
        self.assertIn("IMPORT_MISSING_FILE", self.codes())

    def test_one_byte_tamper_is_rejected(self):
        target = self.pkg / "input/cases.json"
        target.write_bytes(target.read_bytes() + b" ")
        self.assertIn("IMPORT_HASH_MISMATCH", self.codes())

    def test_unlisted_file_is_rejected(self):
        (self.pkg / "input/extra.txt").write_text("not in manifest\n", encoding="utf-8")
        self.assertIn("IMPORT_HASH_MISMATCH", self.codes())

    def test_missing_license_is_rejected(self):
        package = json.loads((self.pkg / "PACKAGE.json").read_text(encoding="utf-8"))
        package["license"] = {"redistributable": True}
        (self.pkg / "PACKAGE.json").write_text(json.dumps(package), encoding="utf-8")
        self.assertIn("IMPORT_LICENSE_MISSING", self.codes())

    def test_unsupported_version_is_rejected(self):
        package = json.loads((self.pkg / "PACKAGE.json").read_text(encoding="utf-8"))
        package["ale_data_version"] = "task-data-v1.0"
        (self.pkg / "PACKAGE.json").write_text(json.dumps(package), encoding="utf-8")
        self.assertIn("IMPORT_VERSION_UNSUPPORTED", self.codes())

    def test_bad_slug_is_rejected(self):
        package = json.loads((self.pkg / "PACKAGE.json").read_text(encoding="utf-8"))
        package["task_id"] = "legal/UPPER"
        (self.pkg / "PACKAGE.json").write_text(json.dumps(package), encoding="utf-8")
        self.assertIn("IMPORT_SLUG_INVALID", self.codes())


class HarborConversionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ale-harbor-"))
        self.pkg = self.tmp / "base"
        shutil.copytree(FIXTURE, self.pkg)
        self.task = self.tmp / "task"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_generated_folder_has_harbor_required_files(self):
        fmt.to_harbor(self.pkg, self.task)
        for rel in (
            "task.toml",
            "instruction.md",
            "environment/Dockerfile",
            "tests/test.sh",
            "tests/verify.py",
            "solution/solve.sh",
        ):
            self.assertTrue((self.task / rel).is_file(), rel)

    def test_task_toml_carries_schema_and_mapping(self):
        fmt.to_harbor(self.pkg, self.task)
        config = fmt._read_toml((self.task / "task.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["schema_version"], fmt.HARBOR_SCHEMA)
        self.assertEqual(config["task"]["name"], "agentslastexam/legal_dr_fees_01")
        self.assertEqual(config["environment"]["os"], "linux")
        self.assertEqual(config["environment"]["gpus"], 0)
        self.assertEqual(config["agent"]["network_mode"], "no-network")
        self.assertEqual(
            config["artifacts"],
            ["/media/user/data/agenthle/legal_compliance/legal_dr_fees_01/base/output/arbitration_fee_results.json"],
        )

    def test_instruction_is_verbatim(self):
        fmt.to_harbor(self.pkg, self.task)
        self.assertEqual(
            (self.task / "instruction.md").read_bytes(),
            (self.pkg / "input/task_brief.md").read_bytes(),
        )

    def test_roundtrip_is_lossless(self):
        before = fmt.canonical_package_hash(self.pkg)
        conversion = fmt.to_harbor(self.pkg, self.task)
        back = self.tmp / "back"
        fmt.from_harbor(self.task, back)
        self.assertEqual(fmt.errors(fmt.validate_package(back)), [])
        self.assertEqual(fmt.canonical_package_hash(back), before)
        self.assertEqual(conversion["ale_data_version"], fmt.ALEDATA_VERSION)
        self.assertEqual(conversion["harbor_schema_version"], fmt.HARBOR_SCHEMA)

    def test_missing_oracle_still_converts_but_is_marked(self):
        package = json.loads((self.pkg / "PACKAGE.json").read_text(encoding="utf-8"))
        package["oracle"] = False
        (self.pkg / "PACKAGE.json").write_text(json.dumps(package), encoding="utf-8")
        conversion = fmt.to_harbor(self.pkg, self.task)
        self.assertFalse(conversion["oracle"])
        self.assertIn("NO_ORACLE", (self.task / "solution/solve.sh").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
