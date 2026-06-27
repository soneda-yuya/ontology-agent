"""Example-based tests for type-definition validators (BR-1..BR-6)."""

import pytest

from mini_aip.domain.ontology import (
    ActionEffect,
    ActionType,
    Cardinality,
    DataType,
    LinkType,
    ObjectType,
    PropertyType,
)


def test_enum_requires_values():
    with pytest.raises(ValueError):
        PropertyType(name="status", data_type=DataType.ENUM)


def test_reference_requires_target():
    with pytest.raises(ValueError):
        PropertyType(name="owner", data_type=DataType.REFERENCE)


def test_object_type_id_property_must_exist():
    with pytest.raises(ValueError):
        ObjectType(
            name="Customer",
            properties=(PropertyType(name="name", data_type=DataType.STRING),),
            id_property="id",
        )


def test_object_type_rejects_duplicate_property_names():
    with pytest.raises(ValueError):
        ObjectType(
            name="Customer",
            properties=(
                PropertyType(name="id", data_type=DataType.STRING),
                PropertyType(name="id", data_type=DataType.STRING),
            ),
        )


def test_link_type_inverse_must_differ():
    with pytest.raises(ValueError):
        LinkType(
            name="owns",
            source_type="Customer",
            target_type="Account",
            cardinality=Cardinality.ONE_TO_MANY,
            inverse_name="owns",
        )


def test_valid_object_type_constructs():
    ot = ObjectType(
        name="Flight",
        properties=(
            PropertyType(name="id", data_type=DataType.STRING, required=True),
            PropertyType(name="number", data_type=DataType.STRING),
        ),
        title_property="number",
        text_properties=("number",),
    )
    assert ot.property("number") is not None
    assert ot.property("missing") is None


def test_action_type_constructs():
    at = ActionType(
        name="cancel_flight",
        target_type="Flight",
        input_schema=(PropertyType(name="reason", data_type=DataType.STRING),),
        effect=ActionEffect.STATE_TRANSITION,
    )
    assert at.effect is ActionEffect.STATE_TRANSITION
