"""Shared PostgreSQL connection configuration."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


# EN: Load local configuration from the repository root.
# FR: Charger la configuration locale depuis la racine du dépôt.
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

@lru_cache
def get_engine() -> Engine:
    """Create and reuse the SQLAlchemy engine."""

    # EN: Read the connection URL without displaying its credentials.
    # FR: Lire l'URL de connexion sans afficher ses identifiants.
    url = os.getenv("DATABASE_URL")

    if not url:
        raise ValueError("DATABASE_URL is missing")

    # EN: Check pooled connections before reuse and limit connection time.
    # FR: Vérifier les connexions réutilisées et limiter le délai de connexion.
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3},
    )