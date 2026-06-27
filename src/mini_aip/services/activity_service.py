"""ActivityService — records and queries the shared work history (U5).

Activity is team-shared context (ActivityEvent is SHARED). Reads pass through
the gateway; for a SHARED type the constraint is unconstrained, so the whole
team can read it (a NONE constraint means denied -> fail closed).
"""

from __future__ import annotations

from ..domain.audit import ActivityEvent, ActivityFilter
from ..domain.permission import ConstraintKind, PermissionDenied
from ..domain.permission.models import Principal
from ..ports import ActivityLogPort
from .permission_gateway import PermissionGateway

ACTIVITY_TYPE = "ActivityEvent"  # pseudo type; SHARED -> broadly readable


class ActivityService:
    def __init__(self, log: ActivityLogPort, gateway: PermissionGateway) -> None:
        self._log = log
        self._gateway = gateway

    def record(self, event: ActivityEvent) -> None:
        self._log.append(event)

    def query(self, principal: Principal, filter: ActivityFilter) -> list[ActivityEvent]:
        constraint = self._gateway.authorize_query(principal, ACTIVITY_TYPE)
        if constraint.kind is ConstraintKind.NONE:
            raise PermissionDenied("activity not readable")
        return self._log.query(filter)
