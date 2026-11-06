"""API endpoints for health, database readiness and monthly indicators."""

from datetime import date

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_engine
from app.indicators import (
    get_available_observation_months,
    get_monthly_indicators,
)

app = FastAPI(title="StreamRetain API", version="0.1.0")


@app.get("/api/health")
def health():
    """Report API availability independently of PostgreSQL."""

    # EN: This endpoint does not query the database.
    # FR: Cette route n'interroge pas la base de données.
    return {"status": "ok", "service": "streamretain-api"}


@app.get("/api/readiness")
def readiness():
    """Check whether PostgreSQL accepts a real query."""

    try:
        # EN: Release the connection automatically after the query.
        # FR: Libérer automatiquement la connexion après la requête.
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))

    except (ValueError, SQLAlchemyError):
        # EN: Return a generic error without exposing credentials.
        # FR: Renvoyer une erreur générique sans exposer les identifiants.
        raise HTTPException(
            status_code=503,
            detail="Database is not ready",
        ) from None

    return {"status": "ready", "database": "connected"}


@app.get("/api/indicators")
def monthly_indicators(
    observation_month: date,
    plan: str | None = None,
):
    """Return monthly indicators with an optional subscription-plan filter."""

    # EN: Require the first day as the observation month's identifier.
    # FR: Exiger le premier jour comme identifiant du mois d'observation.
    if observation_month.day != 1:
        raise HTTPException(
            status_code=422,
            detail="observation_month must be the first day of the month",
        )

    # EN: Reject unsupported plans before accessing the database.
    # FR: Refuser les abonnements non acceptés avant l'accès à la base.
    if plan is not None and plan not in ("Basic", "Standard", "Premium"):
        raise HTTPException(
            status_code=422,
            detail="plan must be Basic, Standard or Premium",
        )

    try:
        # EN: Obtain the engine or report missing configuration.
        # FR: Obtenir le moteur ou signaler une configuration absente.
        engine = get_engine()
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Unable to load indicators",
        ) from None

    try:
        # EN: Read the indicators and release the connection afterwards.
        # FR: Lire les indicateurs puis libérer la connexion.
        with engine.connect() as connection:
            indicators = get_monthly_indicators(
                connection,
                observation_month=observation_month,
                plan=plan,
            )

    except SQLAlchemyError:
        # EN: Hide internal database details from the HTTP response.
        # FR: Masquer les détails internes de la base dans la réponse HTTP.
        raise HTTPException(
            status_code=503,
            detail="Unable to load indicators",
        ) from None

    # EN: Convert the decimal average into a JSON-compatible number.
    # FR: Convertir la moyenne décimale en nombre destiné au JSON.
    average_hours = indicators["average_viewing_hours"]

    return {
        "observation_month": observation_month.isoformat(),
        "cohort_size": indicators["cohort_size"],
        "cancellation_count": indicators["cancellation_count"],
        "cancellation_rate": indicators["cancellation_rate"],
        "average_viewing_hours": (
            float(average_hours) if average_hours is not None else None
        ),
    }


@app.get("/api/observation-months")
def observation_months():
    """Return the observation months available in stored data."""

    try:
        # EN: Obtain the engine or report missing configuration.
        # FR: Obtenir le moteur ou signaler une configuration absente.
        engine = get_engine()
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Unable to load observation months",
        ) from None

    try:
        # EN: Read unique months using the existing database function.
        # FR: Lire les mois uniques avec la fonction de base existante.
        with engine.connect() as connection:
            months = get_available_observation_months(connection)

    except SQLAlchemyError:
        # EN: Report database failure without exposing internal details.
        # FR: Signaler l'échec sans exposer les détails internes.
        raise HTTPException(
            status_code=503,
            detail="Unable to load observation months",
        ) from None

    # EN: Convert each date to its ISO representation for JSON.
    # FR: Convertir chaque date au format ISO pour le JSON.
    return {
        "observation_months": [
            month.isoformat()
            for month in months
        ],
    }
