-- U5 Audit & Activity — append-only event stores
-- The application DB user must be granted INSERT/SELECT only on these tables
-- (no UPDATE/DELETE) so the app cannot modify or delete its own trail (SECURITY-14).

CREATE TABLE IF NOT EXISTS audit_events (
    id          TEXT PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor       TEXT,
    roles       JSONB NOT NULL DEFAULT '[]'::jsonb,
    operation   TEXT NOT NULL,
    object_type TEXT,
    object_id   TEXT,
    decision    TEXT NOT NULL,
    outcome     TEXT NOT NULL,
    reason      TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_events (actor);
CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_events (object_type);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_events (ts);

CREATE TABLE IF NOT EXISTS activity_events (
    id          TEXT PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor       TEXT NOT NULL,
    action      TEXT NOT NULL,
    object_type TEXT,
    object_id   TEXT,
    visibility  TEXT NOT NULL DEFAULT 'shared'
);
CREATE INDEX IF NOT EXISTS idx_activity_actor ON activity_events (actor);
CREATE INDEX IF NOT EXISTS idx_activity_ts ON activity_events (ts);
