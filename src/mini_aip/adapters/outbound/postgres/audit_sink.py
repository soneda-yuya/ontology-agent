"""PostgresAuditSink — append-only AuditSinkPort implementation.

INSERT/SELECT only (no UPDATE/DELETE). Parameterized queries (SECURITY-05).
The app DB user is not granted UPDATE/DELETE on audit_events (SECURITY-14).
"""

from __future__ import annotations

from psycopg.types.json import Jsonb

from ....domain.audit import AuditEvent, AuditFilter
from .connection import ConnectionProvider


def _row_to_event(r: tuple) -> AuditEvent:
    ts = r[1].isoformat() if hasattr(r[1], "isoformat") else str(r[1])
    return AuditEvent(
        id=r[0],
        timestamp=ts,
        operation=r[4],
        actor=r[2],
        roles=tuple(r[3] or ()),
        object_type=r[5],
        object_id=r[6],
        decision=r[7],
        outcome=r[8],
        reason=r[9] or "",
    )


class PostgresAuditSink:
    def __init__(self, provider: ConnectionProvider) -> None:
        self._provider = provider

    def append(self, event: AuditEvent) -> None:
        with self._provider.unit_of_work() as conn:
            conn.execute(
                """
                INSERT INTO audit_events
                  (id, ts, actor, roles, operation, object_type, object_id,
                   decision, outcome, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.id,
                    event.timestamp,
                    event.actor,
                    Jsonb(list(event.roles)),
                    event.operation,
                    event.object_type,
                    event.object_id,
                    event.decision,
                    event.outcome,
                    event.reason,
                ),
            )

    def query(self, filter: AuditFilter) -> list[AuditEvent]:
        clauses: list[str] = []
        params: list[object] = []
        if filter.actor is not None:
            clauses.append("actor = %s")
            params.append(filter.actor)
        if filter.object_type is not None:
            clauses.append("object_type = %s")
            params.append(filter.object_type)
        if filter.since is not None:
            clauses.append("ts >= %s")
            params.append(filter.since)
        if filter.until is not None:
            clauses.append("ts <= %s")
            params.append(filter.until)
        if filter.decision is not None:
            clauses.append("decision = %s")
            params.append(filter.decision)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        params.append(filter.limit)
        sql = (
            "SELECT id, ts, actor, roles, operation, object_type, object_id, "
            "decision, outcome, reason FROM audit_events"
            f"{where} ORDER BY ts DESC LIMIT %s"
        )
        with self._provider.connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_row_to_event(r) for r in rows]
