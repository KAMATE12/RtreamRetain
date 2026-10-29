"""API health and PostgreSQL readiness endpoints."""

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_engine


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