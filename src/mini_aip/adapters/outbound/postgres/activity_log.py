"""PostgresActivityLog — append-only ActivityLogPort implementation.

INSERT/SELECT only. Parameterized queries (SECURITY-05).
"""

from __future__ import annotations

from ....domain.audit import ActivityEvent, ActivityFilter
from .connection import ConnectionProvider


def _row_to_event(r: tuple) -> ActivityEvent:
    ts = r[1].isoformat() if hasattr(r[1], "isoformat") else str(r[1])
    return ActivityEvent(
        id=r[0],
        timestamp=ts,
        actor=r[2],
        action=r[3],
        object_type=r[4],
        object_id=r[5],
        visibility=r[6],
    )


class PostgresActivityLog:
    def __init__(self, provider: ConnectionProvider) -> None:
        self._provider = provider

    def append(self, event: ActivityEvent) -> None:
        with self._provider.unit_of_work() as conn:
            conn.execute(
                """
                INSERT INTO activity_events
                  (id, ts, actor, action, object_type, object_id, visibility)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.id,
                    event.timestamp,
                    event.actor,
                    event.action,
                    event.object_type,
                    event.object_id,
                    event.visibility,
                ),
            )

    def query(self, filter: ActivityFilter) -> list[ActivityEvent]:
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
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        params.append(filter.limit)
        sql = (
            "SELECT id, ts, actor, action, object_type, object_id, visibility "
            "FROM activity_events"
            f"{where} ORDER BY ts DESC LIMIT %s"
        )
        with self._provider.connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_row_to_event(r) for r in rows]
