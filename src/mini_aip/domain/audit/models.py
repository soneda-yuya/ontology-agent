"""Audit & Activity event models.

Both are immutable, PII-free (refs only), and round-trip serializable (PBT-02).
Design: construction/u5-audit/functional-design/domain-entities.md
"""

from __future__ import annotations

from pydantic import BaseModel

_FROZEN = {"frozen": True, "extra": "forbid"}

# Operations that warrant a shared Activity entry (Q-A2 = significant only).
SIGNIFICANT_OPS = frozenset({"put_object", "invoke_action", "register_type"})


class AuditEvent(BaseModel):
    """Tamper-evident security trail entry. Never contains PII values."""

    model_config = _FROZEN

    id: str
    timestamp: str  # ISO-8601, assigned at record time
    operation: str
    actor: str | None = None
    roles: tuple[str, ...] = ()
    object_type: str | None = None
    object_id: str | None = None
    decision: str = "allowed"  # allowed | denied
    outcome: str = "ok"  # ok | error
    reason: str = ""  # PII-free


class ActivityEvent(BaseModel):
    """Team-shared work history entry, readable as context."""

    model_config = _FROZEN

    id: str
    timestamp: str
    actor: str
    action: str
    object_type: str | None = None
    object_id: str | None = None
    visibility: str = "shared"


class AuditFilter(BaseModel):
    model_config = {"extra": "forbid"}

    actor: str | None = None
    object_type: str | None = None
    since: str | None = None
    until: str | None = None
    decision: str | None = None
    limit: int = 100


class ActivityFilter(BaseModel):
    model_config = {"extra": "forbid"}

    actor: str | None = None
    object_type: str | None = None
    since: str | None = None
    until: str | None = None
    limit: int = 100
