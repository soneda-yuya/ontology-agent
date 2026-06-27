"""Pure decision functions (no I/O) — the heart of U2.

Resolution order (deny-by-default + explicit-deny-precedence):
  1. matching explicit DENY  -> deny
  2. READ on a SHARED type   -> allow (row constraint bypass)
  3. matching ALLOW          -> allow (row predicate evaluated when attrs given)
  4. otherwise               -> deny

`decide` and `row_constraint` are kept consistent (TP-P4): for READ on a
RESTRICTED type, decide(..., attrs)=allowed  <=>  attrs satisfies row_constraint.
Reasons are PII-free (BR-P7).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..ontology import SharingLevel
from .models import (
    AccessConstraint,
    AccessDecision,
    Effect,
    Operation,
    PermissionRule,
    Principal,
)

Policy = Sequence[PermissionRule]


def _applicable(
    policy: Policy, principal: Principal, object_type: str, operation: Operation
) -> list[PermissionRule]:
    return [r for r in policy if r.applies_to(principal.roles, object_type, operation)]


def decide(
    policy: Policy,
    principal: Principal,
    operation: Operation,
    object_type: str,
    sharing_level: SharingLevel,
    object_attrs: dict[str, Any] | None = None,
) -> AccessDecision:
    applicable = _applicable(policy, principal, object_type, operation)

    if any(r.effect is Effect.DENY for r in applicable):
        return AccessDecision(allowed=False, reason="explicit deny")

    if operation is Operation.READ and sharing_level is SharingLevel.SHARED:
        return AccessDecision(allowed=True, reason="shared type")

    for r in applicable:
        if r.effect is not Effect.ALLOW:
            continue
        if r.row_predicate is None:
            return AccessDecision(allowed=True, reason="type-level allow")
        if object_attrs is None:
            # Type-level grant; row check deferred to where attrs are available.
            return AccessDecision(allowed=True, reason="type-level allow (row deferred)")
        if r.row_predicate.matches(object_attrs, principal):
            return AccessDecision(allowed=True, reason="row allow")

    return AccessDecision(allowed=False, reason="deny-by-default")


def row_constraint(
    policy: Policy,
    principal: Principal,
    operation: Operation,
    object_type: str,
    sharing_level: SharingLevel,
) -> AccessConstraint:
    applicable = _applicable(policy, principal, object_type, operation)

    if any(r.effect is Effect.DENY for r in applicable):
        return AccessConstraint.none()

    if operation is Operation.READ and sharing_level is SharingLevel.SHARED:
        return AccessConstraint.unconstrained()

    allow = [r for r in applicable if r.effect is Effect.ALLOW]
    if any(r.row_predicate is None for r in allow):
        return AccessConstraint.unconstrained()

    predicates = tuple(r.row_predicate for r in allow if r.row_predicate is not None)
    if not predicates:
        return AccessConstraint.none()
    return AccessConstraint.of(predicates)
