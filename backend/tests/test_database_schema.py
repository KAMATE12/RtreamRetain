"""Integration tests using isolated PostgreSQL schemas."""

import os
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.schema import CreateSchema

from app.database import get_engine
from app.schema import customer, customer_month, metadata

from sqlalchemy.exc import IntegrityError

from app.csv_import import (
    ObservationConflictError,
    store_validated_records,
)

# EN: Run these tests only when explicitly enabled.
# FR: Exécuter ces tests uniquement lorsqu'ils sont activés explicitement.
pytestmark = pytest.mark.skipif(
    os.getenv("STREAMRETAIN_DB_TESTS") != "1",
    reason="Set STREAMRETAIN_DB_TESTS=1 to run PostgreSQL integration tests.",
)


@pytest.fixture
def db_connection():
    """Provide isolated tables and undo all test changes afterwards."""

    # EN: Generate a different schema name for each test.
    # FR: Générer un nom de schéma différent pour chaque test.
    schema_name = f"test_streamretain_{uuid4().hex}"

    with get_engine().connect() as connection:
        transaction = connection.begin()

        try:
            # EN: Create the isolated schema inside the transaction.
            # FR: Créer le schéma isolé dans la transaction.
            connection.execute(CreateSchema(schema_name))

            # EN: Direct our table operations to this test schema.
            # FR: Diriger les opérations sur nos tables vers ce schéma de test.
            connection = connection.execution_options(
                schema_translate_map={None: schema_name},
            )

            metadata.create_all(bind=connection)

            # EN: Give the prepared connection to the test.
            # FR: Fournir la connexion préparée au test.
            yield connection

        finally:
            # EN: Undo the test data, tables and schema creation.
            # FR: Annuler les données, les tables et le schéma créés pour le test.
            transaction.rollback()


@pytest.fixture
def sample_observation():
    """Provide a small observation with precisely defined values."""

    return {
        "customer_id": "C000001",
        "observation_month": date(2026, 9, 1),
        "plan": "Premium",
        "tenure_months": 7,
        "viewing_hours": Decimal("0.125"),
        "payment_failures": 2,
        "support_requests": 1,
        "cancelled_in_month": False,
    }


def test_stored_observation_matches_input(db_connection, sample_observation):
    """PostgreSQL must preserve every observation value."""

    # EN: Create the customer before its monthly observation.
    # FR: Créer le client avant son observation mensuelle.
    db_connection.execute(
        customer.insert(),
        {"customer_id": sample_observation["customer_id"]},
    )
    db_connection.execute(
        customer_month.insert(),
        sample_observation,
    )

    # EN: Read the stored row as a mapping of column names to values.
    # FR: Relire la ligne sous forme d'association entre colonnes et valeurs.
    stored = db_connection.execute(
        select(customer_month)
    ).mappings().one()

    assert dict(stored) == sample_observation


def test_schema_creation_preserves_data(db_connection, sample_observation):
    """Repeating schema creation must preserve existing observations."""

    db_connection.execute(
        customer.insert(),
        {"customer_id": sample_observation["customer_id"]},
    )
    db_connection.execute(
        customer_month.insert(),
        sample_observation,
    )

    # EN: Repeat schema creation while the tables contain data.
    # FR: Répéter la création alors que les tables contiennent des données.
    metadata.create_all(
        bind=db_connection,
        checkfirst=True,
    )

    stored = db_connection.execute(
        select(customer_month)
    ).mappings().one()

    assert dict(stored) == sample_observation

def test_same_customer_can_have_two_months(db_connection, sample_observation):
    """Different months for the same customer must be accepted."""

    db_connection.execute(
        customer.insert(),
        {"customer_id": sample_observation["customer_id"]},
    )

    # EN: Copy the observation and change only its month.
    # FR: Copier l'observation et modifier uniquement son mois.
    october_observation = {
        **sample_observation,
        "observation_month": date(2026, 10, 1),
    }

    db_connection.execute(
        customer_month.insert(),
        [sample_observation, october_observation],
    )

    # EN: Check that both months belong to the same existing customer.
    # FR: Vérifier que les deux mois appartiennent au même client existant.
    customer_ids = db_connection.execute(
        select(customer.c.customer_id)
    ).scalars().all()

    months = db_connection.execute(
        select(customer_month.c.observation_month)
        .order_by(customer_month.c.observation_month)
    ).scalars().all()

    assert customer_ids == ["C000001"]
    assert months == [date(2026, 9, 1), date(2026, 10, 1)]


def test_duplicate_customer_month_is_rejected(
    db_connection,
    sample_observation,
):
    """The same customer-month pair must not be stored twice."""

    db_connection.execute(
        customer.insert(),
        {"customer_id": sample_observation["customer_id"]},
    )
    db_connection.execute(
        customer_month.insert(),
        sample_observation,
    )

    # EN: Expect the duplicate insertion to fail inside a savepoint.
    # FR: Attendre le refus du doublon dans un point de sauvegarde.
    with pytest.raises(IntegrityError) as captured:
        with db_connection.begin_nested():
            db_connection.execute(
                customer_month.insert(),
                sample_observation,
            )

    # EN: PostgreSQL code 23505 means a uniqueness violation.
    # FR: Le code PostgreSQL 23505 indique une violation d'unicité.
    assert captured.value.orig.sqlstate == "23505"

    # EN: The original observation must remain unchanged.
    # FR: L'observation initiale doit rester inchangée.
    stored = db_connection.execute(
        select(customer_month)
    ).mappings().one()

    assert dict(stored) == sample_observation


def test_observation_without_customer_is_rejected(
    db_connection,
    sample_observation,
):
    """An observation must reference an existing customer."""

    # EN: Deliberately omit the customer insertion.
    # FR: Omettre volontairement la création du client.
    with pytest.raises(IntegrityError) as captured:
        with db_connection.begin_nested():
            db_connection.execute(
                customer_month.insert(),
                sample_observation,
            )

    # EN: PostgreSQL code 23503 means a foreign-key violation.
    # FR: Le code PostgreSQL 23503 indique une violation de clé étrangère.
    assert captured.value.orig.sqlstate == "23503"

    # EN: No observation should have been inserted.
    # FR: Aucune observation ne doit avoir été insérée.
    stored = db_connection.execute(
        select(customer_month)
    ).mappings().all()

    assert stored == []

@pytest.mark.parametrize(
    "field,value,expected_constraint",
    [
        (
            "observation_month",
            date(2026, 9, 15),
            "ck_customer_month_first_day",
        ),
        (
            "plan",
            "Unknown",
            "ck_customer_month_plan",
        ),
        (
            "tenure_months",
            -1,
            "ck_customer_month_tenure_non_negative",
        ),
        (
            "payment_failures",
            -1,
            "ck_customer_month_payment_failures_non_negative",
        ),
        (
            "support_requests",
            -1,
            "ck_customer_month_support_requests_non_negative",
        ),
        (
            "viewing_hours",
            Decimal("-0.01"),
            "ck_customer_month_viewing_hours_valid",
        ),
        (
            "viewing_hours",
            Decimal("NaN"),
            "ck_customer_month_viewing_hours_valid",
        ),
        (
            "viewing_hours",
            Decimal("Infinity"),
            "ck_customer_month_viewing_hours_valid",
        ),
        (
            "viewing_hours",
            Decimal("-Infinity"),
            "ck_customer_month_viewing_hours_valid",
        ),
    ],
)
def test_invalid_observation_value_is_rejected(
    db_connection,
    sample_observation,
    field,
    value,
    expected_constraint,
):
    """Each invalid value must fail its intended database constraint."""

    db_connection.execute(
        customer.insert(),
        {"customer_id": sample_observation["customer_id"]},
    )

    # EN: Change one field while keeping all other values valid.
    # FR: Modifier un champ en conservant les autres valeurs valides.
    invalid_observation = {
        **sample_observation,
        field: value,
    }

    with pytest.raises(IntegrityError) as captured:
        with db_connection.begin_nested():
            db_connection.execute(
                customer_month.insert(),
                invalid_observation,
            )

    # EN: Confirm a CHECK violation and identify the exact constraint.
    # FR: Confirmer une violation CHECK et identifier la contrainte exacte.
    assert captured.value.orig.sqlstate == "23514"
    assert (
        captured.value.orig.diag.constraint_name
        == expected_constraint
    )

    # EN: The rejected observation must not remain in the table.
    # FR: L'observation refusée ne doit pas rester dans la table.
    stored = db_connection.execute(
        select(customer_month)
    ).mappings().all()

    assert stored == []

def test_import_inserts_new_observation(db_connection, sample_observation):
    """Import must create the missing customer and its observation."""

    # EN: Import without creating the customer manually.
    # FR: Importer sans créer le client manuellement.
    result = store_validated_records(
        db_connection,
        [sample_observation],
    )

    # EN: Counts refer to observations, not customer identities.
    # FR: Les compteurs concernent les observations, pas les identités clients.
    assert result == {"inserted": 1, "unchanged": 0}

    customer_ids = db_connection.execute(
        select(customer.c.customer_id)
    ).scalars().all()

    stored = db_connection.execute(
        select(customer_month)
    ).mappings().one()

    assert customer_ids == ["C000001"]
    assert dict(stored) == sample_observation


def test_identical_reimport_keeps_one_observation(
    db_connection,
    sample_observation,
):
    """Repeating an identical import must not create duplicates."""

    # EN: The first import creates the observation.
    # FR: Le premier import crée l'observation.
    first_result = store_validated_records(
        db_connection,
        [sample_observation],
    )

    # EN: The second import recognizes the identical observation.
    # FR: Le deuxième import reconnaît l'observation identique.
    second_result = store_validated_records(
        db_connection,
        [sample_observation],
    )

    assert first_result == {"inserted": 1, "unchanged": 0}
    assert second_result == {"inserted": 0, "unchanged": 1}

    # EN: Exactly one customer and one observation must remain.
    # FR: Il doit rester exactement un client et une observation.
    customer_ids = db_connection.execute(
        select(customer.c.customer_id)
    ).scalars().all()

    observations = db_connection.execute(
        select(customer_month)
    ).mappings().all()

    assert customer_ids == ["C000001"]
    assert len(observations) == 1
    assert dict(observations[0]) == sample_observation

def test_conflict_rolls_back_new_customer_and_observation(
    db_connection,
    sample_observation,
):
    """A conflict must undo earlier additions in the same import attempt."""

    # EN: Prepare an observation that exists before the attempted import.
    # FR: Préparer une observation existant avant la tentative d'import.
    store_validated_records(
        db_connection,
        [sample_observation],
    )

    # EN: The first incoming observation belongs to a new customer.
    # FR: La première observation entrante appartient à un nouveau client.
    new_observation = {
        **sample_observation,
        "customer_id": "C000002",
    }

    # EN: The second observation conflicts with the existing viewing hours.
    # FR: La deuxième observation contredit les heures déjà enregistrées.
    conflicting_observation = {
        **sample_observation,
        "viewing_hours": Decimal("20.00"),
    }

    # EN: Group both incoming observations in one rollback boundary.
    # FR: Regrouper les deux observations dans un même périmètre d'annulation.
    with pytest.raises(ObservationConflictError) as captured:
        with db_connection.begin_nested():
            store_validated_records(
                db_connection,
                [new_observation, conflicting_observation],
            )

    # EN: The message must identify the conflicting observation and field.
    # FR: Le message doit identifier l'observation et le champ en conflit.
    assert str(captured.value) == (
        "Conflict for customer-month (C000001, 2026-09-01): "
        "different fields: viewing_hours."
    )

    # EN: The newly created customer must have been rolled back.
    # FR: La création du nouveau client doit avoir été annulée.
    customer_ids = db_connection.execute(
        select(customer.c.customer_id)
        .order_by(customer.c.customer_id)
    ).scalars().all()

    assert customer_ids == ["C000001"]

    # EN: Only the original, unchanged observation must remain.
    # FR: Seule l'observation initiale, inchangée, doit rester.
    observations = db_connection.execute(
        select(customer_month)
    ).mappings().all()

    assert len(observations) == 1
    assert dict(observations[0]) == sample_observation

def test_database_error_rolls_back_entire_attempt(
    db_connection,
    sample_observation,
):
    """A failed database write must undo earlier additions."""

    # EN: Prepare data that must survive the failed import attempt.
    # FR: Préparer des données qui doivent survivre à l'import échoué.
    store_validated_records(
        db_connection,
        [sample_observation],
    )

    # EN: This observation can be inserted successfully.
    # FR: Cette observation peut être insérée correctement.
    new_observation = {
        **sample_observation,
        "customer_id": "C000002",
    }

    # EN: Deliberately bypass CSV validation to trigger a database error.
    # FR: Contourner volontairement la validation CSV pour provoquer une erreur SQL.
    invalid_observation = {
        **sample_observation,
        "customer_id": "C000003",
        "tenure_months": -1,
    }

    with pytest.raises(IntegrityError) as captured:
        with db_connection.begin_nested():
            store_validated_records(
                db_connection,
                [new_observation, invalid_observation],
            )

    # EN: Verify that the intended database constraint caused the failure.
    # FR: Vérifier que la contrainte attendue a provoqué l'échec.
    assert captured.value.orig.sqlstate == "23514"
    assert (
        captured.value.orig.diag.constraint_name
        == "ck_customer_month_tenure_non_negative"
    )

    # EN: Neither of the two new customer identities should remain.
    # FR: Aucune des deux nouvelles identités clients ne doit rester.
    customer_ids = db_connection.execute(
        select(customer.c.customer_id)
        .order_by(customer.c.customer_id)
    ).scalars().all()

    assert customer_ids == ["C000001"]

    # EN: Preserve only the observation that existed before the attempt.
    # FR: Conserver uniquement l'observation présente avant la tentative.
    observations = db_connection.execute(
        select(customer_month)
    ).mappings().all()

    assert len(observations) == 1
    assert dict(observations[0]) == sample_observation