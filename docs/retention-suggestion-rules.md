# Retention suggestion rules

Project: StreamRetain

Task: E4-01 — Transparent suggestion rules, issue #23

Sprint: Sprint 4 — November 16–29, 2026

Status: implemented and locally verified; publication and CI evidence pending.

## Purpose

Help the retention manager identify subscription-plan cohorts worth
investigating using an explicit, explainable rule.

Suggestions are investigation proposals, not proven retention solutions.
All observations are synthetic.

Reviewing a suggestion does not save an action.
Action creation and tracking belong to E4-02 and E4-03.

## Implemented rule

Identifier: `PLAN_RATE_ABOVE_OVERALL`

Version: `1`

One rule is implemented in this version.

For the selected observation month, propose an investigation for each
eligible subscription plan whose cancellation-request rate is strictly
greater than the overall rate across all represented plans.

The overall reference includes the evaluated plan itself.
It is not a comparison against the other plans alone.

This is an educational heuristic. Its usefulness for real retention
decisions has not been validated.

## Inputs and definitions

The rule uses the existing monthly cohort definitions:

- Subscription plan at the beginning of the observation month.
- Beginning-of-month cohort size.
- Number of customers who requested cancellation during that month.

Customers who requested cancellation during the month remain included
in the beginning-of-month denominator.

For a non-empty cohort:

`cancellation rate = cancellation count / cohort size * 100`

For an empty cohort, the rate is unavailable and represented as `null`.

The overall reference uses combined counts:

`overall rate = total cancellation count / total cohort size * 100`

It is not the unweighted average of subscription-plan rates.

## Exact decision and display precision

Let:

- `c` be the plan cancellation count.
- `n` be the plan cohort size.
- `C` be the overall cancellation count.
- `N` be the overall cohort size.

For a non-empty plan cohort, the rule triggers when:

`c * N > C * n`

Integer cross-multiplication avoids making the decision from rounded
percentages.

Equal rates do not trigger the rule.

Numeric rates in the interface use up to two decimal places.
The backend-generated rationale formats rates with two decimal places.

Very small differences may therefore disappear after display rounding,
even though the exact comparison triggers the rule.

## Selection behavior

### All plans

Read all represented plans for the selected month.
Evaluate each plan against the overall reference for that month.

Suggestions follow the documented Basic, Standard, Premium order,
with non-triggering plans omitted.

### One selected plan

Evaluate only the selected plan for display.

The reference still includes all represented plans for the same month.
The interface explicitly labels this reference as all plans.

For example, selecting Premium does not replace the overall reference
with Premium's own rate.

### Empty data and no matching suggestion

An empty month produces:

- Overall cohort size: `0`.
- Overall cancellation count: `0`.
- Overall cancellation rate: `null`.
- Suggestions: `[]`.

If the selected plan has no observations but other plans do,
the overall reference remains available and suggestions are empty.

If observations exist but the rule does not trigger, the interface
explains that no plan in the selection meets the rule.

This does not establish that no retention problem exists.

If only one plan is represented in a month, its rate equals the overall
rate, so this rule produces no suggestion.

## Small cohorts and interpretation limits

There is no minimum cohort-size threshold in version 1.

Every suggestion includes cohort size and cancellation count.
The rationale asks the reader to consider cohort size.
A one-customer cohort receives an additional explicit notice.

A high rate from a small cohort may change substantially with one
additional observation.

No statistical significance testing is implemented.
The application does not claim that an observed difference is
statistically significant or insignificant.

The rule does not establish:

- A causal effect of the subscription plan.
- Actual IVI customer behavior.
- The effectiveness of a proposed retention action.
- Validated product usefulness.

## Backend implementation

Rule evaluation:

`backend/app/suggestions.py`

API route:

`backend/app/main.py`

Existing grouped calculation:

`backend/app/indicators.py`

The route reads all plan groups for one month using one grouped SQL
query through `get_plan_comparisons(..., plan=None)`.

The rule calculates overall totals from those returned groups, then
applies the requested plan restriction to the proposals.

This keeps the rule's plan values and overall reference based on the
same database read.

The rule evaluator does not access the database or modify its input.
The endpoint does not insert, update or delete records.

## Read-only API contract

`GET /api/retention-suggestions`

| Parameter | Required | Meaning |
|---|---|---|
| observation_month | Yes | ISO date identifying the first day of the month |
| plan | No | Basic, Standard or Premium, with exact capitalization |

Omit `plan` for All plans. The literal string `All` is not accepted.

Example request:

`/api/retention-suggestions?observation_month=2026-09-01&plan=Premium`

Response fields:

| Field | Meaning |
|---|---|
| observation_month | Requested month as an ISO date |
| plan | Requested plan, or null for All plans |
| reference.scope | Always all_plans |
| reference.cohort_size | Total monthly cohort across all plans |
| reference.cancellation_count | Total monthly cancellation requests |
| reference.cancellation_rate | Overall percentage, or null for an empty month |
| suggestions | List of investigation proposals |

Each suggestion contains:

- `rule_id` and `rule_version`.
- `plan`.
- `cohort_size`.
- `cancellation_count`.
- `cancellation_rate`.
- `proposed_action`.
- `rationale`.

The rationale identifies the relevant month, plan counts, overall counts,
rates and interpretation limits.

### Errors

- HTTP 422: missing or invalid month, a date other than the first day,
  or an unsupported plan.
- HTTP 503: unavailable database configuration or a database operation
  failure.

The HTTP 503 message is:

`Unable to load retention suggestions`

Configuration details and raw database errors are not returned.

A failed request is not represented as a successful empty suggestion list.

## Frontend behavior

The Angular service sends the active month and optional plan.
The backend remains responsible for the rule calculation.

The panel loads summary indicators, plan comparisons and suggestions
using `forkJoin`.

Results are displayed only after all three requests succeed.
A failure clears the result sections and displays a retry message,
while preserving the selected filters.

Selection changes use `switchMap` to cancel obsolete requests.
Previously displayed suggestions and their reference are cleared
during loading.

The interface displays:

- The proposal and its rationale.
- The rule identifier and version.
- The all-plan monthly reference.
- The distinction between unavailable observations and no matching rule.
- A statement that suggestions are proposals and no action is saved
  automatically.

### Consistency limitation

Coordinated display does not create a shared database snapshot.

The summary, comparison and suggestion endpoints remain separate
HTTP requests. An import between their reads could make the sections
reflect different database states.

Within the suggestion endpoint, groups and reference are derived from
one grouped read.

## Controlled examples

| Plan | Cohort size | Cancellation requests | Rate | Suggestion |
|---|---:|---:|---:|---|
| Basic | 80 | 8 | 10% | No |
| Premium | 20 | 4 | 20% | Yes |
| Overall reference | 100 | 12 | 12% | Not a plan suggestion |

The reference is 12%, not 15%.

Selecting Premium retains the overall reference of 100 customers,
12 requests and 12%.

Additional automated cases cover:

- Equal rates.
- Empty cohorts and empty months.
- A month containing only one plan.
- A selected plan absent from the month.
- A one-customer cohort.
- Differences hidden by display rounding.
- Invalid and duplicate input groups.
- Invalid API filters.
- Configuration and database failures.

## Local verification evidence

These are local results, not GitHub Actions results.

### Backend

From `backend/`:

```powershell
$env:STREAMRETAIN_DB_TESTS = "1"

try {
    ..\.venv\Scripts\python.exe -m pytest
}
finally {
    Remove-Item Env:\STREAMRETAIN_DB_TESTS -ErrorAction SilentlyContinue
}
```

Observed complete-suite result:

**233 passed, 1 warning in 6.52 seconds**, with no skipped tests.

The warning concerns deprecated httpx usage in Starlette TestClient.
It remains a maintenance finding.

Earlier targeted checks:

- Rule unit tests: 14 passed.
- Suggestion API tests: 16 passed.
- Suggestions and existing API checks: 72 passed.
- Indicator, comparison and suggestion PostgreSQL integration file:
  6 passed in 4.07 seconds.

Integration tests use isolated PostgreSQL schemas.
The suggestion integration test checks month filtering, reference
totals and preservation of all stored customer and observation fields
in its test tables.

### Frontend

From `frontend/`:

```powershell
npm.cmd test -- --watch=false
npm.cmd run build
```

Observed test result:

**34 passed across 2 files**, including:

- 14 service tests.
- 20 panel tests.

Reported test-run duration: 5.42 seconds.

The tests use controlled HTTP responses rather than the real API.

Observed production build:

- Succeeded.
- Build duration: 4.373 seconds.
- Initial bundle total: 243.18 kB.
- Estimated transfer size: 66.37 kB.

No dependency upgrade or new dependency-audit result is claimed.

## Browser verification

Environment: local application at `http://127.0.0.1:4200`,
Microsoft Edge on Windows.

The screenshots show September 2026 with All plans selected:

| Plan | Cohort size | Cancellation requests | Displayed rate |
|---|---:|---:|---:|
| Basic | 38 | 7 | 18.42% |
| Standard | 19 | 3 | 15.79% |
| Premium | 43 | 9 | 20.93% |
| Overall | 100 | 19 | 19% |

Only Premium produces a suggestion.

The visible rationale compares 9 requests among 43 Premium customers
with 19 requests among 100 customers across all plans.

The rule identifier and version are visible.

The project author additionally confirmed this browser sequence:

1. Selecting Premium retains its suggestion and the all-plan reference.
2. Selecting Basic removes the Premium suggestion and displays the
   no-matching-rule message.
3. Returning to All plans restores the Premium suggestion.

Loading, failure, retry and obsolete-response behavior are covered
by automated panel tests. A new manual browser failure-and-recovery
check has not yet been recorded for this implementation.

The current header still says Sprint 3.
Updating the header and refining the layout remain tracked under
S4-04, issue #26.

## Remaining completion work

- Review and publish the implementation, tests and this documentation.
- Record the corresponding GitHub Actions run.
- Review issue #23 acceptance criteria against the available evidence.
- Update issue #23 and the project board after that review.

Action creation and listing remain under issue #24.
Status updates and persistence remain under issue #25.

Technical verification does not establish product validation.