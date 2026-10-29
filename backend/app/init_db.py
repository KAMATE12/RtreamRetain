"""Create missing project tables without deleting existing data."""

from sqlalchemy.exc import SQLAlchemyError

from app.database import get_engine
from app.schema import metadata


def main() -> int:
    """Create the schema and return a command-line exit code."""

    try:
        # EN: Group schema creation operations in one transaction.
        # FR: Regrouper les opérations de création dans une transaction.
        with get_engine().begin() as connection:

            # EN: Create missing tables in dependency order.
            # FR: Créer les tables manquantes dans l'ordre des dépendances.
            metadata.create_all(
                bind=connection,
                checkfirst=True,
            )

    except (ValueError, SQLAlchemyError):
        # EN: Hide technical details that might contain credentials.
        # FR: Masquer les détails techniques pouvant contenir des identifiants.
        print(
            "Database initialization failed. "
            "Check the local configuration and PostgreSQL availability."
        )
        return 1

    # EN: This message also applies when the tables already existed.
    # FR: Ce message convient aussi lorsque les tables existaient déjà.
    print("Database initialization successful.")
    print("Required tables are present: customer, customer_month.")
    print("No existing data was deleted.")
    return 0


if __name__ == "__main__":
    # EN: Return the result to the calling terminal.
    # FR: Transmettre le résultat au terminal appelant.
    raise SystemExit(main())