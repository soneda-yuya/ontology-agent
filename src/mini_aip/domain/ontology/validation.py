"""Validation for type definitions and object instances.

Hybrid model: a Pydantic model is built *dynamically* from an ``ObjectType``
to validate object instances at write time (F4 = write-time only). Error
messages list offending *field names only* — never values — so PII never
leaks into errors/logs (SECURITY-03). All failures are fail-closed
(SECURITY-15): nothing is persisted on error.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Callable

from pydantic import BaseModel, ConfigDict, ValidationError, create_model

from .errors import DomainValidationError, TypeNotFoundError
from .types import ActionType, DataType, LinkType, ObjectType, OntologyObject, TypeDef

if TYPE_CHECKING:
    from .registry import TypeRegistry

# Structural python type per data type. DATE/DATETIME/ENUM/REFERENCE are stored
# as strings (JSON-native) and checked semantically below.
_PY_TYPE: dict[DataType, type] = {
    DataType.STRING: str,
    DataType.INTEGER: int,
    DataType.FLOAT: float,
    DataType.BOOLEAN: bool,
    DataType.DATE: str,
    DataType.DATETIME: str,
    DataType.ENUM: str,
    DataType.REFERENCE: str,
}

# Existence check for REFERENCE properties: (object_type, id) -> bool.
ExistsFn = Callable[[str, str], bool]


class DynamicModelFactory:
    """Builds (and caches) a Pydantic model for an ObjectType's structure."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[ObjectType, type[BaseModel]]] = {}

    def build(self, ot: ObjectType) -> type[BaseModel]:
        cached = self._cache.get(ot.name)
        if cached is not None and cached[0] == ot:
            return cached[1]
        fields: dict[str, Any] = {}
        for p in ot.properties:
            ann = _PY_TYPE[p.data_type]
            if p.required:
                fields[p.name] = (ann, ...)
            else:
                fields[p.name] = (ann | None, None)
        model = create_model(  # type: ignore[call-overload]
            f"Obj_{ot.name}",
            __config__=ConfigDict(extra="forbid"),
            **fields,
        )
        self._cache[ot.name] = (ot, model)
        return model


def _parse_or_raise(value: str, parser: Callable[[str], Any], ot_name: str, field: str) -> None:
    try:
        parser(value)
    except (ValueError, TypeError) as exc:
        raise DomainValidationError(
            f"object of type {ot_name!r}: field {field!r} is not a valid {parser.__name__}"
        ) from exc


def validate_object(
    ot: ObjectType,
    obj: OntologyObject,
    factory: DynamicModelFactory,
    exists: ExistsFn | None = None,
) -> None:
    """Validate an object instance against its type. Raises DomainValidationError.

    Checks: structure/required/no-surplus (dynamic Pydantic, BR-7/8/10),
    then ENUM membership, DATE/DATETIME format, and REFERENCE existence (BR-9).
    """
    if obj.object_type != ot.name:
        raise DomainValidationError(
            f"object_type mismatch: object says {obj.object_type!r}, type is {ot.name!r}"
        )
    model = factory.build(ot)
    try:
        model.model_validate(obj.properties)
    except ValidationError as exc:
        # Names only — never include values (SECURITY-03 / PII-safe).
        fields = sorted({str(e["loc"][0]) for e in exc.errors() if e.get("loc")})
        raise DomainValidationError(
            f"object of type {ot.name!r}: invalid properties: {fields}"
        ) from None

    for p in ot.properties:
        value = obj.properties.get(p.name)
        if value is None:
            continue
        if p.data_type is DataType.ENUM:
            assert p.enum_values is not None
            if value not in p.enum_values:
                raise DomainValidationError(
                    f"object of type {ot.name!r}: field {p.name!r} not an allowed enum value"
                )
        elif p.data_type is DataType.DATE:
            _parse_or_raise(value, date.fromisoformat, ot.name, p.name)
        elif p.data_type is DataType.DATETIME:
            _parse_or_raise(value, datetime.fromisoformat, ot.name, p.name)
        elif p.data_type is DataType.REFERENCE and exists is not None:
            assert p.ref_object_type is not None
            if not exists(p.ref_object_type, str(value)):
                raise DomainValidationError(
                    f"object of type {ot.name!r}: field {p.name!r} references a missing object"
                )


def validate_type_def(typedef: TypeDef, registry: "TypeRegistry") -> None:
    """Cross-type integrity checks against the registry (BR-4/5/6).

    Within-model checks already run in the type's own validators.
    """
    if isinstance(typedef, ObjectType):
        for p in typedef.properties:
            if p.data_type is DataType.REFERENCE:
                assert p.ref_object_type is not None
                # self-reference is allowed
                if p.ref_object_type != typedef.name and not registry.has_object_type(
                    p.ref_object_type
                ):
                    raise TypeNotFoundError(p.ref_object_type)
    elif isinstance(typedef, LinkType):
        for ref in (typedef.source_type, typedef.target_type):
            if not registry.has_object_type(ref):
                raise TypeNotFoundError(ref)
    elif isinstance(typedef, ActionType):
        if not registry.has_object_type(typedef.target_type):
            raise TypeNotFoundError(typedef.target_type)
        for p in typedef.input_schema:
            if p.data_type is DataType.REFERENCE:
                assert p.ref_object_type is not None
                if not registry.has_object_type(p.ref_object_type):
                    raise TypeNotFoundError(p.ref_object_type)
    else:  # pragma: no cover - guarded by typing
        raise DomainValidationError("unknown type definition")
