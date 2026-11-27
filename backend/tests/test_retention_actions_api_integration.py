"""Verify action API persistence using isolated PostgreSQL schemas."""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

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

def test_api_status_update_persists_and_preserves_other_fields(
    seeded_action_engine,
    action_payload,
):
    engine = seeded_action_engine
    before_customers = customer_snapshot(engine)

    with TestClient(api.app) as client:
        created = client.post(
            "/api/retention-actions",
            json=action_payload,
        )
        assert created.status_code == 201
        original = created.json()

        status_url = (
            f"/api/retention-actions/{original['id']}/status"
        )

        # EN: Proposed -> Completed must be rejected.
        # FR: Le passage direct Proposed -> Completed doit être refusé.
        rejected = client.patch(
            status_url,
            json={"status": "Completed"},
        )
        assert rejected.status_code == 409

        listed = client.get("/api/retention-actions")
        assert listed.status_code == 200
        assert listed.json() == {"actions": [original]}

        # EN: A permitted change must preserve every other response field.
        # FR: Une transition autorisée doit conserver tous les autres champs.
        changed = client.patch(
            status_url,
            json={"status": "In Progress"},
        )
        assert changed.status_code == 200

        expected = {**original, "status": "In Progress"}
        assert changed.json() == expected

        # EN: Repeating the current status is a successful no-op.
        # FR: Redemander le statut actuel réussit sans changement.
        repeated = client.patch(
            status_url,
            json={"status": "In Progress"},
        )
        assert repeated.status_code == 200
        assert repeated.json() == expected

    # EN: Reconnect to check committed state independently of the response.
    # FR: Se reconnecter pour vérifier l'état validé indépendamment de la réponse.
    engine.dispose()

    with engine.connect() as connection:
        stored = dict(
            connection.execute(
                select(retention_action).where(
                    retention_action.c.id == UUID(original["id"])
                )
            ).mappings().one()
        )

    assert stored["status"] == "In Progress"
    assert stored["created_at"] == datetime.fromisoformat(
        original["created_at"].replace("Z", "+00:00")
    )

    with TestClient(api.app) as client:
        listed = client.get("/api/retention-actions")

    assert listed.status_code == 200
    assert listed.json() == {"actions": [expected]}
    assert customer_snapshot(engine) == before_customers

# EN: Check all status pairs through the API and real PostgreSQL storage.
# FR: Vérifier toutes les paires via l'API et le stockage PostgreSQL réel.
@pytest.mark.parametrize(
    "current_status",
    ["Proposed", "In Progress", "Completed", "Dismissed"],
)
@pytest.mark.parametrize(
    "target_status",
    ["Proposed", "In Progress", "Completed", "Dismissed"],
)
def test_api_checks_every_stored_status_transition(
    seeded_action_engine,
    action_payload,
    current_status,
    target_status,
):
    engine = seeded_action_engine
    before_customers = customer_snapshot(engine)

    permitted_changes = {
        ("Proposed", "In Progress"),
        ("Proposed", "Dismissed"),
        ("In Progress", "Completed"),
        ("In Progress", "Dismissed"),
    }

    with TestClient(api.app) as client:
        created = client.post(
            "/api/retention-actions",
            json=action_payload,
        )
        assert created.status_code == 201
        original = created.json()
        action_id = UUID(original["id"])

        # EN: Arrange the initial state only inside this isolated test schema.
        # FR: Préparer l'état initial uniquement dans le schéma isolé du test.
        with engine.begin() as connection:
            connection.execute(
                retention_action.update()
                .where(retention_action.c.id == action_id)
                .values(status=current_status)
            )

        response = client.patch(
            f"/api/retention-actions/{action_id}/status",
            json={"status": target_status},
        )

        allowed = (
            current_status == target_status
            or (current_status, target_status) in permitted_changes
        )

        expected_status = target_status if allowed else current_status
        expected_action = {
            **original,
            "status": expected_status,
        }

        if allowed:
            assert response.status_code == 200
            assert response.json() == expected_action
        else:
            assert response.status_code == 409

        # EN: Read persisted values independently of the PATCH response.
        # FR: Relire les valeurs enregistrées indépendamment de la réponse PATCH.
        listed = client.get("/api/retention-actions")
        assert listed.status_code == 200
        assert listed.json() == {"actions": [expected_action]}

    assert customer_snapshot(engine) == before_customers


def test_status_api_returns_404_for_missing_action(action_engine):
    with TestClient(api.app) as client:
        response = client.patch(
            f"/api/retention-actions/{uuid4()}/status",
            json={"status": "In Progress"},
        )
        listed = client.get("/api/retention-actions")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "The requested action does not exist."
    }
    assert listed.status_code == 200
    assert listed.json() == {"actions": []}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"status": None},
        {"status": "Unknown"},
        {"status": "completed"},
        {"status": " In Progress "},
        {"status": 1},
        {"status": True},
        {
            "status": "In Progress",
            "proposed_action": "Unauthorized text change",
        },
        {
            "status": "In Progress",
            "created_at": "2026-11-27T00:00:00Z",
        },
    ],
)
def test_status_api_rejects_invalid_body_without_database_access(
    monkeypatch,
    payload,
):
    def unexpected_database_access():
        pytest.fail("Invalid requests must not access PostgreSQL.")

    monkeypatch.setattr(api, "get_engine", unexpected_database_access)

    with TestClient(api.app) as client:
        response = client.patch(
            f"/api/retention-actions/{uuid4()}/status",
            json=payload,
        )

    assert response.status_code == 422


def test_status_api_rejects_invalid_identifier_before_database_access(
    monkeypatch,
):
    def unexpected_database_access():
        pytest.fail("An invalid identifier must not access PostgreSQL.")

    monkeypatch.setattr(api, "get_engine", unexpected_database_access)

    with TestClient(api.app) as client:
        response = client.patch(
            "/api/retention-actions/not-a-uuid/status",
            json={"status": "In Progress"},
        )

    assert response.status_code == 422

def test_competing_status_updates_cannot_reopen_a_terminal_action(
    seeded_action_engine,
    action_payload,
    monkeypatch,
):
    engine = seeded_action_engine
    before_customers = customer_snapshot(engine)

    with TestClient(api.app) as client:
        created = client.post(
            "/api/retention-actions",
            json=action_payload,
        )
        assert created.status_code == 201
        original = created.json()
        status_url = (
            f"/api/retention-actions/{original['id']}/status"
        )

        started = client.patch(
            status_url,
            json={"status": "In Progress"},
        )
        assert started.status_code == 200

    original_update = api.update_retention_action_status
    barrier = Barrier(2)

    def synchronized_update(connection, *, action_id, target_status):
        # EN: Bound database waits so a broken test cannot wait indefinitely.
        # FR: Limiter l'attente en base pour éviter un blocage indéfini.
        connection.execute(text("SET LOCAL lock_timeout = '5s'"))
        connection.execute(text("SET LOCAL statement_timeout = '10s'"))

        # EN: Both requests reach this point before either updates the row.
        # FR: Les deux demandes arrivent ici avant toute modification.
        barrier.wait(timeout=10)

        return original_update(
            connection,
            action_id=action_id,
            target_status=target_status,
        )

    monkeypatch.setattr(
        api,
        "update_retention_action_status",
        synchronized_update,
    )

    def send_update(target_status):
        # EN: Give each concurrent request its own API client.
        # FR: Utiliser un client API distinct pour chaque demande concurrente.
        with TestClient(api.app) as client:
            response = client.patch(
                status_url,
                json={"status": target_status},
            )
        return response.status_code, response.json()

    with ThreadPoolExecutor(max_workers=2) as executor:
        completed_future = executor.submit(send_update, "Completed")
        dismissed_future = executor.submit(send_update, "Dismissed")

        results = [
            completed_future.result(timeout=30),
            dismissed_future.result(timeout=30),
        ]

    # EN: Either request may win, but both must not succeed.
    # FR: Chaque demande peut gagner, mais les deux ne doivent pas réussir.
    assert sorted(code for code, _ in results) == [200, 409]

    successful_action = next(
        body for code, body in results if code == 200
    )
    assert successful_action["status"] in {"Completed", "Dismissed"}
    assert successful_action == {
        **original,
        "status": successful_action["status"],
    }

    with TestClient(api.app) as client:
        listed = client.get("/api/retention-actions")

    assert listed.status_code == 200
    assert listed.json() == {"actions": [successful_action]}
    assert customer_snapshot(engine) == before_customers


def test_status_update_is_rolled_back_after_database_error(
    seeded_action_engine,
    action_payload,
    monkeypatch,
):
    engine = seeded_action_engine
    before_customers = customer_snapshot(engine)

    with TestClient(api.app) as client:
        created = client.post(
            "/api/retention-actions",
            json=action_payload,
        )
        assert created.status_code == 201
        original = created.json()

    original_update = api.update_retention_action_status
    attempts = []

    def update_then_fail(connection, *, action_id, target_status):
        attempts.append(action_id)

        changed = original_update(
            connection,
            action_id=action_id,
            target_status=target_status,
        )
        assert changed["status"] == "In Progress"

        # EN: Simulate failure after SQL UPDATE but before transaction commit.
        # FR: Simuler un échec après l'UPDATE SQL, avant le commit.
        raise SQLAlchemyError("PRIVATE_DATABASE_DETAIL")

    monkeypatch.setattr(
        api,
        "update_retention_action_status",
        update_then_fail,
    )

    with TestClient(api.app) as client:
        response = client.patch(
            f"/api/retention-actions/{original['id']}/status",
            json={"status": "In Progress"},
        )

        assert response.status_code == 503
        assert "PRIVATE_DATABASE_DETAIL" not in response.text
        assert response.json() == {
            "detail": (
                "The status update could not be confirmed. "
                "Refresh the saved-action list before trying again."
            )
        }

        # EN: No automatic retry and no partial committed change.
        # FR: Aucun nouvel essai automatique ni modification partielle validée.
        assert len(attempts) == 1

        listed = client.get("/api/retention-actions")

    assert listed.status_code == 200
    assert listed.json() == {"actions": [original]}
    assert customer_snapshot(engine) == before_customers
