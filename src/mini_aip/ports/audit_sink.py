"""AuditSinkPort — append-only sink for audit events.

Deliberately exposes no update/delete: audit records are immutable (SECURITY-14).
"""

from __future__ import annotations

from typing import Protocol

from ..domain.audit import AuditEvent, AuditFilter


class AuditSinkPort(Protocol):
    def append(self, event: AuditEvent) -> None: ...

    def query(self, filter: AuditFilter) -> list[AuditEvent]: ...
