# Monthly indicators — Definitions, API and verification

Project: StreamRetain
Task: E3-01 — Monthly indicators and API
GitHub issue: https://github.com/KAMATE12/RtreamRetain/issues/18
Verification recorded: November 6, 2026

## 1. Purpose and scope

Provide descriptive monthly indicators from validated synthetic
customer-month observations stored in PostgreSQL.

The implementation supports month selection and an optional
subscription-plan filter.

These indicators do not predict individual cancellations or
establish actual IVI cancellation behavior or causes.

## 2. Cohort assumptions

Each stored customer-month observation is assumed to represent
a customer eligible for the beginning-of-month cohort.

The composite primary key permits only one observation per
customer and month.

Customers joining after the beginning of the month must be
excluded from that month's cohort during data preparation.

The current schema contains no subscription start date.
The API therefore cannot independently verify this eligibility.
It uses all stored observations matching the selected filters.

Eligible customers with tenure_months = 0 remain included.
Tenure alone is not used to determine cohort eligibility.

A customer who cancels during the month remains in the
denominator and is also counted in the numerator.

The first day identifies the observation month. It does not
represent the date of every event recorded during that month.

Complete monthly observation is an assumption, not something
verified by the presence of a month in the database.

## 3. Indicator definitions

All indicators use the same selected month and optional plan.

| Field | Definition |
|---|---|
| observation_month | Selected month, represented by its first day |
| cohort_size | Number of matching customer-month observations |
| cancellation_count | Matching observations where cancelled_in_month is true |
| cancellation_rate | cancellation_count / cohort_size * 100 |
| average_viewing_hours | Mean viewing_hours across all matching observations |

The cancellation count represents customers flagged as having
cancelled during the month, not a count of repeated requests.

Average viewing hours includes customers who cancelled and
customers with zero viewing hours.

For an empty selection:

- cohort_size is 0.
- cancellation_count is 0.
- cancellation_rate is null.
- average_viewing_hours is null.

For a non-empty selection with no cancellations, the rate is 0.

## 4. Filtering rules

observation_month is required.

plan is optional and accepts exactly:

- Basic
- Standard
- Premium

Omitting plan includes all subscription plans for the month.
The strings "All", "basic", an empty string and values with
surrounding spaces are rejected.

Month and plan conditions are applied together before
calculating every aggregate.

A valid plan with no matching observations returns empty
indicators, not an invalid-input error.

Overall rates are calculated from overall counts.
They are not unweighted averages of individual plan rates.

## 5. API routes

### GET /api/indicators

Example without a plan filter:

/api/indicators?observation_month=2026-09-01

Example with a plan filter:

/api/indicators?observation_month=2026-09-01&plan=Basic

Clients should supply observation_month as YYYY-MM-DD,
using the first day of the month.

Example response observed for the project's September dataset,
without a plan filter:

```json
{
  "observation_month": "2026-09-01",
  "cohort_size": 100,
  "cancellation_count": 19,
  "cancellation_rate": 19.0,
  "average_viewing_hours": 57.1351
}
```

Counts are JSON integers. The rate and average are JSON numbers
or null. The month is an ISO date string.

### GET /api/observation-months

Returns distinct stored months in descending chronological
order, newest first.

Observed response for the project's current dataset:

```json
{
  "observation_months": ["2026-09-01"]
}
```

Without observations:

```json
{
  "observation_months": []
}
```

The list describes stored data availability. It does not prove
that the newest month is complete.

## 6. Precision rules

Counts are integers.

The cancellation rate is calculated using Python floating-point
division, without explicit rounding.

PostgreSQL calculates the average from Numeric values.
The Python database result is a Decimal, converted to float
for the JSON response.

JSON rates and averages may therefore contain floating-point
approximations. The API does not guarantee a fixed number of
decimal places.

Any future display rounding must not replace the underlying
values used for calculations.

Tests use approximate comparisons where division produces
non-terminating decimal values.

## 7. Error behavior

Missing or invalid observation_month values return HTTP 422.

A date that is not the first day of a month returns HTTP 422:

```json
{
  "detail": "observation_month must be the first day of the month"
}
```

An unsupported plan returns HTTP 422:

```json
{
  "detail": "plan must be Basic, Standard or Premium"
}
```

Month and plan validation occurs before database access.

Missing database configuration and handled database connection
or query errors return HTTP 503 with a generic message:

- Indicators: "Unable to load indicators"
- Available months: "Unable to load observation months"

Tested error responses do not expose credentials or raw SQL
details. Database unavailability must not be represented as
zero customers or a zero cancellation rate.

## 8. Read-only behavior and test isolation

The indicator functions execute SELECT queries.

Integration tests use unique PostgreSQL schemas. Setup is
committed so that the API can read it through another connection.

Cleanup removes only the test's own tables and schema.
Transaction-based database tests roll back their isolated setup.

An API integration test reads all customer and customer-month
fields before and after calls to both data endpoints.
The stored rows remain identical in the tested scenario.

This verifies the absence of persistent data changes for those
calls; it is not a database-level read-only permission policy.

## 9. Verification results

### Complete backend suite

Executed locally from backend with PostgreSQL tests enabled:

```powershell
$env:STREAMRETAIN_DB_TESTS = "1"

try {
    ..\.venv\Scripts\python.exe -m pytest -v
}
finally {
    Remove-Item Env:\STREAMRETAIN_DB_TESTS -ErrorAction SilentlyContinue
}
```

Observed on November 6, 2026:

183 passed, 1 warning in 4.42s.

The warning concerns deprecated httpx usage by Starlette
TestClient. It remains a maintenance item.

This is a local result, not evidence of a GitHub Actions run.

### Controlled examples

- 100 eligible customers, including tenure_months = 0,
  with 12 cancellations produce 12%.
- Twelve observations at 10 viewing hours and 88 at 25 hours
  produce an average of 23.2 hours.
- Two Basic customers with 10 and 30 hours, one cancelled,
  produce: 2 customers, 1 cancellation, 50%, 20 average hours.
- Adding one Premium customer with 100 hours and a cancellation
  produces all-plans results of 3 customers, 2 cancellations,
  approximately 66.6667% and 46.6667 average hours.
- An additional October observation does not affect September.
- Standard has no observations in this example and returns
  zero counts with null rate and average.
- Available months are unique and newest first.

### Independent CSV comparison

The running API's September results were compared with values
calculated independently from the validated example CSV:

data/synthetic_customer_month_2026-09.csv

Observed values:

- Cohort size: 100.
- Cancellations: 19.
- Cancellation rate: 19.0%.
- Total viewing hours: 5713.51.
- Average viewing hours: 57.1351.

All returned indicators matched the independent CSV calculation.

### Manual API requests

With the API running locally:

```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/indicators?observation_month=2026-09-01" `
    -Method Get | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/observation-months" `
    -Method Get | ConvertTo-Json
```

### Relevant test files

- backend/tests/test_indicators.py
- backend/tests/test_database_schema.py
- backend/tests/test_indicators_api.py
- backend/tests/test_indicators_api_integration.py
- backend/tests/test_health.py

The complete suite also checks existing generation, validation
and import behavior.

## 10. Limitations and completion evidence

All data is synthetic. No real retention-manager validation
or real IVI behavioral analysis is claimed.

Same-month viewing may be affected by cancellation.
An association does not establish a cause.

Large-data performance and concurrent-import behavior have
not been established by these tests.

The Angular dashboard and selectors are separate tasks.
This document describes the backend functionality only.

## 11. Publication and CI evidence

Implementation and documentation were committed and pushed:

[Commit 5c4b209](https://github.com/KAMATE12/RtreamRetain/commit/5c4b209)

GitHub Actions completed successfully for this commit:

[CI run](https://github.com/KAMATE12/RtreamRetain/actions/runs/42148255599)

- Overall status: Success.
- Total workflow duration: 22 seconds.
- Backend job: passed, 18 seconds.
- Frontend job: passed, 14 seconds.
- Backend pytest result: 153 passed, 30 skipped, 1 warning in 0.91s.

The 30 PostgreSQL tests were skipped in this CI run:
3 import integration tests, 24 database-schema and indicator
tests, and 3 indicator API integration tests.

The complete local run with PostgreSQL enabled passed all
183 tests. CI success does not imply that PostgreSQL integration
tests ran on GitHub.

The Starlette TestClient warning and GitHub Actions runtime
deprecation annotations remain maintenance items.

Completion evidence was added to issue #18.
Its acceptance criteria were checked, the issue was closed
as completed, and its project-board status was set to Done
on November 6, 2026.

E3-01 was checked in parent epic #11.
The epic remains open for the remaining implementation tasks.