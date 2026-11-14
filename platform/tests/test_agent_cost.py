"""Agent persistence keeps a truthful cost status."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.auth import resolve_principal
from app.db import connect
from app.domain import agent_service, tasks
from seed import seed
from web.forms import empty_payload


class AgentCostStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "platform.db"
        self.env = {
            "ALE_DB_PATH": str(self.db),
            "ALE_STORAGE_ROOT": str(self.root / "objects"),
            "ALE_PACKAGE_ROOT": str(self.root / "packages"),
            "ALE_SECRET_PATH": str(self.root / "session.key"),
            "ALE_MODEL_PROVIDER": "mock",
        }
        self.patch = patch.dict(os.environ, self.env, clear=False)
        self.patch.start()
        seed(self.db, "AleDemo123!", allow_demo=True)
        self.conn = connect(self.db)
        self.expert = resolve_principal(self.conn, "u_expert")
        self.task_id = "business_finance/agent_cost_01"
        payload = empty_payload(self.task_id, "business_finance", "accounting", "u_expert")
        payload["identity"]["title_zh"] = "成本状态任务"
        tasks.create_draft(
            self.conn,
            self.expert,
            {
                "task_id": self.task_id,
                "domain_code": "business_finance",
                "subdomain_code": "accounting",
                "batch_id": "w1-demo",
                "title_zh": "成本状态任务",
                "source_payload": payload,
            },
        )

    def tearDown(self) -> None:
        self.conn.close()
        self.patch.stop()
        self.tmp.cleanup()

    def test_mock_run_is_not_reported_as_zero_cost(self) -> None:
        result = agent_service.generate(self.conn, self.expert, self.task_id, "structuring")
        self.assertTrue(result["mock_only"])
        self.assertGreaterEqual(result["count"], 1)
        run = self.conn.execute(
            "SELECT cost_cents, cost_status, mock_only FROM agent_runs WHERE run_id = ?",
            (result["run_id"],),
        ).fetchone()
        self.assertEqual(int(run["cost_cents"]), 0)
        self.assertEqual(run["cost_status"], "not_applicable")
        self.assertEqual(int(run["mock_only"]), 1)

    def test_unknown_pricing_is_explicit_for_a_non_mock_gateway(self) -> None:
        from agent import AgentGateway, MockProvider
        from agent.config import ModelConfig

        provider = MockProvider()
        provider.name = "openai_compatible"
        provider.is_mock = False
        run = AgentGateway(provider, ModelConfig(provider="mock"))._run_record(
            run_id="run_test",
            capability="structuring",
            digest="x" * 64,
            prompt_digest="y" * 64,
            started=0.0,
            response=None,
            status="success",
            error_code=None,
            attempts=1,
            degraded=False,
            latency_ms=0,
        )
        self.assertEqual(run.cost_cents, 0)
        self.assertEqual(run.cost_status, "unknown")


if __name__ == "__main__":
    unittest.main()
