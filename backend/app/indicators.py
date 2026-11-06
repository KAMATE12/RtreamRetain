"""Calculations for monthly customer indicators."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.engine import Connection

from app.schema import customer_month


def calculate_cancellation_rate(
    *,
    cohort_size: int,
    cancellation_count: int,
) -> float | None:
    """Calculate the rate, rejecting inconsistent or negative counts."""

    # EN: Accept only built-in integers, excluding Boolean values.
    # FR: Accepter uniquement les entiers Python, en excluant les booléens.
    if type(cohort_size) is not int:
        raise TypeError("cohort_size must be an integer")

    if type(cancellation_count) is not int:
        raise TypeError("cancellation_count must be an integer")

    # EN: Reject a negative cohort size.
    # FR: Refuser un effectif de cohorte négatif.
    if cohort_size < 0:
        raise ValueError("cohort_size must be non-negative")

    # EN: Reject a negative cancellation count.
    # FR: Refuser un nombre d'annulations négatif.
    if cancellation_count < 0:
        raise ValueError("cancellation_count must be non-negative")

    # EN: Cancellations cannot exceed the number of cohort customers.
    # FR: Les annulations ne peuvent pas dépasser l'effectif de la cohorte.
    if cancellation_count > cohort_size:
        raise ValueError(
            "cancellation_count cannot exceed cohort_size"
        )

    # EN: An empty cohort has no calculable cancellation rate.
    # FR: Une cohorte vide n'a pas de taux d'annulation calculable.
    if cohort_size == 0:
        return None

    # EN: Convert the proportion of cancellations into a percentage.
    # FR: Convertir la proportion d'annulations en pourcentage.
    return cancellation_count / cohort_size * 100


def get_monthly_indicators(
    connection: Connection,
    *,
    observation_month: date,
    plan: str | None = None,
) -> dict:
    """Read indicators for the selected month's stored cohort."""

    # EN: Calculate all aggregates from the same month's observations.
    # FR: Calculer les agrégats sur les observations du même mois.
    statement = (
        select(
            func.count().label("cohort_size"),
            func.count()
            .filter(customer_month.c.cancelled_in_month.is_(True))
            .label("cancellation_count"),
            func.avg(customer_month.c.viewing_hours)
            .label("average_viewing_hours"),
        )
        .select_from(customer_month)
        .where(
            customer_month.c.observation_month == observation_month
        )
    )

    # EN: Apply the optional plan filter to every aggregate.
    # FR: Appliquer le filtre facultatif d'abonnement à tous les agrégats.
    if plan is not None:
        statement = statement.where(customer_month.c.plan == plan)

    # EN: Read the single aggregate row using its column labels.
    # FR: Lire l'unique ligne de résultats grâce aux noms des colonnes.
    totals = connection.execute(statement).mappings().one()

    # EN: Reuse the tested calculation for the cancellation percentage.
    # FR: Réutiliser le calcul testé du pourcentage d'annulation.
    cancellation_rate = calculate_cancellation_rate(
        cohort_size=totals["cohort_size"],
        cancellation_count=totals["cancellation_count"],
    )

    return {
        "cohort_size": totals["cohort_size"],
        "cancellation_count": totals["cancellation_count"],
        "cancellation_rate": cancellation_rate,
        "average_viewing_hours": totals["average_viewing_hours"],
    }


def get_available_observation_months(
    connection: Connection,
) -> list[date]:
    """Return stored observation months, unique and newest first."""

    # EN: Select each stored month once, ordered from newest to oldest.
    # FR: Sélectionner chaque mois une fois, du plus récent au plus ancien.
    statement = (
        select(customer_month.c.observation_month)
        .distinct()
        .order_by(customer_month.c.observation_month.desc())
    )

    # EN: Return date values rather than rows containing one column.
    # FR: Renvoyer les dates plutôt que des lignes contenant une colonne.
    return list(connection.execute(statement).scalars().all())
