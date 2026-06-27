-- U1 Ontology Core — schema
-- Type definitions and generic objects are stored as data (JSONB) so that
-- adding new ontology types requires no DDL (data-driven, NFR-U1-2).
-- Encryption at rest / TLS are enforced at the infrastructure layer (SECURITY-01).

CREATE TABLE IF NOT EXISTS type_defs (
    name        TEXT PRIMARY KEY,
    kind        TEXT NOT NULL CHECK (kind IN ('object', 'link', 'action')),
    definition  JSONB NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS objects (
    object_type TEXT NOT NULL,
    id          TEXT NOT NULL,
    properties  JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (object_type, id)
);

-- GIN index for attribute search over JSONB properties (NFR-U1-6).
CREATE INDEX IF NOT EXISTS idx_objects_props_gin ON objects USING GIN (properties);
