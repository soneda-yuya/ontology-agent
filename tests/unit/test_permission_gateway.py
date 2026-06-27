"""Tests for PermissionGateway and its U1 authorize-hook adapter."""

import pytest

from mini_aip.domain.ontology import (
    DataType,
    ObjectType,
    PropertyType,
    SharingLevel,
    TypeRegistry,
)
from mini_aip.domain.permission import (
    ConstraintKind,
    Effect,
    Operation,
    PermissionDenied,
    PermissionRule,
    PolicyRegistry,
    Principal,
)
from mini_aip.services import OntologyService, PermissionGateway

from tests.unit.test_ontology_service import InMemoryObjectStore, InMemoryTypeStore


def _registries():
    types = TypeRegistry()
    types.register(
        ObjectType(
            name="Note",
            properties=(PropertyType(name="id", data_type=DataType.STRING, required=True),),
            sharing_level=SharingLevel.SHARED,
        )
    )
    types.register(
        ObjectType(
            name="Customer",
            properties=(PropertyType(name="id", data_type=DataType.STRING, required=True),),
            sharing_level=SharingLevel.RESTRICTED,
        )
    )
    policies = PolicyRegistry()
    return types, policies


def test_hook_allows_shared_read():
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    gw.authorize_hook("get_object", {"principal": Principal(id="u", roles=("cs",)), "type": "Note"})


def test_hook_denies_restricted_without_policy():
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    with pytest.raises(PermissionDenied):
        gw.authorize_hook(
            "get_object", {"principal": Principal(id="u", roles=("cs",)), "type": "Customer"}
        )


def test_hook_denies_missing_principal():
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    with pytest.raises(PermissionDenied):
        gw.authorize_hook("get_object", {"principal": None, "type": "Note"})


def test_hook_denies_unknown_operation():
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    with pytest.raises(PermissionDenied):
        gw.authorize_hook("explode", {"principal": Principal(id="u"), "type": "Note"})


def test_authorize_query_returns_constraint():
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    c = gw.authorize_query(Principal(id="u", roles=("cs",)), "Note")
    assert c.kind is ConstraintKind.UNCONSTRAINED


def test_secured_service_blocks_register_without_admin_policy():
    types, policies = _registries()
    gw = PermissionGateway(policies, types)
    svc = OntologyService(
        registry=types,
        type_store=InMemoryTypeStore(),
        object_store=InMemoryObjectStore(),
        authorize=gw.authorize_hook,
    )
    new_type = ObjectType(
        name="Ticket",
        properties=(PropertyType(name="id", data_type=DataType.STRING, required=True),),
    )
    with pytest.raises(PermissionDenied):
        svc.register_type(new_type, principal=Principal(id="u", roles=("cs",)))


def test_secured_service_allows_register_with_admin_policy():
    types, policies = _registries()
    policies.upsert(
        PermissionRule(
            id="admin-all",
            role="governance",
            object_type="*",
            operation=Operation.ADMIN,
            effect=Effect.ALLOW,
        )
    )
    gw = PermissionGateway(policies, types)
    svc = OntologyService(
        registry=types,
        type_store=InMemoryTypeStore(),
        object_store=InMemoryObjectStore(),
        authorize=gw.authorize_hook,
    )
    new_type = ObjectType(
        name="Ticket",
        properties=(PropertyType(name="id", data_type=DataType.STRING, required=True),),
    )
    svc.register_type(new_type, principal=Principal(id="g", roles=("governance",)))
    assert svc.get_object_type("Ticket").name == "Ticket"
