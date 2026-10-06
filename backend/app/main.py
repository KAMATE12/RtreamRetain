"""Sprint 1: API availability and database connectivity only."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
app = FastAPI(title="StreamRetain API", version="0.1.0")


@lru_cache
def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is missing")
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 3})


@app.get("/api/health")
def health():
    """A live Python process is not proof that PostgreSQL is available."""
    return {"status": "ok", "service": "streamretain-api"}


@app.get("/api/readiness")
def readiness():
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except (ValueError, SQLAlchemyError):
        raise HTTPException(status_code=503, detail="Database is not ready") from None
    return {"status": "ready", "database": "connected"}
