-- U2 Permission — policy rules
-- Role-based rules with optional JSONB row predicate. deny-by-default is
-- enforced in code (absence of an ALLOW => deny).

CREATE TABLE IF NOT EXISTS policies (
    id            TEXT PRIMARY KEY,
    role          TEXT NOT NULL,
    object_type   TEXT NOT NULL,                 -- '*' matches any type
    operation     TEXT NOT NULL CHECK (operation IN ('read', 'write', 'admin')),
    effect        TEXT NOT NULL CHECK (effect IN ('allow', 'deny')),
    row_predicate JSONB,                          -- {object_property, principal_attribute} | null
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_policies_role ON policies (role);
