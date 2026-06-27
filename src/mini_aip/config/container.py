"""Composition root — wires ports to concrete adapters (dependency injection).

U1 wires the ontology service against the Postgres adapters. Permission (U2)
and Audit (U5) hooks are left at their no-op defaults until those units exist;
this is the single place they will later be injected.
"""

from __future__ import annotations

from ..adapters.outbound.postgres import (
    ConnectionProvider,
    PostgresObjectStore,
    PostgresTypeRegistry,
)
from ..domain.ontology import TypeRegistry
from ..services import OntologyService
from .settings import Settings


def build_ontology_service(settings: Settings | None = None) -> OntologyService:
    settings = settings or Settings()
    provider = ConnectionProvider(settings.database_url)
    type_store = PostgresTypeRegistry(provider)
    object_store = PostgresObjectStore(provider)
    registry = TypeRegistry()

    service = OntologyService(
        registry=registry,
        type_store=type_store,
        object_store=object_store,
        # authorize / audit: no-op defaults (U2/U5 inject real implementations here).
    )
    service.reload_types()
    return service
