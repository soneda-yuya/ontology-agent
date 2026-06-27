"""TypeRegistryPort — the contract for persisting type definitions."""

from __future__ import annotations

from typing import Protocol

from ..domain.ontology import TypeDef


class TypeRegistryPort(Protocol):
    def load_all(self) -> list[TypeDef]:
        """Load every persisted type definition (used at startup)."""
        ...

    def save(self, typedef: TypeDef) -> None:
        """Insert or update a single type definition."""
        ...
