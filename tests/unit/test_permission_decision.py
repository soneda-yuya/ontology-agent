"""Example-based tests for U2 decision functions."""

from mini_aip.domain.ontology import SharingLevel
from mini_aip.domain.permission import (
    AttributePredicate,
    ConstraintKind,
    Effect,
    Operation,
    PermissionRule,
    Principal,
    decide,
    row_constraint,
)


def _allow(role, type_, op, predicate=None, rid="a"):
    return PermissionRule(
        id=rid, role=role, object_type=type_, operation=op, effect=Effect.ALLOW,
        row_predicate=predicate,
    )


def _deny(role, type_, op, rid="d"):
    return PermissionRule(
        id=rid, role=role, object_type=type_, operation=op, effect=Effect.DENY
    )


def test_deny_by_default():
    p = Principal(id="u", roles=("cs",))
    assert not decide([], p, Operation.READ, "Flight", SharingLevel.RESTRICTED).allowed


def test_explicit_deny_beats_allow():
    p = Principal(id="u", roles=("cs",))
    policy = [_allow("cs", "Flight", Operation.READ), _deny("cs", "Flight", Operation.READ)]
    assert not decide(policy, p, Operation.READ, "Flight", SharingLevel.RESTRICTED).allowed


def test_shared_type_allows_read():
    p = Principal(id="u", roles=("cs",))
    assert decide([], p, Operation.READ, "Note", SharingLevel.SHARED).allowed


def test_shared_does_not_allow_write():
    p = Principal(id="u", roles=("cs",))
    assert not decide([], p, Operation.WRITE, "Note", SharingLevel.SHARED).allowed


def test_row_predicate_match():
    p = Principal(id="u", roles=("sales",), attributes={"territory": ("apac",)})
    pred = AttributePredicate(object_property="territory", principal_attribute="territory")
    policy = [_allow("sales", "Account", Operation.READ, predicate=pred)]
    assert decide(
        policy, p, Operation.READ, "Account", SharingLevel.RESTRICTED,
        object_attrs={"territory": "apac"},
    ).allowed
    assert not decide(
        policy, p, Operation.READ, "Account", SharingLevel.RESTRICTED,
        object_attrs={"territory": "emea"},
    ).allowed


def test_wildcard_type_rule():
    p = Principal(id="u", roles=("admin",))
    policy = [_allow("admin", "*", Operation.ADMIN)]
    assert decide(policy, p, Operation.ADMIN, "AnyType", SharingLevel.RESTRICTED).allowed


def test_row_constraint_shapes():
    p = Principal(id="u", roles=("sales",), attributes={"territory": ("apac",)})
    pred = AttributePredicate(object_property="territory", principal_attribute="territory")
    # shared -> unconstrained
    c = row_constraint([], p, Operation.READ, "Note", SharingLevel.SHARED)
    assert c.kind is ConstraintKind.UNCONSTRAINED
    # no allow -> none
    c = row_constraint([], p, Operation.READ, "Account", SharingLevel.RESTRICTED)
    assert c.kind is ConstraintKind.NONE
    # predicate allow -> predicates
    c = row_constraint(
        [_allow("sales", "Account", Operation.READ, predicate=pred)],
        p, Operation.READ, "Account", SharingLevel.RESTRICTED,
    )
    assert c.kind is ConstraintKind.PREDICATES
    assert c.allows({"territory": "apac"}, p)
    assert not c.allows({"territory": "emea"}, p)
