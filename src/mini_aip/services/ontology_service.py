"""OntologyService — application orchestration for the ontology core (U1).

U1 is the foundation unit and has no dependency on U2 (Permission) or U5
(Audit), which are not implemented yet. Per the application design, type/object
operations must ultimately pass through the PermissionGateway and be recorded by
AuditService. To stay self-contained *and* ready for that wiring, this service
accepts injectable hooks that default to no-ops:

    - ``authorize(operation, context)``: raise to deny. Default: allow.
    - ``audit(event)``: record an event. Default: ignore.

When U2/U5 land, the container injects real implementations — no change to this
service's callers.
"""

from __future__ import annotations

from typing import Any, Callable

from ..domain.ontology import (
    DynamicModelFactory,
    ObjectType,
    OntologyObject,
    TypeDef,
    TypeRegistry,
    validate_object,
    validate_type_def,
)
from ..ports import ObjectStorePort, TypeRegistryPort

AuthorizeHook = Callable[[str, dict[str, Any]], None]
AuditHook = Callable[[dict[str, Any]], None]


def _allow(operation: str, context: dict[str, Any]) -> None:  # noqa: ARG001
    return None


def _ignore(event: dict[str, Any]) -> None:  # noqa: ARG001
    return None


class OntologyService:
    def __init__(
        self,
        registry: TypeRegistry,
        type_store: TypeRegistryPort,
        object_store: ObjectStorePort,
        factory: DynamicModelFactory | None = None,
        *,
        authorize: AuthorizeHook = _allow,
        audit: AuditHook = _ignore,
    ) -> None:
        self._registry = registry
        self._type_store = type_store
        self._object_store = object_store
        self._factory = factory or DynamicModelFactory()
        self._authorize = authorize
        self._audit = audit

    # ---- startup -----------------------------------------------------------
    def reload_types(self) -> None:
        """Load all persisted type definitions into the in-memory registry."""
        self._registry.load(self._type_store.load_all())

    # ---- type operations (US-F1 / US-D2) -----------------------------------
    def register_type(self, typedef: TypeDef, principal: Any = None) -> None:
        self._authorize("register_type", {"principal": principal, "type": typedef.name})
        # Cross-type integrity (within-model checks already ran in validators).
        validate_type_def(typedef, self._registry)
        # Persist first, then update the in-memory registry (single process).
        self._type_store.save(typedef)
        self._registry.register(typedef)
        self._audit({"op": "register_type", "principal": principal, "type": typedef.name})

    def get_object_type(self, name: str) -> ObjectType:
        return self._registry.get_object_type(name)

    def list_object_types(self) -> list[ObjectType]:
        return self._registry.list_object_types()

    # ---- object operations (US-F1 / US-H1 storage foundation) --------------
    def put_object(self, obj: OntologyObject, principal: Any = None) -> None:
        self._authorize("put_object", {"principal": principal, "type": obj.object_type})
        ot = self._registry.get_object_type(obj.object_type)
        validate_object(ot, obj, self._factory, exists=self._object_store.exists)
        self._object_store.write(obj)
        self._audit(
            {"op": "put_object", "principal": principal, "type": obj.object_type, "id": obj.id}
        )

    def get_object(
        self, object_type: str, obj_id: str, principal: Any = None
    ) -> OntologyObject | None:
        self._authorize("get_object", {"principal": principal, "type": object_type})
        # Ensures the type exists (raises TypeNotFoundError otherwise).
        self._registry.get_object_type(object_type)
        obj = self._object_store.get(object_type, obj_id)
        self._audit(
            {"op": "get_object", "principal": principal, "type": object_type, "id": obj_id}
        )
        return obj
