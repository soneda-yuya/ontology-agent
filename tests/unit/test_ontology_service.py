"""Tests for OntologyService using in-memory fake adapters (no DB).

Demonstrates the ports/adapters seam: the service is exercised with simple
in-memory implementations of ObjectStorePort and TypeRegistryPort.
"""

import pytest

from mini_aip.domain.ontology import (
    DataType,
    DomainValidationError,
    ObjectType,
    OntologyObject,
    PropertyType,
    TypeDef,
    TypeNotFoundError,
    TypeRegistry,
)
from mini_aip.services import OntologyService


class InMemoryObjectStore:
    def __init__(self) -> None:
        self.data: dict[tuple[str, str], OntologyObject] = {}

    def get(self, object_type, obj_id):
        return self.data.get((object_type, obj_id))

    def exists(self, object_type, obj_id):
        return (object_type, obj_id) in self.data

    def write(self, obj):
        self.data[(obj.object_type, obj.id)] = obj

    def list_by_type(self, object_type, limit=100):
        return [o for (t, _), o in self.data.items() if t == object_type][:limit]


class InMemoryTypeStore:
    def __init__(self) -> None:
        self.data: dict[str, TypeDef] = {}

    def load_all(self):
        return list(self.data.values())

    def save(self, typedef):
        self.data[typedef.name] = typedef


def _customer_type():
    return ObjectType(
        name="Customer",
        properties=(
            PropertyType(name="id", data_type=DataType.STRING, required=True),
            PropertyType(name="name", data_type=DataType.STRING),
        ),
    )


def _service(**kwargs):
    return OntologyService(
        registry=TypeRegistry(),
        type_store=InMemoryTypeStore(),
        object_store=InMemoryObjectStore(),
        **kwargs,
    )


def test_register_then_put_then_get():
    svc = _service()
    svc.register_type(_customer_type())
    obj = OntologyObject(
        object_type="Customer", id="c1", properties={"id": "c1", "name": "Alice"}
    )
    svc.put_object(obj)
    got = svc.get_object("Customer", "c1")
    assert got is not None
    assert got.properties["name"] == "Alice"


def test_put_unknown_type_raises():
    svc = _service()
    obj = OntologyObject(object_type="Ghost", id="g1", properties={"id": "g1"})
    with pytest.raises(TypeNotFoundError):
        svc.put_object(obj)


def test_put_invalid_object_rejected():
    svc = _service()
    svc.register_type(_customer_type())
    bad = OntologyObject(
        object_type="Customer", id="c1", properties={"id": "c1", "extra": 1}
    )
    with pytest.raises(DomainValidationError):
        svc.put_object(bad)


def test_authorize_hook_can_deny():
    def deny(operation, context):
        raise PermissionError(f"denied: {operation}")

    svc = _service(authorize=deny)
    with pytest.raises(PermissionError):
        svc.register_type(_customer_type())


def test_audit_hook_receives_events():
    events = []
    svc = _service(audit=events.append)
    svc.register_type(_customer_type())
    svc.put_object(
        OntologyObject(object_type="Customer", id="c1", properties={"id": "c1"})
    )
    svc.get_object("Customer", "c1")
    ops = [e["op"] for e in events]
    assert ops == ["register_type", "put_object", "get_object"]


def test_reload_types_loads_from_store():
    store = InMemoryTypeStore()
    store.save(_customer_type())
    svc = OntologyService(
        registry=TypeRegistry(),
        type_store=store,
        object_store=InMemoryObjectStore(),
    )
    svc.reload_types()
    assert svc.get_object_type("Customer").name == "Customer"
