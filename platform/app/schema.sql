-- ALE 500 platform skeleton schema (SQLite for local runs, PostgreSQL target).
-- Timestamps are ISO-8601 UTC strings in SQLite; the PostgreSQL profile maps
-- them to timestamptz. JSON columns hold canonical JSON text in SQLite and
-- jsonb in the PostgreSQL profile.
--
-- Frozen snapshots, task versions and material versions are append-only. The
-- application never issues UPDATE on those tables; the triggers below make the
-- rule hold even for an operator at a psql prompt.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS batches (
    batch_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    quota_total     INTEGER NOT NULL DEFAULT 0,
    state           TEXT NOT NULL DEFAULT 'planned',
    opens_at        TEXT,
    closes_at       TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS users (
    user_id         TEXT PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    display_name    TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',
    created_at      TEXT NOT NULL,
    deactivated_at  TEXT,
    CHECK (status IN ('active', 'disabled'))
);

CREATE TABLE IF NOT EXISTS roles (
    role_code       TEXT PRIMARY KEY,
    name_zh         TEXT NOT NULL,
    description     TEXT
);

-- Scope '*' means unrestricted at that level. A row grants one role inside one
-- (domain, subdomain, batch) window, which is how task-level authorisation is
-- derived without per-task rows.
CREATE TABLE IF NOT EXISTS user_roles (
    user_role_id    TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(user_id),
    role_code       TEXT NOT NULL REFERENCES roles(role_code),
    scope_domain    TEXT NOT NULL DEFAULT '*',
    scope_subdomain TEXT NOT NULL DEFAULT '*',
    scope_batch     TEXT NOT NULL DEFAULT '*',
    granted_at      TEXT NOT NULL,
    granted_by      TEXT,
    UNIQUE (user_id, role_code, scope_domain, scope_subdomain, scope_batch)
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id           TEXT PRIMARY KEY,
    batch_id          TEXT REFERENCES batches(batch_id),
    domain_code       TEXT NOT NULL,
    subdomain_code    TEXT NOT NULL,
    owner_expert_id   TEXT NOT NULL REFERENCES users(user_id),
    state             TEXT NOT NULL,
    draft_payload     TEXT NOT NULL DEFAULT '{}',
    current_version_no INTEGER NOT NULL DEFAULT 0,
    lock_version      INTEGER NOT NULL DEFAULT 1,
    return_count      INTEGER NOT NULL DEFAULT 0,
    void_reason       TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    CHECK (state IN ('draft', 'submitted', 'auto_checked', 'in_review',
                     'approved', 'frozen', 'packaged', 'package_validated',
                     'ingested', 'returned', 'void')),
    CHECK (json_valid(draft_payload))
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner_expert_id, state);
CREATE INDEX IF NOT EXISTS idx_tasks_scope ON tasks(domain_code, subdomain_code, batch_id);

-- A version is created at submit time and never changes afterwards. The
-- canonical payload is stored verbatim so a later schema change cannot rewrite
-- history.
CREATE TABLE IF NOT EXISTS task_versions (
    task_id        TEXT NOT NULL REFERENCES tasks(task_id),
    version_no     INTEGER NOT NULL,
    payload_json   TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    submitted_by   TEXT NOT NULL REFERENCES users(user_id),
    submitted_at   TEXT NOT NULL,
    PRIMARY KEY (task_id, version_no),
    CHECK (json_valid(payload_json))
);

CREATE TABLE IF NOT EXISTS materials (
    material_id            TEXT PRIMARY KEY,
    task_id                TEXT REFERENCES tasks(task_id),
    owner_expert_id        TEXT NOT NULL REFERENCES users(user_id),
    kind                   TEXT NOT NULL,
    role                   TEXT NOT NULL,
    layer                  TEXT NOT NULL,
    license_type           TEXT NOT NULL,
    license_redistribution INTEGER NOT NULL DEFAULT 0,
    pii_level              TEXT NOT NULL DEFAULT 'none',
    pii_confirmed_by       TEXT,
    source_url             TEXT,
    source_accessed_at     TEXT,
    status                 TEXT NOT NULL DEFAULT 'active',
    created_at             TEXT NOT NULL,
    CHECK (role IN ('input', 'reference', 'template')),
    CHECK (layer IN ('raw', 'deidentified', 'work', 'reference')),
    CHECK (pii_level IN ('none', 'low', 'medium', 'high'))
);

CREATE INDEX IF NOT EXISTS idx_materials_task ON materials(task_id, role);

-- Same name uploaded twice becomes version 2; version 1 keeps its bytes and
-- hash. storage_key is opaque so the adapter can move from local disk to S3
-- without touching rows.
CREATE TABLE IF NOT EXISTS material_versions (
    material_version_id TEXT PRIMARY KEY,
    material_id         TEXT NOT NULL REFERENCES materials(material_id),
    version_no          INTEGER NOT NULL,
    filename            TEXT NOT NULL,
    bytes               INTEGER NOT NULL,
    sha256              TEXT NOT NULL,
    storage_key         TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    UNIQUE (material_id, version_no)
);

CREATE TABLE IF NOT EXISTS checks (
    check_id     TEXT PRIMARY KEY,
    task_id      TEXT NOT NULL REFERENCES tasks(task_id),
    version_no   INTEGER,
    run_id       TEXT NOT NULL,
    check_code   TEXT NOT NULL,
    severity     TEXT NOT NULL,
    passed       INTEGER NOT NULL,
    field_path   TEXT,
    message      TEXT,
    created_at   TEXT NOT NULL,
    CHECK (severity IN ('blocker', 'warning', 'info'))
);

CREATE INDEX IF NOT EXISTS idx_checks_run ON checks(task_id, run_id);
CREATE INDEX IF NOT EXISTS idx_checks_blocking ON checks(task_id, severity, passed);

CREATE TABLE IF NOT EXISTS reviews (
    review_id        TEXT PRIMARY KEY,
    task_id          TEXT NOT NULL REFERENCES tasks(task_id),
    version_no       INTEGER NOT NULL,
    round_no         INTEGER NOT NULL DEFAULT 1,
    kind             TEXT NOT NULL,
    state            TEXT NOT NULL DEFAULT 'pending',
    reviewer_id      TEXT REFERENCES users(user_id),
    decision         TEXT,
    decision_reason  TEXT,
    claimed_at       TEXT,
    decided_at       TEXT,
    sla_due_at       TEXT,
    created_at       TEXT NOT NULL,
    CHECK (kind IN ('domain', 'quality')),
    CHECK (state IN ('pending', 'in_review', 'passed', 'returned', 'rejected', 'escalated'))
);

CREATE INDEX IF NOT EXISTS idx_reviews_queue ON reviews(state, kind, created_at);
CREATE INDEX IF NOT EXISTS idx_reviews_task ON reviews(task_id, version_no);

CREATE TABLE IF NOT EXISTS assignments (
    assignment_id TEXT PRIMARY KEY,
    review_id     TEXT NOT NULL REFERENCES reviews(review_id),
    task_id       TEXT NOT NULL REFERENCES tasks(task_id),
    reviewer_id   TEXT NOT NULL REFERENCES users(user_id),
    strategy      TEXT NOT NULL,
    state         TEXT NOT NULL DEFAULT 'assigned',
    assigned_at   TEXT NOT NULL,
    due_at        TEXT,
    UNIQUE (review_id, reviewer_id)
);

CREATE TABLE IF NOT EXISTS review_items (
    item_id      TEXT PRIMARY KEY,
    review_id    TEXT NOT NULL REFERENCES reviews(review_id),
    dimension    TEXT NOT NULL,
    field_path   TEXT,
    severity     TEXT NOT NULL,
    verdict      TEXT NOT NULL,
    comment      TEXT,
    created_at   TEXT NOT NULL,
    CHECK (verdict IN ('pass', 'blocker', 'suggestion'))
);

CREATE INDEX IF NOT EXISTS idx_review_items_review ON review_items(review_id);

-- Snapshot content is a manifest plus the full canonical payload. It is the
-- only input the packager may read.
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id     TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL REFERENCES tasks(task_id),
    version_no      INTEGER NOT NULL,
    payload_json    TEXT NOT NULL,
    manifest_json   TEXT NOT NULL,
    native_hash     TEXT NOT NULL,
    hash_status     TEXT NOT NULL DEFAULT 'candidate',
    frozen_by       TEXT NOT NULL REFERENCES users(user_id),
    frozen_at       TEXT NOT NULL,
    UNIQUE (task_id, version_no)
);

CREATE TABLE IF NOT EXISTS packages (
    package_id    TEXT PRIMARY KEY,
    snapshot_id   TEXT NOT NULL REFERENCES snapshots(snapshot_id),
    task_id       TEXT NOT NULL REFERENCES tasks(task_id),
    version_no    INTEGER NOT NULL,
    state         TEXT NOT NULL DEFAULT 'queued',
    package_hash  TEXT,
    built_by      TEXT NOT NULL DEFAULT 'platform',
    failure_code  TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    CHECK (state IN ('queued', 'building', 'built', 'validated', 'ingested', 'failed', 'quarantined'))
);

CREATE INDEX IF NOT EXISTS idx_packages_task ON packages(task_id, version_no);

CREATE TABLE IF NOT EXISTS package_validations (
    validation_id TEXT PRIMARY KEY,
    package_id    TEXT NOT NULL REFERENCES packages(package_id),
    layer         TEXT NOT NULL,
    code          TEXT NOT NULL,
    severity      TEXT NOT NULL,
    passed        INTEGER NOT NULL,
    message       TEXT,
    report_json   TEXT,
    created_at    TEXT NOT NULL,
    CHECK (layer IN ('L1', 'L2', 'L3', 'L4', 'L5'))
);

CREATE TABLE IF NOT EXISTS ingest_records (
    ingest_id      TEXT PRIMARY KEY,
    package_id     TEXT NOT NULL REFERENCES packages(package_id),
    package_hash   TEXT NOT NULL UNIQUE,
    state          TEXT NOT NULL DEFAULT 'received',
    received_at    TEXT NOT NULL,
    received_by    TEXT NOT NULL,
    receipt_json   TEXT,
    CHECK (state IN ('received', 'validating', 'validated', 'published',
                     'rejected', 'quarantined', 'superseded', 'withdrawn'))
);

CREATE TABLE IF NOT EXISTS agent_runs (
    run_id        TEXT PRIMARY KEY,
    task_id       TEXT NOT NULL REFERENCES tasks(task_id),
    capability    TEXT NOT NULL,
    model         TEXT NOT NULL,
    model_version TEXT NOT NULL,
    prompt_hash   TEXT NOT NULL,
    input_hash    TEXT NOT NULL,
    status        TEXT NOT NULL,
    latency_ms    INTEGER,
    cost_cents    INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_suggestions (
    suggestion_id      TEXT PRIMARY KEY,
    run_id             TEXT NOT NULL REFERENCES agent_runs(run_id),
    task_id            TEXT NOT NULL REFERENCES tasks(task_id),
    field_path         TEXT NOT NULL,
    suggested_value    TEXT NOT NULL,
    confidence         REAL NOT NULL,
    model              TEXT NOT NULL,
    model_version      TEXT NOT NULL,
    prompt_hash        TEXT NOT NULL,
    input_hash         TEXT NOT NULL,
    state              TEXT NOT NULL DEFAULT 'proposed',
    decision           TEXT,
    edited_value       TEXT,
    confirmed_by       TEXT REFERENCES users(user_id),
    confirmed_at       TEXT,
    applied_version_no INTEGER,
    created_at         TEXT NOT NULL,
    CHECK (state IN ('proposed', 'accepted', 'edited', 'rejected', 'expired')),
    CHECK (decision IS NULL OR decision IN ('accepted', 'edited', 'rejected'))
);

CREATE INDEX IF NOT EXISTS idx_suggestions_task ON agent_suggestions(task_id, state);

CREATE TABLE IF NOT EXISTS audit_events (
    event_id     TEXT PRIMARY KEY,
    seq          INTEGER NOT NULL UNIQUE,
    actor_id     TEXT NOT NULL,
    actor_role   TEXT,
    action       TEXT NOT NULL,
    object_type  TEXT NOT NULL,
    object_id    TEXT NOT NULL,
    from_state   TEXT,
    to_state     TEXT,
    payload_json TEXT NOT NULL DEFAULT '{}',
    request_id   TEXT,
    created_at   TEXT NOT NULL,
    prev_hash    TEXT NOT NULL,
    event_hash   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_object ON audit_events(object_type, object_id, seq);

CREATE TABLE IF NOT EXISTS idempotency_keys (
    id            TEXT PRIMARY KEY,
    actor_id      TEXT NOT NULL,
    endpoint      TEXT NOT NULL,
    idem_key      TEXT NOT NULL,
    request_hash  TEXT NOT NULL,
    status_code   INTEGER NOT NULL,
    response_json TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    UNIQUE (actor_id, endpoint, idem_key)
);

-- Append-only guards. SQLite cannot express "no UPDATE unless column X", so
-- these triggers reject every UPDATE/DELETE on the immutable tables.
CREATE TRIGGER IF NOT EXISTS trg_task_versions_no_update
BEFORE UPDATE ON task_versions
BEGIN
    SELECT RAISE(ABORT, 'task_versions is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_task_versions_no_delete
BEFORE DELETE ON task_versions
BEGIN
    SELECT RAISE(ABORT, 'task_versions is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_snapshots_no_update
BEFORE UPDATE ON snapshots
BEGIN
    SELECT RAISE(ABORT, 'snapshots is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_snapshots_no_delete
BEFORE DELETE ON snapshots
BEGIN
    SELECT RAISE(ABORT, 'snapshots is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_material_versions_no_update
BEFORE UPDATE ON material_versions
BEGIN
    SELECT RAISE(ABORT, 'material_versions is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_no_update
BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_no_delete
BEFORE DELETE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events is append-only');
END;



-- Background jobs. The worker claims rows with a conditional UPDATE; SQLite
-- serialises writers, PostgreSQL uses FOR UPDATE SKIP LOCKED in the claim.
CREATE TABLE IF NOT EXISTS jobs (
    job_id        TEXT PRIMARY KEY,
    kind          TEXT NOT NULL,
    task_id       TEXT REFERENCES tasks(task_id),
    payload_json  TEXT NOT NULL DEFAULT '{}',
    state         TEXT NOT NULL DEFAULT 'queued',
    attempts      INTEGER NOT NULL DEFAULT 0,
    max_attempts  INTEGER NOT NULL DEFAULT 3,
    available_at  TEXT NOT NULL,
    locked_by     TEXT,
    locked_at     TEXT,
    last_error    TEXT,
    result_json   TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    CHECK (state IN ('queued', 'running', 'succeeded', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_jobs_claim ON jobs(state, available_at);

-- Web credential store. The skeleton authenticated with an X-Actor-Id header;
-- the real workbench stores a PBKDF2 digest instead and never keeps plaintext.
CREATE TABLE IF NOT EXISTS user_credentials (
    user_id       TEXT PRIMARY KEY REFERENCES users(user_id),
    password_hash TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

-- Migration ledger. schema.sql is idempotent, but a deployed database needs an
-- auditable record of which additive migration has run.
CREATE TABLE IF NOT EXISTS schema_migrations (
    migration_id TEXT PRIMARY KEY,
    applied_at   TEXT NOT NULL
);
