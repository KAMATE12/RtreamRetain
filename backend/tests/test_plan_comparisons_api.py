"""
EN: Verify the comparison API contract, validation and error handling.
Replace database access with mocks to check HTTP behavior independently
of PostgreSQL. Real grouped calculations are tested separately.

FR: Vérifier le contrat API, la validation et la gestion des erreurs.
Simuler l'accès à la base pour contrôler le comportement HTTP sans
PostgreSQL. Les calculs réels sont vérifiés dans les tests d'intégration.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app


@pytest.fixture
def client():
    """Provide a client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize("plan", [None, "Basic", "Standard", "Premium"])
def test_comparison_api_forwards_filters_and_returns_groups(client, plan):
    # EN: This test checks forwarding, not the database's grouping logic.
    # FR: Ce test contrôle la transmission, pas le regroupement en base.
    represented_plan = plan if plan is not None else "Basic"
    groups = [
        {
            "plan": represented_plan,
            "cohort_size": 80,
            "cancellation_count": 8,
            "cancellation_rate": 10.0,
        }
    ]

    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    params = {"observation_month": "2026-09-01"}

    if plan is not None:
        params["plan"] = plan

    with (
        patch("app.main.get_engine", return_value=engine),
        patch(
            "app.main.get_plan_comparisons",
            return_value=groups,
        ) as calculation,
    ):
        response = client.get("/api/plan-comparisons", params=params)

    assert response.status_code == 200
    assert response.json() == {
        "observation_month": "2026-09-01",
        "plan": plan,
        "comparisons": groups,
    }

    calculation.assert_called_once_with(
        connection,
        observation_month=date(2026, 9, 1),
        plan=plan,
    )
    engine.connect.return_value.__exit__.assert_called_once()


def test_comparison_api_returns_an_empty_list_without_invented_groups(client):
    engine = MagicMock()

    with (
        patch("app.main.get_engine", return_value=engine),
        patch("app.main.get_plan_comparisons", return_value=[]),
    ):
        response = client.get(
            "/api/plan-comparisons",
            params={
                "observation_month": "2026-09-01",
                "plan": "Standard",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "observation_month": "2026-09-01",
        "plan": "Standard",
        "comparisons": [],
    }


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"observation_month": "invalid"},
        {"observation_month": "2026-02-30"},
        {"observation_month": "2026-09-15"},
    ],
    ids=["missing", "invalid-text", "impossible-date", "not-first-day"],
)
def test_comparison_api_rejects_invalid_month_before_database_access(
    client,
    params,
):
    with patch("app.main.get_engine") as get_engine_mock:
        response = client.get("/api/plan-comparisons", params=params)

    assert response.status_code == 422
    assert response.json()["detail"]
    get_engine_mock.assert_not_called()


@pytest.mark.parametrize("plan", ["Unknown", "basic", "", " Premium ", "All"])
def test_comparison_api_rejects_invalid_plan_before_database_access(
    client,
    plan,
):
    with patch("app.main.get_engine") as get_engine_mock:
        response = client.get(
            "/api/plan-comparisons",
            params={
                "observation_month": "2026-09-01",
                "plan": plan,
            },
        )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "plan must be Basic, Standard or Premium",
    }
    get_engine_mock.assert_not_called()


def test_comparison_api_hides_configuration_errors(client):
    with patch(
        "app.main.get_engine",
        side_effect=ValueError("PRIVATE_CONFIGURATION_DETAIL"),
    ):
        response = client.get(
            "/api/plan-comparisons",
            params={"observation_month": "2026-09-01"},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load plan comparisons",
    }
    assert "PRIVATE_CONFIGURATION_DETAIL" not in response.text


@pytest.mark.parametrize("failure_stage", ["connection", "query"])
def test_comparison_api_hides_database_errors(client, failure_stage):
    engine = MagicMock()
    private_detail = "postgresql://user:secret@host/db SELECT private_data"

    with (
        patch("app.main.get_engine", return_value=engine),
        patch("app.main.get_plan_comparisons") as calculation,
    ):
        # EN: Exercise connection failure and query failure separately.
        # FR: Tester séparément l'échec de connexion et celui de la requête.
        if failure_stage == "connection":
            engine.connect.side_effect = SQLAlchemyError(private_detail)
        else:
            calculation.side_effect = SQLAlchemyError(private_detail)

        response = client.get(
            "/api/plan-comparisons",
            params={"observation_month": "2026-09-01"},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load plan comparisons",
    }
    assert "secret" not in response.text
    assert "SELECT" not in response.text