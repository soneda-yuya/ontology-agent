"""Permission errors.

``PermissionDenied`` messages are intentionally generic — never include
principal attribute values or PII (SECURITY-03/09, BR-P7).
"""

from __future__ import annotations


class PermissionDenied(Exception):
    """Raised by the gateway when access is not allowed (fail-closed)."""

    def __init__(self, reason: str = "access denied") -> None:
        super().__init__(reason)
        self.reason = reason
