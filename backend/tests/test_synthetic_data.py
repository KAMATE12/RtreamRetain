"""Tests for reproducible synthetic CSV generation."""

import pytest

import argparse

from app.synthetic_data import generate_dataset, write_dataset_csv


def test_same_configuration_produces_identical_csv(tmp_path):
    """Identical settings must produce identical CSV bytes."""

    # EN: Generate both datasets independently with identical settings.
    # FR: Générer séparément les données avec les mêmes paramètres.
    first_records = generate_dataset(
        customer_count=100,
        observation_month="2026-09-01",
        seed=42,
    )
    second_records = generate_dataset(
        customer_count=100,
        observation_month="2026-09-01",
        seed=42,
    )

    # EN: Use temporary files, keeping the project's example untouched.
    # FR: Utiliser des fichiers temporaires sans toucher au CSV du projet.
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"

    write_dataset_csv(first_records, first_path)
    write_dataset_csv(second_records, second_path)

    # EN: Compare exact bytes, including formatting and line endings.
    # FR: Comparer les octets, y compris le format et les fins de ligne.
    assert first_path.read_bytes() == second_path.read_bytes()

def test_existing_file_is_not_overwritten(tmp_path):
    """Refusing an overwrite must preserve the original content."""

    # EN: Define the path and the original bytes.
    # FR: Définir le chemin et les octets d'origine.
    output_path = tmp_path / "existing.csv"
    original_content = b"existing content\n"

    # EN: Actually create the file before attempting to overwrite it.
    # FR: Créer réellement le fichier avant de tenter de l'écraser.
    output_path.write_bytes(original_content)

    records = generate_dataset(customer_count=3)

    # EN: Writing to an existing file must raise FileExistsError.
    # FR: L'écriture vers un fichier existant doit être refusée.
    with pytest.raises(FileExistsError):
        write_dataset_csv(records, output_path)

    # EN: Verify that the original content is unchanged.
    # FR: Vérifier que le contenu d'origine est resté intact.
    assert output_path.read_bytes() == original_content


def test_generated_records_follow_documented_rules():
    """Check record count, uniqueness, ordering and field constraints."""

    records = generate_dataset(
        customer_count=100,
        observation_month="2026-09-01",
        seed=42,
    )

    # EN: Generate exactly the requested number of observations.
    # FR: Produire exactement le nombre d'observations demandé.
    assert len(records) == 100

    # EN: A set removes duplicate keys; its size must remain unchanged.
    # FR: Un ensemble élimine les doublons ; sa taille doit rester 100.
    observation_keys = {
        (record["customer_id"], record["observation_month"])
        for record in records
    }
    assert len(observation_keys) == 100

    # EN: Check the exact field names independently of the implementation.
    # FR: Vérifier les champs attendus indépendamment du code de génération.
    expected_fields = {
        "customer_id",
        "observation_month",
        "plan",
        "tenure_months",
        "viewing_hours",
        "payment_failures",
        "support_requests",
        "cancelled_in_month",
    }

    for number, record in enumerate(records, start=1):
        assert set(record) == expected_fields

        # EN: Check sequential identifiers and the configured month.
        # FR: Vérifier l'ordre des identifiants et le mois configuré.
        assert record["customer_id"] == f"C{number:06d}"
        assert record["observation_month"] == "2026-09-01"
        assert record["plan"] in {"Basic", "Standard", "Premium"}

        # EN: Verify both integer types and generation bounds.
        # FR: Vérifier les types entiers et les limites de génération.
        for field, maximum in (
            ("tenure_months", 60),
            ("payment_failures", 3),
            ("support_requests", 5),
        ):
            assert type(record[field]) is int
            assert 0 <= record[field] <= maximum

        # EN: Viewing hours must have exactly two decimal digits.
        # FR: Les heures doivent comporter exactement deux décimales.
        hours = record["viewing_hours"]
        assert isinstance(hours, str)

        whole, separator, fraction = hours.partition(".")
        assert separator == "."
        assert whole.isdigit()
        assert fraction.isdigit()
        assert len(fraction) == 2
        assert 0 <= float(hours) <= 120

        # EN: Keep a genuine Boolean in the Python record.
        # FR: Conserver un véritable booléen dans l'observation Python.
        assert type(record["cancelled_in_month"]) is bool


@pytest.mark.parametrize(
    "parameters, expected_exception",
    [
        ({"customer_count": 0}, ValueError),
        ({"customer_count": -1}, ValueError),
        ({"customer_count": 2.5}, TypeError),
        ({"customer_count": True}, TypeError),
        ({"seed": "42"}, TypeError),
        ({"seed": False}, TypeError),
        ({"observation_month": "2026-09-15"}, ValueError),
        ({"observation_month": "2026-02-30"}, ValueError),
        ({"observation_month": "01/09/2026"}, ValueError),
        ({"observation_month": "20260901"}, ValueError),
        ({"observation_month": None}, TypeError),
    ],
)
def test_invalid_generator_parameters_are_rejected(
    parameters,
    expected_exception,
):
    """Reject invalid configuration before producing a dataset."""

    # EN: Expand the dictionary into named function arguments.
    # FR: Transmettre le dictionnaire sous forme d'arguments nommés.
    with pytest.raises(expected_exception):
        generate_dataset(**parameters)