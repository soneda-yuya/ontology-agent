"""Property-based round-trip tests (PBT-02, TP-1/TP-2).

Invariants:
    deserialize_type(serialize_type(t)) == t
    deserialize_object(serialize_object(o)) == o
"""

from __future__ import annotations

from hypothesis import given

from mini_aip.domain.ontology import (
    deserialize_object,
    deserialize_type,
    serialize_object,
    serialize_type,
)

from tests.pbt.generators import ontology_objects, type_defs


@given(type_defs)
def test_type_definition_round_trips(t):
    assert deserialize_type(serialize_type(t)) == t


@given(ontology_objects())
def test_object_round_trips(o):
    assert deserialize_object(serialize_object(o)) == o
