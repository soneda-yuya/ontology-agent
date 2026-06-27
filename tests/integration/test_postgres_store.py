"""Integration tests for the Postgres adapters.

Marked ``integration`` — executed in the Build & Test phase against a live
PostgreSQL (e.g. the docker-compose dev DB). Skipped automatically when
MINIAIP_DATABASE_URL is not set.
"""

import os

import pytest

pytestmark = pytest.mark.integration

DSN = os.environ.get("MINIAIP_DATABASE_URL")


@pytest.fixture()
def provider():
    if not DSN:
        pytest.skip("MINIAIP_DATABASE_URL not set")
    from mini_aip.adapters.outbound.postgres import ConnectionProvider

    return ConnectionProvider(DSN)


def test_type_registry_round_trips_through_db(provider):
    from mini_aip.adapters.outbound.postgres import PostgresTypeRegistry
    from mini_aip.domain.ontology import DataType, ObjectType, PropertyType

    store = PostgresTypeRegistry(provider)
    ot = ObjectType(
        name="ITCustomer",
        properties=(PropertyType(name="id", data_type=DataType.STRING, required=True),),
    )
    store.save(ot)
    loaded = {t.name: t for t in store.load_all()}
    assert loaded["ITCustomer"] == ot


def test_object_store_write_get(provider):
    from mini_aip.adapters.outbound.postgres import PostgresObjectStore
    from mini_aip.domain.ontology import OntologyObject

    store = PostgresObjectStore(provider)
    obj = OntologyObject(object_type="ITCustomer", id="x1", properties={"id": "x1"})
    store.write(obj)
    assert store.exists("ITCustomer", "x1")
    assert store.get("ITCustomer", "x1") == obj
