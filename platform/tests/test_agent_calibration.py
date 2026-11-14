"""The calibration harness must distinguish mock flow from live quality."""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "agent_calibration", ROOT / "tools/wave5/agent_calibration.py"
)
assert SPEC and SPEC.loader
CALIBRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CALIBRATION)


class CalibrationTests(unittest.TestCase):
    def test_mock_flow_covers_five_capabilities_without_live_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"ALE_MODEL_PROVIDER": "mock"}, clear=False
        ):
            report = CALIBRATION.run(
                Path(tmp) / "calibration.json",
                ROOT / "tools/wave5/calibration-task.json",
            )
        self.assertEqual(report["status"], "MOCK_FLOW_ONLY")
        self.assertTrue(report["flow_compatible"])
        self.assertFalse(report["live_pass"])
        self.assertTrue(report["reference_removed_before_prompt"])
        self.assertEqual(
            {row["capability"] for row in report["capabilities"]},
            {"interview", "followup", "structuring", "precheck", "review_assist"},
        )
        self.assertTrue(all(row["path_contract_ok"] for row in report["capabilities"]))
        self.assertTrue(all(row["ok"] for row in report["resilience"]))


if __name__ == "__main__":
    unittest.main()
