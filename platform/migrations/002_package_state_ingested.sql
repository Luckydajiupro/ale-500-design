PRAGMA foreign_keys = OFF;
PRAGMA legacy_alter_table = ON;

ALTER TABLE packages RENAME TO packages_old;

CREATE TABLE packages (
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

INSERT INTO packages (package_id, snapshot_id, task_id, version_no, state, package_hash, built_by, failure_code, created_at, updated_at)
SELECT package_id, snapshot_id, task_id, version_no, state, package_hash, built_by, failure_code, created_at, updated_at FROM packages_old;

DROP TABLE packages_old;

CREATE INDEX IF NOT EXISTS idx_packages_task ON packages(task_id, version_no);

PRAGMA legacy_alter_table = OFF;
PRAGMA foreign_keys = ON;
