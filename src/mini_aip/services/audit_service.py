"""AuditService — records and queries the tamper-evident audit trail (U5).

record() is synchronous and propagates failures so callers fail closed
(no action survives without its audit record — INV-2 / SECURITY-14/15).
Querying is governance-only (AuditEvent is RESTRICTED, enforced via the gateway).
"""

from __future__ import annotations

from ..domain.audit import AuditEvent, AuditFilter
from ..domain.permission import Operation
from ..domain.permission.models import Principal
from ..ports import AuditSinkPort
from .permission_gateway import PermissionGateway

AUDIT_TYPE = "AuditEvent"  # pseudo type; RESTRICTED -> governance-only reads


class AuditService:
    def __init__(self, sink: AuditSinkPort, gateway: PermissionGateway) -> None:
        self._sink = sink
        self._gateway = gateway

    def record(self, event: AuditEvent) -> None:
        # Errors propagate on purpose (fail-closed).
        self._sink.append(event)

    def query(self, principal: Principal, filter: AuditFilter) -> list[AuditEvent]:
        self._gateway.authorize_object(principal, AUDIT_TYPE, Operation.READ)
        return self._sink.query(filter)
