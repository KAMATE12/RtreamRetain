# StreamRetain

Monthly customer cancellation analysis for a fictional streaming platform
inspired by IVI.

**Student:** Emmanuel Kamate

**Group:** M80-103CB-26

**Course:** Agile Development Methodologies

## Project purpose

Help retention managers inspect cancellation patterns and compare
subscription plans using monthly customer observations.

The broader product backlog also includes organising proposed retention
actions. Retention-action management is not implemented yet.

All customer data is synthetic.
This is an educational project, not an official IVI product.

## Latest delivery — Sprint 3

**Sprint:** November 2–15, 2026.

**Goal:** Deliver a monthly customer dashboard with observation-month
and subscription-plan filters and a subscription-plan comparison table.

The demonstration, review, retrospective and reading takeaways were
submitted to the course chat on November 14, 2026.

Implementation issues #18–#21 and the Sprint 3 delivery issue #22
are closed and marked Done on the project board.

Epic #11 remains open because activity-based filtering is deferred.

- [Project board and sprint planning](https://github.com/users/KAMATE12/projects/3)
- [Sprint 3 plan](docs/sprint-3-plan.md)
- [Product backlog](docs/product-backlog.md)
- [Sprint 3 review and retrospective](docs/sprint-3-report.md)
- [Sprint 3 reading notes](docs/sprint-3-reading-notes.md)

## Demonstration

[Download the English Sprint 3 demonstration](https://github.com/KAMATE12/RtreamRetain/releases/tag/sprint-3-demo)

On the release page, open **Assets** and download
`StreamRetain_Sprint3.zip`, then extract the archive to play the video.

- Duration: 12 minutes 15 seconds.
- The instructor approved this duration for Sprint 3.
- Archive size: approximately 639 MB.
- The project author downloaded the published archive, extracted it
  and successfully played the video.

The release provides a recorded demonstration.
It is not a publicly deployed application.

## Implemented functionality

### Synthetic data and CSV import

- Reproducible generation of synthetic customer-month observations.
- CSV structure, field-value and duplicate validation.
- Whole-file rejection when validation errors are detected.
- PostgreSQL customer and customer-month tables.
- Transactional CSV import.
- Identical existing observations left unchanged.
- Conflicting observations rejected without a partial import.
- Database persistence verified after restarting PostgreSQL.

### Monthly customer dashboard

The Angular interface displays:

- Beginning-of-month cohort size.
- Customers who requested cancellation during the selected month.
- Monthly cancellation-request rate.
- Average viewing hours per cohort customer.

Users can select:

- An available observation month.
- All subscription plans, Basic, Standard or Premium.

The latest available month is selected initially.
This is a display default, not proof that the observation period is complete.

### Subscription-plan comparisons

The comparison table displays each represented plan in the selected scope:

- Subscription plan at the beginning of the month.
- Beginning-of-month cohort size.
- Cancellation-request count.
- Cancellation-request rate.

The display order is Basic, Standard, then Premium.
Plans absent from the selected scope are not invented.

Summary indicators and comparisons use the same month and plan filters.
Selecting one plan restricts both sections to that plan.

### Interface states

- Loading messages.
- Empty-data messages.
- Generic API-error messages.
- Retry using the current selection.
- Removal of previous results during loading and after errors.
- Cancellation of obsolete requests when selections change.
- Coordinated display after both summary and comparison requests succeed.

The connection-checking panel also remains available.

## Definitions and interpretation

Each observation represents one customer in one month.
The same customer may appear in different months without being a duplicate.

The cohort is assumed to contain customers active at the beginning
of the observation month, including customers who requested cancellation
during that month.

The cancellation-request rate is:

```text
cancellation requests / beginning-of-month cohort size × 100
```

Counts and rates answer different questions.
Comparisons therefore show denominators alongside cancellation counts
and rates.

The overall rate is calculated from combined counts, not from an
unweighted average of plan rates.

### Zero versus unavailable data

- Customers observed, no cancellation requests: a measured rate of 0%.
- No customers matching the selection: an unavailable rate, represented
  as `null` by the API and displayed as **No data**.

Rates and averages are displayed with up to two decimal places.

### Interpretation limits

All observations are synthetic and reflect generation assumptions.

A higher observed cancellation-request rate is a reason for investigation.
It does not establish that a subscription plan caused cancellations.

No statistical significance testing, actual IVI behavior or proven
retention effectiveness is claimed.

## Stack and structure

- `frontend/`: Angular 21 and TypeScript; dashboard, filters,
  comparison table and interface tests.
- `backend/`: Python 3.12 and FastAPI; read-only APIs, synthetic data
  generation, CSV validation and transactional import.
- `compose.yaml`: local PostgreSQL 17 service.
- `docs/`: setup, data definitions, verification evidence,
  sprint plans, reading notes and reports.
- `data/`: example synthetic dataset.
- `.github/workflows/checks.yml`: backend tests, frontend tests
  and frontend production compilation.

SQLAlchemy and psycopg provide PostgreSQL access.

The comparison interface uses a table.
Charts are not required by the delivered Sprint 3 scope.

## Run locally

Use Node.js 24, Python 3.12, Git, and Docker Desktop with Compose.

The following commands are for Windows PowerShell.
Start each terminal at the repository root.

See [SETUP](docs/setup.md) for explanations and troubleshooting.

### 1. Configure the environment

```powershell
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Edit `.env` and replace the example password in both
`POSTGRES_PASSWORD` and `DATABASE_URL` with the same local password.

For this exercise, use letters and numbers to avoid URL-encoding issues.
Do not commit local credentials.

The database is published at `127.0.0.1:5433` on Windows.
PostgreSQL inside the container uses port `5432`.

Keep the host port in `DATABASE_URL` consistent with `compose.yaml`.
Restart FastAPI after changing `.env`.

### 2. Start PostgreSQL and the backend

Start Docker Desktop, then run:

```powershell
docker compose up -d db
docker compose ps
```

Wait until PostgreSQL is healthy.

Create the Python environment if it does not already exist,
install dependencies, and start FastAPI:

```powershell
if (-not (Test-Path .venv)) {
    py -3.12 -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt

Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Leave this terminal running.

### 3. Start the frontend

Open a second terminal at the repository root:

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd start
```

Leave this terminal running.

Open:

- Application: http://localhost:4200
- API documentation: http://127.0.0.1:8000/docs

Use **Check connections** to inspect backend and database connectivity.

The dashboard requires imported observations to show measured results.
An empty database does not contain the example CSV automatically.

Follow the [PostgreSQL import guide](docs/postgresql-import.md)
to import the synthetic example dataset.

## Read-only API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Backend health |
| `GET /api/readiness` | PostgreSQL readiness |
| `GET /api/observation-months` | Available observation months |
| `GET /api/indicators` | Summary indicators for the selected scope |
| `GET /api/plan-comparisons` | Subscription-plan comparisons for the selected scope |

The indicator and comparison endpoints accept:

| Parameter | Required | Meaning |
|---|---|---|
| `observation_month` | Yes | ISO date representing the first day of the month, such as `2026-09-01` |
| `plan` | No | `Basic`, `Standard` or `Premium`, with exact capitalization |

Omit `plan` to include all represented plans.

Examples:

```text
/api/indicators?observation_month=2026-09-01
/api/indicators?observation_month=2026-09-01&plan=Premium
/api/plan-comparisons?observation_month=2026-09-01
/api/plan-comparisons?observation_month=2026-09-01&plan=Premium
```

See the [dashboard documentation](docs/monthly-indicators-dashboard.md)
for response fields, validation rules and interface behavior.

## Verify

Recorded results below describe the verified Sprint 3 implementation.
They are dated evidence, not a guarantee about future changes.

### Backend tests without PostgreSQL integration

From the repository root:

```powershell
Set-Location backend
Remove-Item Env:\STREAMRETAIN_DB_TESTS -ErrorAction SilentlyContinue
..\.venv\Scripts\python.exe -m pytest -v
```

Unit tests and API tests with controlled dependencies do not require
a real PostgreSQL database.

Recorded result on November 12, 2026:

- 170 passed.
- 32 PostgreSQL tests skipped.
- One deprecation warning.
- Duration: 2.53 seconds.

Skipped tests do not verify database behavior.

### Complete backend suite with PostgreSQL

Start Docker Desktop and run from the repository root:

```powershell
docker compose up -d db
docker compose ps
```

Wait until PostgreSQL is healthy.
The local `.env` must contain the correct database configuration.

From the repository root:

```powershell
Set-Location backend
$env:STREAMRETAIN_DB_TESTS = "1"

try {
    ..\.venv\Scripts\python.exe -m pytest -v
}
finally {
    Remove-Item Env:\STREAMRETAIN_DB_TESTS -ErrorAction SilentlyContinue
}
```

Integration tests use isolated PostgreSQL schemas.
Their cleanup does not delete the project's working tables.

Recorded complete local result on November 12, 2026:

- 202 passed.
- No skipped tests.
- One deprecation warning.
- Duration: 5.03 seconds.

The warning concerns deprecated httpx usage in Starlette TestClient.
It remains a maintenance item.

### Frontend tests

From the repository root:

```powershell
npm.cmd --prefix frontend test -- --watch=false
```

Recorded result on November 12, 2026:

- 2 test files passed.
- 8 service tests passed.
- 15 component tests passed.
- Total: 23 tests passed.

These tests cover requests and component behavior using controlled
HTTP responses. They are not end-to-end browser tests against the
running backend and PostgreSQL.

### Frontend production build

From the repository root:

```powershell
npm.cmd --prefix frontend run build
```

Latest recorded local result on November 12, 2026:

- Build succeeded in 4.276 seconds.
- Initial bundle total: 240.23 kB.
- Estimated transfer size: 65.77 kB.

Compilation does not independently verify browser behavior.

### Continuous integration

[Successful Sprint 3 implementation CI run](https://github.com/KAMATE12/RtreamRetain/actions/runs/43151108867)

For implementation commit
[766ef96](https://github.com/KAMATE12/RtreamRetain/commit/766ef96):

- Backend job succeeded.
- Frontend job succeeded.
- All 23 frontend tests passed.
- Frontend production compilation succeeded.
- PostgreSQL tests were skipped in the CI configuration.

PostgreSQL integration evidence comes from the separate local run
with `STREAMRETAIN_DB_TESTS=1`.

A successful workflow proves only the checks enabled in that workflow.
It does not establish that documented dependency or deprecation
warnings have been resolved.

## Known results

For the working synthetic September 2026 dataset:

| Plan | Cohort size | Cancellation requests | Displayed rate |
|---|---:|---:|---:|
| Basic | 38 | 7 | 18.42% |
| Standard | 19 | 3 | 15.79% |
| Premium | 43 | 9 | 20.93% |
| All plans | 100 | 19 | 19% |

The All plans summary displays 57.14 average viewing hours.

Group counts reconcile with the summary:

- 38 + 19 + 43 = 100 customers.
- 7 + 3 + 9 = 19 cancellation requests.

A separate controlled test fixture verifies unequal group sizes:

- Basic: 80 customers, 8 requests, 10%.
- Premium: 20 customers, 4 requests, 20%.
- Combined: 100 customers, 12 requests, 12%, not 15%.

The controlled fixture is separate from the working dataset.

## Data design and import evidence

See the [data model and cancellation definition](docs/data-design.md).

The `customer` and `customer_month` tables are implemented.
The example dataset was imported into local PostgreSQL:
100 customers and 100 monthly observations.

The command-line importer validates the complete file before
database access and uses one transaction per import.

Recorded repeated-import behavior:

- Initial import: 100 inserted observations.
- Identical reimport: 0 inserted and 100 unchanged observations.
- PostgreSQL restart: 100 customers and 100 observations preserved.

This verifies the recorded scenarios.
It is not a performance benchmark or proof of every concurrent-import case.

Documentation:

- [Synthetic data generation rules and usage](docs/synthetic-data-generation.md)
- [Example CSV: 100 customer-month observations](data/synthetic_customer_month_2026-09.csv)
- [CSV validation rules, usage and tests](docs/csv-validation.md)
- [PostgreSQL import guide and verification](docs/postgresql-import.md)
- [Initial PostgreSQL verification report](docs/S1-06-postgresql-data-model.md)
- [Verification history](docs/verification.md)

To validate the example, run from the repository root:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m app.csv_validation ../data/synthetic_customer_month_2026-09.csv
```

Validation does not write records to PostgreSQL.

## Current limitations and future work

- The working browser demonstration uses September 2026 only.
  Multiple months and empty scopes were verified with controlled tests.
- Summary and comparison requests use the same filters, but separate
  reads do not guarantee a shared database snapshot during a concurrent import.
- No automated end-to-end browser suite is recorded.
- The new comparison table has no recorded narrow-screen verification.
- No user research, statistical significance testing or product
  validation is claimed.
- Activity-based filtering remains deferred under epic #11.
- Retention-action management is not implemented.
- Prediction and proven retention recommendations are not implemented.
- Public application deployment remains future work.
- Dependency and deprecation maintenance remains documented follow-up work.

The interface is a functional prototype.
Proposed visual improvements include better use of screen width,
clearer indicator hierarchy, more readable comparisons and moving
technical connection checks to a secondary area.

These improvements must be prioritised during future sprint planning;
they are not presented as already delivered.

## Sprint reports and learning

### Sprint 1 — Foundation

- [Review and retrospective](docs/sprint-1-report.md)
- [Demonstration](https://github.com/KAMATE12/RtreamRetain/releases/tag/sprint-1-demo)

The submission was posted on October 18, 2026.
The instructor accepted the 13-minute demonstration.

### Sprint 2 — Synthetic data and validated import

- [Sprint plan](docs/sprint-2-plan.md)
- [Review and retrospective](docs/sprint-2-report.md)
- [Reading notes](docs/sprint-2-reading-notes.md)
- [Import verification](docs/postgresql-import.md)

The review, retrospective, reading takeaways and demonstrations
were submitted in the course chat on October 31, 2026.

The additional Sprint 2 GitHub Release upload remains a separate follow-up.

### Sprint 3 — Monthly dashboard and comparisons

- [Sprint plan](docs/sprint-3-plan.md)
- [Review and retrospective](docs/sprint-3-report.md)
- [Reading notes](docs/sprint-3-reading-notes.md)
- [Dashboard implementation and verification](docs/monthly-indicators-dashboard.md)
- [English demonstration](https://github.com/KAMATE12/RtreamRetain/releases/tag/sprint-3-demo)

The demonstration and documents were submitted on November 14, 2026.

The reading notes identify the actual sources and sections studied,
record the corrected reading chronology, and distinguish source
reading from guided project discussion.

Publication evidence:

- [Implementation: 766ef96](https://github.com/KAMATE12/RtreamRetain/commit/766ef96)
- [Reading corrections and demo evidence: c14e6df](https://github.com/KAMATE12/RtreamRetain/commit/c14e6df)
- [Course-chat submission record: 399f2c7](https://github.com/KAMATE12/RtreamRetain/commit/399f2c7)
- [Issue closure and board review: 27a3d5d](https://github.com/KAMATE12/RtreamRetain/commit/27a3d5d)

The final semester demonstration remains planned for Sprint 5.