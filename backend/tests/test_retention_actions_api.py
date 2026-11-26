"""Check action API validation and transaction handling without PostgreSQL."""

from contextlib import contextmanager
from datetime import date, datetime, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

import app.main as api
from app.retention_actions import SuggestionUnavailableError


client = TestClient(api.app)


@pytest.fixture
def valid_payload():
    return {
        "observation_month": "2026-09-01",
        "plan": "Premium",
        "proposed_action": "Investigate Premium cancellation requests.",
        "rationale": "Review the observations for this cohort.",
        "rule_id": "PLAN_RATE_ABOVE_OVERALL",
        "rule_version": 1,
    }


@pytest.fixture
def stored_action(valid_payload):
    return {
        **valid_payload,
        "observation_month": date(2026, 9, 1),
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "created_at": datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc),
        "status": "Proposed",
    }


def test_creation_returns_201_after_transaction_exit(
    monkeypatch,
    valid_payload,
    stored_action,
):
    events = []
    connection = object()

    class Engine:
        @contextmanager
        def begin(self):
            events.append("begin")
            yield connection
            events.append("commit")

    def create(actual_connection, *, request):
        assert actual_connection is connection
        assert request.plan == "Premium"
        events.append("insert")
        return stored_action

    monkeypatch.setattr(api, "get_engine", lambda: Engine())
    monkeypatch.setattr(api, "create_retention_action", create)

    response = client.post("/api/retention-actions", json=valid_payload)

    assert response.status_code == 201
    assert response.json()["id"] == str(stored_action["id"])
    assert response.json()["status"] == "Proposed"
    assert response.json()["observation_month"] == "2026-09-01"
    assert events == ["begin", "insert", "commit"]


@pytest.mark.parametrize(
    "change",
    [
        {"plan": None},
        {"observation_month": "2026-09-15"},
        {"proposed_action": "   "},
        {"rule_version": True},
        {"status": "Completed"},
    ],
)
def test_invalid_request_never_accesses_database(
    monkeypatch,
    valid_payload,
    change,
):
    def unexpected_engine():
        pytest.fail("Invalid input must be rejected before database access")

    monkeypatch.setattr(api, "get_engine", unexpected_engine)

    response = client.post(
        "/api/retention-actions",
        json={**valid_payload, **change},
    )

    assert response.status_code == 422


def test_unavailable_suggestion_returns_409(monkeypatch, valid_payload):
    events = []

    class Engine:
        @contextmanager
        def begin(self):
            try:
                yield object()
            except Exception:
                events.append("rollback")
                raise
            else:
                events.append("commit")

    def unavailable(connection, *, request):
        raise SuggestionUnavailableError("No matching suggestion")

    monkeypatch.setattr(api, "get_engine", lambda: Engine())
    monkeypatch.setattr(api, "create_retention_action", unavailable)

    response = client.post("/api/retention-actions", json=valid_payload)

    assert response.status_code == 409
    assert events == ["rollback"]


def test_commit_failure_does_not_report_success_or_retry(
    monkeypatch,
    valid_payload,
    stored_action,
):
    calls = []

    class Engine:
        @contextmanager
        def begin(self):
            yield object()
            # EN: Simulate an error when completing the transaction.
            # FR: Simuler une erreur à la finalisation de la transaction.
            raise SQLAlchemyError("Internal transaction details")

    def create(connection, *, request):
        calls.append("insert")
        return stored_action

    monkeypatch.setattr(api, "get_engine", lambda: Engine())
    monkeypatch.setattr(api, "create_retention_action", create)

    response = client.post("/api/retention-actions", json=valid_payload)

    assert response.status_code == 503
    assert calls == ["insert"]
    assert "could not be confirmed" in response.json()["detail"]
    assert "Internal transaction details" not in response.text


def test_empty_action_list_returns_success(monkeypatch):
    connection = object()

    class Engine:
        @contextmanager
        def connect(self):
            yield connection

    def list_actions(actual_connection):
        assert actual_connection is connection
        return []

    monkeypatch.setattr(api, "get_engine", lambda: Engine())
    monkeypatch.setattr(api, "list_retention_actions", list_actions)

    response = client.get("/api/retention-actions")

    assert response.status_code == 200
    assert response.json() == {"actions": []}


def test_list_failure_is_not_reported_as_empty(monkeypatch):
    class Engine:
        @contextmanager
        def connect(self):
            raise SQLAlchemyError("Internal database details")
            yield  # Makes this function a context manager.

    monkeypatch.setattr(api, "get_engine", lambda: Engine())

    response = client.get("/api/retention-actions")

    assert response.status_code == 503
    assert response.json()["detail"] == "Unable to load saved actions"
    assert "Internal database details" not in response.text