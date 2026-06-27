"""Permission domain models.

Design: construction/u2-permission/functional-design/domain-entities.md
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

WILDCARD = "*"

_FROZEN = {"frozen": True, "extra": "forbid"}


class Operation(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class Effect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class Principal(BaseModel):
    """The calling subject. AI clients act as proxies and carry the user's id,
    roles and attributes (resolved at authentication time by U6)."""

    model_config = _FROZEN

    id: str
    roles: tuple[str, ...] = ()
    # e.g. {"department": ("sales",), "territory": ("apac",)}
    attributes: dict[str, tuple[str, ...]] = Field(default_factory=dict)


class AttributePredicate(BaseModel):
    """Row-level condition: object[object_property] ∈ principal.attributes[principal_attribute]."""

    model_config = _FROZEN

    object_property: str
    principal_attribute: str

    def matches(self, object_attrs: dict[str, Any], principal: Principal) -> bool:
        allowed = principal.attributes.get(self.principal_attribute, ())
        value = object_attrs.get(self.object_property)
        return value is not None and value in allowed


class PermissionRule(BaseModel):
    model_config = _FROZEN

    id: str
    role: str
    object_type: str  # WILDCARD ("*") matches any type
    operation: Operation
    effect: Effect
    # Only meaningful for ALLOW rules. DENY rules are unconditional (type+op level).
    row_predicate: AttributePredicate | None = None

    def applies_to(self, roles: tuple[str, ...], object_type: str, operation: Operation) -> bool:
        return (
            self.role in roles
            and (self.object_type == object_type or self.object_type == WILDCARD)
            and self.operation == operation
        )


class AccessDecision(BaseModel):
    model_config = {"frozen": True}

    allowed: bool
    reason: str = ""  # PII-free, for audit/debug


class ConstraintKind(str, Enum):
    UNCONSTRAINED = "unconstrained"  # all rows
    NONE = "none"  # no rows (deny)
    PREDICATES = "predicates"  # rows matching any predicate (OR)


class AccessConstraint(BaseModel):
    model_config = _FROZEN

    kind: ConstraintKind
    predicates: tuple[AttributePredicate, ...] = ()

    @classmethod
    def unconstrained(cls) -> "AccessConstraint":
        return cls(kind=ConstraintKind.UNCONSTRAINED)

    @classmethod
    def none(cls) -> "AccessConstraint":
        return cls(kind=ConstraintKind.NONE)

    @classmethod
    def of(cls, predicates: tuple[AttributePredicate, ...]) -> "AccessConstraint":
        return cls(kind=ConstraintKind.PREDICATES, predicates=predicates)

    def allows(self, object_attrs: dict[str, Any], principal: Principal) -> bool:
        if self.kind is ConstraintKind.UNCONSTRAINED:
            return True
        if self.kind is ConstraintKind.NONE:
            return False
        return any(p.matches(object_attrs, principal) for p in self.predicates)
