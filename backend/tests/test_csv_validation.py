"""Tests for customer-month CSV validation."""

from app.csv_validation import validate_header
from app.synthetic_data import FIELDNAMES

from app.csv_validation import validate_csv_header

import pytest

from app.csv_validation import parse_non_negative_integer

from app.csv_validation import parse_csv_boolean

from decimal import Decimal

from app.csv_validation import parse_viewing_hours

from app.csv_validation import parse_plan

from datetime import date

from app.csv_validation import parse_csv_month

from app.csv_validation import parse_customer_id

from app.csv_validation import validate_customer_month

import csv

from app.csv_validation import validate_csv_file


def test_valid_header_is_accepted():
    # EN: All required columns occur exactly once.
    # FR: Toutes les colonnes obligatoires apparaissent une seule fois.
    assert validate_header(list(FIELDNAMES)) == []


def test_reordered_header_is_accepted():
    # EN: Column names identify fields, so their order may change.
    # FR: Les noms identifient les champs ; leur ordre peut changer.
    header = list(reversed(FIELDNAMES))

    assert validate_header(header) == []


def test_duplicate_column_is_rejected():
    # EN: Add a second occurrence of an existing column.
    # FR: Ajouter une deuxième occurrence d'une colonne existante.
    header = list(FIELDNAMES) + ["plan"]

    assert validate_header(header) == [
        "Header: duplicate column 'plan'."
    ]


def test_wrong_case_reports_missing_and_unexpected_columns():
    # EN: Work on a copy without modifying the shared field names.
    # FR: Travailler sur une copie sans modifier les noms partagés.
    header = list(FIELDNAMES)
    header[header.index("plan")] = "Plan"

    assert validate_header(header) == [
        "Header: missing required column 'plan'.",
        "Header: unexpected column 'Plan'.",
    ]


def test_missing_column_is_rejected():
    # EN: Remove a required column from the header.
    # FR: Retirer une colonne obligatoire de l'en-tête.
    header = list(FIELDNAMES)
    header.remove("plan")

    assert validate_header(header) == [
        "Header: missing required column 'plan'."
    ]


def test_additional_column_is_rejected():
    # EN: Reject a column outside the agreed data contract.
    # FR: Refuser une colonne absente du contrat de données.
    header = list(FIELDNAMES) + ["email"]

    assert validate_header(header) == [
        "Header: unexpected column 'email'."
    ]


def test_absent_header_is_rejected():
    # EN: None represents an absent header.
    # FR: None représente l'absence d'en-tête.
    assert validate_header(None) == [
        "Header: missing column names."
    ]


def test_empty_header_is_rejected():
    # EN: An empty list contains no column names.
    # FR: Une liste vide ne contient aucun nom de colonne.
    assert validate_header([]) == [
        "Header: missing column names."
    ]


def test_csv_file_with_valid_header_is_accepted(tmp_path):
    # EN: Create a temporary CSV containing a valid header.
    # FR: Créer un CSV temporaire contenant un en-tête valide.
    input_path = tmp_path / "valid.csv"
    content = ",".join(FIELDNAMES) + "\n"
    input_path.write_text(content, encoding="utf-8")

    assert validate_csv_header(input_path) == []


def test_empty_csv_file_is_rejected(tmp_path):
    # EN: Create an existing file with no content.
    # FR: Créer un fichier existant sans contenu.
    input_path = tmp_path / "empty.csv"
    input_path.write_text("", encoding="utf-8")

    assert validate_csv_header(input_path) == [
        "Header: missing column names."
    ]


def test_missing_csv_file_is_reported(tmp_path):
    # EN: Build a path without creating the file.
    # FR: Construire un chemin sans créer le fichier.
    input_path = tmp_path / "missing.csv"

    errors = validate_csv_header(input_path)

    # EN: The operating system's detailed message may vary.
    # FR: Le message détaillé du système peut varier.
    assert len(errors) == 1
    assert errors[0].startswith("File: cannot read input:")


def test_invalid_utf8_is_rejected(tmp_path):
    # EN: Write a byte that is invalid on its own in UTF-8.
    # FR: Écrire un octet qui, seul, est invalide en UTF-8.
    input_path = tmp_path / "invalid_encoding.csv"
    input_path.write_bytes(b"\xff")

    assert validate_csv_header(input_path) == [
        "File: cannot decode the input as UTF-8."
    ]


def test_unclosed_csv_quote_is_rejected(tmp_path):
    # EN: Start a quoted field without closing its quotation mark.
    # FR: Commencer un champ entre guillemets sans le refermer.
    input_path = tmp_path / "malformed.csv"
    input_path.write_text(
        '"customer_id,observation_month\n',
        encoding="utf-8",
    )

    errors = validate_csv_header(input_path)

    assert len(errors) == 1
    assert errors[0].startswith("Header: malformed CSV:")

@pytest.mark.parametrize(
    "value, expected",
    [
        ("0", 0),
        ("90", 90),
        ("007", 7),
    ],
)
def test_valid_integer_text_is_converted(value, expected):
    # EN: Convert valid CSV text into the expected integer.
    # FR: Convertir le texte CSV valide en l'entier attendu.
    result = parse_non_negative_integer(value)

    assert result == expected
    assert type(result) is int


def test_empty_integer_value_is_rejected():
    # EN: Missing information must not silently become zero.
    # FR: Une information manquante ne doit pas devenir zéro.
    with pytest.raises(ValueError, match="^value is required$"):
        parse_non_negative_integer("")


@pytest.mark.parametrize(
    "value",
    [
        "-3",
        "2.5",
        "+3",
        " 3 ",
        "three",
        "1_000",
        "\u0663",  # EN: Arabic-Indic digit. FR: Chiffre arabo-indien.
    ],
)
def test_invalid_integer_format_is_rejected(value):
    # EN: Each invalid format must raise an explanatory error.
    # FR: Chaque format invalide doit déclencher une erreur explicative.
    with pytest.raises(
        ValueError,
        match="must contain only digits 0-9",
    ):
        parse_non_negative_integer(value)

@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", True),
        ("false", False),
    ],
)
def test_valid_boolean_text_is_converted(value, expected):
    # EN: Require the exact expected Boolean value.
    # FR: Exiger exactement la valeur booléenne attendue.
    assert parse_csv_boolean(value) is expected


def test_empty_boolean_value_is_rejected():
    # EN: An empty cell must not become False.
    # FR: Une cellule vide ne doit pas devenir False.
    with pytest.raises(ValueError, match="^value is required$"):
        parse_csv_boolean("")


@pytest.mark.parametrize(
    "value",
    ["True", "FALSE", "1", "0", "yes", " false "],
)
def test_invalid_boolean_format_is_rejected(value):
    # EN: Reject spellings outside the agreed CSV format.
    # FR: Refuser les écritures hors du format CSV convenu.
    with pytest.raises(
        ValueError,
        match="must be exactly 'true' or 'false'",
    ):
        parse_csv_boolean(value)

@pytest.mark.parametrize(
    "value, expected",
    [
        ("0", Decimal("0")),
        ("4.09", Decimal("4.09")),
        ("150.5", Decimal("150.5")),
        ("0.125", Decimal("0.125")),
    ],
)
def test_valid_viewing_hours_are_converted(value, expected):
    # EN: Preserve the supplied decimal value without rounding.
    # FR: Conserver la valeur décimale fournie sans l'arrondir.
    result = parse_viewing_hours(value)

    assert result == expected
    assert isinstance(result, Decimal)


def test_empty_viewing_hours_are_rejected():
    # EN: Missing viewing information must not become zero.
    # FR: Une durée manquante ne doit pas devenir zéro.
    with pytest.raises(ValueError, match="^value is required$"):
        parse_viewing_hours("")


@pytest.mark.parametrize(
    "value",
    [
        "-3",
        "4,09",
        "NaN",
        "Infinity",
        "-Infinity",
        " 4.09 ",
        ".5",
        "5.",
        "1e2",
        "+3",
        "1_000",
        "abc",
    ],
)
def test_invalid_viewing_hours_are_rejected(value):
    # EN: Reject negative, non-finite and incorrectly formatted values.
    # FR: Refuser les valeurs négatives, non finies ou mal écrites.
    with pytest.raises(
        ValueError,
        match="must be a non-negative finite decimal",
    ):
        parse_viewing_hours(value)

@pytest.mark.parametrize(
    "value",
    ["Basic", "Standard", "Premium"],
)
def test_allowed_plan_is_accepted(value):
    # EN: Each documented category must be accepted unchanged.
    # FR: Chaque catégorie documentée doit être acceptée sans modification.
    assert parse_plan(value) == value


def test_empty_plan_is_rejected():
    # EN: A missing plan must not receive an invented default.
    # FR: Un abonnement manquant ne doit pas recevoir une valeur inventée.
    with pytest.raises(ValueError, match="^value is required$"):
        parse_plan("")


@pytest.mark.parametrize(
    "value",
    ["basic", "PREMIUM", " Premium ", "Gold"],
)
def test_unknown_plan_is_rejected(value):
    # EN: Reject incorrect spelling and unsupported categories.
    # FR: Refuser les écritures incorrectes et les catégories non prévues.
    with pytest.raises(
        ValueError,
        match="must be one of: Basic, Standard, Premium",
    ):
        parse_plan(value)

@pytest.mark.parametrize(
    "value, expected",
    [
        ("2026-09-01", date(2026, 9, 1)),
        ("2024-02-01", date(2024, 2, 1)),
    ],
)
def test_valid_csv_month_is_converted(value, expected):
    # EN: Return a date object representing the requested month.
    # FR: Renvoyer un objet date représentant le mois demandé.
    result = parse_csv_month(value)

    assert result == expected
    assert type(result) is date


def test_empty_csv_month_is_rejected():
    # EN: A missing month must not receive a default date.
    # FR: Un mois manquant ne doit pas recevoir une date par défaut.
    with pytest.raises(ValueError, match="^value is required$"):
        parse_csv_month("")


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-15",
        "2026-02-30",
        "2026-13-01",
        "01/09/2026",
        "20260901",
        " 2026-09-01 ",
    ],
)
def test_invalid_csv_month_is_rejected(value):
    # EN: Reject invalid dates, formats and non-first days.
    # FR: Refuser les dates, formats et jours non autorisés.
    with pytest.raises(ValueError, match="observation_month"):
        parse_csv_month(value)


@pytest.mark.parametrize(
    "value",
    ["C000001", "C000025", "C1000000"],
)
def test_valid_customer_id_is_accepted(value):
    # EN: Keep valid identifiers unchanged.
    # FR: Conserver les identifiants valides sans modification.
    assert parse_customer_id(value) == value


def test_empty_customer_id_is_rejected():
    # EN: A customer identifier is mandatory.
    # FR: Un identifiant client est obligatoire.
    with pytest.raises(ValueError, match="^value is required$"):
        parse_customer_id("")


@pytest.mark.parametrize(
    "value",
    ["C1", "c000001", "X000001", "C00001A", " C000001 "],
)
def test_invalid_customer_id_format_is_rejected(value):
    # EN: Reject incorrect prefixes, digits and spacing.
    # FR: Refuser les préfixes, caractères et espaces incorrects.
    with pytest.raises(ValueError, match="must start with C"):
        parse_customer_id(value)


def test_zero_customer_number_is_rejected():
    # EN: Zero does not identify a generated customer.
    # FR: Zéro n'identifie aucun client du générateur.
    with pytest.raises(ValueError, match="must be at least 1"):
        parse_customer_id("C000000")


def test_noncanonical_customer_id_is_rejected():
    # EN: Extra leading zeros must not create an alias for customer 1.
    # FR: Des zéros supplémentaires ne doivent pas créer un alias du client 1.
    with pytest.raises(ValueError, match="canonical format"):
        parse_customer_id("C0000001")

def example_customer_month_row():
    """Return a fresh CSV-like row for each test."""

    # EN: CSV values are text before conversion.
    # FR: Les valeurs CSV sont du texte avant conversion.
    return {
        "customer_id": "C000001",
        "observation_month": "2026-09-01",
        "plan": "Premium",
        "tenure_months": "90",
        "viewing_hours": "4.09",
        "payment_failures": "0",
        "support_requests": "1",
        "cancelled_in_month": "false",
    }


def test_valid_customer_month_is_converted():
    # EN: Check the complete converted observation.
    # FR: Vérifier l'observation convertie dans son ensemble.
    converted, errors = validate_customer_month(
        example_customer_month_row(),
        row_number=2,
    )

    assert errors == []
    assert converted == {
        "customer_id": "C000001",
        "observation_month": date(2026, 9, 1),
        "plan": "Premium",
        "tenure_months": 90,
        "viewing_hours": Decimal("4.09"),
        "payment_failures": 0,
        "support_requests": 1,
        "cancelled_in_month": False,
    }


def test_customer_month_reports_multiple_field_errors():
    # EN: Introduce two independent problems in the same row.
    # FR: Introduire deux problèmes indépendants dans la même ligne.
    row = example_customer_month_row()
    row["tenure_months"] = "-3"
    row["cancelled_in_month"] = ""

    converted, errors = validate_customer_month(row, row_number=7)

    assert converted is None
    assert errors == [
        "Row 7, field 'tenure_months': "
        "must contain only digits 0-9 for a non-negative integer",
        "Row 7, field 'cancelled_in_month': value is required",
    ]


def test_customer_month_validation_preserves_input():
    # EN: Validation must not replace the original CSV text values.
    # FR: La validation ne doit pas remplacer les textes CSV d'origine.
    row = example_customer_month_row()
    original = row.copy()

    validate_customer_month(row, row_number=2)

    assert row == original

def write_example_csv(path, rows):
    """Write small CSV examples for file-validation tests."""

    # EN: Create test files using the same eight column names.
    # FR: Créer les fichiers de test avec les huit colonnes attendues.
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=FIELDNAMES,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def test_complete_valid_csv_is_accepted(tmp_path):
    # EN: Prepare two different customer observations.
    # FR: Préparer les observations de deux clients différents.
    first = example_customer_month_row()
    second = example_customer_month_row()
    second["customer_id"] = "C000002"

    input_path = tmp_path / "valid.csv"
    write_example_csv(input_path, [first, second])

    records, errors = validate_csv_file(input_path)

    assert errors == []
    assert len(records) == 2
    assert records[1]["customer_id"] == "C000002"
    assert records[0]["viewing_hours"] == Decimal("4.09")


def test_one_invalid_row_rejects_the_entire_csv(tmp_path):
    # EN: Place an invalid observation after a valid one.
    # FR: Placer une observation incorrecte après une observation valide.
    first = example_customer_month_row()
    second = example_customer_month_row()
    second["customer_id"] = "C000002"
    second["tenure_months"] = "-3"

    input_path = tmp_path / "invalid.csv"
    write_example_csv(input_path, [first, second])

    records, errors = validate_csv_file(input_path)

    # EN: Even the valid first observation must not be returned.
    # FR: Même la première observation valide ne doit pas être renvoyée.
    assert records == []
    assert errors == [
        "Row 3, field 'tenure_months': "
        "must contain only digits 0-9 for a non-negative integer"
    ]


def test_header_only_csv_is_rejected(tmp_path):
    # EN: A valid header alone is insufficient for a complete import.
    # FR: Un en-tête correct seul ne suffit pas pour un import complet.
    input_path = tmp_path / "header_only.csv"
    write_example_csv(input_path, [])

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert errors == [
        "File: at least one observation is required."
    ]


def test_csv_row_with_missing_values_is_rejected(tmp_path):
    # EN: Supply only two cells under an eight-column header.
    # FR: Fournir seulement deux cellules sous un en-tête de huit colonnes.
    input_path = tmp_path / "short_row.csv"
    content = (
        ",".join(FIELDNAMES)
        + "\nC000001,2026-09-01\n"
    )
    input_path.write_text(content, encoding="utf-8")

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert errors == [
        "Row 2: expected 8 values, got 2."
    ]


def test_csv_validation_preserves_source_file(tmp_path):
    # EN: Compare the file bytes before and after validation.
    # FR: Comparer les octets du fichier avant et après validation.
    input_path = tmp_path / "unchanged.csv"
    write_example_csv(input_path, [example_customer_month_row()])
    original_content = input_path.read_bytes()

    records, errors = validate_csv_file(input_path)

    assert errors == []
    assert len(records) == 1
    assert input_path.read_bytes() == original_content

def test_duplicate_customer_month_is_rejected(tmp_path):
    # EN: Repeat the same customer and month with a different plan.
    # FR: Répéter le même client et le même mois avec un autre abonnement.
    first = example_customer_month_row()
    second = example_customer_month_row()
    second["plan"] = "Basic"

    input_path = tmp_path / "duplicate.csv"
    write_example_csv(input_path, [first, second])

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert errors == [
        "Row 3: duplicate customer-month pair "
        "(C000001, 2026-09-01); first seen at row 2."
    ]


def test_same_customer_in_different_months_is_accepted(tmp_path):
    # EN: The same customer may have observations in different months.
    # FR: Un même client peut avoir des observations sur plusieurs mois.
    first = example_customer_month_row()
    second = example_customer_month_row()
    second["observation_month"] = "2026-10-01"

    input_path = tmp_path / "different_months.csv"
    write_example_csv(input_path, [first, second])

    records, errors = validate_csv_file(input_path)

    assert errors == []
    assert len(records) == 2


def test_duplicate_is_reported_when_first_row_has_another_error(tmp_path):
    # EN: An invalid duration must not hide a repeated valid key.
    # FR: Une durée invalide ne doit pas masquer une clé valide répétée.
    first = example_customer_month_row()
    first["viewing_hours"] = "-3"
    second = example_customer_month_row()

    input_path = tmp_path / "invalid_and_duplicate.csv"
    write_example_csv(input_path, [first, second])

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert len(errors) == 2
    assert errors[0].startswith("Row 2, field 'viewing_hours':")
    assert errors[1] == (
        "Row 3: duplicate customer-month pair "
        "(C000001, 2026-09-01); first seen at row 2."
    )


def test_complete_empty_csv_is_rejected(tmp_path):
    # EN: An empty file has no header and no observations.
    # FR: Un fichier vide ne contient ni en-tête ni observations.
    input_path = tmp_path / "empty.csv"
    input_path.write_text("", encoding="utf-8")

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert errors == ["Header: missing column names."]


def test_blank_row_rejects_complete_csv(tmp_path):
    # EN: Insert a blank row after a valid observation.
    # FR: Insérer une ligne vide après une observation valide.
    input_path = tmp_path / "blank_row.csv"
    write_example_csv(input_path, [example_customer_month_row()])

    with input_path.open("a", encoding="utf-8", newline="") as csv_file:
        csv_file.write("\n")

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert errors == ["Row 3: expected 8 values, got 0."]


def test_extra_value_rejects_complete_csv(tmp_path):
    # EN: A ninth value must not be silently ignored.
    # FR: Une neuvième valeur ne doit pas être ignorée silencieusement.
    input_path = tmp_path / "extra_value.csv"
    row = example_customer_month_row()
    values = [row[field] for field in FIELDNAMES] + ["unexpected"]

    with input_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(FIELDNAMES)
        writer.writerow(values)

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert errors == ["Row 2: expected 8 values, got 9."]


def test_malformed_csv_after_valid_row_returns_no_records(tmp_path):
    # EN: A later parsing error must discard earlier valid results.
    # FR: Une erreur de lecture tardive doit écarter les résultats précédents.
    input_path = tmp_path / "malformed_later.csv"
    write_example_csv(input_path, [example_customer_month_row()])

    with input_path.open("a", encoding="utf-8", newline="") as csv_file:
        csv_file.write('"unclosed field\n')

    records, errors = validate_csv_file(input_path)

    assert records == []
    assert len(errors) == 1
    assert errors[0].startswith("Row 3: malformed CSV:")