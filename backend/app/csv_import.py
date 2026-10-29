"""Store validated customer-month observations without overwriting data."""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from app.schema import customer, customer_month

import argparse
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.csv_validation import validate_csv_file
from app.database import get_engine


class ObservationConflictError(ValueError):
    """An existing customer-month observation has different values."""


def store_validated_records(
    connection: Connection,
    records: list[dict],
) -> dict[str, int]:
    """Store validated records inside a transaction managed by the caller."""

    # EN: Require an active transaction before any write.
    # FR: Exiger une transaction active avant toute écriture.
    if not connection.in_transaction():
        raise RuntimeError("An active transaction is required.")

    inserted = 0
    unchanged = 0

    for record in records:
        customer_id = record["customer_id"]
        observation_month = record["observation_month"]

        # EN: Create the customer only if it does not already exist.
        # FR: Créer le client uniquement s'il n'existe pas déjà.
        customer_statement = (
            insert(customer)
            .values(customer_id=customer_id)
            .on_conflict_do_nothing(
                index_elements=[customer.c.customer_id],
            )
        )
        connection.execute(customer_statement)

        # EN: Try to insert the observation without overwriting an existing one.
        # FR: Tenter l'insertion sans écraser une observation existante.
        observation_statement = (
            insert(customer_month)
            .values(**record)
            .on_conflict_do_nothing(
                index_elements=[
                    customer_month.c.customer_id,
                    customer_month.c.observation_month,
                ],
            )
            .returning(customer_month.c.customer_id)
        )

        inserted_id = connection.execute(
            observation_statement
        ).scalar_one_or_none()

        # EN: RETURNING produces an identifier only when insertion occurred.
        # FR: RETURNING fournit un identifiant uniquement en cas d'insertion.
        if inserted_id is not None:
            inserted += 1
            continue

        # EN: Read and lock the existing observation for comparison.
        # FR: Lire et verrouiller l'observation existante pour la comparaison.
        existing_statement = (
            select(customer_month)
            .where(
                customer_month.c.customer_id == customer_id,
                customer_month.c.observation_month == observation_month,
            )
            .with_for_update()
        )

        existing = connection.execute(
            existing_statement
        ).mappings().one()

        # EN: Identify exactly which validated fields differ.
        # FR: Identifier précisément les champs validés qui diffèrent.
        different_fields = [
            column.name
            for column in customer_month.columns
            if existing[column.name] != record[column.name]
        ]

        if different_fields:
            # EN: Stop immediately; the caller must roll back the import.
            # FR: Arrêter immédiatement ; l'appelant doit annuler l'import.
            raise ObservationConflictError(
                f"Conflict for customer-month "
                f"({customer_id}, {observation_month.isoformat()}): "
                f"different fields: {', '.join(different_fields)}."
            )

        unchanged += 1

    # EN: These counts become final only after the transaction is committed.
    # FR: Ces compteurs deviennent définitifs après validation de la transaction.
    return {
        "inserted": inserted,
        "unchanged": unchanged,
    }

def main(argv: list[str] | None = None) -> int:
    """Validate a complete CSV, then import it in one transaction."""

    parser = argparse.ArgumentParser(
        description="Import validated customer-month CSV data into PostgreSQL.",
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to the customer-month CSV file.",
    )
    args = parser.parse_args(argv)

    # EN: Validate the entire file before opening a database connection.
    # FR: Valider tout le fichier avant d'ouvrir une connexion à la base.
    records, errors = validate_csv_file(args.input_path)

    if errors:
        print("Import rejected: CSV validation failed.")
        for error in errors:
            print(f"- {error}")

        print("No database writes were attempted.")
        return 1

    try:
        # EN: Commit only if every observation is processed successfully.
        # FR: Valider la transaction uniquement si toutes les observations passent.
        with get_engine().begin() as connection:
            result = store_validated_records(connection, records)

        # EN: The transaction has committed before these results are printed.
        # FR: La transaction est validée avant l'affichage de ces résultats.

    except ObservationConflictError as error:
        # EN: The exception has left the transaction block, triggering rollback.
        # FR: L'exception est sortie du bloc transactionnel, déclenchant l'annulation.
        print(f"Import rejected: {error}")
        print("The import transaction was rolled back.")
        return 1

    except (ValueError, SQLAlchemyError):
        # EN: Do not display database exceptions or connection credentials.
        # FR: Ne pas afficher les exceptions SQL ni les identifiants de connexion.
        print(
            "Import failed: database operation could not be completed. "
            "Check PostgreSQL availability, configuration, schema "
            "and database storage limits."
        )
        return 1

    print("Import successful.")
    print(f"Inserted observations: {result['inserted']}")
    print(f"Unchanged observations: {result['unchanged']}")
    return 0


if __name__ == "__main__":
    # EN: Return the command's exit code to the terminal.
    # FR: Transmettre le code de sortie de la commande au terminal.
    raise SystemExit(main())