"""Verify suggestion API filters and reference scope without PostgreSQL."""

from contextlib import contextmanager
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app import main


client = TestClient(main.app)


@pytest.mark.parametrize(
    ("selected_plan", "expected_plans"),
    [
        (None, ["Premium"]),
        ("Premium", ["Premium"]),
        ("Basic", []),
        ("Standard", []),
    ],
)
def test_api_preserves_global_reference(
    monkeypatch, selected_plan, expected_plans
):
    connection_marker = object()
    calls = []

    class FakeEngine:
        @contextmanager
        def connect(self):
            yield connection_marker

    def fake_comparisons(connection, *, observation_month, plan):
        assert connection is connection_marker
        calls.append((observation_month, plan))
        return [
            {
                "plan": "Basic",
                "cohort_size": 80,
                "cancellation_count": 8,
            },
            {
                "plan": "Premium",
                "cohort_size": 20,
                "cancellation_count": 4,
            },
        ]

    monkeypatch.setattr(main, "get_engine", lambda: FakeEngine())
    monkeypatch.setattr(main, "get_plan_comparisons", fake_comparisons)

    params = {"observation_month": "2026-09-01"}

    if selected_plan is not None:
        params["plan"] = selected_plan

    response = client.get("/api/retention-suggestions", params=params)

    assert response.status_code == 200
    body = response.json()

    # EN: Exactly one grouped read, always including all plans.
    # FR: Une seule lecture regroupée, incluant tous les abonnements.
    assert calls == [(date(2026, 9, 1), None)]
    assert body["observation_month"] == "2026-09-01"
    assert body["plan"] == selected_plan
    assert body["reference"]["scope"] == "all_plans"
    assert body["reference"]["cohort_size"] == 100
    assert body["reference"]["cancellation_count"] == 12
    assert body["reference"]["cancellation_rate"] == 12.0
    assert [
        item["plan"] for item in body["suggestions"]
    ] == expected_plans


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"observation_month": "invalid"},
        {"observation_month": "2026-02-30"},
        {"observation_month": "2026-09-02"},
        {"observation_month": "2026-09-01", "plan": "Unknown"},
        {"observation_month": "2026-09-01", "plan": "premium"},
        {"observation_month": "2026-09-01", "plan": ""},
        {"observation_month": "2026-09-01", "plan": "All"},
    ],
)
def test_invalid_filters_are_rejected_before_database_access(
    monkeypatch, params
):
    def forbidden_engine():
        pytest.fail("Invalid filters must not access the database")

    monkeypatch.setattr(main, "get_engine", forbidden_engine)

    response = client.get("/api/retention-suggestions", params=params)

    assert response.status_code == 422

def test_empty_month_returns_no_suggestions_and_no_measured_rate(monkeypatch):
    class FakeEngine:
        @contextmanager
        def connect(self):
            yield object()

    monkeypatch.setattr(main, "get_engine", lambda: FakeEngine())
    monkeypatch.setattr(
        main,
        "get_plan_comparisons",
        lambda connection, *, observation_month, plan: [],
    )

    response = client.get(
        "/api/retention-suggestions",
        params={"observation_month": "2026-09-01"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["suggestions"] == []
    assert body["reference"] == {
        "scope": "all_plans",
        "cohort_size": 0,
        "cancellation_count": 0,
        "cancellation_rate": None,
    }


def test_configuration_failure_returns_a_generic_error(monkeypatch):
    def failing_engine():
        raise ValueError("private configuration details")

    monkeypatch.setattr(main, "get_engine", failing_engine)

    response = client.get(
        "/api/retention-suggestions",
        params={"observation_month": "2026-09-01"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load retention suggestions"
    }
    assert "private configuration details" not in response.text


@pytest.mark.parametrize("failure_stage", ["connection", "query"])
def test_database_failure_returns_a_generic_error(
    monkeypatch, failure_stage
):
    from sqlalchemy.exc import SQLAlchemyError

    class FailingEngine:
        @contextmanager
        def connect(self):
            if failure_stage == "connection":
                raise SQLAlchemyError("private connection details")
            yield object()

    def failing_query(connection, *, observation_month, plan):
        raise SQLAlchemyError("private SQL details")

    monkeypatch.setattr(main, "get_engine", lambda: FailingEngine())
    monkeypatch.setattr(main, "get_plan_comparisons", failing_query)

    response = client.get(
        "/api/retention-suggestions",
        params={"observation_month": "2026-09-01"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load retention suggestions"
    }
    assert "private" not in response.text