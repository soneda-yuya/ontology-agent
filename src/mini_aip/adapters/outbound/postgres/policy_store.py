"""PostgresPolicyStore — PolicyStorePort implementation.

Parameterized queries only (SECURITY-05). Rules live in the `policies` table;
the optional row predicate is stored as JSONB.
"""

from __future__ import annotations

from psycopg.types.json import Jsonb

from ....domain.permission import PermissionRule
from ....domain.permission.models import AttributePredicate, Effect, Operation
from .connection import ConnectionProvider


class PostgresPolicyStore:
    def __init__(self, provider: ConnectionProvider) -> None:
        self._provider = provider

    def load_all(self) -> list[PermissionRule]:
        with self._provider.connection() as conn:
            rows = conn.execute(
                "SELECT id, role, object_type, operation, effect, row_predicate FROM policies"
            ).fetchall()
        result: list[PermissionRule] = []
        for r in rows:
            predicate = AttributePredicate.model_validate(r[5]) if r[5] else None
            result.append(
                PermissionRule(
                    id=r[0],
                    role=r[1],
                    object_type=r[2],
                    operation=Operation(r[3]),
                    effect=Effect(r[4]),
                    row_predicate=predicate,
                )
            )
        return result

    def save(self, rule: PermissionRule) -> None:
        predicate = (
            Jsonb(rule.row_predicate.model_dump(mode="json")) if rule.row_predicate else None
        )
        with self._provider.unit_of_work() as conn:
            conn.execute(
                """
                INSERT INTO policies (id, role, object_type, operation, effect, row_predicate)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    role = EXCLUDED.role,
                    object_type = EXCLUDED.object_type,
                    operation = EXCLUDED.operation,
                    effect = EXCLUDED.effect,
                    row_predicate = EXCLUDED.row_predicate,
                    updated_at = now()
                """,
                (
                    rule.id,
                    rule.role,
                    rule.object_type,
                    rule.operation.value,
                    rule.effect.value,
                    predicate,
                ),
            )
