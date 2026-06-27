"""In-memory TypeRegistry (NFR: load at startup, update on register).

Single-process assumption (NFR-U1-3). For multi-process deployments this is
where a LISTEN/NOTIFY-based invalidation would be added — the interface stays
the same.
"""

from __future__ import annotations

from .errors import DuplicateTypeError, TypeNotFoundError
from .types import ActionType, LinkType, ObjectType, TypeDef


class TypeRegistry:
    def __init__(self) -> None:
        self._objects: dict[str, ObjectType] = {}
        self._links: dict[str, LinkType] = {}
        self._actions: dict[str, ActionType] = {}

    # ---- loading -----------------------------------------------------------
    def load(self, defs: list[TypeDef]) -> None:
        """Replace the registry contents (e.g. at startup)."""
        self._objects.clear()
        self._links.clear()
        self._actions.clear()
        for d in defs:
            self._put(d)

    def register(self, typedef: TypeDef) -> None:
        """Insert or update a single type definition (in-memory)."""
        self._put(typedef)

    def _put(self, typedef: TypeDef) -> None:
        name = typedef.name
        if isinstance(typedef, ObjectType):
            self._reject_other_kind(name, self._links, self._actions)
            self._objects[name] = typedef
        elif isinstance(typedef, LinkType):
            self._reject_other_kind(name, self._objects, self._actions)
            self._links[name] = typedef
        elif isinstance(typedef, ActionType):
            self._reject_other_kind(name, self._objects, self._links)
            self._actions[name] = typedef

    @staticmethod
    def _reject_other_kind(name: str, *others: dict[str, object]) -> None:
        if any(name in o for o in others):
            raise DuplicateTypeError(name)

    # ---- lookups -----------------------------------------------------------
    def has_object_type(self, name: str) -> bool:
        return name in self._objects

    def get_object_type(self, name: str) -> ObjectType:
        try:
            return self._objects[name]
        except KeyError:
            raise TypeNotFoundError(name) from None

    def get_link_type(self, name: str) -> LinkType:
        try:
            return self._links[name]
        except KeyError:
            raise TypeNotFoundError(name) from None

    def get_action_type(self, name: str) -> ActionType:
        try:
            return self._actions[name]
        except KeyError:
            raise TypeNotFoundError(name) from None

    def list_object_types(self) -> list[ObjectType]:
        return list(self._objects.values())

    def list_link_types(self) -> list[LinkType]:
        return list(self._links.values())

    def list_action_types(self) -> list[ActionType]:
        return list(self._actions.values())

    def links_from(self, object_type: str) -> list[LinkType]:
        return [lt for lt in self._links.values() if lt.source_type == object_type]
