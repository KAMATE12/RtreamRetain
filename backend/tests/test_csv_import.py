"""Tests for CSV import command validation."""

import csv
from unittest.mock import patch

from app.csv_import import main
from app.synthetic_data import FIELDNAMES

from sqlalchemy.exc import OperationalError


def test_invalid_csv_is_rejected_before_database_access(tmp_path, capsys):
    """An invalid file must be rejected without accessing PostgreSQL."""

    input_path = tmp_path / "invalid.csv"

    # EN: Prepare one valid row followed by an invalid row.
    # FR: Préparer une ligne valide suivie d'une ligne invalide.
    valid_row = {
        "customer_id": "C000001",
        "observation_month": "2026-09-01",
        "plan": "Premium",
        "tenure_months": "7",
        "viewing_hours": "4.09",
        "payment_failures": "2",
        "support_requests": "1",
        "cancelled_in_month": "false",
    }

    invalid_row = {
        **valid_row,
        "customer_id": "C000002",
        "tenure_months": "-1",
    }

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows([valid_row, invalid_row])

    original_content = input_path.read_bytes()

    # EN: Fail immediately if the command tries to obtain a database engine.
    # FR: Échouer immédiatement si la commande tente d'obtenir un moteur SQL.
    with patch(
        "app.csv_import.get_engine",
        side_effect=AssertionError("Database access must not occur"),
    ) as mocked_engine:
        exit_code = main([str(input_path)])

    output = capsys.readouterr().out

    assert exit_code == 1
    mocked_engine.assert_not_called()
    assert "Import rejected: CSV validation failed." in output
    assert "tenure_months" in output
    assert "No database writes were attempted." in output
    assert "Import successful." not in output

    # EN: Validation must leave the source file unchanged.
    # FR: La validation doit laisser le fichier source inchangé.
    assert input_path.read_bytes() == original_content

def test_database_error_does_not_expose_credentials(tmp_path, capsys):
    """A database failure must produce a safe message and failure exit code."""

    input_path = tmp_path / "valid.csv"

    # EN: Prepare valid input so execution reaches the database step.
    # FR: Préparer une entrée valide pour atteindre l'étape de connexion.
    valid_row = {
        "customer_id": "C000001",
        "observation_month": "2026-09-01",
        "plan": "Premium",
        "tenure_months": "7",
        "viewing_hours": "4.09",
        "payment_failures": "2",
        "support_requests": "1",
        "cancelled_in_month": "false",
    }

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(valid_row)

    # EN: Use invented credentials to simulate a sensitive technical error.
    # FR: Utiliser des identifiants inventés pour simuler une erreur sensible.
    fake_url = (
        "postgresql+psycopg://test_user:DO_NOT_EXPOSE"
        "@localhost:5433/test_database"
    )
    simulated_error = OperationalError(
        "SELECT 1",
        {},
        Exception(f"Connection failed: {fake_url}"),
    )

    # EN: Simulate failure when the transaction tries to open its connection.
    # FR: Simuler un échec lors de l'ouverture de la connexion transactionnelle.
    with patch("app.csv_import.get_engine") as mocked_engine:
        transaction_context = mocked_engine.return_value.begin.return_value
        transaction_context.__enter__.side_effect = simulated_error

        exit_code = main([str(input_path)])

    captured = capsys.readouterr()
    displayed_text = captured.out + captured.err

    assert exit_code == 1
    mocked_engine.return_value.begin.assert_called_once()
    assert "Import failed: database operation could not be completed." in captured.out

    # EN: Neither credentials nor a success message may be displayed.
    # FR: Aucun identifiant ni message de réussite ne doit être affiché.
    assert fake_url not in displayed_text
    assert "DO_NOT_EXPOSE" not in displayed_text
    assert "test_user" not in displayed_text
    assert "Import successful." not in displayed_text
    assert "Inserted observations:" not in displayed_text