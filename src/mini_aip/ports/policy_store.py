"""PolicyStorePort — the contract for persisting permission rules."""

from __future__ import annotations

from typing import Protocol

from ..domain.permission import PermissionRule


class PolicyStorePort(Protocol):
    def load_all(self) -> list[PermissionRule]:
        """Load every persisted permission rule (used at startup)."""
        ...

    def save(self, rule: PermissionRule) -> None:
        """Insert or update a single rule."""
        ...
