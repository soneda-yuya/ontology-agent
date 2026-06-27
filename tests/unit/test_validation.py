"""Tests for object validation and cross-type validation (BR-7..BR-10)."""

import pytest

from mini_aip.domain.ontology import (
    DataType,
    DomainValidationError,
    DynamicModelFactory,
    LinkType,
    ObjectType,
    OntologyObject,
    PropertyType,
    TypeNotFoundError,
    TypeRegistry,
    validate_object,
    validate_type_def,
)
from mini_aip.domain.ontology.types import Cardinality

FACTORY = DynamicModelFactory()


def _customer_type():
    return ObjectType(
        name="Customer",
        properties=(
            PropertyType(name="id", data_type=DataType.STRING, required=True),
            PropertyType(name="tier", data_type=DataType.ENUM, enum_values=("free", "pro")),
            PropertyType(name="joined", data_type=DataType.DATE),
            PropertyType(name="ssn", data_type=DataType.STRING, is_pii=True),
        ),
    )


def test_valid_object_passes():
    ot = _customer_type()
    obj = OntologyObject(
        object_type="Customer",
        id="c1",
        properties={"id": "c1", "tier": "pro", "joined": "2020-01-01"},
    )
    validate_object(ot, obj, FACTORY)  # no raise


def test_missing_required_rejected():
    ot = _customer_type()
    obj = OntologyObject(object_type="Customer", id="c1", properties={"tier": "pro"})
    with pytest.raises(DomainValidationError):
        validate_object(ot, obj, FACTORY)


def test_surplus_property_rejected():
    # BR-10 / TP-3: properties not in the type are rejected.
    ot = _customer_type()
    obj = OntologyObject(
        object_type="Customer", id="c1", properties={"id": "c1", "surprise": 1}
    )
    with pytest.raises(DomainValidationError):
        validate_object(ot, obj, FACTORY)


def test_enum_membership_enforced():
    ot = _customer_type()
    obj = OntologyObject(
        object_type="Customer", id="c1", properties={"id": "c1", "tier": "enterprise"}
    )
    with pytest.raises(DomainValidationError):
        validate_object(ot, obj, FACTORY)


def test_bad_date_rejected():
    ot = _customer_type()
    obj = OntologyObject(
        object_type="Customer", id="c1", properties={"id": "c1", "joined": "not-a-date"}
    )
    with pytest.raises(DomainValidationError):
        validate_object(ot, obj, FACTORY)


def test_error_does_not_leak_pii_value():
    # SECURITY-03 / BR-11: validation errors list field names, never values.
    ot = _customer_type()
    secret = "999-88-7777"
    obj = OntologyObject(
        object_type="Customer", id="c1", properties={"id": "c1", "ssn": 12345}
    )
    # wrong type for ssn (int) triggers structural error; ensure no value leak
    with pytest.raises(DomainValidationError) as exc:
        validate_object(ot, obj, FACTORY)
    assert "12345" not in str(exc.value)
    assert secret not in str(exc.value)


def test_reference_existence_checked():
    ot = ObjectType(
        name="Account",
        properties=(
            PropertyType(name="id", data_type=DataType.STRING, required=True),
            PropertyType(
                name="owner", data_type=DataType.REFERENCE, ref_object_type="Customer"
            ),
        ),
    )
    obj = OntologyObject(
        object_type="Account", id="a1", properties={"id": "a1", "owner": "c-missing"}
    )
    with pytest.raises(DomainValidationError):
        validate_object(ot, obj, FACTORY, exists=lambda t, i: False)


def test_validate_type_def_requires_referenced_types():
    reg = TypeRegistry()
    link = LinkType(
        name="owns",
        source_type="Customer",
        target_type="Account",
        cardinality=Cardinality.ONE_TO_MANY,
        inverse_name="owned_by",
    )
    with pytest.raises(TypeNotFoundError):
        validate_type_def(link, reg)
