"""Round-trip properties for audit/activity events (PBT-02, TP-AU1)."""

from __future__ import annotations

from hypothesis import given

from mini_aip.domain.audit import ActivityEvent, AuditEvent

from tests.pbt.audit_generators import activity_events, audit_events


@given(audit_events())
def test_audit_event_round_trips(e):
    assert AuditEvent.model_validate(e.model_dump(mode="json")) == e


@given(activity_events())
def test_activity_event_round_trips(e):
    assert ActivityEvent.model_validate(e.model_dump(mode="json")) == e
