"""Domain errors for the ontology core.

All errors are designed to be *safe* to surface: messages must never include
PII property *values* (SECURITY-03). They carry enough structure for the
service layer to map to safe API responses without leaking internals
(SECURITY-09).
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all ontology domain errors."""


class DomainValidationError(DomainError):
    """A type definition or object failed validation (BR-1..BR-10).

    Raised before any persistence happens — fail-closed (SECURITY-15).
    """


class TypeNotFoundError(DomainError):
    """A referenced type name is not present in the registry."""

    def __init__(self, name: str) -> None:
        super().__init__(f"type not found: {name!r}")
        self.name = name


class DuplicateTypeError(DomainError):
    """A type name is already registered with a different kind."""

    def __init__(self, name: str) -> None:
        super().__init__(f"type already registered under a different kind: {name!r}")
        self.name = name
