"""
EN: Verify indicators and plan comparisons using isolated PostgreSQL schemas.
Create synthetic fixtures in test-only tables and remove only those tables.
Check known calculations, filtering and preservation of stored observations.

FR: Vérifier les indicateurs et comparaisons dans des schémas PostgreSQL isolés.
Créer les données synthétiques dans les tables de test uniquement.
Contrôler les calculs, les filtres et la conservation des observations.
"""

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

def test_plan_comparisons_match_summary_and_preserve_data(isolated_engine):
    """Verify unequal groups, month filtering, ordering and empty scopes."""

    from app.indicators import (
        get_monthly_indicators,
        get_plan_comparisons,
    )

    september = date(2026, 9, 1)
    october = date(2026, 10, 1)

    customers = [
        {"customer_id": f"C{number:06d}"}
        for number in range(1, 101)
    ]

    observations = []

    # EN: September contains 80 Basic customers and 20 Premium customers.
    # FR: Septembre contient 80 clients Basic et 20 clients Premium.
    for number in range(1, 101):
        observations.append(
            {
                "customer_id": f"C{number:06d}",
                "observation_month": september,
                "plan": "Basic" if number <= 80 else "Premium",
                "tenure_months": 0,
                "viewing_hours": Decimal("10"),
                "payment_failures": 0,
                "support_requests": 0,
                "cancelled_in_month": (
                    number <= 8 or 81 <= number <= 84
                ),
            }
        )

    # EN: Insert October plans in a different order from the required display.
    # FR: Insérer octobre dans un ordre différent de l'affichage attendu.
    for number, plan in enumerate(
        ["Premium", "Standard", "Basic"],
        start=1,
    ):
        observations.append(
            {
                **observations[0],
                "customer_id": f"C{number:06d}",
                "observation_month": october,
                "plan": plan,
                "cancelled_in_month": False,
            }
        )

    with isolated_engine.begin() as connection:
        connection.execute(customer.insert(), customers)
        connection.execute(customer_month.insert(), observations)

    customers_query = select(customer).order_by(customer.c.customer_id)
    observations_query = select(customer_month).order_by(
        customer_month.c.customer_id,
        customer_month.c.observation_month,
    )

    with isolated_engine.connect() as connection:
        customers_before = connection.execute(customers_query).all()
        observations_before = connection.execute(observations_query).all()

        groups = get_plan_comparisons(
            connection,
            observation_month=september,
        )
        summary = get_monthly_indicators(
            connection,
            observation_month=september,
        )

        assert groups == [
            {
                "plan": "Basic",
                "cohort_size": 80,
                "cancellation_count": 8,
                "cancellation_rate": 10.0,
            },
            {
                "plan": "Premium",
                "cohort_size": 20,
                "cancellation_count": 4,
                "cancellation_rate": 20.0,
            },
        ]

        # EN: The overall rate uses combined counts, not average group rates.
        # FR: Le taux global utilise les effectifs, pas la moyenne des taux.
        assert summary["cohort_size"] == 100
        assert summary["cancellation_count"] == 12
        assert summary["cancellation_rate"] == pytest.approx(12.0)
        assert summary["cancellation_rate"] != 15.0

        assert sum(row["cohort_size"] for row in groups) == (
            summary["cohort_size"]
        )
        assert sum(row["cancellation_count"] for row in groups) == (
            summary["cancellation_count"]
        )

        # EN: Each single-plan comparison must agree with its summary.
        # FR: Chaque comparaison filtrée doit correspondre à son résumé.
        for expected_group in groups:
            selected_plan = expected_group["plan"]

            filtered_groups = get_plan_comparisons(
                connection,
                observation_month=september,
                plan=selected_plan,
            )
            filtered_summary = get_monthly_indicators(
                connection,
                observation_month=september,
                plan=selected_plan,
            )

            assert filtered_groups == [expected_group]

            for field in (
                "cohort_size",
                "cancellation_count",
                "cancellation_rate",
            ):
                assert filtered_groups[0][field] == filtered_summary[field]

        # EN: October has different counts and all three plans in stable order.
        # FR: Octobre a d'autres effectifs et les trois abonnements ordonnés.
        october_groups = get_plan_comparisons(
            connection,
            observation_month=october,
        )

        assert october_groups == [
            {
                "plan": plan,
                "cohort_size": 1,
                "cancellation_count": 0,
                "cancellation_rate": 0.0,
            }
            for plan in ["Basic", "Standard", "Premium"]
        ]

        # EN: An absent plan and an absent month both produce an empty list.
        # FR: Un abonnement absent et un mois absent donnent une liste vide.
        assert get_plan_comparisons(
            connection,
            observation_month=september,
            plan="Standard",
        ) == []

        assert get_plan_comparisons(
            connection,
            observation_month=date(2026, 11, 1),
        ) == []

        empty_summary = get_monthly_indicators(
            connection,
            observation_month=september,
            plan="Standard",
        )

        assert empty_summary["cohort_size"] == 0
        assert empty_summary["cancellation_count"] == 0
        assert empty_summary["cancellation_rate"] is None

    # EN: Check every stored field again through a fresh connection.
    # FR: Revérifier tous les champs stockés avec une nouvelle connexion.
    with isolated_engine.connect() as connection:
        assert connection.execute(customers_query).all() == customers_before
        assert connection.execute(observations_query).all() == (
            observations_before
        )


def test_plan_comparison_api_matches_summary_and_preserves_data(
    isolated_engine,
):
    """Verify real HTTP comparisons and summaries in an isolated schema."""

    september = date(2026, 9, 1)
    october = date(2026, 10, 1)

    customers = [
        {"customer_id": f"C{number:06d}"}
        for number in range(1, 101)
    ]

    # EN: Use unequal group sizes to distinguish 12% overall from 15%.
    # FR: Utiliser des groupes inégaux pour distinguer 12 % de 15 %.
    observations = [
        {
            "customer_id": f"C{number:06d}",
            "observation_month": september,
            "plan": "Basic" if number <= 80 else "Premium",
            "tenure_months": 0,
            "viewing_hours": Decimal("10"),
            "payment_failures": 0,
            "support_requests": 0,
            "cancelled_in_month": (
                number <= 8 or 81 <= number <= 84
            ),
        }
        for number in range(1, 101)
    ]

    # EN: Add a different month with all plans, inserted in reverse order.
    # FR: Ajouter un autre mois avec les abonnements dans l'ordre inverse.
    for number, plan in enumerate(
        ["Premium", "Standard", "Basic"],
        start=1,
    ):
        observations.append(
            {
                **observations[0],
                "customer_id": f"C{number:06d}",
                "observation_month": october,
                "plan": plan,
                "cancelled_in_month": False,
            }
        )

    with isolated_engine.begin() as connection:
        connection.execute(customer.insert(), customers)
        connection.execute(customer_month.insert(), observations)

    customers_query = select(customer).order_by(customer.c.customer_id)
    observations_query = select(customer_month).order_by(
        customer_month.c.customer_id,
        customer_month.c.observation_month,
    )

    with isolated_engine.connect() as connection:
        customers_before = connection.execute(customers_query).all()
        observations_before = connection.execute(observations_query).all()

    basic = {
        "plan": "Basic",
        "cohort_size": 80,
        "cancellation_count": 8,
        "cancellation_rate": 10.0,
    }
    premium = {
        "plan": "Premium",
        "cohort_size": 20,
        "cancellation_count": 4,
        "cancellation_rate": 20.0,
    }
    october_groups = [
        {
            "plan": plan,
            "cohort_size": 1,
            "cancellation_count": 0,
            "cancellation_rate": 0.0,
        }
        for plan in ["Basic", "Standard", "Premium"]
    ]

    # EN: Expected groups and totals are specified independently.
    # FR: Définir indépendamment les groupes et les totaux attendus.
    cases = [
        ("2026-09-01", None, [basic, premium], 100, 12, 12.0),
        ("2026-09-01", "Basic", [basic], 80, 8, 10.0),
        ("2026-09-01", "Premium", [premium], 20, 4, 20.0),
        ("2026-09-01", "Standard", [], 0, 0, None),
        ("2026-10-01", None, october_groups, 3, 0, 0.0),
        ("2026-10-01", "Standard", [october_groups[1]], 1, 0, 0.0),
        ("2026-11-01", None, [], 0, 0, None),
    ]

    # EN: Replace only engine selection; HTTP handling and SQL remain real.
    # FR: Remplacer uniquement le moteur ; HTTP et SQL restent réels.
    with patch("app.main.get_engine", return_value=isolated_engine):
        with TestClient(app) as client:
            for month, plan, groups, count, cancellations, rate in cases:
                params = {"observation_month": month}

                if plan is not None:
                    params["plan"] = plan

                comparison_response = client.get(
                    "/api/plan-comparisons",
                    params=params,
                )
                summary_response = client.get(
                    "/api/indicators",
                    params=params,
                )

                assert comparison_response.status_code == 200
                assert summary_response.status_code == 200

                comparison = comparison_response.json()
                summary = summary_response.json()

                assert comparison == {
                    "observation_month": month,
                    "plan": plan,
                    "comparisons": groups,
                }

                assert summary["observation_month"] == month
                assert summary["cohort_size"] == count
                assert summary["cancellation_count"] == cancellations

                if rate is None:
                    assert summary["cancellation_rate"] is None
                    assert summary["average_viewing_hours"] is None
                else:
                    assert summary["cancellation_rate"] == pytest.approx(
                        rate
                    )

                # EN: Group counts must reconcile with the same-scope summary.
                # FR: Les effectifs des groupes doivent correspondre au résumé.
                assert sum(
                    group["cohort_size"]
                    for group in comparison["comparisons"]
                ) == summary["cohort_size"]

                assert sum(
                    group["cancellation_count"]
                    for group in comparison["comparisons"]
                ) == summary["cancellation_count"]

    # EN: Verify all stored fields after requests through fresh connections.
    # FR: Vérifier tous les champs stockés après les appels API.
    with isolated_engine.connect() as connection:
        assert connection.execute(customers_query).all() == customers_before
        assert connection.execute(observations_query).all() == (
            observations_before
        )


def test_suggestions_api_uses_monthly_data_and_preserves_observations(
    isolated_engine,
):
    """Verify real SQL, reference scope and read-only behavior."""

    customers = [
        {"customer_id": f"C{number:06d}"}
        for number in range(1, 101)
    ]

    # EN: September: Basic 8/80, Premium 4/20, overall 12/100.
    # FR: Septembre : Basic 8/80, Premium 4/20, ensemble 12/100.
    observations = [
        {
            "customer_id": f"C{number:06d}",
            "observation_month": date(2026, 9, 1),
            "plan": "Basic" if number <= 80 else "Premium",
            "tenure_months": 0,
            "viewing_hours": Decimal("10"),
            "payment_failures": 0,
            "support_requests": 0,
            "cancelled_in_month": (
                number <= 8 or 81 <= number <= 84
            ),
        }
        for number in range(1, 101)
    ]

    # EN: October has three customers and no cancellation requests.
    # FR: Octobre contient trois clients et aucune demande de résiliation.
    for number, plan in enumerate(
        ["Basic", "Standard", "Premium"],
        start=1,
    ):
        observations.append(
            {
                **observations[0],
                "customer_id": f"C{number:06d}",
                "observation_month": date(2026, 10, 1),
                "plan": plan,
                "cancelled_in_month": False,
            }
        )

    with isolated_engine.begin() as connection:
        connection.execute(customer.insert(), customers)
        connection.execute(customer_month.insert(), observations)

    customers_query = select(customer).order_by(customer.c.customer_id)
    observations_query = select(customer_month).order_by(
        customer_month.c.customer_id,
        customer_month.c.observation_month,
    )

    with isolated_engine.connect() as connection:
        customers_before = connection.execute(customers_query).all()
        observations_before = connection.execute(observations_query).all()

    # EN: Expected reference counts always include all plans of that month.
    # FR: Les effectifs de référence incluent tous les abonnements du mois.
    cases = [
        ("2026-09-01", None, ["Premium"], 100, 12, 12.0),
        ("2026-09-01", "Premium", ["Premium"], 100, 12, 12.0),
        ("2026-09-01", "Basic", [], 100, 12, 12.0),
        ("2026-09-01", "Standard", [], 100, 12, 12.0),
        ("2026-10-01", None, [], 3, 0, 0.0),
        ("2026-10-01", "Premium", [], 3, 0, 0.0),
        ("2026-11-01", None, [], 0, 0, None),
    ]

    # EN: Only engine selection is replaced; SQL and rule evaluation are real.
    # FR: Seul le moteur est remplacé ; SQL et règle sont réellement exécutés.
    with patch("app.main.get_engine", return_value=isolated_engine):
        with TestClient(app) as client:
            for month, plan, expected_plans, count, cancellations, rate in cases:
                params = {"observation_month": month}

                if plan is not None:
                    params["plan"] = plan

                response = client.get(
                    "/api/retention-suggestions",
                    params=params,
                )

                assert response.status_code == 200
                body = response.json()

                assert body["observation_month"] == month
                assert body["plan"] == plan
                assert body["reference"] == {
                    "scope": "all_plans",
                    "cohort_size": count,
                    "cancellation_count": cancellations,
                    "cancellation_rate": rate,
                }
                assert [
                    item["plan"] for item in body["suggestions"]
                ] == expected_plans

                # EN: Compare the reference with the unfiltered monthly summary.
                # FR: Comparer la référence au résumé mensuel sans filtre de plan.
                summary_response = client.get(
                    "/api/indicators",
                    params={"observation_month": month},
                )

                assert summary_response.status_code == 200
                summary = summary_response.json()

                for field in (
                    "cohort_size",
                    "cancellation_count",
                    "cancellation_rate",
                ):
                    assert body["reference"][field] == summary[field]

                if expected_plans:
                    suggestion = body["suggestions"][0]
                    assert suggestion["rule_id"] == "PLAN_RATE_ABOVE_OVERALL"
                    assert suggestion["rule_version"] == 1
                    assert suggestion["cohort_size"] == 20
                    assert suggestion["cancellation_count"] == 4
                    assert suggestion["cancellation_rate"] == 20.0
                    assert "4 of 20" in suggestion["rationale"]
                    assert "12 of 100" in suggestion["rationale"]

    # EN: Confirm that every stored field remains unchanged.
    # FR: Confirmer que tous les champs enregistrés restent inchangés.
    with isolated_engine.connect() as connection:
        assert connection.execute(customers_query).all() == customers_before
        assert connection.execute(observations_query).all() == (
            observations_before
        )