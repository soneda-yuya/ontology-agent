"""Composition root — wires ports to concrete adapters (dependency injection).

U1 wires the ontology service against the Postgres adapters. Permission (U2)
and Audit (U5) hooks are left at their no-op defaults until those units exist;
this is the single place they will later be injected.
"""

from __future__ import annotations

from ..adapters.outbound.postgres import (
    ConnectionProvider,
    PostgresObjectStore,
    PostgresPolicyStore,
    PostgresTypeRegistry,
)
from ..domain.ontology import TypeRegistry
from ..domain.permission import PolicyRegistry
from ..services import OntologyService, PermissionGateway
from .settings import Settings


def build_ontology_service(settings: Settings | None = None) -> OntologyService:
    """Unsecured build (authorize/audit = no-op). Useful for bootstrap/tests."""
    settings = settings or Settings()
    provider = ConnectionProvider(settings.database_url)
    type_store = PostgresTypeRegistry(provider)
    object_store = PostgresObjectStore(provider)
    registry = TypeRegistry()

    service = OntologyService(
        registry=registry,
        type_store=type_store,
        object_store=object_store,
        # authorize / audit: no-op defaults (U5 audit injected later).
    )
    service.reload_types()
    return service


def build_secured_ontology_service(settings: Settings | None = None) -> OntologyService:
    """Wires U2 PermissionGateway into U1's authorize hook (real enforcement).

    Bootstrap note: with an empty `policies` table, deny-by-default blocks even
    ADMIN (register_type). Seed at least one admin ALLOW rule (e.g. via
    PostgresPolicyStore.save) before using this service to register types.
    """
    settings = settings or Settings()
    provider = ConnectionProvider(settings.database_url)
    type_store = PostgresTypeRegistry(provider)
    object_store = PostgresObjectStore(provider)
    policy_store = PostgresPolicyStore(provider)

    type_registry = TypeRegistry()
    type_registry.load(type_store.load_all())

    policy_registry = PolicyRegistry()
    policy_registry.load(policy_store.load_all())

    gateway = PermissionGateway(policy_registry, type_registry)

    return OntologyService(
        registry=type_registry,
        type_store=type_store,
        object_store=object_store,
        authorize=gateway.authorize_hook,
        # audit: injected when U5 lands.
    )
