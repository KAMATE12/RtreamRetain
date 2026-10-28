# CSV validation — E2-02

## Purpose and status

Validate synthetic customer-month CSV files before PostgreSQL import.

Implementation and local verification are complete.
Documentation publication and issue closure remain pending.

Task: [E2-02 — CSV validation](https://github.com/KAMATE12/RtreamRetain/issues/15).

The validator reads the source file without modifying it.
It does not connect to PostgreSQL or write database records.

## File structure

- Encoding: UTF-8 without a byte-order mark (BOM).
- Separator: comma.
- Header: required.
- LF and CRLF line endings are accepted.
- Exactly eight required columns must appear once each.
- Column order may change: values are mapped by column name.
- Additional, repeated, empty or misspelled column names are rejected.
- Column names are case-sensitive and are not stripped of whitespace.
- Every observation must contain exactly eight values.
- Blank rows are rejected.
- Empty files and header-only files are rejected.

Required columns:

customer_id,observation_month,plan,tenure_months,viewing_hours,payment_failures,support_requests,cancelled_in_month

The file is read with Python's csv.reader using strict=True.
Detected CSV parsing errors are reported and reject the file.
Quoted CSV fields are handled by the CSV reader.

## Field rules and converted types

All eight values are required. Empty values are never replaced
with zero, false, a default subscription plan or a default date.

| Field | Accepted input | Python result |
|---|---|---|
| customer_id | Canonical synthetic identifier such as C000001 | str |
| observation_month | Exact YYYY-MM-DD date, with day 01 | date |
| plan | Exactly Basic, Standard or Premium | str |
| tenure_months | One or more ASCII digits 0-9 | int |
| viewing_hours | ASCII digits, optionally followed by a dot and more digits | Decimal |
| payment_failures | One or more ASCII digits 0-9 | int |
| support_requests | One or more ASCII digits 0-9 | int |
| cancelled_in_month | Exactly lowercase true or false | bool |

### Customer identifiers

Identifiers use uppercase C followed by a positive number
padded to at least six digits.

Examples:
- C000001: accepted.
- C1000000: accepted.
- C000000: rejected because numbering starts at one.
- C1: rejected because padding is missing.
- c000001: rejected because the prefix has the wrong case.
- C0000001: rejected because it is an alternative spelling of C000001.

Validation checks the identifier's format, not whether the
customer already exists in PostgreSQL.

### Integers

Signs, whitespace, decimal points, underscores and non-ASCII
digits are rejected.

Leading zeros are accepted: 007 becomes integer 7.
90 is valid for tenure_months.

The generator's upper bounds are not general validation limits.
Python conversion limits still apply to exceptionally long inputs.
Database storage limits must be defined and checked during E2-03.

### Viewing hours

Examples accepted: 0, 4.09, 150.5, 0.125.

Examples rejected: -3, +3, 4,09, .5, 5., 1e2, NaN and Infinity.
Surrounding whitespace is rejected.

The value is converted directly from text to Decimal.
Validation does not round it to two decimal places.
The generator's 120-hour upper bound is not a validation limit.

### Observation month

The date must exist in the calendar and represent the first day
of the month. For example, 2026-09-15 and 2026-02-30 are rejected.

The validator does not compare the month with today's date.
Choosing fully observed months remains the caller's responsibility.

### Cancellation

false is valid information, not a validation failure.
An empty cancellation value is missing information and is rejected.

The field describes a cancellation request during the month,
not necessarily the end of paid access.

## Duplicate handling within a file

The unique observation key is:

(customer_id, observation_month)

Repeated keys reject the file, even when other field values differ.

The same customer may appear in different months.
Different customers may appear in the same month.

The duplicate message identifies the repeated row and the first
row containing that key.

If both key fields are valid, duplicate detection still runs when
another field in the observation is invalid.

Keys cannot be checked reliably when their identifier or month is invalid.

Comparison with records already stored in PostgreSQL belongs to E2-03.

## Whole-file acceptance

validate_csv_file returns two values:

- Success: converted observations and an empty error list.
- Failure: an empty observation list and collected error messages.

One invalid observation rejects the entire file.
Valid observations are not returned for a partial import.

An invalid header stops observation processing.
Field errors are collected across readable observations.
An unrecoverable CSV, decoding or filesystem error stops reading
and rejects the file.

Row numbers identify the physical line where an observation starts.
The header normally occupies line 1.

## Usage

Run from the repository root:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m app.csv_validation --help
..\.venv\Scripts\python.exe -m app.csv_validation ../data/synthetic_customer_month_2026-09.csv
$LASTEXITCODE
```

Relative input paths are resolved from the current working directory.

Expected successful output for the generated example:

```text
Validation successful.
Validated records: 100
No data was written to the database.
```

Exit codes:

- 0: successful validation, or help displayed.
- 1: file validation or file-reading failure.
- 2: incorrect command-line usage.

## Invalid example

This example contains a negative tenure and a duplicate key:

```csv
customer_id,observation_month,plan,tenure_months,viewing_hours,payment_failures,support_requests,cancelled_in_month
C000001,2026-09-01,Premium,7,4.09,2,1,false
C000001,2026-09-01,Basic,-3,10.00,0,0,true
```

Observed output:

```text
Validation failed:
- Row 3, field 'tenure_months': must contain only digits 0-9 for a non-negative integer
- Row 3: duplicate customer-month pair (C000001, 2026-09-01); first seen at row 2.
```

The command returned exit code 1.
A SHA-256 comparison before and after validation confirmed
that the source file was unchanged.

## Local verification — October 28, 2026

Environment: Windows, Python 3.12.10, pytest 9.1.1.

Command executed from backend:

```powershell
..\.venv\Scripts\python.exe -m pytest -v
```

Latest observed result: 111 passed, 1 warning in 1.93 seconds.

Breakdown:
- 93 CSV validation tests.
- 14 synthetic generator tests.
- 4 API tests using mocked database connections.

Coverage includes:
- Header names, missing columns, additional columns and duplicates.
- File reading and representative encoding or CSV syntax failures.
- Field conversion and representative invalid values.
- Multiple errors in one observation.
- Preservation of input dictionaries and source file content.
- Rejection of partial results.
- Empty files, header-only files, blank rows and incorrect row widths.
- Duplicate customer-month keys.

Manual command-line checks:
- Help displayed successfully.
- The generated example returned 100 observations and exit code 0.
- A deliberately invalid file returned explanatory errors and exit code 1.
- The invalid file's SHA-256 fingerprint remained unchanged.

The Starlette TestClient httpx deprecation warning did not fail
the tests. Dependency maintenance remains separate work.

During review, an obsolete duplicate definition of validate_csv_file
was removed. Exactly one definition remains, and all tests passed again.

## Boundaries and limitations

- This is a local command-line validator, not an Angular upload interface.
- PostgreSQL import, transactions and persistence belong to E2-03.
- Validated observations and errors are collected in memory.
- Large-file performance has not been verified.
- Internal field parsers expect strings from the CSV reader.
- validate_customer_month expects an already checked row structure.
- Passing validation does not prove cohort eligibility or consistency
  of customer histories across months.
- All records are synthetic; validation does not establish real IVI
  behaviour, cancellation causes or retention effectiveness.

## Related files

- [Validator](../backend/app/csv_validation.py)
- [Tests](../backend/tests/test_csv_validation.py)
- [Valid generated example](../data/synthetic_customer_month_2026-09.csv)
- [Generation rules](synthetic-data-generation.md)
- [Data design](data-design.md)