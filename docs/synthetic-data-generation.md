# Synthetic data generation — Version 1

## Status and purpose

Implementation and generation rules for E2-01, issue #14.

The Python generator and command-line interface are implemented,
locally verified and published.

Implementation commit: [45bdc6f](https://github.com/KAMATE12/RtreamRetain/commit/45bdc6f).
Task and completion evidence: [E2-01, issue #14](https://github.com/KAMATE12/RtreamRetain/issues/14).

Provide a small, reproducible fictional dataset for testing
CSV validation, PostgreSQL import and later analysis.

These generation assumptions are not verified IVI statistics.

## Observation unit and cohort

One row represents one synthetic customer during one calendar month.

Every generated customer is assumed to have an active subscription
at the start of that month.

Customers joining during the month are excluded.

Version 1 generates one month per run.
It does not simulate customer histories across multiple months.
Separate runs must not be interpreted as a coherent longitudinal
history without additional rules.

The unique observation key is:
(customer_id, observation_month).

## Default configuration

- Customer count: 100.
- Observation month: 2026-09-01.
- Random seed: 42.
- Generator version: 1.

These defaults are explicit constants.
Generation must not depend on the current date.

September 2026 is a completed month before Sprint 2 begins.
Examples and demonstrations must use fully observed months.

The customer count, observation month and seed are configurable
through command-line options.

## CSV format

- Encoding: UTF-8 without a byte-order mark.
- Separator: comma.
- Header: required.
- Line endings: LF.
- Decimal separator: dot.
- Boolean values: lowercase true or false.
- No missing values.
- No extra index column.
- Rows ordered by ascending generated customer number.

Column order:

customer_id,observation_month,plan,tenure_months,viewing_hours,payment_failures,support_requests,cancelled_in_month

## Generation rules

| Field | Version 1 generation rule |
|---|---|
| customer_id | Sequential synthetic identifiers: C000001, C000002, etc.; numeric part padded to at least six digits. |
| observation_month | The configured month, written as YYYY-MM-01. |
| plan | Basic, Standard or Premium, with equal selection probabilities. |
| tenure_months | Uniform integer draw from 0 to 60 inclusive. |
| viewing_hours | Uniform integer draw from 0 to 12000 inclusive, divided by 100 and written with two decimal places. |
| payment_failures | Uniform integer draw from 0 to 3 inclusive. |
| support_requests | Uniform integer draw from 0 to 5 inclusive. |
| cancelled_in_month | True with probability 0.20, otherwise false. |

Each customer represents an eligible member of the starting cohort.
An individual customer's eligibility is assumed by construction;
it is not inferred from viewing or payment activity.

## Cancellation meaning

cancelled_in_month indicates at least one cancellation request
during the observation month.

It does not necessarily indicate the end of paid access.

Viewing hours cover the entire month, including viewing before
the request and any viewing afterwards while access remains active.

Payment failures alone do not count as cancellation.

A probability of 0.20 does not guarantee exactly 20 cancellations
among 100 customers.

## Generation limits versus validation constraints

The generator produces a restricted example dataset.

Its upper bounds are not general CSV validation limits.

For example:

- The generator produces tenure_months between 0 and 60.
- The data contract accepts any non-negative integer tenure,
  subject to the documented storage representation.
- Therefore, 90 months is valid even though this generator
  does not produce that value.

The same distinction applies to viewing hours, payment failures
and support requests.

See data-design.md for field meanings and general constraints.

## Independence and interpretation

Version 1 imposes no dependency between plan, tenure,
viewing, payment failures, support requests and cancellation.

Observed differences between groups may result from random variation.
They are not evidence of actual customer behaviour.

This simple baseline tests software behavior.
It is not intended to reproduce a realistic customer population
or establish cancellation causes.

## Reproducibility

Use a dedicated seeded random-number generator.

Keep the order of random draws, row ordering and CSV formatting fixed.
Do not include a generation timestamp in the CSV.

The same configuration, generator version and documented runtime
must produce identical CSV bytes.

Record the Python version used.
Changing the algorithm or its draw order may change the output,
even when the seed remains unchanged.

Generated identifiers restart on each run.
Files generated with different seeds may therefore contain
conflicting observations for the same customer-month keys.
They must not be treated as automatically mergeable datasets.


## Verification checklist

- Two runs with identical settings produce identical file content.
- The output contains the requested number of records.
- Headers and column order match this specification.
- Customer-month pairs are unique.
- Generated values satisfy their generation rules.
- Dates, decimals and Boolean values use the documented format.
- Invalid generator parameters produce clear errors.
- Existing output files are not silently overwritten.

## Usage

Run these commands from the repository root using the project's
Python virtual environment.

Display available options:

```powershell
.\.venv\Scripts\python.exe backend/app/synthetic_data.py --help
```

Generate the default example: 100 customers, September 2026,
seed 42:

```powershell
.\.venv\Scripts\python.exe backend/app/synthetic_data.py
```

Default output:
data/synthetic_customer_month_2026-09.csv

Reproduce the default configuration in a new file:

```powershell
.\.venv\Scripts\python.exe backend/app/synthetic_data.py --customers 100 --month 2026-09-01 --seed 42 --output data/reproduced_2026-09.csv
```

The destination must not already exist.

Generate a different example:

```powershell
.\.venv\Scripts\python.exe backend/app/synthetic_data.py --customers 10 --month 2026-08-01 --seed 7 --output data/demo_cli_10.csv
```

An explicit relative output path is resolved from the current
working directory.

Without --output, the destination is inside the project's data
directory and its filename includes the configured month.

## Command exit codes

- 0: CSV created successfully.
- 1: Destination already exists or a filesystem operation failed.
- 2: Invalid command-line arguments or generator configuration.

Existing output files are never silently overwritten.

## Observation-period responsibility

The month parser checks the exact date format, calendar validity
and first day of the month.

It does not compare the observation month with today's date.
Selecting a fully observed month remains the caller's responsibility.

Version 1 does not generate subscription events or reconstruct
customer histories. Start-of-month eligibility is assumed
by construction.

## Local verification — October 23, 2026

Environment: Windows, Python 3.12.10, pytest 9.1.1.

Automated command executed from backend:

```powershell
..\.venv\Scripts\python.exe -m pytest -v
```

Result: 18 passed, 1 warning in 2.42 seconds.

The suite includes:

- 4 existing API tests using mocked database connections.
- 14 generator tests covering reproducible CSV bytes,
  overwrite protection, generated-data rules and invalid parameters.

Manual command-line checks:

- --help displayed the available options.
- A custom generation produced 10 observations and exit code 0.
- Repeating the command against the existing destination
  returned exit code 1.
- SHA-256 comparison before and after the refused overwrite
  confirmed that the file content was unchanged.
- --customers 0 returned an explanatory error and exit code 2.
- The default example CSV contained 100 observations.

The warning concerns deprecated httpx usage in Starlette TestClient.
It did not fail the tests and remains a maintenance item.

These checks verify the generator. They do not demonstrate
CSV input validation or PostgreSQL import, which belong
to E2-02 and E2-03.

## Implementation and related work

- [Generator implementation](../backend/app/synthetic_data.py)
- [Generator tests](../backend/tests/test_synthetic_data.py)
- [Published example CSV](../data/synthetic_customer_month_2026-09.csv)
- [Implementation commit](https://github.com/KAMATE12/RtreamRetain/commit/45bdc6f)
- [CSV validation — E2-02](csv-validation.md)

PostgreSQL import remains the responsibility of E2-03.