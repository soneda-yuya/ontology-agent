"""Integration tests for the Postgres audit/activity sinks (requires PostgreSQL)."""

import os

import pytest

pytestmark = pytest.mark.integration

DSN = os.environ.get("MINIAIP_DATABASE_URL")


@pytest.fixture()
def provider():
    if not DSN:
        pytest.skip("MINIAIP_DATABASE_URL not set")
    from mini_aip.adapters.outbound.postgres import ConnectionProvider

    return ConnectionProvider(DSN)


def test_audit_append_and_query(provider):
    from mini_aip.adapters.outbound.postgres import PostgresAuditSink
    from mini_aip.domain.audit import AuditEvent, AuditFilter

    sink = PostgresAuditSink(provider)
    ev = AuditEvent(
        id="audit-it-1",
        timestamp="2026-06-27T00:00:00+00:00",
        operation="put_object",
        actor="u1",
        roles=("cs",),
        object_type="Customer",
        object_id="c1",
        decision="allowed",
    )
    sink.append(ev)
    loaded = {e.id: e for e in sink.query(AuditFilter(actor="u1"))}
    got = loaded["audit-it-1"]
    assert got.operation == "put_object"
    assert got.decision == "allowed"
    assert got.object_type == "Customer"
    assert got.roles == ("cs",)


def test_activity_append_and_query(provider):
    from mini_aip.adapters.outbound.postgres import PostgresActivityLog
    from mini_aip.domain.audit import ActivityEvent, ActivityFilter

    log = PostgresActivityLog(provider)
    ev = ActivityEvent(
        id="act-it-1",
        timestamp="2026-06-27T00:00:00+00:00",
        actor="u1",
        action="put_object Customer",
        object_type="Customer",
        object_id="c1",
    )
    log.append(ev)
    loaded = {e.id: e for e in log.query(ActivityFilter(actor="u1"))}
    assert loaded["act-it-1"].action == "put_object Customer"
