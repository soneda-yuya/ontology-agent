"""Integration test for PostgresPolicyStore (requires PostgreSQL)."""

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


def test_policy_round_trips_through_db(provider):
    from mini_aip.adapters.outbound.postgres import PostgresPolicyStore
    from mini_aip.domain.permission import AttributePredicate, Effect, Operation, PermissionRule

    store = PostgresPolicyStore(provider)
    rule = PermissionRule(
        id="it-rule-1",
        role="sales",
        object_type="Account",
        operation=Operation.READ,
        effect=Effect.ALLOW,
        row_predicate=AttributePredicate(
            object_property="territory", principal_attribute="territory"
        ),
    )
    store.save(rule)
    loaded = {r.id: r for r in store.load_all()}
    assert loaded["it-rule-1"] == rule
