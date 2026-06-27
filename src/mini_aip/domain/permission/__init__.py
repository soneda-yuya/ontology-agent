"""Permission domain (U2): models, pure decision functions, in-memory registry."""

from .decision import Policy, decide, row_constraint
from .errors import PermissionDenied
from .models import (
    AccessConstraint,
    AccessDecision,
    AttributePredicate,
    ConstraintKind,
    Effect,
    Operation,
    PermissionRule,
    Principal,
    WILDCARD,
)
from .registry import PolicyRegistry

__all__ = [
    "WILDCARD",
    "AccessConstraint",
    "AccessDecision",
    "AttributePredicate",
    "ConstraintKind",
    "Effect",
    "Operation",
    "PermissionDenied",
    "PermissionRule",
    "Policy",
    "PolicyRegistry",
    "Principal",
    "decide",
    "row_constraint",
]
