"""Tests for the monthly plan investigation rule."""

from datetime import date

import pytest

from app.suggestions import build_plan_suggestions


MONTH = date(2026, 9, 1)


def group(plan, customers, cancellations):
    return {
        "plan": plan,
        "cohort_size": customers,
        "cancellation_count": cancellations,
    }


def test_known_dataset_proposes_premium_and_uses_weighted_reference():
    result = build_plan_suggestions(
        [group("Basic", 80, 8), group("Premium", 20, 4)],
        observation_month=MONTH,
    )

    assert result["reference"]["cohort_size"] == 100
    assert result["reference"]["cancellation_count"] == 12
    assert result["reference"]["cancellation_rate"] == 12.0
    assert len(result["suggestions"]) == 1

    suggestion = result["suggestions"][0]
    assert suggestion["plan"] == "Premium"
    assert suggestion["cancellation_rate"] == 20.0
    assert suggestion["rule_id"] == "PLAN_RATE_ABOVE_OVERALL"
    assert suggestion["rule_version"] == 1
    assert "4 of 20" in suggestion["rationale"]
    assert "12 of 100" in suggestion["rationale"]


@pytest.mark.parametrize(
    ("selected_plan", "expected_plans"),
    [
        (None, ["Premium"]),
        ("Premium", ["Premium"]),
        ("Basic", []),
        ("Standard", []),
    ],
)
def test_plan_selection_preserves_all_plan_reference(
    selected_plan, expected_plans
):
    result = build_plan_suggestions(
        [group("Basic", 80, 8), group("Premium", 20, 4)],
        observation_month=MONTH,
        plan=selected_plan,
    )

    assert result["plan"] == selected_plan
    assert result["reference"]["cancellation_rate"] == 12.0
    assert [item["plan"] for item in result["suggestions"]] == expected_plans


@pytest.mark.parametrize(
    "groups",
    [
        [],
        [group("Basic", 0, 0)],
        [group("Basic", 10, 0), group("Premium", 20, 0)],
        [group("Basic", 10, 1), group("Premium", 20, 2)],
        [group("Premium", 20, 4)],
    ],
)
def test_empty_equal_and_single_plan_cases_produce_no_suggestions(groups):
    result = build_plan_suggestions(groups, observation_month=MONTH)

    assert result["suggestions"] == []

    if not groups or sum(item["cohort_size"] for item in groups) == 0:
        assert result["reference"]["cancellation_rate"] is None


def test_decision_does_not_use_display_rounding():
    result = build_plan_suggestions(
        [group("Basic", 100_000, 10_000), group("Premium", 100_000, 10_001)],
        observation_month=MONTH,
    )

    assert [item["plan"] for item in result["suggestions"]] == ["Premium"]


def test_single_customer_proposal_explains_its_small_denominator():
    result = build_plan_suggestions(
        [group("Basic", 99, 0), group("Premium", 1, 1)],
        observation_month=MONTH,
    )

    suggestion = result["suggestions"][0]
    assert suggestion["cancellation_rate"] == 100.0
    assert "based on one observation" in suggestion["rationale"]


def test_inconsistent_counts_are_rejected():
    with pytest.raises(ValueError):
        build_plan_suggestions(
            [group("Basic", 2, 3)],
            observation_month=MONTH,
        )


def test_duplicate_groups_are_rejected():
    with pytest.raises(ValueError):
        build_plan_suggestions(
            [group("Basic", 10, 1), group("Basic", 10, 1)],
            observation_month=MONTH,
        )