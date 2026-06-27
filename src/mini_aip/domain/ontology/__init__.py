"""Ontology core domain (U1).

Public API for the ontology type system: type definitions, generic objects,
the in-memory registry, validation, serialization, and PII redaction.
"""

from .errors import (
    DomainError,
    DomainValidationError,
    DuplicateTypeError,
    TypeNotFoundError,
)
from .redaction import PiiRedactor
from .registry import TypeRegistry
from .serialization import (
    deserialize_object,
    deserialize_type,
    kind_of,
    serialize_object,
    serialize_type,
)
from .types import (
    ActionEffect,
    ActionType,
    Cardinality,
    DataType,
    LinkType,
    ObjectType,
    OntologyObject,
    PropertyType,
    SharingLevel,
    TypeDef,
    TypeKind,
)
from .validation import DynamicModelFactory, validate_object, validate_type_def

__all__ = [
    "ActionEffect",
    "ActionType",
    "Cardinality",
    "DataType",
    "DomainError",
    "DomainValidationError",
    "DuplicateTypeError",
    "DynamicModelFactory",
    "LinkType",
    "ObjectType",
    "OntologyObject",
    "PiiRedactor",
    "PropertyType",
    "SharingLevel",
    "TypeDef",
    "TypeKind",
    "TypeNotFoundError",
    "TypeRegistry",
    "deserialize_object",
    "deserialize_type",
    "kind_of",
    "serialize_object",
    "serialize_type",
    "validate_object",
    "validate_type_def",
]
