"""
EN: Test every status pair and validate status-only requests.
FR: Tester chaque paire de statuts et valider les demandes de statut.
"""

import pytest
from pydantic import ValidationError

from app.retention_action_models import RetentionActionStatusUpdate
from app.retention_action_status import (
    InvalidStatusTransitionError,
    validate_status_transition,
)


STATUSES = (
    "Proposed",
    "In Progress",
    "Completed",
    "Dismissed",
)

# EN: Expected business rules are specified independently of implementation.
# FR: Définir les résultats métier indépendamment de l'implémentation.
EXPECTED_CHANGES = {
    ("Proposed", "In Progress"),
    ("Proposed", "Dismissed"),
    ("In Progress", "Completed"),
    ("In Progress", "Dismissed"),
}


@pytest.mark.parametrize("current_status", STATUSES)
@pytest.mark.parametrize("target_status", STATUSES)
def test_every_status_pair(current_status, target_status):
    if current_status == target_status:
        assert validate_status_transition(
            current_status,
            target_status,
        ) is False

    elif (current_status, target_status) in EXPECTED_CHANGES:
        assert validate_status_transition(
            current_status,
            target_status,
        ) is True

    else:
        with pytest.raises(InvalidStatusTransitionError):
            validate_status_transition(
                current_status,
                target_status,
            )


@pytest.mark.parametrize("status", STATUSES)
def test_request_accepts_each_supported_status(status):
    request = RetentionActionStatusUpdate.model_validate({
        "status": status,
    })

    assert request.model_dump() == {"status": status}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"status": None},
        {"status": ""},
        {"status": "completed"},
        {"status": "Unknown"},
        {"status": " In Progress "},
        {"status": 1},
        {"status": True},
        {"status": []},
        {"status": {}},
    ],
)
def test_request_rejects_missing_or_invalid_status(payload):
    with pytest.raises(ValidationError):
        RetentionActionStatusUpdate.model_validate(payload)


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", "00000000-0000-0000-0000-000000000001"),
        ("created_at", "2026-11-26T00:00:00Z"),
        ("observation_month", "2026-09-01"),
        ("plan", "Premium"),
        ("proposed_action", "Changed proposal"),
        ("rationale", "Changed rationale"),
        ("rule_id", "PLAN_RATE_ABOVE_OVERALL"),
        ("rule_version", 1),
    ],
)
def test_request_rejects_unrelated_fields(field, value):
    with pytest.raises(ValidationError):
        RetentionActionStatusUpdate.model_validate({
            "status": "In Progress",
            field: value,
        })


@pytest.mark.parametrize(
    "current_status,target_status",
    [
        ("Unknown", "Proposed"),
        ("Proposed", "Unknown"),
        ("Unknown", "Unknown"),
    ],
)
def test_transition_rejects_unsupported_statuses(
    current_status,
    target_status,
):
    with pytest.raises(InvalidStatusTransitionError):
        validate_status_transition(
            current_status,
            target_status,
        )