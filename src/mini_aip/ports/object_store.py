"""ObjectStorePort — the contract for persisting ontology objects.

U1 provides the foundational subset (get / write / exists / list_by_type).
Rich querying (attribute filters, aggregation, traversal) is added by U3
Retrieval, which extends this port.
"""

from __future__ import annotations

from typing import Protocol

from ..domain.ontology import OntologyObject


class ObjectStorePort(Protocol):
    def get(self, object_type: str, obj_id: str) -> OntologyObject | None: ...

    def exists(self, object_type: str, obj_id: str) -> bool: ...

    def write(self, obj: OntologyObject) -> None:
        """Insert or update an object (upsert)."""
        ...

    def list_by_type(self, object_type: str, limit: int = 100) -> list[OntologyObject]: ...
