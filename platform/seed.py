#!/usr/bin/env python3
"""Create local demo roles, users and one batch.

The seed is idempotent. Passwords are printed only for local development and
can be overridden with ``ALE_SEED_PASSWORD``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapters import now  # noqa: E402
from app.db import connect, initialize, is_postgres, run_migrations, transaction  # noqa: E402
from app.repo import users as user_repo  # noqa: E402
from web.security import hash_password  # noqa: E402

DEFAULT_PASSWORD = os.environ.get("ALE_SEED_PASSWORD", "AleDemo123!")
_TRUTHY = {"1", "true", "yes", "on"}


def demo_seed_allowed(env=None) -> bool:
    """Demo identities must be explicit outside a local environment."""

    environment = os.environ if env is None else env
    if str(environment.get("ALE_ALLOW_DEMO_SEED", "")).strip().lower() in _TRUTHY:
        return True
    return str(environment.get("ALE_ENV", "production")).strip().lower() == "local"
USERS = (
    ("u_expert", "expert@ale.local", "王会计", "expert", "business_finance/accounting"),
    ("u_expert2", "expert2@ale.local", "周工程", "expert", "engineering/building"),
    ("u_domain", "reviewer@ale.local", "李评审", "domain_reviewer", "business_finance/accounting"),
    ("u_quality", "quality@ale.local", "陈质量", "quality_reviewer", "*/*"),
    ("u_admin", "admin@ale.local", "赵管理员", "platform_admin", "*/*"),
    ("u_lead", "lead@ale.local", "项目负责人", "project_lead", "*/*"),
)
ROLE_NAMES = {
    "expert": "专家",
    "domain_reviewer": "领域评审",
    "quality_reviewer": "质量审核",
    "platform_admin": "平台管理员",
    "engineer": "工程接口人",
    "project_lead": "项目负责人",
}


def seed(database, password: str, allow_demo: Optional[bool] = None) -> None:
    if allow_demo is None:
        allow_demo = demo_seed_allowed()
    if not allow_demo:
        raise RuntimeError(
            "拒绝在非本地环境创建演示账号；如确需创建，设置 ALE_ALLOW_DEMO_SEED=1"
        )
    conn = connect(database)
    if is_postgres(conn):
        run_migrations(conn, ROOT / "pg" / "migrations")
    else:
        initialize(conn, ROOT / "app" / "schema.sql")
        run_migrations(conn, ROOT / "migrations")
    with transaction(conn):
        user_repo.create_batch(conn, "w1-demo", "W1 演示批次", 30, "active")
        for role, name in ROLE_NAMES.items():
            user_repo.upsert_role(conn, role, name)
        for user_id, email, display_name, role, scope in USERS:
            existing = user_repo.get_user(conn, user_id)
            if existing is None:
                user_repo.create_user(conn, user_id, email, display_name, "active", now())
            domain, subdomain = scope.split("/", 1)
            user_repo.grant_role(
                conn,
                "ur_%s_%s" % (user_id, role),
                user_id,
                role,
                now(),
                scope_domain=domain,
                scope_subdomain=subdomain,
                scope_batch="*",
            )
            conn.execute(
                """INSERT INTO user_credentials (user_id, password_hash, updated_at)
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET password_hash = excluded.password_hash,
                                                     updated_at = excluded.updated_at""",
                (user_id, hash_password(password), now()),
            )
    conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=os.environ.get("ALE_DB_URL") or os.environ.get("ALE_DB_PATH", str(ROOT / "var" / "platform.db")))
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--allow-demo", action="store_true", help="allow demo users outside local")
    args = parser.parse_args()
    seed(args.db, args.password, allow_demo=True if args.allow_demo else None)
    print("seeded %s" % args.db)
    for user_id, email, display_name, role, scope in USERS:
        print("%s  %s  %s  %s  %s" % (user_id, email, display_name, role, scope))
    print("password: %s" % args.password)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
