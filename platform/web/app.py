"""Server-rendered expert workbench.

The workbench is a thin HTTP layer over the domain services. It deliberately
does not own business rules: every state change goes through the same service
functions the tests and the API surface use.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.adapters import LocalObjectStore, new_id, now
from app.auth import Principal, resolve_principal
from app.db import connect, initialize, run_migrations, transaction
from app.domain import agent_service
from app.domain import delivery as delivery_service
from app.domain import jobs as job_service
from app.domain import materials as material_service
from app.domain import reviews as review_service
from app.domain import state_machine as sm
from app.domain import tasks as task_service
from app.errors import AppError
from app.repo import delivery as delivery_repo
from app.repo import jobs as job_repo
from app.repo import reviews as review_repo
from app.repo import tasks as task_repo
from contracts import canonical_schema
from web.forms import DOMAINS, DELIVERABLE_FORMATS, empty_payload, payload_from_form
from web.security import COOKIE_NAME, SESSION_MAX_AGE, SessionCodec, check_csrf, csrf_token, load_secret, verify_password

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Jinja2Templates(directory=str(ROOT / "web" / "templates"))


class Settings:
    def __init__(self, repo_root: Path = ROOT) -> None:
        import os

        self.database_url = os.environ.get("ALE_DB_URL", "").strip()
        self.database_path = Path(os.environ.get("ALE_DB_PATH", str(repo_root / "var" / "platform.db")))
        self.database = self.database_url or self.database_path
        self.storage_root = Path(os.environ.get("ALE_STORAGE_ROOT", str(repo_root / "var" / "objects")))
        self.package_root = Path(os.environ.get("ALE_PACKAGE_ROOT", str(repo_root / "var" / "packages")))
        self.secret_path = Path(os.environ.get("ALE_SECRET_PATH", str(repo_root / "var" / "session.key")))
        self.is_postgres = bool(self.database_url)

    @property
    def bootstrap_schema(self) -> Path:
        return ROOT / "pg" / "schema.sql" if self.is_postgres else ROOT / "app" / "schema.sql"


class RedirectLogin(Exception):
    pass


def _session(request: Request) -> Dict[str, Any]:
    codec: SessionCodec = request.app.state.codec
    data = codec.decode(request.cookies.get(COOKIE_NAME))
    if not isinstance(data, dict):
        data = {}
    data.setdefault("csrf", csrf_token(data))
    return data


def _principal(conn: sqlite3.Connection, request: Request) -> Optional[Principal]:
    session = _session(request)
    user_id = session.get("user_id")
    if not user_id:
        return None
    principal = resolve_principal(conn, str(user_id))
    if principal is None:
        return None
    return principal


def _render(
    request: Request,
    template: str,
    context: Optional[Dict[str, Any]] = None,
    *,
    status_code: int = 200,
    session: Optional[Dict[str, Any]] = None,
) -> HTMLResponse:
    session = session or _session(request)
    principal = getattr(request.state, "principal", None)
    values: Dict[str, Any] = {
        "request": request,
        "principal": principal,
        "csrf": csrf_token(session),
        "domains": DOMAINS,
        "formats": DELIVERABLE_FORMATS,
        "dimensions": ["correctness", "completeness", "format", "professional_judgment", "process"],
        "methods": ["auto_script", "artifact_diff", "llm_judge", "human_rubric"],
        "error": None,
        "backend": "PostgreSQL" if request.app.state.settings.is_postgres else "SQLite",
    }
    values.update(context or {})
    response = TEMPLATES.TemplateResponse(request, template, values, status_code=status_code)
    response.set_cookie(
        COOKIE_NAME,
        request.app.state.codec.encode(session),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


def _redirect(path: str, *, msg: Optional[str] = None, err: Optional[str] = None) -> RedirectResponse:
    query: List[str] = []
    if msg:
        query.append("msg=" + urllib.parse.quote(msg))
    if err:
        query.append("err=" + urllib.parse.quote(err))
    if query:
        path = path + ("&" if "?" in path else "?") + "&".join(query)
    return RedirectResponse(path, status_code=303)


def _require(conn: sqlite3.Connection, request: Request) -> Principal:
    principal = _principal(conn, request)
    if principal is None:
        raise RedirectLogin()
    request.state.conn = conn
    request.state.principal = principal
    return principal


def _check_csrf(request: Request, form: Dict[str, Any]) -> None:
    if not check_csrf(_session(request), form.get("csrf")):
        raise AppError("CSRF_INVALID", 400, "表单已过期，请刷新后重试")


def _issue(principal: Principal, action: str) -> bool:
    return principal.has(action)


def _suggestions(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM agent_suggestions WHERE task_id = ? ORDER BY created_at DESC",
            (task_id,),
        ).fetchall()
    ]


def _insert_suggestion_run(conn: sqlite3.Connection, task: Dict[str, Any], payload: Dict[str, Any]) -> int:
    run_id = new_id("ar")
    created = now()
    input_hash = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    prompt_hash = hashlib.sha256(b"rule-based-structuring-v1").hexdigest()
    suggestions: List[tuple] = []
    scenario = payload.setdefault("scenario", {})
    identity = payload.setdefault("identity", {})
    environment = payload.setdefault("environment", {})
    review = payload.setdefault("review", {})
    handoff = payload.setdefault("handoff", {})
    if not scenario.get("role"):
        suggestions.append(("scenario.role", "财务分析师", 0.72))
    if not scenario.get("trigger"):
        suggestions.append(("scenario.trigger", "季度结账与报表复核", 0.68))
    if not scenario.get("audience"):
        suggestions.append(("scenario.audience", "财务负责人", 0.66))
    if not identity.get("difficulty_rationale"):
        suggestions.append(("identity.difficulty_rationale", "需要跨表核对、判断异常并解释差异，不能靠单步规则完成。", 0.74))
    if (environment.get("network") or {}).get("mode") == "online-required" and not (environment.get("network") or {}).get("justification"):
        suggestions.append(("environment.network.justification", "任务需要公开网页的实时数据；记录访问时间与来源，失败时允许使用给定快照。", 0.63))
    if not review.get("tier_rationale"):
        suggestions.append(("review.tier_rationale", "含真实专业判断与多步核对，按中风险评审。", 0.61))
    if not handoff.get("known_gaps"):
        suggestions.append(("handoff.known_gaps", "没有独立 reference，采用专业 rubric 与双人复核。", 0.58))
    conn.execute(
        "INSERT INTO agent_runs (run_id, task_id, capability, model, model_version, prompt_hash, input_hash, status, latency_ms, cost_cents, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (run_id, task["task_id"], "structuring", "rule-based-local", "1", prompt_hash, input_hash, "succeeded", 1, 0, created),
    )
    for field_path, value, confidence in suggestions:
        conn.execute(
            """INSERT INTO agent_suggestions
               (suggestion_id, run_id, task_id, field_path, suggested_value, confidence, model, model_version,
                prompt_hash, input_hash, state, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?, 'proposed', ?)""",
            (
                new_id("sug"), run_id, task["task_id"], field_path,
                json.dumps(value, ensure_ascii=False), confidence, "rule-based-local", "1",
                prompt_hash, input_hash, created,
            ),
        )
    return len(suggestions)


def _path_tokens(path: str) -> List[Any]:
    tokens: List[Any] = []
    for match in re.finditer(r"([A-Za-z0-9_]+)|\[(\d+)\]", path):
        if match.group(2) is not None:
            tokens.append(int(match.group(2)))
        else:
            tokens.append(match.group(1))
    if not tokens:
        raise AppError("SUGGESTION_PATH", 422, "建议字段路径不可写")
    return tokens


def _set_path(payload: Dict[str, Any], path: str, value: Any) -> None:
    tokens = _path_tokens(path)
    node: Any = payload
    for index, token in enumerate(tokens[:-1]):
        nxt = tokens[index + 1]
        if isinstance(token, int):
            if not isinstance(node, list) or token >= len(node):
                raise AppError("SUGGESTION_PATH", 422, "建议字段路径不可写")
            node = node[token]
        else:
            if not isinstance(node, dict):
                raise AppError("SUGGESTION_PATH", 422, "建议字段路径不可写")
            if token not in node:
                node[token] = [] if isinstance(nxt, int) else {}
            node = node[token]
    last = tokens[-1]
    if isinstance(last, int):
        if not isinstance(node, list) or last >= len(node):
            raise AppError("SUGGESTION_PATH", 422, "建议字段路径不可写")
        node[last] = value
    else:
        if not isinstance(node, dict):
            raise AppError("SUGGESTION_PATH", 422, "建议字段路径不可写")
        node[last] = value


def _parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return raw


def create_app() -> FastAPI:
    app = FastAPI(title="ALE Expert Workbench", docs_url=None, redoc_url=None)
    settings = Settings()
    if not settings.is_postgres:
        settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    settings.package_root.mkdir(parents=True, exist_ok=True)
    app.state.settings = settings
    app.state.codec = SessionCodec(load_secret(settings.secret_path))
    app.state.store = LocalObjectStore(settings.storage_root)
    app.mount("/static", StaticFiles(directory=str(ROOT / "web" / "static")), name="static")

    def db_dependency():
        conn = connect(settings.database)
        try:
            yield conn
        finally:
            conn.close()

    def bootstrap(conn) -> None:
        if settings.is_postgres:
            run_migrations(conn, ROOT / "pg" / "migrations")
        else:
            initialize(conn, ROOT / "app" / "schema.sql")
            run_migrations(conn, ROOT / "migrations")
        if conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"] == 0:
            from seed import seed
            seed(settings.database, os.environ.get("ALE_SEED_PASSWORD", "AleDemo123!"))

    bootstrap_conn = connect(settings.database)
    bootstrap(bootstrap_conn)
    bootstrap_conn.close()

    @app.get("/healthz")
    def healthz(conn=Depends(db_dependency)):
        conn.execute("SELECT 1 AS ok").fetchone()
        return {"status": "ok", "backend": getattr(conn, "backend", "unknown")}

    @app.get("/login", response_class=HTMLResponse)
    def login_page(request: Request):
        session = _session(request)
        return _render(request, "login.html", {"email": ""}, session=session)

    @app.post("/login")
    async def login(request: Request, conn=Depends(db_dependency)):
        form = dict(await request.form())
        _check_csrf(request, form)
        email = str(form.get("email") or "").strip().lower()
        password = str(form.get("password") or "")
        user = conn.execute("SELECT * FROM users WHERE lower(email) = ? AND status = 'active'", (email,)).fetchone()
        credential = None
        if user is not None:
            credential = conn.execute("SELECT password_hash FROM user_credentials WHERE user_id = ?", (user["user_id"],)).fetchone()
        if user is None or credential is None or not verify_password(password, credential["password_hash"]):
            session = _session(request)
            return _render(request, "login.html", {"email": email, "error": "邮箱或密码不正确"}, status_code=401, session=session)
        session = _session(request)
        session["user_id"] = user["user_id"]
        session["csrf"] = csrf_token(session)
        return _login_response(request, session)

    def _login_response(request: Request, session: Dict[str, Any]) -> RedirectResponse:
        response = _redirect("/dashboard", msg="已登录")
        response.set_cookie(
            COOKIE_NAME,
            request.app.state.codec.encode(session),
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax",
            path="/",
        )
        return response

    @app.post("/logout")
    async def logout(request: Request):
        form = dict(await request.form())
        _check_csrf(request, form)
        response = _redirect("/login", msg="已退出")
        response.delete_cookie(COOKIE_NAME, path="/")
        return response

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard(request: Request, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        if principal.has("task:read:all"):
            tasks = task_repo.list_tasks(conn)
        else:
            tasks = task_repo.list_tasks(conn, owner_expert_id=principal.user_id)
        return _render(request, "dashboard.html", {"tasks": tasks})

    @app.get("/tasks/new", response_class=HTMLResponse)
    def new_task_page(request: Request, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        if not principal.has("task:create"):
            raise AppError("FORBIDDEN", 403, "没有创建任务的权限")
        return _render(request, "task_new.html")

    @app.post("/tasks/new")
    async def new_task(request: Request, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        task_id = str(form.get("task_id") or "").strip()
        domain = str(form.get("domain_code") or "").strip()
        subdomain = str(form.get("subdomain_code") or "").strip()
        payload = empty_payload(task_id, domain, subdomain, principal.user_id)
        payload["identity"]["title_zh"] = str(form.get("title_zh") or "").strip()
        payload["identity"]["title_en"] = str(form.get("title_en") or "").strip()
        payload["identity"]["language"] = str(form.get("language") or "en").strip()
        payload["identity"]["batch_id"] = str(form.get("batch_id") or "w1-demo").strip()
        with transaction(conn):
            task = task_service.create_draft(
                conn,
                principal,
                {
                    "task_id": task_id,
                    "domain_code": domain,
                    "subdomain_code": subdomain,
                    "batch_id": payload["identity"]["batch_id"],
                    "title_zh": payload["identity"]["title_zh"],
                    "title_en": payload["identity"]["title_en"],
                    "language": payload["identity"]["language"],
                    "source_payload": payload,
                },
            )
        return _redirect("/tasks/%s/edit" % task["task_id"], msg="草稿已创建")

    @app.get("/tasks/{task_id:path}/edit", response_class=HTMLResponse)
    def task_edit(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        task = task_service.get_task(conn, principal, task_id)
        if task["owner_expert_id"] != principal.user_id or task["state"] not in sm.EDITABLE_STATES:
            raise AppError("TASK_NOT_EDITABLE", 409, "当前状态或权限不能编辑任务源")
        return _render(request, "task_form.html", {"task": task})

    @app.get("/tasks/{task_id:path}", response_class=HTMLResponse)
    def task_detail(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        task = task_service.get_task(conn, principal, task_id)
        editable = task["owner_expert_id"] == principal.user_id and task["state"] in sm.EDITABLE_STATES
        package = delivery_repo.get_package_for_task(conn, task_id, int(task["current_version_no"]))
        ingest = None
        if package:
            package = dict(package)
            row = conn.execute("SELECT * FROM ingest_records WHERE package_id = ? ORDER BY received_at DESC LIMIT 1", (package["package_id"],)).fetchone()
            ingest = dict(row) if row else None
            if package.get("package_hash") and ingest and ingest.get("receipt_json"):
                receipt = ingest["receipt_json"]
                if isinstance(receipt, str):
                    receipt = json.loads(receipt)
                package["native_hash"] = receipt.get("native_hash")
        return _render(
            request,
            "task_detail.html",
            {
                "task": task,
                "editable": editable,
                "package": package,
                "ingest": ingest,
                "suggestions": _suggestions(conn, task_id),
                "jobs": job_repo.list_jobs(conn, task_id, limit=5),
            },
        )

    @app.post("/tasks/{task_id:path}/draft")
    async def save_draft(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = await request.form()
        flat = dict(form)
        _check_csrf(request, flat)
        task = task_repo.get_task(conn, task_id)
        if task is None:
            raise AppError("NOT_FOUND", 404, "任务不存在: %s" % task_id)
        existing = json.loads(task["draft_payload"])
        payload = payload_from_form(
            form,
            existing=existing,
            owner_expert_id=principal.user_id,
            task_id=task["task_id"],
            domain_code=task["domain_code"],
            subdomain_code=task["subdomain_code"],
        )
        with transaction(conn):
            task_service.update_draft(
                conn,
                principal,
                task_id,
                {"source_payload": payload, "expected_lock_version": int(flat.get("expected_lock_version") or 0)},
            )
        return _redirect("/tasks/%s" % task_id, msg="草稿已保存")

    @app.post("/tasks/{task_id:path}/package/validate")
    async def validate_package(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        task = task_repo.get_task(conn, task_id)
        if task is None:
            raise AppError("NOT_FOUND", 404, "任务不存在: %s" % task_id)
        package = delivery_repo.get_package_for_task(conn, task_id, int(task["current_version_no"]))
        if package is None:
            raise AppError("PACKAGE_NOT_FOUND", 404, "任务还没有包")
        with transaction(conn):
            result = delivery_service.validate_package(conn, principal, package["package_id"], settings.package_root)
        if result["ok"]:
            return _redirect("/tasks/%s" % task_id, msg="L1–L5 校验通过")
        return _redirect("/tasks/%s" % task_id, err="包校验失败：%s" % ",".join(result["blockers"]))

    @app.post("/tasks/{task_id:path}/validate")
    async def validate_task(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        with transaction(conn):
            result = task_service.validate(conn, principal, task_id)
        if result["ok"]:
            return _redirect("/tasks/%s" % task_id, msg="自动检查通过")
        return _redirect("/tasks/%s" % task_id, err="自动检查有 %d 个阻断项" % result["blocker_count"])

    @app.post("/tasks/{task_id:path}/submit")
    async def submit_task(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        with transaction(conn):
            task_service.submit(conn, principal, task_id, {"expected_lock_version": form.get("expected_lock_version")})
        return _redirect("/tasks/%s" % task_id, msg="已提交，进入自动检查与领域评审")

    @app.post("/tasks/{task_id:path}/materials")
    async def upload_material(request: Request, task_id: str, file: UploadFile = File(...), conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = await request.form()
        flat = dict(form)
        _check_csrf(request, flat)
        task = task_repo.get_task(conn, task_id)
        if task is None or task["owner_expert_id"] != principal.user_id:
            raise AppError("FORBIDDEN", 403, "只能给自己的任务上传资料")
        if task["state"] not in sm.EDITABLE_STATES:
            raise AppError("TASK_NOT_EDITABLE", 409, "只有草稿或退回任务可以上传资料")
        data = await file.read()
        if len(data) > 20 * 1024 * 1024:
            raise AppError("MATERIAL_TOO_LARGE", 422, "单个文件不能超过 20 MiB")
        material_id = str(flat.get("material_id") or "").strip()
        if not material_id:
            count = conn.execute("SELECT COUNT(*) AS n FROM materials").fetchone()["n"]
            material_id = "M-%03d" % (count + 1)
        role = str(flat.get("role") or "input")
        layer = "reference" if role == "reference" else str(flat.get("layer") or "raw")
        license_type = str(flat.get("license_type") or "").strip()
        if not license_type:
            raise AppError("MATERIAL_LICENSE_REQUIRED", 422, "上传资料前必须选择许可类型")
        redistribution = str(flat.get("license_redistribution") or "") in ("1", "on", "true")
        pii_level = str(flat.get("pii_level") or "none")
        with transaction(conn):
            if conn.execute("SELECT 1 FROM materials WHERE material_id = ?", (material_id,)).fetchone() is None:
                material_service.register(
                    conn,
                    principal,
                    {
                        "task_id": task_id,
                        "material_id": material_id,
                        "kind": str(flat.get("kind") or "document"),
                        "role": role,
                        "layer": layer,
                        "license_type": license_type,
                        "license_redistribution": redistribution,
                        "pii_level": pii_level,
                    },
                )
            uploaded = material_service.upload(conn, principal, request.app.state.store, material_id, file.filename or "file.bin", data)
            version = uploaded["versions"][-1]
            payload = json.loads(task["draft_payload"])
            prefix = "reference" if role == "reference" else "template" if role == "template" else "input"
            path = "%s/%s" % (prefix, (file.filename or "file.bin").replace("\\", "/").split("/")[-1])
            item = {
                "material_id": material_id,
                "kind": str(flat.get("kind") or "document"),
                "role": role,
                "path": path,
                "sha256": version["sha256"],
                "bytes": version["bytes"],
                "license": {"type": license_type, "redistribution": redistribution},
                "pii_level": pii_level,
                "used_by": ["1"],
            }
            materials = [entry for entry in payload.get("materials", []) if entry.get("material_id") != material_id]
            materials.append(item)
            payload["materials"] = materials
            task_service.update_draft(
                conn,
                principal,
                task_id,
                {"source_payload": payload, "expected_lock_version": int(task["lock_version"])},
            )
        return _redirect("/tasks/%s" % task_id, msg="资料已上传并挂到任务源")

    @app.post("/tasks/{task_id:path}/agent/suggest")
    async def agent_suggest(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        task = task_repo.get_task(conn, task_id)
        capability = str(form.get("capability") or "structuring")
        if task is None:
            raise AppError("NOT_FOUND", 404, "任务不存在")
        if capability != "review_assist" and task["state"] not in sm.EDITABLE_STATES:
            raise AppError("TASK_NOT_EDITABLE", 409, "当前状态不能生成建议")
        try:
            with transaction(conn):
                result = agent_service.generate(conn, principal, task_id, capability)
        except agent_service.AgentServiceError as exc:
            raise AppError(exc.code, exc.status, exc.message)
        if result["degraded"]:
            message = "模型暂不可用，未生成建议；请使用人工清单继续"
        else:
            label = "真实模型" if not result["mock_only"] else "Mock 模式"
            message = "已生成 %d 条建议（%s），等待逐条确认" % (result["count"], label)
        return _redirect("/tasks/%s" % task_id, msg=message)

    @app.post("/tasks/{task_id:path}/agent/{suggestion_id}/confirm")
    async def agent_confirm(request: Request, task_id: str, suggestion_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        decision = str(form.get("decision") or "")
        if decision not in ("accepted", "edited", "rejected"):
            raise AppError("SUGGESTION_DECISION", 422, "未知的建议处理方式")
        task = task_repo.get_task(conn, task_id)
        suggestion = conn.execute("SELECT * FROM agent_suggestions WHERE suggestion_id = ? AND task_id = ?", (suggestion_id, task_id)).fetchone()
        if task is None or suggestion is None:
            raise AppError("NOT_FOUND", 404, "建议不存在")
        if task["owner_expert_id"] != principal.user_id or task["state"] not in sm.EDITABLE_STATES:
            raise AppError("TASK_NOT_EDITABLE", 409, "当前状态不能确认建议")
        if suggestion["state"] != "proposed":
            raise AppError("SUGGESTION_CLOSED", 409, "建议已经处理")
        timestamp = now()
        with transaction(conn):
            if decision == "rejected":
                conn.execute(
                    "UPDATE agent_suggestions SET state='rejected', decision='rejected', confirmed_by=?, confirmed_at=? WHERE suggestion_id=?",
                    (principal.user_id, timestamp, suggestion_id),
                )
            else:
                raw = suggestion["suggested_value"] if decision == "accepted" else str(form.get("edited_value") or suggestion["suggested_value"])
                value = _parse_value(raw)
                payload = json.loads(task["draft_payload"])
                _set_path(payload, suggestion["field_path"], value)
                task_service.update_draft(
                    conn,
                    principal,
                    task_id,
                    {"source_payload": payload, "expected_lock_version": int(task["lock_version"])},
                )
                conn.execute(
                    "UPDATE agent_suggestions SET state=?, decision=?, edited_value=?, confirmed_by=?, confirmed_at=?, applied_version_no=? WHERE suggestion_id=?",
                    (decision, decision, raw, principal.user_id, timestamp, task["current_version_no"], suggestion_id),
                )
        return _redirect("/tasks/%s" % task_id, msg="建议已处理")

    @app.get("/reviews", response_class=HTMLResponse)
    def review_queue(request: Request, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        rows = review_service.queue_for(conn, principal)
        return _render(request, "review_queue.html", {"rows": rows})

    @app.post("/reviews/{review_id}/claim")
    async def claim_review(request: Request, review_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        with transaction(conn):
            review_service.claim(conn, principal, review_id)
        return _redirect("/reviews/%s" % review_id, msg="评审已领取")

    @app.get("/reviews/{review_id}", response_class=HTMLResponse)
    def review_detail(request: Request, review_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        review = review_repo.get_review(conn, review_id)
        if review is None:
            raise AppError("NOT_FOUND", 404, "评审不存在")
        if review["reviewer_id"] not in (None, principal.user_id) and not principal.has("task:read:all"):
            raise AppError("FORBIDDEN", 403, "评审已被其他审核人领取")
        if review["kind"] == "domain" and "domain_reviewer" not in principal.roles and not principal.has("task:read:all"):
            raise AppError("FORBIDDEN", 403, "没有领域评审权限")
        if review["kind"] == "quality" and "quality_reviewer" not in principal.roles and not principal.has("task:read:all"):
            raise AppError("FORBIDDEN", 403, "没有质量审核权限")
        task = task_repo.get_task(conn, review["task_id"])
        if task is None:
            raise AppError("NOT_FOUND", 404, "评审关联任务不存在: %s" % review["task_id"])
        detail = task_service._detail(conn, task)
        items = review_repo.list_items(conn, review_id)
        return _render(request, "review_detail.html", {"review": review, "task": detail, "items": items})

    @app.post("/reviews/{review_id}/decision")
    async def review_decision(request: Request, review_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        decision = str(form.get("decision") or "")
        items: List[Dict[str, Any]] = []
        for line in str(form.get("issues") or "").splitlines():
            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 4 and parts[0]:
                items.append({"dimension": parts[0], "field_path": parts[1], "severity": parts[2], "comment": parts[3]})
        with transaction(conn):
            result = review_service.decide(conn, principal, review_id, decision, str(form.get("reason") or ""), items)
        return _redirect("/tasks/%s" % result["task_id"], msg="评审决定已记录")

    @app.post("/tasks/{task_id:path}/freeze")
    async def freeze_task(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        with transaction(conn):
            snapshot = delivery_service.freeze_task(conn, principal, task_id)
        return _redirect("/tasks/%s" % task_id, msg="已冻结 %s" % snapshot.get("snapshot_id", ""))

    @app.post("/tasks/{task_id:path}/package")
    async def build_package(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        if os.environ.get("ALE_ASYNC_PACKAGE") == "1":
            with transaction(conn):
                job = job_service.enqueue(conn, "package.build", task_id, {"task_id": task_id})
            return _redirect("/tasks/%s" % task_id, msg="组包任务已排队 %s" % job.get("job_id", ""))
        with transaction(conn):
            package = delivery_service.build_package(conn, principal, task_id, settings.package_root, request.app.state.store)
        return _redirect("/tasks/%s" % task_id, msg="已组包 %s" % package.get("package_id", ""))

    @app.post("/tasks/{task_id:path}/ingest")
    async def ingest_package(request: Request, task_id: str, conn=Depends(db_dependency)):
        principal = _require(conn, request)
        form = dict(await request.form())
        _check_csrf(request, form)
        task = task_repo.get_task(conn, task_id)
        package = delivery_repo.get_package_for_task(conn, task_id, int(task["current_version_no"])) if task else None
        if package is None:
            raise AppError("PACKAGE_NOT_FOUND", 404, "任务还没有包")
        with transaction(conn):
            receipt = delivery_service.ingest_package(conn, principal, package["package_id"], settings.package_root)
        return _redirect("/tasks/%s" % task_id, msg="已入库 %s" % receipt.get("ingest_id", ""))

    @app.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError):
        return _render(
            request,
            "error.html",
            {"code": exc.code, "message": exc.message, "details": exc.details},
            status_code=exc.status_code,
        )

    @app.exception_handler(RedirectLogin)
    async def login_redirect(request: Request, exc: RedirectLogin):
        return _redirect("/login", msg="请先登录")

    return app
