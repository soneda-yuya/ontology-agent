"""Property-based invariants for U2 permission (PBT-03, TP-P1/P2/P4)."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from mini_aip.domain.ontology import SharingLevel
from mini_aip.domain.permission import (
    Effect,
    Operation,
    PermissionRule,
    decide,
    row_constraint,
)

from tests.pbt.perm_generators import object_attrs, policies, principals

ANY_SHARING = st.sampled_from(list(SharingLevel))
ANY_OP = st.sampled_from(list(Operation))


@given(policies(), principals(), ANY_OP, ANY_SHARING, st.one_of(st.none(), object_attrs()))
def test_explicit_deny_always_denies(policy, principal, op, sharing, attrs):
    """TP-P1: an applicable explicit DENY denies regardless of allows/sharing."""
    if not principal.roles:
        return  # need a role to attach the deny to
    deny = PermissionRule(
        id="deny-rule",
        role=principal.roles[0],
        object_type="t1",
        operation=op,
        effect=Effect.DENY,
    )
    d = decide([*policy, deny], principal, op, "t1", sharing, object_attrs=attrs)
    assert d.allowed is False


@given(principals(), ANY_OP)
def test_deny_by_default_on_empty_policy(principal, op):
    """TP-P2: no rules and RESTRICTED type => deny."""
    d = decide([], principal, op, "t1", SharingLevel.RESTRICTED)
    assert d.allowed is False


@given(policies(), principals(), object_attrs(), ANY_SHARING)
def test_decide_consistent_with_row_constraint(policy, principal, attrs, sharing):
    """TP-P4: for READ, decide(attrs) == row_constraint.allows(attrs)."""
    decided = decide(
        policy, principal, Operation.READ, "t1", sharing, object_attrs=attrs
    ).allowed
    constraint = row_constraint(policy, principal, Operation.READ, "t1", sharing)
    assert decided == constraint.allows(attrs, principal)
