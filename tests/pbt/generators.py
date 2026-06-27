"""Reusable Hypothesis strategies for ontology domain types (PBT-07).

Generators respect business constraints so they produce *valid* definitions and
type-appropriate object values — not meaningless random data.
"""

from __future__ import annotations

from hypothesis import strategies as st

from mini_aip.domain.ontology import (
    ActionEffect,
    ActionType,
    Cardinality,
    DataType,
    LinkType,
    ObjectType,
    OntologyObject,
    PropertyType,
)

identifiers = st.from_regex(r"[a-z][a-z0-9_]{0,15}", fullmatch=True)
_scalar_types = [
    DataType.STRING,
    DataType.INTEGER,
    DataType.FLOAT,
    DataType.BOOLEAN,
    DataType.DATE,
    DataType.DATETIME,
]


@st.composite
def property_types(draw: st.DrawFn, name: str | None = None) -> PropertyType:
    pname = name if name is not None else draw(identifiers)
    data_type = draw(st.sampled_from(_scalar_types + [DataType.ENUM, DataType.REFERENCE]))
    kwargs: dict = {
        "name": pname,
        "data_type": data_type,
        "required": draw(st.booleans()),
        "is_pii": draw(st.booleans()),
    }
    if data_type is DataType.ENUM:
        kwargs["enum_values"] = tuple(
            draw(st.lists(identifiers, min_size=1, max_size=4, unique=True))
        )
    elif data_type is DataType.REFERENCE:
        kwargs["ref_object_type"] = draw(identifiers)
    return PropertyType(**kwargs)


@st.composite
def object_types(draw: st.DrawFn) -> ObjectType:
    # Always include a required "id" string property so id_property is valid.
    extra_names = draw(
        st.lists(identifiers.filter(lambda s: s != "id"), max_size=4, unique=True)
    )
    props = [PropertyType(name="id", data_type=DataType.STRING, required=True)]
    props += [draw(property_types(name=n)) for n in extra_names]
    string_names = [p.name for p in props if p.data_type is DataType.STRING]
    title = draw(st.one_of(st.none(), st.sampled_from(string_names)))
    text = tuple(draw(st.lists(st.sampled_from(string_names), max_size=2, unique=True)))
    return ObjectType(
        name=draw(identifiers),
        properties=tuple(props),
        id_property="id",
        title_property=title,
        text_properties=text,
    )


@st.composite
def link_types(draw: st.DrawFn) -> LinkType:
    name = draw(identifiers)
    inverse = draw(identifiers.filter(lambda s: s != name))
    return LinkType(
        name=name,
        source_type=draw(identifiers),
        target_type=draw(identifiers),
        cardinality=draw(st.sampled_from(list(Cardinality))),
        inverse_name=inverse,
    )


@st.composite
def action_types(draw: st.DrawFn) -> ActionType:
    in_names = draw(st.lists(identifiers, max_size=3, unique=True))
    return ActionType(
        name=draw(identifiers),
        target_type=draw(identifiers),
        input_schema=tuple(draw(property_types(name=n)) for n in in_names),
        effect=draw(st.sampled_from(list(ActionEffect))),
        preconditions=tuple(draw(st.lists(st.text(max_size=20), max_size=2))),
    )


type_defs = st.one_of(object_types(), link_types(), action_types())


def _value_for(draw: st.DrawFn, p: PropertyType):
    if p.data_type is DataType.STRING:
        return draw(st.text(max_size=20))
    if p.data_type is DataType.INTEGER:
        return draw(st.integers(min_value=-(10**9), max_value=10**9))
    if p.data_type is DataType.FLOAT:
        return draw(st.floats(allow_nan=False, allow_infinity=False, width=32))
    if p.data_type is DataType.BOOLEAN:
        return draw(st.booleans())
    if p.data_type is DataType.ENUM:
        assert p.enum_values is not None
        return draw(st.sampled_from(p.enum_values))
    if p.data_type is DataType.DATE:
        return draw(st.dates()).isoformat()
    if p.data_type is DataType.DATETIME:
        return draw(st.datetimes()).isoformat()
    # REFERENCE
    return draw(identifiers)


@st.composite
def objects_for(draw: st.DrawFn, ot: ObjectType) -> OntologyObject:
    """A valid object instance for a given ObjectType."""
    props: dict = {}
    for p in ot.properties:
        if p.required or draw(st.booleans()):
            props[p.name] = _value_for(draw, p)
    props[ot.id_property] = draw(identifiers)  # ensure id present & string
    return OntologyObject(object_type=ot.name, id=props[ot.id_property], properties=props)


@st.composite
def ontology_objects(draw: st.DrawFn) -> OntologyObject:
    ot = draw(object_types())
    return draw(objects_for(ot))
