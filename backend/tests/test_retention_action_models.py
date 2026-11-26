"""Validate action requests without accessing PostgreSQL."""

from copy import deepcopy
from datetime import date

import pytest
from pydantic import ValidationError

from app.retention_action_models import RetentionActionCreate


@pytest.fixture
def valid_payload():
    return {
        "observation_month": "2026-09-01",
        "plan": "Premium",
        "proposed_action": "Investigate Premium cancellations.",
        "rationale": "Premium has 9 requests among 43 customers.",
        "rule_id": "PLAN_RATE_ABOVE_OVERALL",
        "rule_version": 1,
    }


def test_valid_request_preserves_context(valid_payload):
    result = RetentionActionCreate.model_validate(valid_payload)

    assert result.model_dump() == {
        **valid_payload,
        "observation_month": date(2026, 9, 1),
    }


def test_text_is_trimmed_without_mutating_input(valid_payload):
    valid_payload["proposed_action"] = " \tInvestigate cancellations.\n"
    valid_payload["rationale"] = "  First reason.\nSecond reason.  "
    original = deepcopy(valid_payload)

    result = RetentionActionCreate.model_validate(valid_payload)

    assert result.proposed_action == "Investigate cancellations."
    assert result.rationale == "First reason.\nSecond reason."
    assert valid_payload == original


@pytest.mark.parametrize("plan", ["Basic", "Standard", "Premium"])
def test_supported_plan_scopes_are_accepted(valid_payload, plan):
    result = RetentionActionCreate.model_validate(
        {**valid_payload, "plan": plan}
    )
    assert result.plan == plan


@pytest.mark.parametrize(
    "field,value",
    [
        ("observation_month", "2026-09-15"),
        ("observation_month", "2026-02-30"),
        ("observation_month", "2026-09"),
        ("observation_month", "2026-09-01T00:00:00"),
        ("observation_month", 0),
        ("observation_month", None),
        ("plan", None),
        ("plan", "All plans"),
        ("plan", "premium"),
        ("plan", "Unknown"),
        ("proposed_action", ""),
        ("proposed_action", " \t\n "),
        ("proposed_action", "x" * 1001),
        ("proposed_action", 123),
        ("proposed_action", "Invalid\x00text"),
        ("rationale", ""),
        ("rationale", " \t\n "),
        ("rationale", "x" * 3001),
        ("rationale", None),
        ("rationale", "Invalid\x00text"),
        ("rule_id", "UNKNOWN_RULE"),
        ("rule_id", ""),
        ("rule_version", 0),
        ("rule_version", 2),
        ("rule_version", True),
        ("rule_version", "1"),
        ("rule_version", 1.0),
    ],
)
def test_invalid_values_are_rejected(valid_payload, field, value):
    with pytest.raises(ValidationError) as captured:
        RetentionActionCreate.model_validate(
            {**valid_payload, field: value}
        )

    assert any(
        error["loc"] == (field,)
        for error in captured.value.errors()
    )


@pytest.mark.parametrize(
    "field",
    [
        "observation_month",
        "plan",
        "proposed_action",
        "rationale",
        "rule_id",
        "rule_version",
    ],
)
def test_required_fields_cannot_be_omitted(valid_payload, field):
    payload = {key: value for key, value in valid_payload.items()
               if key != field}

    with pytest.raises(ValidationError) as captured:
        RetentionActionCreate.model_validate(payload)

    assert any(
        error["loc"] == (field,) and error["type"] == "missing"
        for error in captured.value.errors()
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", "client-generated-id"),
        ("created_at", "2026-11-24T12:00:00Z"),
        ("status", "Completed"),
        ("status", "Proposed"),
        ("unexpected", "value"),
    ],
)
def test_extra_fields_are_rejected(valid_payload, field, value):
    with pytest.raises(ValidationError) as captured:
        RetentionActionCreate.model_validate(
            {**valid_payload, field: value}
        )

    assert any(
        error["loc"] == (field,)
        and error["type"] == "extra_forbidden"
        for error in captured.value.errors()
    )


@pytest.mark.parametrize(
    "field,limit",
    [
        ("proposed_action", 1000),
        ("rationale", 3000),
    ],
)
def test_length_limit_is_applied_after_trimming(valid_payload, field, limit):
    result = RetentionActionCreate.model_validate(
        {**valid_payload, field: "  " + "x" * limit + "\n"}
    )

    assert getattr(result, field) == "x" * limit