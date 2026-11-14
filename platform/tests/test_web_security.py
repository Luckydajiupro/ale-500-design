"""HTTP-level authorization checks for the workbench."""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.auth import resolve_principal
from app.db import connect
from app.domain import tasks
from seed import seed
from web.app import create_app
from web.forms import empty_payload


def _csrf(html: str) -> str:
    match = re.search(r'name="csrf" value="([^"]+)"', html)
    assert match, html[:500]
    return match.group(1)


class WorkbenchSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = {
            "ALE_DB_PATH": str(self.root / "platform.db"),
            "ALE_STORAGE_ROOT": str(self.root / "objects"),
            "ALE_PACKAGE_ROOT": str(self.root / "packages"),
            "ALE_SECRET_PATH": str(self.root / "session.key"),
        }
        self.patch = patch.dict(os.environ, self.env, clear=False)
        self.patch.start()
        for key in ("ALE_DB_URL", "ALE_ASYNC_PACKAGE"):
            os.environ.pop(key, None)
        seed(self.root / "platform.db", "AleDemo123!")
        self.app = create_app()
        self.conn = connect(self.root / "platform.db")
        expert = resolve_principal(self.conn, "u_expert")
        payload = empty_payload("business_finance/private_task", "business_finance", "accounting", "u_expert")
        payload["identity"]["title_zh"] = "私有任务"
        tasks.create_draft(
            self.conn,
            expert,
            {
                "task_id": "business_finance/private_task",
                "domain_code": "business_finance",
                "subdomain_code": "accounting",
                "batch_id": "w1-demo",
                "title_zh": "私有任务",
                "source_payload": payload,
            },
        )

    def tearDown(self) -> None:
        self.conn.close()
        self.patch.stop()
        self.tmp.cleanup()

    def _login(self, email: str) -> TestClient:
        client = TestClient(self.app)
        page = client.get("/login")
        token = _csrf(page.text)
        response = client.post(
            "/login",
            data={"email": email, "password": "AleDemo123!", "csrf": token},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        return client

    def test_anonymous_task_read_redirects_to_login(self) -> None:
        client = TestClient(self.app)
        response = client.get("/tasks/business_finance/private_task", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertIn("/login", response.headers["location"])

    def test_other_expert_cannot_read_private_task(self) -> None:
        client = self._login("expert2@ale.local")
        response = client.get("/tasks/business_finance/private_task")
        self.assertEqual(response.status_code, 403)

    def test_unassigned_reviewer_cannot_read_private_task(self) -> None:
        client = self._login("reviewer@ale.local")
        response = client.get("/tasks/business_finance/private_task")
        self.assertEqual(response.status_code, 403)

    def test_owner_can_read_private_task(self) -> None:
        client = self._login("expert@ale.local")
        response = client.get("/tasks/business_finance/private_task")
        self.assertEqual(response.status_code, 200)
        self.assertIn("私有任务", response.text)


if __name__ == "__main__":
    unittest.main()
