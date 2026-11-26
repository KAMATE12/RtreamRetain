"""Verify action API persistence using isolated PostgreSQL schemas."""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.schema import CreateSchema, DropSchema

import app.main as api
from app.database import get_engine
from app.schema import customer, customer_month, metadata, retention_action


pytestmark = pytest.mark.skipif(
    os.getenv("STREAMRETAIN_DB_TESTS") != "1",
    reason="Set STREAMRETAIN_DB_TESTS=1 for PostgreSQL integration tests.",
)


@pytest.fixture
def action_engine(monkeypatch):
    """Create committed test tables outside the working schema."""

    base_engine = get_engine()
    schema_name = f"test_actions_{uuid4().hex}"

    # EN: Create a unique schema containing only this test's data.
    # FR: Créer un schéma unique contenant uniquement les données du test.
    with base_engine.begin() as connection:
        connection.execute(CreateSchema(schema_name))

    engine = base_engine.execution_options(
        schema_translate_map={None: schema_name},
    )

    try:
        with engine.begin() as connection:
            metadata.create_all(bind=connection)

        monkeypatch.setattr(api, "get_engine", lambda: engine)
        yield engine

    finally:
        # EN: Remove only the uniquely named test schema.
        # FR: Supprimer uniquement le schéma de test au nom unique.
        with base_engine.begin() as connection:
            connection.execute(DropSchema(schema_name, cascade=True))


@pytest.fixture
def seeded_action_engine(action_engine):
    """Premium triggers in September; Basic does not."""

    with action_engine.begin() as connection:
        connection.execute(
            customer.insert(),
            [
                {"customer_id": "C000001"},
                {"customer_id": "C000002"},
            ],
        )

        common = {
            "observation_month": date(2026, 9, 1),
            "tenure_months": 2,
            "viewing_hours": Decimal("12.50"),
            "payment_failures": 0,
            "support_requests": 0,
        }

        connection.execute(
            customer_month.insert(),
            [
                {
                    **common,
                    "customer_id": "C000001",
                    "plan": "Premium",
                    "cancelled_in_month": True,
                },
                {
                    **common,
                    "customer_id": "C000002",
                    "plan": "Basic",
                    "cancelled_in_month": False,
                },
            ],
        )

    return action_engine


@pytest.fixture
def action_payload():
    return {
        "observation_month": "2026-09-01",
        "plan": "Premium",
        "proposed_action": "Review support history for this cohort.",
        "rationale": "Manager-reviewed investigation proposal.",
        "rule_id": "PLAN_RATE_ABOVE_OVERALL",
        "rule_version": 1,
    }


def customer_snapshot(engine):
    """Read all customer fields for comparison before and after saves."""

    with engine.connect() as connection:
        customers = [
            dict(row)
            for row in connection.execute(
                select(customer).order_by(customer.c.customer_id)
            ).mappings()
        ]
        observations = [
            dict(row)
            for row in connection.execute(
                select(customer_month).order_by(
                    customer_month.c.customer_id,
                    customer_month.c.observation_month,
                )
            ).mappings()
        ]

    return customers, observations


def test_api_action_survives_new_connection_and_preserves_customers(
    seeded_action_engine,
    action_payload,
):
    engine = seeded_action_engine
    before = customer_snapshot(engine)

    with TestClient(api.app) as client:
        response = client.post(
            "/api/retention-actions",
            json=action_payload,
        )

    assert response.status_code == 201
    saved = response.json()
    action_id = UUID(saved["id"])

    assert saved["status"] == "Proposed"
    for field, value in action_payload.items():
        assert saved[field] == value

    created_at = datetime.fromisoformat(
        saved["created_at"].replace("Z", "+00:00")
    )
    assert created_at.utcoffset() == timedelta(0)

    # EN: Close pooled connections so the next read reconnects to PostgreSQL.
    # FR: Fermer les connexions du pool avant une nouvelle connexion réelle.
    engine.dispose()

    with engine.connect() as connection:
        stored = dict(
            connection.execute(
                select(retention_action).where(
                    retention_action.c.id == action_id
                )
            ).mappings().one()
        )

    assert stored["proposed_action"] == action_payload["proposed_action"]
    assert stored["rationale"] == action_payload["rationale"]
    assert stored["observation_month"] == date(2026, 9, 1)
    assert stored["plan"] == "Premium"
    assert stored["rule_id"] == action_payload["rule_id"]
    assert stored["rule_version"] == 1
    assert stored["status"] == "Proposed"
    assert stored["created_at"] == created_at

    # EN: A new API client must retrieve the same saved action.
    # FR: Un nouveau client API doit retrouver la même action.
    with TestClient(api.app) as client:
        response = client.get("/api/retention-actions")

    assert response.status_code == 200
    assert response.json() == {"actions": [saved]}
    assert customer_snapshot(engine) == before


@pytest.mark.parametrize(
    "changes",
    [
        {"plan": "Basic"},
        {"observation_month": "2026-10-01"},
    ],
)
def test_api_rejects_scope_without_matching_suggestion(
    seeded_action_engine,
    action_payload,
    changes,
):
    engine = seeded_action_engine
    before = customer_snapshot(engine)

    with TestClient(api.app) as client:
        response = client.post(
            "/api/retention-actions",
            json={**action_payload, **changes},
        )
        listed = client.get("/api/retention-actions")

    assert response.status_code == 409
    assert listed.status_code == 200
    assert listed.json() == {"actions": []}
    assert customer_snapshot(engine) == before


def test_api_preserves_multiple_proposals_for_same_segment(
    seeded_action_engine,
    action_payload,
):
    with TestClient(api.app) as client:
        first = client.post(
            "/api/retention-actions",
            json=action_payload,
        )
        second = client.post(
            "/api/retention-actions",
            json={
                **action_payload,
                "proposed_action": "Review payment difficulties.",
            },
        )
        listed = client.get("/api/retention-actions")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]

    assert listed.status_code == 200
    actions = listed.json()["actions"]
    assert len(actions) == 2
    assert {action["id"] for action in actions} == {
        first.json()["id"],
        second.json()["id"],
    }
    assert all(action["status"] == "Proposed" for action in actions)
