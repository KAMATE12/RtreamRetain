"""Validate customer-month CSV input for StreamRetain."""

from collections import Counter

from app.synthetic_data import (
    FIELDNAMES,
    PLANS,
    make_customer_id,
    parse_observation_month,
)

import csv
from pathlib import Path

import re
from decimal import Decimal

from datetime import date

import argparse


def validate_header(header: list[str] | None) -> list[str]:
    """Return header errors; an empty list means no header errors."""

    # EN: No first row means there is no usable header.
    # FR: Sans première ligne, aucun en-tête utilisable n'est présent.
    if not header:
        return ["Header: missing column names."]

    # EN: Collect problems so the user can correct several at once.
    # FR: Regrouper les problèmes pour permettre plusieurs corrections.
    errors: list[str] = []

    # EN: Count how often each column name occurs.
    # FR: Compter le nombre d'apparitions de chaque nom de colonne.
    counts = Counter(header)

    # EN: Check duplicates before converting rows to dictionaries.
    # FR: Vérifier les répétitions avant de créer des dictionnaires.
    for name, count in counts.items():
        if count > 1:
            errors.append(
                f"Header: duplicate column {name!r}."
            )

    # EN: Report required columns that are absent.
    # FR: Signaler les colonnes obligatoires absentes.
    for name in FIELDNAMES:
        if name not in counts:
            errors.append(
                f"Header: missing required column {name!r}."
            )

    # EN: Reject unknown names, including empty or misspelled names.
    # FR: Refuser les noms inconnus, vides ou mal orthographiés.
    for name in counts:
        if name not in FIELDNAMES:
            errors.append(
                f"Header: unexpected column {name!r}."
            )

    return errors

def validate_csv_header(input_path: Path) -> list[str]:
    """Read and validate only the header of a CSV file."""

    try:
        # EN: Read the file without modifying its contents.
        # FR: Lire le fichier sans modifier son contenu.
        # EN: Let the CSV reader handle line endings.
        # FR: Laisser le lecteur CSV gérer les fins de ligne.
        with input_path.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as csv_file:

            # EN: Use commas and report detected CSV syntax errors.
            # FR: Utiliser les virgules et signaler les erreurs CSV détectées.
            reader = csv.reader(csv_file, delimiter=",", strict=True)

            # EN: Read the first record; use None if the file is empty.
            # FR: Lire le premier enregistrement ; utiliser None si vide.
            header = next(reader, None)

            # EN: Reuse our existing column-name validation.
            # FR: Réutiliser notre validation des noms de colonnes.
            return validate_header(header)

    except UnicodeDecodeError:
        # EN: Reject files that cannot be decoded as UTF-8.
        # FR: Refuser les fichiers impossibles à décoder en UTF-8.
        return ["File: cannot decode the input as UTF-8."]

    except csv.Error as error:
        # EN: Explain a CSV parsing error encountered in the header.
        # FR: Expliquer une erreur de lecture CSV dans l'en-tête.
        return [f"Header: malformed CSV: {error}."]

    except OSError as error:
        # EN: Report missing files, access problems and other I/O errors.
        # FR: Signaler les fichiers absents et les problèmes d'accès.
        return [f"File: cannot read input: {error}."]

def parse_non_negative_integer(value: str) -> int:
    """Validate CSV integer text and return its numeric value."""

    # EN: Reject an empty cell instead of replacing it with zero.
    # FR: Refuser une cellule vide au lieu de la remplacer par zéro.
    if value == "":
        raise ValueError("value is required")

    # EN: Accept only ASCII digits, without signs or whitespace.
    # FR: Accepter uniquement les chiffres ASCII, sans signe ni espace.
    if not value.isascii() or not value.isdecimal():
        raise ValueError(
            "must contain only digits 0-9 for a non-negative integer"
        )

    # EN: Convert the validated text into a Python integer.
    # FR: Convertir le texte validé en entier Python.
    return int(value)

def parse_csv_boolean(value: str) -> bool:
    """Convert the exact CSV texts 'true' and 'false' to booleans."""

    # EN: Missing information is different from a false value.
    # FR: Une information manquante est différente de la valeur faux.
    if value == "":
        raise ValueError("value is required")

    # EN: Convert the explicitly accepted true value.
    # FR: Convertir la valeur vraie explicitement autorisée.
    if value == "true":
        return True

    # EN: Convert the explicitly accepted false value.
    # FR: Convertir la valeur fausse explicitement autorisée.
    if value == "false":
        return False

    # EN: Reject any other spelling instead of guessing its meaning.
    # FR: Refuser toute autre écriture sans deviner sa signification.
    raise ValueError("must be exactly 'true' or 'false'")

def parse_viewing_hours(value: str) -> Decimal:
    """Parse a non-negative duration written in decimal notation."""

    # EN: Missing viewing information must not become zero.
    # FR: Une durée manquante ne doit pas devenir zéro.
    if value == "":
        raise ValueError("value is required")

    # EN: Require digits, optionally followed by a decimal fraction.
    # FR: Exiger des chiffres, avec une partie décimale facultative.
    if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value) is None:
        raise ValueError(
            "must be a non-negative finite decimal, "
            "using digits and an optional dot"
        )

    # EN: Preserve the exact decimal value supplied in the CSV.
    # FR: Conserver la valeur décimale exacte fournie dans le CSV.
    return Decimal(value)

def parse_plan(value: str) -> str:
    """Validate a subscription plan and return its unchanged name."""

    # EN: A subscription plan is required.
    # FR: La formule d'abonnement est obligatoire.
    if value == "":
        raise ValueError("value is required")

    # EN: Accept only the categories shared with the generator.
    # FR: Accepter uniquement les catégories partagées avec le générateur.
    if value not in PLANS:
        raise ValueError(
            "must be one of: " + ", ".join(PLANS)
        )

    # EN: Keep the validated name unchanged.
    # FR: Conserver le nom validé sans le modifier.
    return value

def parse_csv_month(value: str) -> date:
    """Validate a CSV observation month and return a date."""

    # EN: Report missing information explicitly.
    # FR: Signaler explicitement une information manquante.
    if value == "":
        raise ValueError("value is required")

    # EN: Reuse the generator's date-format and calendar checks.
    # FR: Réutiliser les contrôles de format et de calendrier du générateur.
    return parse_observation_month(value)

def parse_customer_id(value: str) -> str:
    """Validate the canonical synthetic customer identifier."""

    # EN: Every observation must identify its customer.
    # FR: Chaque observation doit identifier son client.
    if value == "":
        raise ValueError("value is required")

    # EN: Require uppercase C followed by at least six ASCII digits.
    # FR: Exiger C majuscule suivi d'au moins six chiffres ASCII.
    if re.fullmatch(r"C[0-9]{6,}", value) is None:
        raise ValueError(
            "must start with C followed by at least six digits 0-9"
        )

    # EN: Read the numeric part after the initial C.
    # FR: Lire la partie numérique située après le C initial.
    customer_number = int(value[1:])

    # EN: Customer numbering starts at one.
    # FR: La numérotation des clients commence à un.
    if customer_number < 1:
        raise ValueError("customer number must be at least 1")

    # EN: Reject alternative spellings of the same identifier.
    # FR: Refuser les écritures alternatives du même identifiant.
    if value != make_customer_id(customer_number):
        raise ValueError(
            "must use the canonical format, for example C000001"
        )

    return value

def validate_customer_month(
    row: dict[str, str],
    row_number: int,
) -> tuple[dict[str, str | int | bool | date | Decimal] | None, list[str]]:
    """Validate one row whose column structure has already been checked."""

    # EN: Associate each field with its validation function.
    # FR: Associer chaque champ à sa fonction de validation.
    parsers = {
        "customer_id": parse_customer_id,
        "observation_month": parse_csv_month,
        "plan": parse_plan,
        "tenure_months": parse_non_negative_integer,
        "viewing_hours": parse_viewing_hours,
        "payment_failures": parse_non_negative_integer,
        "support_requests": parse_non_negative_integer,
        "cancelled_in_month": parse_csv_boolean,
    }

    # EN: Build a new record without changing the input dictionary.
    # FR: Construire une observation sans modifier le dictionnaire reçu.
    converted = {}
    errors = []

    for field, parser in parsers.items():
        try:
            # EN: Validate and convert this field's text.
            # FR: Valider et convertir le texte de ce champ.
            converted[field] = parser(row[field])

        except ValueError as error:
            # EN: Locate the problem and continue checking other fields.
            # FR: Localiser le problème et vérifier les autres champs.
            errors.append(
                f"Row {row_number}, field {field!r}: {error}"
            )

    # EN: Never return a partially validated observation.
    # FR: Ne jamais renvoyer une observation partiellement validée.
    if errors:
        return None, errors

    return converted, []

def validate_csv_file(
    input_path: Path,
) -> tuple[list[dict[str, str | int | bool | date | Decimal]], list[str]]:
    """Validate CSV structure and values without writing to a database."""

    records = []
    errors = []
    # EN: Remember the first row for each customer-month pair.
    # FR: Mémoriser la première ligne de chaque couple client-mois.
    seen_pairs = {}
    observation_count = 0
    row_number = 1

    try:
        # EN: Open the source file for reading only.
        # FR: Ouvrir le fichier source uniquement en lecture.
        with input_path.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            reader = csv.reader(csv_file, delimiter=",", strict=True)

            # EN: Validate column names before processing observations.
            # FR: Vérifier les colonnes avant de traiter les observations.
            header = next(reader, None)
            header_errors = validate_header(header)

            if header_errors:
                return [], header_errors

            while True:
                # EN: Locate the physical line where the next record starts.
                # FR: Repérer la ligne physique où commence l'enregistrement.
                row_number = reader.line_num + 1
                values = next(reader, None)

                # EN: None means the end of the file, not a blank row.
                # FR: None indique la fin du fichier, pas une ligne vide.
                if values is None:
                    break

                observation_count += 1

                # EN: Check the width before pairing names with values.
                # FR: Vérifier la largeur avant d'associer noms et valeurs.
                if len(values) != len(header):
                    errors.append(
                        f"Row {row_number}: expected {len(header)} values, "
                        f"got {len(values)}."
                    )
                    continue

                # EN: Associate each value with its actual column name.
                # FR: Associer chaque valeur au nom de sa colonne.
                row = dict(zip(header, values))

                converted, row_errors = validate_customer_month(
                    row,
                    row_number=row_number,
                )

                # EN: Collect individual error messages from this row.
                # FR: Regrouper les messages d'erreur de cette observation.
                errors.extend(row_errors)

                # EN: Check duplicates whenever both key fields are valid.
                # FR: Vérifier les doublons si les deux champs de clé sont valides.
                try:
                    customer_id = parse_customer_id(row["customer_id"])
                    month = parse_csv_month(row["observation_month"])
                except ValueError:
                    # EN: These field errors have already been reported.
                    # FR: Les erreurs de ces champs ont déjà été signalées.
                    continue

                pair = (customer_id, month)

                if pair in seen_pairs:
                    first_row = seen_pairs[pair]
                    errors.append(
                        f"Row {row_number}: duplicate customer-month pair "
                        f"({customer_id}, {month.isoformat()}); "
                        f"first seen at row {first_row}."
                    )
                    continue

                # EN: Record the first occurrence, even if another field is invalid.
                # FR: Noter la première occurrence même si un autre champ est invalide.
                seen_pairs[pair] = row_number

                if converted is not None:
                    records.append(converted)



    except UnicodeDecodeError:
        errors.append("File: cannot decode the input as UTF-8.")

    except csv.Error as error:
        errors.append(f"Row {row_number}: malformed CSV: {error}.")

    except OSError as error:
        errors.append(f"File: cannot read input: {error}.")

    # EN: Reject a header-only file after an otherwise successful read.
    # FR: Refuser un fichier sans observations après une lecture sans erreur.
    if observation_count == 0 and not errors:
        errors.append("File: at least one observation is required.")

    # EN: Reject the entire file if any error was detected.
    # FR: Refuser le fichier entier si une erreur a été détectée.
    if errors:
        return [], errors

    return records, []

def main() -> int:
    """Validate a CSV supplied on the command line."""

    # EN: Describe the command and provide automatic --help.
    # FR: Décrire la commande et fournir automatiquement --help.
    parser = argparse.ArgumentParser(
        description="Validate StreamRetain customer-month CSV files."
    )

    # EN: Require the path of the CSV to validate.
    # FR: Exiger le chemin du CSV à valider.
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to the customer-month CSV file.",
    )

    args = parser.parse_args()

    # EN: Read and validate the entire file without importing it.
    # FR: Lire et valider tout le fichier sans l'importer.
    records, errors = validate_csv_file(args.input_path)

    if errors:
        # EN: Display every collected error and report failure.
        # FR: Afficher les erreurs collectées et signaler l'échec.
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    # EN: Report success only when the complete file passes.
    # FR: Signaler la réussite seulement si tout le fichier est valide.
    print("Validation successful.")
    print("Validated records:", len(records))
    print("No data was written to the database.")
    return 0


if __name__ == "__main__":
    # EN: Send the command's exit status to the operating system.
    # FR: Transmettre le code de sortie de la commande au système.
    raise SystemExit(main())