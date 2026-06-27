"""PostgresTypeRegistry — TypeRegistryPort implementation.

Type definitions are stored as data (kind + JSONB definition) so they can be
loaded at startup and round-tripped (PBT-02). Parameterized queries only
(SECURITY-05).
"""

from __future__ import annotations

from psycopg.types.json import Jsonb

from ....domain.ontology import TypeDef, deserialize_type, serialize_type
from .connection import ConnectionProvider


class PostgresTypeRegistry:
    def __init__(self, provider: ConnectionProvider) -> None:
        self._provider = provider

    def load_all(self) -> list[TypeDef]:
        with self._provider.connection() as conn:
            rows = conn.execute("SELECT kind, definition FROM type_defs").fetchall()
        return [deserialize_type({"kind": r[0], "definition": r[1]}) for r in rows]

    def save(self, typedef: TypeDef) -> None:
        payload = serialize_type(typedef)
        with self._provider.unit_of_work() as conn:
            conn.execute(
                """
                INSERT INTO type_defs (name, kind, definition)
                VALUES (%s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET kind = EXCLUDED.kind,
                              definition = EXCLUDED.definition,
                              updated_at = now()
                """,
                (typedef.name, payload["kind"], Jsonb(payload["definition"])),
            )
