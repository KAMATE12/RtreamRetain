"""
EN: Produce investigation proposals from monthly plan counts.
FR: Produire des propositions d'investigation à partir des effectifs mensuels.
"""

from datetime import date

from app.indicators import calculate_cancellation_rate


RULE_ID = "PLAN_RATE_ABOVE_OVERALL"
RULE_VERSION = 1
PLANS = ("Basic", "Standard", "Premium")


def build_plan_suggestions(
    comparisons: list[dict],
    *,
    observation_month: date,
    plan: str | None = None,
) -> dict:
    """Evaluate one rule using all represented plans from one month."""

    if observation_month.day != 1:
        raise ValueError("observation_month must be the first day of the month")

    if plan is not None and plan not in PLANS:
        raise ValueError("Unsupported subscription plan")

    # EN: Validate counts before calculating the overall reference.
    # FR: Valider les effectifs avant de calculer la référence globale.
    seen = set()

    for group in comparisons:
        group_plan = group["plan"]

        if group_plan not in PLANS or group_plan in seen:
            raise ValueError("Unsupported or duplicate comparison plan")

        seen.add(group_plan)

        calculate_cancellation_rate(
            cohort_size=group["cohort_size"],
            cancellation_count=group["cancellation_count"],
        )

    total_customers = sum(group["cohort_size"] for group in comparisons)
    total_cancellations = sum(
        group["cancellation_count"] for group in comparisons
    )

    overall_rate = calculate_cancellation_rate(
        cohort_size=total_customers,
        cancellation_count=total_cancellations,
    )

    suggestions = []

    for group in sorted(
        comparisons,
        key=lambda item: PLANS.index(item["plan"]),
    ):
        # EN: Filter proposals only; keep the all-plan reference.
        # FR: Filtrer les propositions en conservant la référence globale.
        if plan is not None and group["plan"] != plan:
            continue

        customers = group["cohort_size"]
        cancellations = group["cancellation_count"]

        if customers == 0:
            continue

        # EN: Compare exact fractions without rounded percentages.
        # FR: Comparer les fractions exactes sans pourcentages arrondis.
        if cancellations * total_customers <= total_cancellations * customers:
            continue

        rate = calculate_cancellation_rate(
            cohort_size=customers,
            cancellation_count=cancellations,
        )

        rationale = (
            f"{group['plan']}: {cancellations} of {customers} customers "
            f"requested cancellation ({rate:.2f}%), compared with "
            f"{total_cancellations} of {total_customers} customers "
            f"across all plans ({overall_rate:.2f}%) for "
            f"{observation_month:%Y-%m}. "
            "The rule compares exact counts before display rounding. "
            "Consider cohort size when interpreting this difference. "
            "This is an investigation proposal, not evidence of causation "
            "or statistical significance. All observations are synthetic."
        )

        if customers == 1:
            rationale += " This plan's result is based on one observation."

        suggestions.append(
            {
                "rule_id": RULE_ID,
                "rule_version": RULE_VERSION,
                "plan": group["plan"],
                "cohort_size": customers,
                "cancellation_count": cancellations,
                "cancellation_rate": rate,
                "proposed_action": (
                    f"Investigate possible reasons for cancellation "
                    f"requests in the {group['plan']} cohort."
                ),
                "rationale": rationale,
            }
        )

    return {
        "observation_month": observation_month.isoformat(),
        "plan": plan,
        "reference": {
            "scope": "all_plans",
            "cohort_size": total_customers,
            "cancellation_count": total_cancellations,
            "cancellation_rate": overall_rate,
        },
        "suggestions": suggestions,
    }