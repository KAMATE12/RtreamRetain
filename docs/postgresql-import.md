# PostgreSQL import — E2-03

## Status and purpose

Implementation and local automated verification are complete.
Documentation, publication and final issue closure are in progress.

Task: [E2-03 — PostgreSQL import](https://github.com/KAMATE12/RtreamRetain/issues/16).

Store validated synthetic customer-month observations without
duplicates, silent overwrites or partially imported datasets.

This is a command-line feature. The Angular interface still
displays connection status only.

## Implementation files

- `backend/app/database.py`: shared database connection configuration.
- `backend/app/schema.py`: customer and customer-month table definitions.
- `backend/app/init_db.py`: creation of missing tables.
- `backend/app/csv_import.py`: transactional CSV import.
- `backend/app/csv_validation.py`: complete-file CSV validation.

FastAPI and the import command reuse the shared connection module.
The import module does not depend on the FastAPI application.

## Database structure

### customer

One row identifies one synthetic customer.

- Primary key: `customer_id`.
- SQL type: TEXT.
- NULL, empty strings and strings containing only ordinary spaces
  are rejected.
- The CSV validator additionally enforces the canonical synthetic
  identifier format.

### customer_month

One row describes one customer during one observation month.

| Field | PostgreSQL type | Main rule |
|---|---|---|
| customer_id | TEXT | References customer.customer_id |
| observation_month | DATE | First day of the observation month |
| plan | TEXT | Basic, Standard or Premium |
| tenure_months | INTEGER | Non-negative |
| viewing_hours | NUMERIC | Finite and non-negative |
| payment_failures | INTEGER | Non-negative |
| support_requests | INTEGER | Non-negative |
| cancelled_in_month | BOOLEAN | Required |

All fields are NOT NULL.

The composite primary key is `(customer_id, observation_month)`.
A customer may have several observations for different months,
but only one observation for a given month.

NUMERIC has no declared fixed scale. Values such as 0.125 are
preserved without rounding them to two decimal places.

Retention-action tables are outside E2-03 and are not implemented.

## Create the tables

Run from the repository root in Windows PowerShell:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m app.init_db
```

Expected successful exit code: 0.

The command creates missing tables in dependency order.
Repeating it preserves existing data.

It does not migrate the structure of existing tables.
Future schema changes require a migration strategy.

## Import a CSV

From `backend`:

```powershell
..\.venv\Scripts\python.exe -m app.csv_import --help
..\.venv\Scripts\python.exe -m app.csv_import ../data/synthetic_customer_month_2026-09.csv
$LASTEXITCODE
```

The command validates the entire CSV before obtaining a database
engine. Invalid input causes no database writes.

For valid input, one transaction includes customer creation and
all observation processing.

## Duplicate and conflict policy

For each customer-month pair:

- New pair: insert the observation.
- Existing pair with identical validated values: leave it unchanged.
- Existing pair with different values: report the key and differing
  field names, then reject the entire import.

Missing customers are created within the same transaction.
If the import fails, their creation is also rolled back.

Existing observations are never silently overwritten.

A successful command reports inserted and unchanged observation
counts after the transaction has committed.

These counts concern observations, not customer identities.

## Errors and exit codes

- 0: successful import, including an identical reimport.
- 1: CSV validation failure, observation conflict, or handled
  database/configuration failure.
- 2: invalid command-line usage reported by argparse.

Handled database errors produce a generic message rather than
printing the exception or connection credentials.

The command reads the source CSV without modifying it.

## Database storage limits

CSV validity and database storage capacity are distinct.

The non-negative INTEGER columns accept values from 0 through
2147483647. A larger integer can satisfy CSV validation while
exceeding the database column's capacity.

The integration tests use 2147483648 to provoke a real database
write failure and verify complete rollback.

NUMERIC also has PostgreSQL implementation limits despite having
no declared precision or scale.

The current importer relies on PostgreSQL to reject values beyond
storage capacity. It does not provide field-specific preflight
messages for every storage limit.

Such a database failure returns exit code 1 and rolls back the
import transaction.

## Local verification — October 29, 2026

### Automated results

Full backend suite with PostgreSQL tests enabled:

134 passed, 1 warning in 6.63 seconds.

Breakdown:

- 111 existing API, generator and CSV-validation tests.
- 18 schema and storage integration tests.
- 2 import-command tests without a real database.
- 3 complete-command PostgreSQL integration tests.

The warning concerns deprecated httpx usage in Starlette TestClient.
It did not fail the tests and remains a maintenance item.

### Verified behavior

- Stored values match the input, including Decimal("0.125").
- Repeated schema creation preserves data.
- One customer can have observations for different months.
- Duplicate customer-month pairs are rejected by PostgreSQL.
- Observations cannot reference nonexistent customers.
- Tested invalid field values are rejected by database constraints.
- Identical reimport creates no duplicate observations.
- Conflicts preserve existing values and roll back new additions.
- A real database write failure rolls back new additions.
- Invalid CSV input is rejected before database access.
- Simulated connection errors do not expose fake credentials.
- Successful command transactions are visible from another connection.

### Manual example import

The first import of the example CSV reported:

- Inserted observations: 100.
- Unchanged observations: 0.
- Exit code: 0.

The second import reported:

- Inserted observations: 0.
- Unchanged observations: 100.
- Exit code: 0.

A separate Python process read:

- 100 customers.
- 100 observations.
- 100 observations matching every validated CSV field.

A later read also found 100 customers and 100 observations,
followed by an identical reimport reporting 0 inserted and
100 unchanged.

PostgreSQL restart persistence was verified on October 29, 2026:

- docker compose stop db stopped the database service.
- docker compose start db restarted the same service.
- Before any reimport, a new connection found 100 customers
  and 100 observations.
- Reimporting the example then reported 0 inserted and
  100 unchanged observations, with exit code 0.

The existing named volume was preserved.

## Run the automated checks

From `backend`, with PostgreSQL running:

```powershell
$env:STREAMRETAIN_DB_TESTS = "1"

try {
    ..\.venv\Scripts\python.exe -m pytest -v
}
finally {
    Remove-Item Env:\STREAMRETAIN_DB_TESTS -ErrorAction SilentlyContinue
}
```

Without this environment variable, the 21 PostgreSQL integration
tests are skipped. Skipped tests are not successful database checks.

The current GitHub workflow must not be described as verifying
PostgreSQL integration unless it actually enables and provisions
these tests.

## Test isolation

Schema/storage tests use a uniquely named schema inside a
transaction that is rolled back after each test.

Complete-command integration tests use a separate uniquely named
schema that supports real commits. Their cleanup drops only the
tables and schema created for that test.

Test fixtures do not erase the project's working tables.

## Scope and limitations

- All customer data is synthetic.
- No Angular CSV-upload interface is implemented.
- No dashboard calculations or retention-action tables are implemented.
- Large-file performance and concurrent-import scenarios are not verified.
- Validation collects records and errors in memory.
- Schema creation is not a migration system.
- Database constraints do not prove cohort eligibility or coherent
  subscription histories across months.
- Synthetic patterns do not establish real cancellation causes
  or retention effectiveness at IVI.

## Publication evidence

Implementation commit: pending.
GitHub Actions result for the implementation: pending.
Issue completion evidence and final closure: pending.