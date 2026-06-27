"""Tests for U5 Audit & Activity services and the audit_hook adapter."""

import pytest

from mini_aip.adapters.outbound.postgres import PostgresActivityLog, PostgresAuditSink
from mini_aip.domain.audit import (
    ActivityEvent,
    ActivityFilter,
    AuditEvent,
    AuditFilter,
)
from mini_aip.domain.ontology import (
    DataType,
    ObjectType,
    PropertyType,
    SharingLevel,
    TypeRegistry,
)
from mini_aip.domain.permission import (
    Effect,
    Operation,
    PermissionDenied,
    PermissionRule,
    PolicyRegistry,
    Principal,
)
from mini_aip.services import ActivityService, AuditAdapter, AuditService, PermissionGateway


class InMemoryAuditSink:
    def __init__(self):
        self.events: list[AuditEvent] = []

    def append(self, event):
        self.events.append(event)

    def query(self, filter):
        return list(self.events)[: filter.limit]


class InMemoryActivityLog:
    def __init__(self):
        self.events: list[ActivityEvent] = []

    def append(self, event):
        self.events.append(event)

    def query(self, filter):
        return list(self.events)[: filter.limit]


def _id(name):
    return (PropertyType(name="id", data_type=DataType.STRING, required=True),)


def _registries():
    types = TypeRegistry()
    types.register(ObjectType(name="AuditEvent", properties=_id("a"), sharing_level=SharingLevel.RESTRICTED))
    types.register(ObjectType(name="ActivityEvent", properties=_id("a"), sharing_level=SharingLevel.SHARED))
    return types, PolicyRegistry()


def _adapter():
    sink, log = InMemoryAuditSink(), InMemoryActivityLog()
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    return AuditAdapter(AuditService(sink, gw), ActivityService(log, gw)), sink, log


def test_allowed_significant_records_audit_and_activity():
    adapter, sink, log = _adapter()
    adapter.audit_hook({"op": "put_object", "principal": Principal(id="u", roles=("cs",)), "type": "Customer", "id": "c1"})
    assert len(sink.events) == 1
    assert sink.events[0].decision == "allowed"
    assert len(log.events) == 1  # put_object is significant


def test_read_records_audit_only():
    adapter, sink, log = _adapter()
    adapter.audit_hook({"op": "get_object", "principal": Principal(id="u"), "type": "Customer", "id": "c1"})
    assert len(sink.events) == 1
    assert len(log.events) == 0  # get_object not significant


def test_denied_recorded_without_activity():
    adapter, sink, log = _adapter()
    adapter.audit_hook({"op": "put_object", "principal": Principal(id="u"), "type": "Customer", "decision": "denied", "reason": "deny-by-default"})
    assert sink.events[0].decision == "denied"
    assert len(log.events) == 0


def test_audit_event_is_pii_free():
    adapter, sink, _ = _adapter()
    adapter.audit_hook({"op": "get_object", "principal": Principal(id="u", attributes={"ssn": ("999",)}), "type": "Customer", "id": "c1"})
    ev = sink.events[0]
    # only refs/op recorded; no attribute values
    assert "999" not in str(ev.model_dump())


def test_audit_query_requires_governance():
    sink = InMemoryAuditSink()
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    svc = AuditService(sink, gw)
    with pytest.raises(PermissionDenied):
        svc.query(Principal(id="u", roles=("cs",)), AuditFilter())
    policies.upsert(PermissionRule(id="gov", role="governance", object_type="AuditEvent", operation=Operation.READ, effect=Effect.ALLOW))
    assert svc.query(Principal(id="g", roles=("governance",)), AuditFilter()) == []


def test_activity_query_is_shared():
    log = InMemoryActivityLog()
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    svc = ActivityService(log, gw)
    # any authenticated principal can read shared activity
    assert svc.query(Principal(id="u", roles=("cs",)), ActivityFilter()) == []


def test_sinks_are_append_only():
    for cls in (PostgresAuditSink, PostgresActivityLog):
        assert not hasattr(cls, "update")
        assert not hasattr(cls, "delete")
