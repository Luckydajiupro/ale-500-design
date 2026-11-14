CREATE TABLE IF NOT EXISTS user_credentials (
    user_id       TEXT PRIMARY KEY REFERENCES users(user_id),
    password_hash TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS schema_migrations (
    migration_id TEXT PRIMARY KEY,
    applied_at   TEXT NOT NULL
);
