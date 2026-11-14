"""Identity, roles and permission checks.

The skeleton authenticates with an ``X-Actor-Id`` header resolved against the
users table. Real deployments swap :func:`resolve_principal` for the magic-link
session adapter; nothing downstream changes because services only see a
Principal.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

from .errors import forbidden, unauthenticated

# Six human roles plus one service account. The seventh user group, the partner
# contact, never logs in and therefore has no role.
ROLE_EXPERT = "expert"
ROLE_DOMAIN_REVIEWER = "domain_reviewer"
ROLE_QUALITY_REVIEWER = "quality_reviewer"
ROLE_PLATFORM_ADMIN = "platform_admin"
ROLE_ENGINEER = "engineer"
ROLE_PROJECT_LEAD = "project_lead"
ROLE_AGENT_SERVICE = "agent_service"

HUMAN_ROLES: Tuple[str, ...] = (
    ROLE_EXPERT,
    ROLE_DOMAIN_REVIEWER,
    ROLE_QUALITY_REVIEWER,
    ROLE_PLATFORM_ADMIN,
    ROLE_ENGINEER,
    ROLE_PROJECT_LEAD,
)
ALL_ROLES: Tuple[str, ...] = HUMAN_ROLES + (ROLE_AGENT_SERVICE,)

# Permission names are verbs on objects. Services call require() with these
# constants; routes declare them so the OpenAPI document is the access matrix.
PERMISSIONS: Dict[str, FrozenSet[str]] = {
    ROLE_EXPERT: frozenset(
        {
            "task:create",
            "task:read:own",
            "task:edit:own",
            "task:validate:own",
            "task:submit:own",
            "material:write:own",
            "material:read:own",
            "agent:confirm:own",
            "review:read:own-task",
        }
    ),
    ROLE_DOMAIN_REVIEWER: frozenset(
        {
            "task:read:assigned",
            "review:queue:domain",
            "review:claim",
            "review:decide",
            "review:item:write",
            "material:read:review",
        }
    ),
    ROLE_QUALITY_REVIEWER: frozenset(
        {
            "task:read:all",
            "review:queue:quality",
            "review:claim",
            "review:decide",
            "review:item:write",
            "review:assign",
            "freeze:create",
            "audit:read",
            "agent:read:runs",
            "material:read:review",
        }
    ),
    ROLE_PLATFORM_ADMIN: frozenset(
        {
            "task:read:all",
            "review:assign",
            "freeze:create",
            "package:create",
            "package:read",
            "package:validate",
            "ingest:create",
            "ingest:read",
            "batch:manage",
            "user:manage",
            "audit:read",
            "agent:read:runs",
            "material:read:all",
        }
    ),
    ROLE_ENGINEER: frozenset({"package:read", "snapshot:read", "ingest:read", "handoff:write"}),
    ROLE_PROJECT_LEAD: frozenset(
        {"task:read:all", "batch:manage", "audit:read", "stats:read", "freeze:create", "ingest:read"}
    ),
    ROLE_AGENT_SERVICE: frozenset({"agent:suggest", "task:read:agent-view", "material:read:agent-view"}),
}

# Which material layers each role may read. raw is the author plus privacy and
# admin; reference is closed to reviewers until the task passes review.
LAYER_ACCESS: Dict[str, FrozenSet[str]] = {
    ROLE_EXPERT: frozenset({"raw", "deidentified", "work", "reference"}),
    ROLE_DOMAIN_REVIEWER: frozenset({"deidentified", "work"}),
    ROLE_QUALITY_REVIEWER: frozenset({"deidentified", "work", "reference"}),
    ROLE_PLATFORM_ADMIN: frozenset({"raw", "deidentified", "work", "reference"}),
    ROLE_ENGINEER: frozenset({"deidentified", "work", "reference"}),
    ROLE_PROJECT_LEAD: frozenset({"deidentified", "work", "reference"}),
    ROLE_AGENT_SERVICE: frozenset({"deidentified", "work"}),
}


@dataclass(frozen=True)
class Scope:
    domain: str = "*"
    subdomain: str = "*"
    batch: str = "*"

    def covers(self, domain: str, subdomain: str, batch: Optional[str]) -> bool:
        if self.domain not in ("*", domain):
            return False
        if self.subdomain not in ("*", subdomain):
            return False
        if self.batch in ("*", None):
            return True
        return batch is not None and self.batch == batch


@dataclass
class Principal:
    user_id: str
    display_name: str
    roles: Dict[str, List[Scope]] = field(default_factory=dict)

    @property
    def role_codes(self) -> Set[str]:
        return set(self.roles)

    def permissions(self) -> Set[str]:
        granted: Set[str] = set()
        for role in self.roles:
            granted |= PERMISSIONS.get(role, frozenset())
        return granted

    def has(self, permission: str) -> bool:
        return permission in self.permissions()

    def scopes(self, role: str) -> Sequence[Scope]:
        return self.roles.get(role, ())

    def can_in_scope(self, permission: str, domain: str, subdomain: str, batch: Optional[str]) -> bool:
        for role, scopes in self.roles.items():
            if permission not in PERMISSIONS.get(role, frozenset()):
                continue
            if any(scope.covers(domain, subdomain, batch) for scope in scopes):
                return True
        return False

    def layer_allowed(self, layer: str) -> bool:
        for role in self.roles:
            if layer in LAYER_ACCESS.get(role, frozenset()):
                return True
        return False


def resolve_principal(conn: sqlite3.Connection, actor_id: Optional[str]) -> Principal:
    if not actor_id:
        raise unauthenticated()
    row = conn.execute(
        "SELECT user_id, display_name, status FROM users WHERE user_id = ?", (actor_id,)
    ).fetchone()
    if row is None or row["status"] != "active":
        raise unauthenticated()
    grants = conn.execute(
        "SELECT role_code, scope_domain, scope_subdomain, scope_batch FROM user_roles WHERE user_id = ?",
        (actor_id,),
    ).fetchall()
    roles: Dict[str, List[Scope]] = {}
    for grant in grants:
        roles.setdefault(grant["role_code"], []).append(
            Scope(grant["scope_domain"], grant["scope_subdomain"], grant["scope_batch"])
        )
    return Principal(user_id=row["user_id"], display_name=row["display_name"], roles=roles)


def require(principal: Principal, permission: str) -> None:
    if not principal.has(permission):
        raise forbidden(permission)


def require_any(principal: Principal, permissions: Iterable[str]) -> None:
    if not any(principal.has(permission) for permission in permissions):
        raise forbidden("/".join(sorted(permissions)))
