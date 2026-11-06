"""Tests for the monthly indicator HTTP endpoint."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
import pytest

from sqlalchemy.exc import OperationalError

from datetime import date

client = TestClient(app)


def test_indicator_api_returns_monthly_values():
    # EN: Simulate the connection obtained through a context manager.
    # FR: Simuler la connexion obtenue par un gestionnaire de contexte.
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value

    # EN: Provide the aggregate row normally returned by PostgreSQL.
    # FR: Fournir la ligne d'agrégats normalement renvoyée par PostgreSQL.
    connection.execute.return_value.mappings.return_value.one.return_value = {
        "cohort_size": 100,
        "cancellation_count": 12,
        "average_viewing_hours": Decimal("23.2"),
    }

    # EN: Request the indicators without connecting to a real database.
    # FR: Demander les indicateurs sans connexion à une vraie base.
    with patch("app.main.get_engine", return_value=engine):
        response = client.get(
            "/api/indicators",
            params={"observation_month": "2026-09-01"},
        )

    # EN: Verify the HTTP status and the complete JSON response.
    # FR: Vérifier le statut HTTP et la réponse JSON complète.
    assert response.status_code == 200
    assert response.json() == {
        "observation_month": "2026-09-01",
        "cohort_size": 100,
        "cancellation_count": 12,
        "cancellation_rate": 12.0,
        "average_viewing_hours": 23.2,
    }

    connection.execute.assert_called_once()


@pytest.mark.parametrize(
    "cohort_size, average_hours, expected_rate, expected_average",
    [
        (0, None, None, None),
        (1, Decimal("0"), 0.0, 0.0),
    ],
)
def test_indicator_api_distinguishes_missing_values_from_zero(
    cohort_size,
    average_hours,
    expected_rate,
    expected_average,
):
    # EN: Simulate the aggregate results returned by PostgreSQL.
    # FR: Simuler les résultats agrégés renvoyés par PostgreSQL.
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value

    connection.execute.return_value.mappings.return_value.one.return_value = {
        "cohort_size": cohort_size,
        "cancellation_count": 0,
        "average_viewing_hours": average_hours,
    }

    with patch("app.main.get_engine", return_value=engine):
        response = client.get(
            "/api/indicators",
            params={"observation_month": "2026-09-01"},
        )

    # EN: Preserve the distinction between missing indicators and zero.
    # FR: Préserver la distinction entre indicateurs absents et zéro.
    assert response.status_code == 200
    assert response.json() == {
        "observation_month": "2026-09-01",
        "cohort_size": cohort_size,
        "cancellation_count": 0,
        "cancellation_rate": expected_rate,
        "average_viewing_hours": expected_average,
    }

    connection.execute.assert_called_once()


def test_indicator_api_reports_database_failure_without_exposing_credentials():
    # EN: Simulate a database error while executing the query.
    # FR: Simuler une erreur de base pendant l'exécution de la requête.
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value

    connection.execute.side_effect = OperationalError(
        "SELECT indicators",
        {},
        Exception("connection failed: password=FAKE_SECRET_FOR_TEST"),
    )

    with patch("app.main.get_engine", return_value=engine):
        response = client.get(
            "/api/indicators",
            params={"observation_month": "2026-09-01"},
        )

    # EN: Return an explicit error instead of fabricated indicators.
    # FR: Renvoyer une erreur explicite au lieu d'indicateurs inventés.
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load indicators",
    }

    # EN: Internal connection details must not appear in the response.
    # FR: Les détails internes de connexion ne doivent pas apparaître.
    assert "FAKE_SECRET_FOR_TEST" not in response.text

def test_indicator_api_handles_missing_database_configuration():
    # EN: Simulate missing configuration without changing the .env file.
    # FR: Simuler une configuration absente sans modifier le fichier .env.
    with patch(
        "app.main.get_engine",
        side_effect=ValueError("DATABASE_URL is missing"),
    ) as mocked_get_engine:
        response = client.get(
            "/api/indicators",
            params={"observation_month": "2026-09-01"},
        )

    # EN: Return the same understandable service-unavailable response.
    # FR: Renvoyer la même réponse compréhensible d'indisponibilité.
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load indicators",
    }

    assert "DATABASE_URL" not in response.text
    mocked_get_engine.assert_called_once()


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"observation_month": "not-a-date"},
        {"observation_month": "2026-02-30"},
        {"observation_month": "2026-09-15"},
    ],
    ids=[
        "missing-month",
        "invalid-date-text",
        "impossible-date",
        "not-first-day",
    ],
)
def test_indicator_api_rejects_invalid_month_before_database_access(params):
    # EN: Invalid requests must be rejected before database access.
    # FR: Les requêtes invalides doivent être refusées avant l'accès à la base.
    with patch("app.main.get_engine") as mocked_get_engine:
        response = client.get(
            "/api/indicators",
            params=params,
        )

    assert response.status_code == 422
    mocked_get_engine.assert_not_called()


@pytest.mark.parametrize(
    "stored_months, expected_months",
    [
        (
            [date(2026, 10, 1), date(2026, 9, 1)],
            ["2026-10-01", "2026-09-01"],
        ),
        ([], []),
    ],
    ids=["available-months", "no-observations"],
)
def test_observation_months_api_returns_stored_months(
    stored_months,
    expected_months,
):
    # EN: Simulate the dates returned by the database query.
    # FR: Simuler les dates renvoyées par la requête en base.
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    connection.execute.return_value.scalars.return_value.all.return_value = (
        stored_months
    )

    with patch("app.main.get_engine", return_value=engine):
        response = client.get("/api/observation-months")

    # EN: Verify the response and conversion of dates to JSON strings.
    # FR: Vérifier la réponse et la conversion des dates en chaînes JSON.
    assert response.status_code == 200
    assert response.json() == {
        "observation_months": expected_months,
    }

    connection.execute.assert_called_once()

def test_observation_months_api_handles_missing_configuration():
    # EN: Simulate missing configuration without changing the .env file.
    # FR: Simuler une configuration absente sans modifier le fichier .env.
    with patch(
        "app.main.get_engine",
        side_effect=ValueError("DATABASE_URL is missing"),
    ):
        response = client.get("/api/observation-months")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load observation months",
    }
    assert "DATABASE_URL" not in response.text


def test_observation_months_api_hides_database_error_details():
    # EN: Simulate a failure during the database query.
    # FR: Simuler un échec pendant la requête en base.
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value

    connection.execute.side_effect = OperationalError(
        "SELECT observation_month",
        {},
        Exception("connection failed: password=FAKE_SECRET_FOR_TEST"),
    )

    with patch("app.main.get_engine", return_value=engine):
        response = client.get("/api/observation-months")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Unable to load observation months",
    }
    assert "FAKE_SECRET_FOR_TEST" not in response.text

@pytest.mark.parametrize("plan", ["Basic", "Standard", "Premium"])
def test_indicator_api_passes_plan_to_calculation(plan):
    # EN: Simulate the connection and the calculation result.
    # FR: Simuler la connexion et le résultat du calcul.
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value

    expected_indicators = {
        "cohort_size": 2,
        "cancellation_count": 1,
        "cancellation_rate": 50.0,
        "average_viewing_hours": Decimal("20"),
    }

    with patch("app.main.get_engine", return_value=engine):
        with patch(
            "app.main.get_monthly_indicators",
            return_value=expected_indicators,
        ) as mocked_calculation:
            response = client.get(
                "/api/indicators",
                params={
                    "observation_month": "2026-09-01",
                    "plan": plan,
                },
            )

    # EN: Verify the HTTP response and the forwarded filters.
    # FR: Vérifier la réponse HTTP et les filtres transmis.
    assert response.status_code == 200
    assert response.json() == {
        "observation_month": "2026-09-01",
        "cohort_size": 2,
        "cancellation_count": 1,
        "cancellation_rate": 50.0,
        "average_viewing_hours": 20.0,
    }

    mocked_calculation.assert_called_once_with(
        connection,
        observation_month=date(2026, 9, 1),
        plan=plan,
    )


@pytest.mark.parametrize(
    "invalid_plan",
    ["Unknown", "basic", "", " Premium ", "All"],
)
def test_indicator_api_rejects_invalid_plan_before_database_access(
    invalid_plan,
):
    # EN: Invalid plans must be rejected before obtaining a database engine.
    # FR: Refuser les abonnements invalides avant d'obtenir le moteur de base.
    with patch(
        "app.main.get_engine",
        side_effect=AssertionError("Database access must not occur"),
    ) as mocked_get_engine:
        response = client.get(
            "/api/indicators",
            params={
                "observation_month": "2026-09-01",
                "plan": invalid_plan,
            },
        )

    # EN: Explain which subscription plans are accepted.
    # FR: Expliquer quels abonnements sont acceptés.
    assert response.status_code == 422
    assert response.json() == {
        "detail": "plan must be Basic, Standard or Premium",
    }
    mocked_get_engine.assert_not_called()