"""Ontology type system (hybrid, data-driven).

Type *definitions* are themselves Pydantic models so they can be persisted as
data and round-tripped (PBT-02). Object *instances* (`OntologyObject`) are
generic and validated against their type at write time via a dynamically built
Pydantic model (see ``validation.py``).

Design references: construction/u1-ontology-core/functional-design/domain-entities.md
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, model_validator


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    REFERENCE = "reference"


class Cardinality(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"


class ActionEffect(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    STATE_TRANSITION = "state_transition"


class TypeKind(str, Enum):
    OBJECT = "object"
    LINK = "link"
    ACTION = "action"


# Frozen + extra=forbid gives value-semantics (needed for round-trip equality)
# and rejects unknown keys (analogous to BR-10 at the type level).
_MODEL_CONFIG = {"frozen": True, "extra": "forbid"}


class PropertyType(BaseModel):
    model_config = _MODEL_CONFIG

    name: str
    data_type: DataType
    required: bool = False
    is_pii: bool = False
    # tuples (not lists) so the model is hashable and round-trips deterministically.
    enum_values: tuple[str, ...] | None = None
    ref_object_type: str | None = None

    @model_validator(mode="after")
    def _check(self) -> "PropertyType":
        if not self.name:
            raise ValueError("property name must be non-empty")
        if self.data_type is DataType.ENUM and not self.enum_values:
            raise ValueError(f"property {self.name!r}: ENUM requires enum_values")
        if self.data_type is DataType.REFERENCE and not self.ref_object_type:
            raise ValueError(f"property {self.name!r}: REFERENCE requires ref_object_type")
        return self


class ObjectType(BaseModel):
    model_config = _MODEL_CONFIG

    name: str
    properties: tuple[PropertyType, ...]
    id_property: str = "id"
    title_property: str | None = None
    text_properties: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _check(self) -> "ObjectType":
        names = [p.name for p in self.properties]
        if not self.name:
            raise ValueError("object type name must be non-empty")
        if len(names) != len(set(names)):
            raise ValueError(f"object type {self.name!r}: duplicate property names")
        if self.id_property not in names:
            raise ValueError(f"object type {self.name!r}: id_property {self.id_property!r} not in properties")
        if self.title_property is not None and self.title_property not in names:
            raise ValueError(f"object type {self.name!r}: title_property not in properties")
        for t in self.text_properties:
            if t not in names:
                raise ValueError(f"object type {self.name!r}: text_property {t!r} not in properties")
        return self

    def property(self, name: str) -> PropertyType | None:
        for p in self.properties:
            if p.name == name:
                return p
        return None


class LinkType(BaseModel):
    model_config = _MODEL_CONFIG

    name: str
    source_type: str
    target_type: str
    cardinality: Cardinality
    inverse_name: str

    @model_validator(mode="after")
    def _check(self) -> "LinkType":
        if not (self.name and self.source_type and self.target_type and self.inverse_name):
            raise ValueError("link type requires name, source_type, target_type, inverse_name")
        if self.name == self.inverse_name:
            raise ValueError(f"link type {self.name!r}: name and inverse_name must differ")
        return self


class ActionType(BaseModel):
    model_config = _MODEL_CONFIG

    name: str
    target_type: str
    input_schema: tuple[PropertyType, ...] = ()
    effect: ActionEffect
    preconditions: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _check(self) -> "ActionType":
        if not (self.name and self.target_type):
            raise ValueError("action type requires name and target_type")
        names = [p.name for p in self.input_schema]
        if len(names) != len(set(names)):
            raise ValueError(f"action type {self.name!r}: duplicate input property names")
        return self


TypeDef = ObjectType | LinkType | ActionType


class OntologyObject(BaseModel):
    """A generic, type-driven object instance.

    ``properties`` holds JSON-native values only (dates/datetimes are stored as
    ISO-8601 strings) so serialization round-trips exactly (PBT-02 / TP-2).
    """

    model_config = {"frozen": True}

    object_type: str
    id: str
    properties: dict[str, Any]
