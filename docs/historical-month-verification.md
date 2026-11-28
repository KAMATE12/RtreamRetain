# S4-05 — Historical-month import verification

Issue: #27
Sprint: Sprint 4 — November 16–29, 2026
Verification date: November 28, 2026

Status: local verification completed; publication pending.

## Objective and scope

Verify the existing command-line importer and dashboard month filtering.
No application code, import mechanism or indicator formula was changed.

## Rules inspected

The review covered:

- docs/postgresql-import.md
- backend/app/csv_validation.py
- backend/app/csv_import.py
- backend/app/schema.py
- backend/app/database.py

The validator checks required columns, canonical customer identifiers,
month format, supported plans, non-negative numeric values, exact boolean
values and duplicate customer-month keys.

The importer validates the complete file before database writes.
New observations are inserted in one transaction.
Identical observations are left unchanged.
Conflicting observations cause the import transaction to roll back.

The customer table stores identity only. Observation attributes belong
to the customer-month record.

Some interface descriptions in the earlier import documentation describe
the historical E2-03 implementation state. Current source code was used
to establish the behaviour relevant to this verification.

## Controlled fixture

Path: data/historical_customer_month_2026-08.csv
Observation month: 2026-08-01
Identifiers: C900001 through C900010
Encoding: UTF-8
Delimiter: comma

This is a deliberately constructed, independent synthetic cohort.
All ten customers are assumed active at the beginning of August.
Their observations were not copied from September with a changed date.

These customers have no September observations in this scenario.
The fixture does not establish longitudinal subscription histories.
The observation month is August; the import was performed in November.

Expected results were calculated and checked before importing:

| Scope | Cohort | Cancellation requests | Rate | Average viewing hours |
|---|---:|---:|---:|---:|
| All plans | 10 | 2 | 20% | 18 |
| Basic | 4 | 1 | 25% | 10 |
| Standard | 4 | 0 | 0% | 20 |
| Premium | 2 | 1 | 50% | 30 |

The overall rate uses 2/10, not an unweighted average of plan rates.
Total viewing hours are 180; the overall average is 180/10.

## Baseline before import

A read-only REPEATABLE READ transaction captured all rows from
customer, customer_month and retention_action.

| Table | Initial rows |
|---|---:|
| customer | 100 |
| customer_month | 100 |
| retention_action | 2 |

Only September 2026 was present.
August contained zero observations.
None of the ten proposed customer identifiers already existed.

September baseline:

| Scope | Cohort | Cancellation requests | Displayed rate |
|---|---:|---:|---:|
| All plans | 100 | 19 | 19% |
| Basic | 38 | 7 | 18.42% |
| Standard | 19 | 3 | 15.79% |
| Premium | 43 | 9 | 20.93% |

The exact overall average viewing duration was 57.1351 hours,
displayed as 57.14 hours.

## Commands and observed results

Commands were executed from the backend directory using the existing
project virtual environment.

Validation:

    ..\.venv\Scripts\python.exe -m app.csv_validation ..\data\historical_customer_month_2026-08.csv

Observed: validation successful, 10 validated records, no database writes.

Initial import:

    ..\.venv\Scripts\python.exe -m app.csv_import ..\data\historical_customer_month_2026-08.csv

Observed: 10 inserted observations, 0 unchanged observations, exit code 0.

Identical reimport:

    ..\.venv\Scripts\python.exe -m app.csv_import ..\data\historical_customer_month_2026-08.csv

Observed: 0 inserted observations, 10 unchanged observations, exit code 0.

The verification harness invoked these CLI commands as separate Python
processes and checked their exit codes and reported observation counts.

## Data preservation

Before importing, the harness checked that the database still matched
the captured baseline.

After the first import, it compared each table by primary key against
the baseline plus the explicitly expected additions:

- customer: exactly ten additional identities.
- customer_month: exactly ten additional validated August observations.
- retention_action: no additions or changes.

Dates, decimal values and identifiers were serialised consistently for
comparison. All fields of existing rows were included.

After the identical reimport, a fresh snapshot matched the entire
post-first-import snapshot.

| Table | After initial import | After reimport |
|---|---:|---:|
| customer | 110 | 110 |
| customer_month | 110 | 110 |
| retention_action | 2 | 2 |

All comparisons passed. No existing customer, observation or action was
modified or deleted. Stored August rows matched the validated fixture.

Local snapshots were retained outside the repository in the Windows
temporary directory:

- StreamRetain-S4-05-before-20261128T074056731366Z.json
- StreamRetain-S4-05-after-20261128T074056731366Z.json

These are local verification snapshots, not a durable backup system.

## Manual browser verification

Browser: Microsoft Edge on Windows.
Application: http://127.0.0.1:4200

Procedure: reload the dashboard with F5 after the command-line import,
then select the historical month and plan.

Observed screenshots:

| Selection | Cohort | Requests | Rate | Average hours |
|---|---:|---:|---:|---:|
| August, All plans | 10 | 2 | 20% | 18 |
| August, Standard | 4 | 0 | 0% | 20 |
| September, All plans | 100 | 19 | 19% | 57.14 |

August became selectable after refresh.
The displayed month and plan matched the corresponding summary.

The author additionally verified the comparison tables:

- August, All plans: Basic 4/1/25%, Standard 4/0/0%, Premium 2/1/50%.
- August, Standard: only Standard, with 4/0/0%.

Standard displayed a measured 0%, not No data.
Returning to September reproduced the recorded baseline.
The observed selections did not combine August and September records.

The author confirmed adding five screenshots to issue #27:
three summary selections and two August comparison-table captures.

## Results and limitations

No defect was observed in this controlled scenario.

Database checks used real local PostgreSQL connections and the existing
CLI. Browser observations were manual. They are distinct from automated
unit-test results and GitHub CI checks.

No new full test-suite execution or production build is claimed for this
fixture-and-documentation task. No application code changed.

This scenario does not verify every import case, concurrent imports,
large-file performance, or the same customer across multiple months.
It does not establish real IVI behaviour or retention effectiveness.

No working data was deleted, overwritten or reset.
No CSV-upload interface or new import mechanism was introduced.

## Publication and acceptance

The fixture and this record are prepared for publication.
Record the resulting commit in issue #27 and review its acceptance
criteria before closing it.

No S4-05-specific CI result is claimed in this record.

## References

- [Issue #27 and browser screenshots](https://github.com/KAMATE12/RtreamRetain/issues/27)
- [Historical fixture](../data/historical_customer_month_2026-08.csv)
- [PostgreSQL import](postgresql-import.md)
- [Monthly dashboard](monthly-indicators-dashboard.md)
- [Sprint 4 plan](sprint-4-plan.md)
