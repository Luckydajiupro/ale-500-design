"""Error envelope shared by every route.

The front end keys on ``code``; ``message`` is for humans and may be translated.
Codes are stable strings, not HTTP status numbers, because the workbench has to
tell "wrong state" apart from "not allowed" without guessing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class AppError(Exception):
    def __init__(
        self,
        code: str,
        status_code: int,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.message = message
        self.details = details or []

    def envelope(self, request_id: str = "") -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": request_id,
            }
        }


def not_found(object_name: str) -> AppError:
    return AppError("NOT_FOUND", 404, f"{object_name} 不存在")


def forbidden(action: str) -> AppError:
    return AppError("FORBIDDEN", 403, f"没有执行 {action} 的权限")


def unauthenticated() -> AppError:
    return AppError("UNAUTHENTICATED", 401, "缺少或无效的身份")


def conflict(code: str, message: str, details: Optional[List[Dict[str, Any]]] = None) -> AppError:
    return AppError(code, 409, message, details)


def invalid(code: str, message: str, details: Optional[List[Dict[str, Any]]] = None) -> AppError:
    return AppError(code, 422, message, details)


def idempotency_required() -> AppError:
    return AppError("IDEMPOTENCY_KEY_REQUIRED", 400, "写操作必须带 Idempotency-Key")
