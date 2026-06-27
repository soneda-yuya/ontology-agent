"""PostgresObjectStore — ObjectStorePort implementation.

All SQL uses bound parameters, never string interpolation (SECURITY-05).
Objects are stored in a single JSONB table so new types need no DDL.
"""

from __future__ import annotations

from psycopg.types.json import Jsonb

from ....domain.ontology import OntologyObject
from .connection import ConnectionProvider


class PostgresObjectStore:
    def __init__(self, provider: ConnectionProvider) -> None:
        self._provider = provider

    def get(self, object_type: str, obj_id: str) -> OntologyObject | None:
        with self._provider.connection() as conn:
            row = conn.execute(
                "SELECT properties FROM objects WHERE object_type = %s AND id = %s",
                (object_type, obj_id),
            ).fetchone()
        if row is None:
            return None
        return OntologyObject(object_type=object_type, id=obj_id, properties=row[0])

    def exists(self, object_type: str, obj_id: str) -> bool:
        with self._provider.connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM objects WHERE object_type = %s AND id = %s",
                (object_type, obj_id),
            ).fetchone()
        return row is not None

    def write(self, obj: OntologyObject) -> None:
        with self._provider.unit_of_work() as conn:
            conn.execute(
                """
                INSERT INTO objects (object_type, id, properties)
                VALUES (%s, %s, %s)
                ON CONFLICT (object_type, id)
                DO UPDATE SET properties = EXCLUDED.properties, updated_at = now()
                """,
                (obj.object_type, obj.id, Jsonb(obj.properties)),
            )

    def list_by_type(self, object_type: str, limit: int = 100) -> list[OntologyObject]:
        with self._provider.connection() as conn:
            rows = conn.execute(
                "SELECT id, properties FROM objects WHERE object_type = %s ORDER BY id LIMIT %s",
                (object_type, limit),
            ).fetchall()
        return [
            OntologyObject(object_type=object_type, id=r[0], properties=r[1]) for r in rows
        ]
