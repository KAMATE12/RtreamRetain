"""Test the indicator API using real PostgreSQL in an isolated schema."""

import os
from datetime import date
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.schema import CreateSchema, DropSchema

from app.database import get_engine
from app.main import app
from app.schema import customer, customer_month, metadata
from sqlalchemy import select


pytestmark = pytest.mark.skipif(
    os.getenv("STREAMRETAIN_DB_TESTS") != "1",
    reason="Set STREAMRETAIN_DB_TESTS=1 to run PostgreSQL integration tests.",
)


@pytest.fixture
def isolated_engine():
    """Provide committed test tables accessible from separate connections."""

    schema_name = f"test_indicators_{uuid4().hex}"

    # EN: Direct table operations to this test's unique schema.
    # FR: Diriger les opérations vers le schéma unique de ce test.
    test_engine = get_engine().execution_options(
        schema_translate_map={None: schema_name},
    )

    with test_engine.begin() as connection:
        connection.execute(CreateSchema(schema_name))
        metadata.create_all(bind=connection)

    try:
        yield test_engine
    finally:
        # EN: Remove only this test's tables and schema.
        # FR: Supprimer uniquement les tables et le schéma de ce test.
        with test_engine.begin() as connection:
            metadata.drop_all(bind=connection)
            connection.execute(DropSchema(schema_name))


def test_indicator_api_reads_the_selected_month_from_postgresql(
    isolated_engine,
):
    september = date(2026, 9, 1)

    customers = [
        {"customer_id": f"C{number:06d}"}
        for number in range(1, 101)
    ]

    observations = []

    for number in range(1, 101):
        cancelled = number <= 12

        observations.append(
            {
                "customer_id": f"C{number:06d}",
                "observation_month": september,
                "plan": "Basic",
                "tenure_months": 0,
                "viewing_hours": (
                    Decimal("10") if cancelled else Decimal("25")
                ),
                "payment_failures": 0,
                "support_requests": 0,
                "cancelled_in_month": cancelled,
            }
        )

    # EN: Add another month to detect a missing month filter.
    # FR: Ajouter un autre mois pour détecter un filtre mensuel manquant.
    observations.append(
        {
            **observations[0],
            "observation_month": date(2026, 10, 1),
            "viewing_hours": Decimal("999"),
        }
    )

    # EN: Commit the data so the API's connection can read it.
    # FR: Valider les données pour que la connexion de l'API puisse les lire.
    with isolated_engine.begin() as connection:
        connection.execute(customer.insert(), customers)
        connection.execute(customer_month.insert(), observations)

    # EN: Replace only the engine selection; SQL operations remain real.
    # FR: Remplacer uniquement le choix du moteur ; le SQL reste réel.
    with patch("app.main.get_engine", return_value=isolated_engine):
        with TestClient(app) as client:
            response = client.get(
                "/api/indicators",
                params={"observation_month": "2026-09-01"},
            )

    assert response.status_code == 200
    assert response.json() == {
        "observation_month": "2026-09-01",
        "cohort_size": 100,
        "cancellation_count": 12,
        "cancellation_rate": 12.0,
        "average_viewing_hours": 23.2,
    }


def test_observation_months_api_reads_real_database(isolated_engine):
    # EN: Check the response before inserting any observations.
    # FR: Vérifier la réponse avant toute insertion d'observations.
    with patch("app.main.get_engine", return_value=isolated_engine):
        with TestClient(app) as client:
            response = client.get("/api/observation-months")

    assert response.status_code == 200
    assert response.json() == {"observation_months": []}

    base_observation = {
        "customer_id": "C000001",
        "observation_month": date(2026, 9, 1),
        "plan": "Basic",
        "tenure_months": 0,
        "viewing_hours": Decimal("10"),
        "payment_failures": 0,
        "support_requests": 0,
        "cancelled_in_month": False,
    }

    # EN: Store two months, with two customers in September.
    # FR: Stocker deux mois, avec deux clients en septembre.
    with isolated_engine.begin() as connection:
        connection.execute(
            customer.insert(),
            [
                {"customer_id": "C000001"},
                {"customer_id": "C000002"},
            ],
        )
        connection.execute(
            customer_month.insert(),
            [
                base_observation,
                {
                    **base_observation,
                    "observation_month": date(2026, 10, 1),
                },
                {
                    **base_observation,
                    "customer_id": "C000002",
                },
            ],
        )

    # EN: Read the committed observations through the API.
    # FR: Lire les observations enregistrées à travers l'API.
    with patch("app.main.get_engine", return_value=isolated_engine):
        with TestClient(app) as client:
            response = client.get("/api/observation-months")

    assert response.status_code == 200
    assert response.json() == {
        "observation_months": [
            "2026-10-01",
            "2026-09-01",
        ],
    }


def test_indicator_api_filters_plans_and_preserves_stored_data(
    isolated_engine,
):
    base_observation = {
        "customer_id": "C000001",
        "observation_month": date(2026, 9, 1),
        "plan": "Basic",
        "tenure_months": 0,
        "viewing_hours": Decimal("10"),
        "payment_failures": 0,
        "support_requests": 0,
        "cancelled_in_month": True,
    }

    observations = [
        base_observation,
        {
            **base_observation,
            "customer_id": "C000002",
            "viewing_hours": Decimal("30"),
            "cancelled_in_month": False,
        },
        {
            **base_observation,
            "customer_id": "C000003",
            "plan": "Premium",
            "viewing_hours": Decimal("100"),
        },
        {
            **base_observation,
            "observation_month": date(2026, 10, 1),
            "viewing_hours": Decimal("999"),
        },
    ]

    # EN: Commit the isolated data before calling the API.
    # FR: Enregistrer les données isolées avant d'appeler l'API.
    with isolated_engine.begin() as connection:
        connection.execute(
            customer.insert(),
            [
                {"customer_id": "C000001"},
                {"customer_id": "C000002"},
                {"customer_id": "C000003"},
            ],
        )
        connection.execute(customer_month.insert(), observations)

    # EN: Use stable ordering to compare every stored field.
    # FR: Utiliser un ordre stable pour comparer tous les champs stockés.
    customers_query = select(customer).order_by(customer.c.customer_id)
    observations_query = select(customer_month).order_by(
        customer_month.c.customer_id,
        customer_month.c.observation_month,
    )

    with isolated_engine.connect() as connection:
        customers_before = connection.execute(customers_query).all()
        observations_before = connection.execute(observations_query).all()

    # EN: Define independently calculated results for each selection.
    # FR: Définir les résultats calculés indépendamment pour chaque sélection.
    cases = [
        ("Basic", 2, 1, 50.0, 20.0),
        ("Premium", 1, 1, 100.0, 100.0),
        ("Standard", 0, 0, None, None),
        (None, 3, 2, 200 / 3, 140 / 3),
    ]

    with patch("app.main.get_engine", return_value=isolated_engine):
        with TestClient(app) as client:
            for plan, count, cancellations, rate, average in cases:
                params = {"observation_month": "2026-09-01"}

                if plan is not None:
                    params["plan"] = plan

                response = client.get("/api/indicators", params=params)

                assert response.status_code == 200
                actual = response.json()

                assert actual["observation_month"] == "2026-09-01"
                assert actual["cohort_size"] == count
                assert actual["cancellation_count"] == cancellations

                if rate is None:
                    assert actual["cancellation_rate"] is None
                    assert actual["average_viewing_hours"] is None
                else:
                    assert actual["cancellation_rate"] == pytest.approx(rate)
                    assert actual["average_viewing_hours"] == pytest.approx(
                        average
                    )

            # EN: Include the month-list endpoint in the preservation check.
            # FR: Inclure la route des mois dans la vérification de conservation.
            response = client.get("/api/observation-months")

            assert response.status_code == 200
            assert response.json() == {
                "observation_months": ["2026-10-01", "2026-09-01"],
            }

    # EN: Read again through a new connection after all API calls.
    # FR: Relire avec une nouvelle connexion après tous les appels API.
    with isolated_engine.connect() as connection:
        customers_after = connection.execute(customers_query).all()
        observations_after = connection.execute(observations_query).all()

    assert customers_after == customers_before
    assert observations_after == observations_before