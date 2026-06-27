"""Serialize / deserialize type definitions and objects.

Round-trip property (PBT-02, TP-1/TP-2):
    deserialize_type(serialize_type(t)) == t       for all valid TypeDef t
    deserialize_object(serialize_object(o)) == o    for all valid OntologyObject o
"""

from __future__ import annotations

from typing import Any

from .errors import DomainValidationError
from .types import ActionType, LinkType, ObjectType, OntologyObject, TypeDef, TypeKind

_KIND_BY_CLS = {
    ObjectType: TypeKind.OBJECT,
    LinkType: TypeKind.LINK,
    ActionType: TypeKind.ACTION,
}
_CLS_BY_KIND = {
    TypeKind.OBJECT: ObjectType,
    TypeKind.LINK: LinkType,
    TypeKind.ACTION: ActionType,
}


def kind_of(t: TypeDef) -> TypeKind:
    try:
        return _KIND_BY_CLS[type(t)]
    except KeyError as exc:  # pragma: no cover - guarded by typing
        raise DomainValidationError("unknown type definition class") from exc


def serialize_type(t: TypeDef) -> dict[str, Any]:
    """Return ``{"kind": ..., "definition": {...}}`` (JSON-native)."""
    return {"kind": kind_of(t).value, "definition": t.model_dump(mode="json")}


def deserialize_type(data: dict[str, Any]) -> TypeDef:
    try:
        kind = TypeKind(data["kind"])
        definition = data["definition"]
    except (KeyError, ValueError) as exc:
        raise DomainValidationError("malformed serialized type definition") from exc
    cls = _CLS_BY_KIND[kind]
    return cls.model_validate(definition)


def serialize_object(o: OntologyObject) -> dict[str, Any]:
    return o.model_dump(mode="json")


def deserialize_object(data: dict[str, Any]) -> OntologyObject:
    return OntologyObject.model_validate(data)
