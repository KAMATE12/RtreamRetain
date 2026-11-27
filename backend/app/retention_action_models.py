"""
EN: Validate requests for creating reviewed retention proposals.
FR: Valider les demandes de création de propositions examinées.
"""

from datetime import date
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.suggestions import RULE_ID, RULE_VERSION


class RetentionActionCreate(BaseModel):
    """Fields the manager may submit when saving a reviewed suggestion."""

    # EN: Reject extra fields, including client-supplied status and identifiers.
    # FR: Refuser les champs supplémentaires, dont statut et identifiant.
    model_config = ConfigDict(extra="forbid")

    observation_month: date
    plan: Literal["Basic", "Standard", "Premium"]

    proposed_action: str = Field(
        strict=True,
        min_length=1,
        max_length=1000,
    )
    rationale: str = Field(
        strict=True,
        min_length=1,
        max_length=3000,
    )
    rule_id: str = Field(
        strict=True,
        min_length=1,
        max_length=100,
    )
    rule_version: int = Field(strict=True, ge=1)

    @field_validator("observation_month", mode="before")
    @classmethod
    def require_iso_date(cls, value):
        # EN: Accept a date object or an exact YYYY-MM-DD string.
        # FR: Accepter une date ou une chaîne exacte AAAA-MM-JJ.
        if type(value) is date:
            return value

        if (
            isinstance(value, str)
            and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)
        ):
            return value

        raise ValueError("observation_month must use YYYY-MM-DD")

    @field_validator("observation_month")
    @classmethod
    def require_first_day(cls, value):
        if value.day != 1:
            raise ValueError(
                "observation_month must be the first day of the month"
            )
        return value

    @field_validator("proposed_action", "rationale", mode="before")
    @classmethod
    def normalize_reviewed_text(cls, value):
        # EN: Trim before checking length; preserve internal formatting.
        # FR: Retirer les espaces externes avant de vérifier la longueur.
        if isinstance(value, str):
            if "\x00" in value:
                raise ValueError("Text must not contain null characters")
            return value.strip()

        return value

    @field_validator("rule_id")
    @classmethod
    def require_supported_rule(cls, value):
        if value != RULE_ID:
            raise ValueError("Unsupported source rule")
        return value

    @field_validator("rule_version")
    @classmethod
    def require_supported_version(cls, value):
        if value != RULE_VERSION:
            raise ValueError("Unsupported source rule version")
        return value

class RetentionActionStatusUpdate(BaseModel):
    """Validate a request that changes only an action's status."""

    # EN: Reject unrelated fields, even if their values are unchanged.
    # FR: Refuser les autres champs, même si leurs valeurs sont inchangées.
    model_config = ConfigDict(extra="forbid")

    status: Literal[
        "Proposed",
        "In Progress",
        "Completed",
        "Dismissed",
    ]