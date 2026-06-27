"""PII redaction helper (SECURITY-03, BR-11).

Any property whose ``PropertyType.is_pii`` is True must never appear in logs or
error output. Use ``PiiRedactor.redact`` before logging object properties.
"""

from __future__ import annotations

from typing import Any

from .types import ObjectType

REDACTED = "[REDACTED]"


class PiiRedactor:
    """Masks PII property values based on an ObjectType definition."""

    @staticmethod
    def redact(ot: ObjectType, properties: dict[str, Any]) -> dict[str, Any]:
        pii = {p.name for p in ot.properties if p.is_pii}
        return {k: (REDACTED if k in pii else v) for k, v in properties.items()}

    @classmethod
    def redact_for_log(cls, ot: ObjectType, obj_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return {"object_type": ot.name, "id": obj_id, "properties": cls.redact(ot, properties)}
