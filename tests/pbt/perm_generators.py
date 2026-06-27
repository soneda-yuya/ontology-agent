"""Hypothesis strategies for U2 permission domain (PBT-07)."""

from __future__ import annotations

from hypothesis import strategies as st

from mini_aip.domain.permission import (
    AttributePredicate,
    Effect,
    Operation,
    PermissionRule,
    Principal,
)
from mini_aip.domain.permission.models import WILDCARD

ROLES = ["r1", "r2", "r3"]
TYPES = ["t1", "t2"]
ATTR_KEYS = ["department", "territory"]
ATTR_VALS = ["a", "b", "c"]
OBJ_PROPS = ["department", "territory", "owner"]
ids = st.from_regex(r"[a-z][a-z0-9_]{0,8}", fullmatch=True)


@st.composite
def principals(draw: st.DrawFn) -> Principal:
    roles = tuple(draw(st.lists(st.sampled_from(ROLES), max_size=3, unique=True)))
    keys = draw(st.lists(st.sampled_from(ATTR_KEYS), max_size=2, unique=True))
    attributes = {
        k: tuple(draw(st.lists(st.sampled_from(ATTR_VALS), max_size=3, unique=True)))
        for k in keys
    }
    return Principal(id=draw(ids), roles=roles, attributes=attributes)


@st.composite
def predicates(draw: st.DrawFn) -> AttributePredicate:
    return AttributePredicate(
        object_property=draw(st.sampled_from(OBJ_PROPS)),
        principal_attribute=draw(st.sampled_from(ATTR_KEYS)),
    )


@st.composite
def rules(draw: st.DrawFn) -> PermissionRule:
    effect = draw(st.sampled_from(list(Effect)))
    # DENY rules are unconditional (type+op level) by convention.
    predicate = draw(predicates()) if effect is Effect.ALLOW and draw(st.booleans()) else None
    return PermissionRule(
        id=draw(ids),
        role=draw(st.sampled_from(ROLES)),
        object_type=draw(st.sampled_from(TYPES + [WILDCARD])),
        operation=draw(st.sampled_from(list(Operation))),
        effect=effect,
        row_predicate=predicate,
    )


@st.composite
def policies(draw: st.DrawFn) -> list[PermissionRule]:
    return draw(st.lists(rules(), max_size=6))


@st.composite
def object_attrs(draw: st.DrawFn) -> dict:
    keys = draw(st.lists(st.sampled_from(OBJ_PROPS), max_size=3, unique=True))
    return {k: draw(st.sampled_from(ATTR_VALS)) for k in keys}
