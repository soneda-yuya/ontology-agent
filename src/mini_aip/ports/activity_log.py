"""ActivityLogPort — append-only log for shared activity events.

No update/delete (append-only, SECURITY-14).
"""

from __future__ import annotations

from typing import Protocol

from ..domain.audit import ActivityEvent, ActivityFilter


class ActivityLogPort(Protocol):
    def append(self, event: ActivityEvent) -> None: ...

    def query(self, filter: ActivityFilter) -> list[ActivityEvent]: ...
