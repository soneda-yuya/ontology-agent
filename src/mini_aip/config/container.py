"""Composition root — wires ports to concrete adapters (dependency injection).

U1 wires the ontology service against the Postgres adapters. Permission (U2)
and Audit (U5) hooks are left at their no-op defaults until those units exist;
this is the single place they will later be injected.
"""

from __future__ import annotations

from ..adapters.outbound.postgres import (
    ConnectionProvider,
    PostgresActivityLog,
    PostgresAuditSink,
    PostgresObjectStore,
    PostgresPolicyStore,
    PostgresTypeRegistry,
)
from ..domain.ontology import DataType, ObjectType, PropertyType, SharingLevel, TypeRegistry
from ..domain.permission import PolicyRegistry
from ..services import (
    ActivityService,
    AuditAdapter,
    AuditService,
    OntologyService,
    PermissionGateway,
)
from .settings import Settings


def _register_audit_pseudo_types(type_registry: TypeRegistry) -> None:
    """Pseudo types so the gateway can resolve sharing for audit/activity reads.

    AuditEvent = RESTRICTED (governance-only), ActivityEvent = SHARED (team-wide).
    """
    id_prop = (PropertyType(name="id", data_type=DataType.STRING, required=True),)
    type_registry.register(
        ObjectType(name="AuditEvent", properties=id_prop, sharing_level=SharingLevel.RESTRICTED)
    )
    type_registry.register(
        ObjectType(name="ActivityEvent", properties=id_prop, sharing_level=SharingLevel.SHARED)
    )


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
    audit_sink = PostgresAuditSink(provider)
    activity_log = PostgresActivityLog(provider)

    type_registry = TypeRegistry()
    type_registry.load(type_store.load_all())
    _register_audit_pseudo_types(type_registry)

    policy_registry = PolicyRegistry()
    policy_registry.load(policy_store.load_all())

    gateway = PermissionGateway(policy_registry, type_registry)

    # U5 audit/activity, wired into both U1 (post-success) and the gateway (denials).
    audit_service = AuditService(audit_sink, gateway)
    activity_service = ActivityService(activity_log, gateway)
    audit_adapter = AuditAdapter(audit_service, activity_service)
    gateway.set_audit_hook(audit_adapter.audit_hook)

    return OntologyService(
        registry=type_registry,
        type_store=type_store,
        object_store=object_store,
        authorize=gateway.authorize_hook,
        audit=audit_adapter.audit_hook,
    )
