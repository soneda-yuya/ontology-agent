"""PermissionGateway — the single, central authorization point (U2).

Every read/aggregate/action must pass through here. Fail-closed: any error,
missing principal, or unknown type results in denial (SECURITY-08/15).

Wiring: ``authorize_hook`` adapts the gateway to U1 OntologyService's
``authorize(operation, context)`` hook, replacing its no-op default with real,
type-level enforcement. Row-level enforcement for a *single* object (IDOR,
US-C2) is applied by U3 RetrievalService via ``authorize_object`` after the
object is fetched (it has the attributes there); U1's ``get_object`` is a
foundational primitive that only carries the type at hook time.
"""

from __future__ import annotations

from typing import Any

from ..domain.ontology import SharingLevel, TypeNotFoundError, TypeRegistry
from ..domain.permission import (
    AccessConstraint,
    Operation,
    PermissionDenied,
    PolicyRegistry,
    decide,
    row_constraint,
)
from ..domain.permission.models import Principal

# Maps U1 OntologyService hook operations to permission operations.
_OPERATION_MAP = {
    "register_type": Operation.ADMIN,
    "put_object": Operation.WRITE,
    "get_object": Operation.READ,
}


class PermissionGateway:
    def __init__(self, policy_registry: PolicyRegistry, type_registry: TypeRegistry) -> None:
        self._policies = policy_registry
        self._types = type_registry

    def _sharing(self, object_type: str) -> SharingLevel:
        try:
            return self._types.get_object_type(object_type).sharing_level
        except TypeNotFoundError:
            return SharingLevel.RESTRICTED  # safe default (fail-closed)

    # ---- direct API --------------------------------------------------------
    def authorize_object(
        self,
        principal: Principal,
        object_type: str,
        operation: Operation,
        object_attrs: dict[str, Any] | None = None,
    ) -> None:
        d = decide(
            self._policies.rules(),
            principal,
            operation,
            object_type,
            self._sharing(object_type),
            object_attrs=object_attrs,
        )
        if not d.allowed:
            raise PermissionDenied(d.reason)

    def authorize_query(
        self, principal: Principal, object_type: str, operation: Operation = Operation.READ
    ) -> AccessConstraint:
        return row_constraint(
            self._policies.rules(),
            principal,
            operation,
            object_type,
            self._sharing(object_type),
        )

    def authorize_action(
        self, principal: Principal, target_type: str, target_attrs: dict[str, Any] | None = None
    ) -> None:
        self.authorize_object(principal, target_type, Operation.WRITE, target_attrs)

    # ---- U1 hook adapter ---------------------------------------------------
    def authorize_hook(self, operation: str, context: dict[str, Any]) -> None:
        """Adapter matching OntologyService's ``authorize(operation, context)``."""
        principal = context.get("principal")
        if not isinstance(principal, Principal):
            raise PermissionDenied("no principal")  # deny-by-default (SECURITY-08)
        op = _OPERATION_MAP.get(operation)
        if op is None:
            raise PermissionDenied("unknown operation")  # fail-closed
        object_type = context.get("type", "")
        # Type-level gate (row-level for single objects handled by U3 with attrs).
        self.authorize_object(principal, object_type, op, object_attrs=None)
