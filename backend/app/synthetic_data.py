"""Generate synthetic customer data for StreamRetain."""
from datetime import date

from random import Random

import argparse

import csv
from pathlib import Path

PLANS = ("Basic", "Standard", "Premium")

# EN: Keep a fixed column order for reproducible CSV output.
# FR: Fixer l'ordre des colonnes pour obtenir un CSV reproductible.
FIELDNAMES = (
    "customer_id",
    "observation_month",
    "plan",
    "tenure_months",
    "viewing_hours",
    "payment_failures",
    "support_requests",
    "cancelled_in_month",
)

def make_customer_id(customer_number: int) -> str:
    """Return a synthetic identifier for a positive integer."""

    # Reject invalid types, including Boolean values.
    if type(customer_number) is not int:
        raise TypeError("customer_number must be an integer")

    # Customer numbering starts at 1.
    if customer_number < 1:
        raise ValueError("customer_number must be at least 1")

    return f"C{customer_number:06d}"

def parse_observation_month(value: str) -> date:
    """Parse a month represented by its first calendar day."""

    if not isinstance(value, str):
        raise TypeError("observation_month must be a string")

    try:
        month = date.fromisoformat(value)
    except ValueError:
        raise ValueError(
            "observation_month must be a valid date in YYYY-MM-DD format"
        ) from None

    if month.isoformat() != value:
        raise ValueError(
            "observation_month must use the exact YYYY-MM-DD format"
        )

    if month.day != 1:
        raise ValueError(
            "observation_month must be the first day of the month"
        )

    return month

def generate_customer_month(
    customer_number: int,
    observation_month: str,
    rng: Random,
) -> dict[str, str | int | bool]:
    """Generate one fictional customer-month observation."""

    customer_id = make_customer_id(customer_number)
    month = parse_observation_month(observation_month)

    plan = rng.choice(PLANS)
    tenure_months = rng.randint(0, 60)
    viewing_hundredths = rng.randint(0, 12000)
    payment_failures = rng.randint(0, 3)
    support_requests = rng.randint(0, 5)
    cancelled_in_month = rng.random() < 0.20

    viewing_hours = (
        f"{viewing_hundredths // 100}."
        f"{viewing_hundredths % 100:02d}"
    )

    return {
        "customer_id": customer_id,
        "observation_month": month.isoformat(),
        "plan": plan,
        "tenure_months": tenure_months,
        "viewing_hours": viewing_hours,
        "payment_failures": payment_failures,
        "support_requests": support_requests,
        "cancelled_in_month": cancelled_in_month,
    }

def generate_dataset(
    customer_count: int = 100,
    observation_month: str = "2026-09-01",
    seed: int = 42,
) -> list[dict[str, str | int | bool]]:
    """Generate a reproducible list of customer-month records."""

    # EN: Require a genuine integer, excluding True and False.
    # FR: Exiger un entier, sans accepter les booléens.
    if type(customer_count) is not int:
        raise TypeError("customer_count must be an integer")

    # EN: This generator creates at least one customer.
    # FR: Ce générateur doit produire au moins un client.
    if customer_count < 1:
        raise ValueError("customer_count must be at least 1")

    # EN: Restrict the seed to an integer for a clear configuration.
    # FR: Limiter la graine à un entier pour simplifier la configuration.
    if type(seed) is not int:
        raise TypeError("seed must be an integer")

    # EN: Check the month before generating any records.
    # FR: Vérifier le mois avant de commencer les tirages.
    parse_observation_month(observation_month)

    # EN: Initialise one random generator for the entire dataset.
    # FR: Initialiser un seul générateur pour tout le jeu de données.
    # Do not recreate it inside the loop.
    # Ne pas le recréer à chaque passage dans la boucle.
    rng = Random(seed)

    # EN: Collect the generated records in their creation order.
    # FR: Conserver les observations dans leur ordre de création.
    records = []

    # EN: range excludes its upper bound, hence customer_count + 1.
    # FR: La borne supérieure est exclue, d'où customer_count + 1.
    for customer_number in range(1, customer_count + 1):

        # EN: Generate one observation using the next random draws.
        # FR: Générer une observation avec les tirages suivants.
        record = generate_customer_month(
            customer_number=customer_number,
            observation_month=observation_month,
            rng=rng,
        )

        # EN: Add this customer's observation to the list.
        # FR: Ajouter l'observation de ce client à la liste.
        records.append(record)

    # EN: Return the complete list to the calling code.
    # FR: Renvoyer la liste complète au code qui appelle la fonction.
    return records

def write_dataset_csv(
    records: list[dict[str, str | int | bool]],
    output_path: Path,
) -> None:
    """Write generated records to a new UTF-8 CSV file."""

    # EN: Create the destination directory if necessary.
    # FR: Créer le dossier de destination s'il n'existe pas.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # EN: Exclusive creation prevents overwriting an existing file.
    # FR: Le mode "x" empêche d'écraser un fichier existant.
    # EN: Let the CSV writer control line endings.
    # FR: Laisser le module CSV gérer les fins de ligne.
    with output_path.open(
        mode="x",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        # EN: Map dictionary keys to the fixed CSV columns.
        # FR: Associer les clés des dictionnaires aux colonnes fixées.
        writer = csv.DictWriter(
            csv_file,
            fieldnames=FIELDNAMES,
            lineterminator="\n",
        )

        # EN: Write the column names once.
        # FR: Écrire les noms des colonnes une seule fois.
        writer.writeheader()

        for record in records:
            # EN: Copy the record to preserve the original Python values.
            # FR: Copier l'observation pour préserver les valeurs d'origine.
            csv_record = record.copy()

            # EN: Convert Python booleans to the agreed CSV spelling.
            # FR: Convertir les booléens Python au format prévu pour le CSV.
            csv_record["cancelled_in_month"] = (
                "true" if record["cancelled_in_month"] else "false"
            )

            # EN: Write one customer's monthly observation.
            # FR: Écrire l'observation mensuelle d'un client.
            writer.writerow(csv_record)


def main() -> int:
    """Read command-line options and generate a synthetic CSV."""

    # EN: Describe the command and provide automatic --help.
    # FR: Décrire la commande et fournir automatiquement --help.
    parser = argparse.ArgumentParser(
        description="Generate reproducible synthetic customer-month data."
    )

    # EN: Convert numeric command-line values into integers.
    # FR: Convertir les valeurs numériques de la commande en entiers.
    parser.add_argument(
        "--customers",
        type=int,
        default=100,
        help="Number of customers to generate (default: 100).",
    )
    parser.add_argument(
        "--month",
        default="2026-09-01",
        help="Observation month as YYYY-MM-01 (default: 2026-09-01).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42).",
    )

    # EN: An optional destination; relative paths use the current directory.
    # FR: Destination facultative ; un chemin relatif part du dossier courant.
    parser.add_argument(
        "--output",
        type=Path,
        help="Output CSV path. Existing files are never overwritten.",
    )

    # EN: Read the options supplied when launching the program.
    # FR: Lire les options fournies au lancement du programme.
    args = parser.parse_args()

    try:
        # EN: Validate configuration and generate the observations.
        # FR: Valider les paramètres puis générer les observations.
        records = generate_dataset(
            customer_count=args.customers,
            observation_month=args.month,
            seed=args.seed,
        )

        # EN: Use an explicit destination when provided.
        # FR: Utiliser la destination indiquée lorsqu'elle est fournie.
        if args.output is not None:
            output_path = args.output
        else:
            # EN: Build the default destination from the selected month.
            # FR: Construire le chemin par défaut à partir du mois choisi.
            project_root = Path(__file__).resolve().parents[2]
            output_path = (
                project_root
                / "data"
                / f"synthetic_customer_month_{args.month[:7]}.csv"
            )

        write_dataset_csv(records, output_path)

    except FileExistsError:
        # EN: Report the refusal and exit with a nonzero status.
        # FR: Signaler le refus et terminer avec un code d'échec.
        parser.exit(
            status=1,
            message=f"Error: file already exists: {output_path}\n",
        )

    except (TypeError, ValueError) as error:
        # EN: Explain invalid configuration; argparse exits with code 2.
        # FR: Expliquer les paramètres invalides ; sortie avec le code 2.
        parser.error(str(error))

    except OSError as error:
        # EN: Report filesystem problems, such as insufficient permissions.
        # FR: Signaler les problèmes de fichiers, comme un accès refusé.
        parser.exit(
            status=1,
            message=f"Error: could not write CSV: {error}\n",
        )

    # EN: Display success only after the CSV has been written and closed.
    # FR: Afficher le succès après l'écriture et la fermeture du CSV.
    print("Generated records:", len(records))
    print("CSV created:", output_path.resolve())
    return 0


if __name__ == "__main__":
    # EN: Pass the command's exit status to the operating system.
    # FR: Transmettre le code de sortie au système d'exploitation.
    raise SystemExit(main())