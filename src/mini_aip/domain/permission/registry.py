"""In-memory PolicyRegistry (load at startup, update on change).

Same single-process strategy as U1's TypeRegistry; multi-process invalidation
(LISTEN/NOTIFY) is a future extension point.
"""

from __future__ import annotations

from .models import PermissionRule


class PolicyRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, PermissionRule] = {}

    def load(self, rules: list[PermissionRule]) -> None:
        self._rules = {r.id: r for r in rules}

    def upsert(self, rule: PermissionRule) -> None:
        self._rules[rule.id] = rule

    def rules(self) -> list[PermissionRule]:
        return list(self._rules.values())
