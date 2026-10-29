"""Test real import transactions in isolated PostgreSQL schemas."""

import csv
import os
from datetime import date
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.schema import CreateSchema, DropSchema

from app.csv_import import main
from app.database import get_engine
from app.schema import customer, customer_month, metadata
from app.synthetic_data import FIELDNAMES


pytestmark = pytest.mark.skipif(
    os.getenv("STREAMRETAIN_DB_TESTS") != "1",
    reason="Set STREAMRETAIN_DB_TESTS=1 to run PostgreSQL integration tests.",
)


@pytest.fixture
def isolated_engine():
    """Provide isolated tables that support real commits and rollbacks."""

    schema_name = f"test_import_{uuid4().hex}"

    # EN: Route all table operations to this test's unique schema.
    # FR: Diriger les opérations sur les tables vers le schéma unique du test.
    test_engine = get_engine().execution_options(
        schema_translate_map={None: schema_name},
    )

    # EN: Commit setup so other connections can access the test tables.
    # FR: Valider la préparation pour rendre les tables accessibles aux connexions.
    with test_engine.begin() as connection:
        connection.execute(CreateSchema(schema_name))
        metadata.create_all(bind=connection)

    try:
        yield test_engine

    finally:
        # EN: Remove only the tables and schema created for this test.
        # FR: Supprimer uniquement les tables et le schéma créés pour ce test.
        with test_engine.begin() as connection:
            metadata.drop_all(bind=connection)
            connection.execute(DropSchema(schema_name))


@pytest.fixture
def csv_row():
    """Provide one valid CSV observation."""

    return {
        "customer_id": "C000001",
        "observation_month": "2026-09-01",
        "plan": "Premium",
        "tenure_months": "7",
        "viewing_hours": "0.125",
        "payment_failures": "2",
        "support_requests": "1",
        "cancelled_in_month": "false",
    }


def write_csv(path, rows):
    """Write a temporary CSV using the project's column names."""

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def test_command_commits_observation(
    isolated_engine,
    tmp_path,
    capsys,
    csv_row,
):
    """Successful command data must be visible from another connection."""

    input_path = tmp_path / "valid.csv"
    write_csv(input_path, [csv_row])

    # EN: Replace only the engine selection; PostgreSQL operations remain real.
    # FR: Remplacer uniquement le choix du moteur ; les opérations SQL restent réelles.
    with patch(
        "app.csv_import.get_engine",
        return_value=isolated_engine,
    ):
        exit_code = main([str(input_path)])

    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Import successful." in output
    assert "Inserted observations: 1" in output
    assert "Unchanged observations: 0" in output

    # EN: Read through another connection after the command has finished.
    # FR: Relire avec une autre connexion après la fin de la commande.
    with isolated_engine.connect() as connection:
        customer_ids = connection.execute(
            select(customer.c.customer_id)
        ).scalars().all()

        stored = connection.execute(
            select(customer_month)
        ).mappings().one()

    assert customer_ids == ["C000001"]
    assert dict(stored) == {
        "customer_id": "C000001",
        "observation_month": date(2026, 9, 1),
        "plan": "Premium",
        "tenure_months": 7,
        "viewing_hours": Decimal("0.125"),
        "payment_failures": 2,
        "support_requests": 1,
        "cancelled_in_month": False,
    }


def test_command_rolls_back_on_conflict(
    isolated_engine,
    tmp_path,
    capsys,
    csv_row,
):
    """A conflict must preserve existing data and undo all new additions."""

    initial_path = tmp_path / "initial.csv"
    write_csv(initial_path, [csv_row])

    # EN: Prepare one new observation followed by a conflicting observation.
    # FR: Préparer une nouvelle observation suivie d'une observation en conflit.
    new_row = {
        **csv_row,
        "customer_id": "C000002",
    }
    conflicting_row = {
        **csv_row,
        "viewing_hours": "20.00",
    }

    conflict_path = tmp_path / "conflict.csv"
    write_csv(conflict_path, [new_row, conflicting_row])
    original_content = conflict_path.read_bytes()

    with patch(
        "app.csv_import.get_engine",
        return_value=isolated_engine,
    ):
        # EN: Commit the initial observation before attempting the conflict.
        # FR: Enregistrer définitivement l'observation initiale avant le conflit.
        assert main([str(initial_path)]) == 0

        # EN: Clear the initial success output before checking the failed import.
        # FR: Effacer la sortie initiale pour examiner uniquement l'import échoué.
        capsys.readouterr()

        # EN: This command must return failure after rolling back its transaction.
        # FR: Cette commande doit signaler l'échec après annulation de sa transaction.
        exit_code = main([str(conflict_path)])

    output = capsys.readouterr().out

    assert exit_code == 1
    assert "Import rejected:" in output
    assert "(C000001, 2026-09-01)" in output
    assert "different fields: viewing_hours." in output
    assert "The import transaction was rolled back." in output
    assert "Import successful." not in output
    assert "Inserted observations:" not in output

    # EN: Inspect persisted data using another connection.
    # FR: Examiner les données conservées avec une autre connexion.
    with isolated_engine.connect() as connection:
        customer_ids = connection.execute(
            select(customer.c.customer_id)
            .order_by(customer.c.customer_id)
        ).scalars().all()

        observations = connection.execute(
            select(customer_month)
        ).mappings().all()

    # EN: The new customer and its observation must not remain.
    # FR: Le nouveau client et son observation ne doivent pas rester.
    assert customer_ids == ["C000001"]
    assert len(observations) == 1

    # EN: Every field of the original observation must remain unchanged.
    # FR: Chaque champ de l'observation initiale doit rester inchangé.
    assert dict(observations[0]) == {
        "customer_id": "C000001",
        "observation_month": date(2026, 9, 1),
        "plan": "Premium",
        "tenure_months": 7,
        "viewing_hours": Decimal("0.125"),
        "payment_failures": 2,
        "support_requests": 1,
        "cancelled_in_month": False,
    }

    assert conflict_path.read_bytes() == original_content

def test_command_rolls_back_on_database_write_failure(
    isolated_engine,
    tmp_path,
    capsys,
    csv_row,
):
    """A database storage error must undo the entire import attempt."""

    initial_path = tmp_path / "initial.csv"
    write_csv(initial_path, [csv_row])

    # EN: This new observation can be stored successfully.
    # FR: Cette nouvelle observation peut être enregistrée correctement.
    new_row = {
        **csv_row,
        "customer_id": "C000002",
    }

    # EN: This value exceeds PostgreSQL's INTEGER storage capacity.
    # FR: Cette valeur dépasse la capacité du type INTEGER de PostgreSQL.
    oversized_row = {
        **csv_row,
        "customer_id": "C000003",
        "tenure_months": "2147483648",
    }

    failing_path = tmp_path / "storage_error.csv"
    write_csv(failing_path, [new_row, oversized_row])
    original_content = failing_path.read_bytes()

    with patch(
        "app.csv_import.get_engine",
        return_value=isolated_engine,
    ):
        # EN: Commit the initial data before the failing attempt.
        # FR: Enregistrer les données initiales avant la tentative échouée.
        assert main([str(initial_path)]) == 0
        capsys.readouterr()

        exit_code = main([str(failing_path)])

    captured = capsys.readouterr()
    displayed_text = captured.out + captured.err

    assert exit_code == 1
    assert (
        "Import failed: database operation could not be completed."
        in captured.out
    )
    assert "Import successful." not in displayed_text
    assert "Inserted observations:" not in displayed_text
    assert "Traceback" not in displayed_text

    # EN: Read the final state through another connection.
    # FR: Lire l'état final avec une autre connexion.
    with isolated_engine.connect() as connection:
        customer_ids = connection.execute(
            select(customer.c.customer_id)
            .order_by(customer.c.customer_id)
        ).scalars().all()

        observations = connection.execute(
            select(customer_month)
        ).mappings().all()

    # EN: Both newly created customers and all new observations are rolled back.
    # FR: Les deux nouveaux clients et toutes les nouvelles observations sont annulés.
    assert customer_ids == ["C000001"]
    assert len(observations) == 1

    assert dict(observations[0]) == {
        "customer_id": "C000001",
        "observation_month": date(2026, 9, 1),
        "plan": "Premium",
        "tenure_months": 7,
        "viewing_hours": Decimal("0.125"),
        "payment_failures": 2,
        "support_requests": 1,
        "cancelled_in_month": False,
    }

    assert failing_path.read_bytes() == original_content