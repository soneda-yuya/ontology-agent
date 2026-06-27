"""Tests for the in-memory TypeRegistry."""

import pytest

from mini_aip.domain.ontology import (
    Cardinality,
    DataType,
    DuplicateTypeError,
    LinkType,
    ObjectType,
    PropertyType,
    TypeNotFoundError,
    TypeRegistry,
)


def _obj(name: str) -> ObjectType:
    return ObjectType(
        name=name,
        properties=(PropertyType(name="id", data_type=DataType.STRING, required=True),),
    )


def test_register_and_get():
    reg = TypeRegistry()
    reg.register(_obj("Customer"))
    assert reg.has_object_type("Customer")
    assert reg.get_object_type("Customer").name == "Customer"


def test_get_missing_raises():
    reg = TypeRegistry()
    with pytest.raises(TypeNotFoundError):
        reg.get_object_type("Nope")


def test_load_replaces_contents():
    reg = TypeRegistry()
    reg.register(_obj("A"))
    reg.load([_obj("B")])
    assert not reg.has_object_type("A")
    assert reg.has_object_type("B")


def test_links_from():
    reg = TypeRegistry()
    reg.register(_obj("Customer"))
    reg.register(_obj("Account"))
    link = LinkType(
        name="owns",
        source_type="Customer",
        target_type="Account",
        cardinality=Cardinality.ONE_TO_MANY,
        inverse_name="owned_by",
    )
    reg.register(link)
    assert [lt.name for lt in reg.links_from("Customer")] == ["owns"]
    assert reg.links_from("Account") == []


def test_duplicate_name_different_kind_rejected():
    reg = TypeRegistry()
    reg.register(_obj("owns"))
    link = LinkType(
        name="owns",
        source_type="owns",
        target_type="owns",
        cardinality=Cardinality.ONE_TO_ONE,
        inverse_name="owned_by",
    )
    with pytest.raises(DuplicateTypeError):
        reg.register(link)
