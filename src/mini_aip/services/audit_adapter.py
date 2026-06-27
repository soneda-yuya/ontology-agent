"""AuditAdapter — bridges U1/U2's ``audit(event_dict)`` hook to U5 services.

The same hook records both allowed operations (called by OntologyService after
success) and denials (called by PermissionGateway before raising). Significant
allowed operations also produce a shared ActivityEvent (BR-AU3/AU5).

id / timestamp are assigned here (application layer), keeping the domain pure.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from ..domain.audit import SIGNIFICANT_OPS, ActivityEvent, AuditEvent
from ..domain.permission.models import Principal
from .activity_service import ActivityService
from .audit_service import AuditService


class AuditAdapter:
    def __init__(self, audit: AuditService, activity: ActivityService) -> None:
        self._audit = audit
        self._activity = activity

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _new_id() -> str:
        return str(uuid.uuid4())

    def audit_hook(self, event: dict[str, Any]) -> None:
        principal = event.get("principal")
        actor = principal.id if isinstance(principal, Principal) else None
        roles = principal.roles if isinstance(principal, Principal) else ()
        op = event.get("op", "")
        decision = event.get("decision", "allowed")
        ts = self._now()

        self._audit.record(
            AuditEvent(
                id=self._new_id(),
                timestamp=ts,
                operation=op,
                actor=actor,
                roles=roles,
                object_type=event.get("type"),
                object_id=event.get("id"),
                decision=decision,
                outcome=event.get("outcome", "ok"),
                reason=event.get("reason", ""),
            )
        )

        if decision == "allowed" and op in SIGNIFICANT_OPS:
            self._activity.record(
                ActivityEvent(
                    id=self._new_id(),
                    timestamp=ts,
                    actor=actor or "unknown",
                    action=f"{op} {event.get('type', '')}".strip(),
                    object_type=event.get("type"),
                    object_id=event.get("id"),
                )
            )
