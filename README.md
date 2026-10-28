# StreamRetain

Customer churn analysis for a fictional streaming platform inspired by IVI.

**Student:** Emmanuel Kamate | **Group:** M80-103CB-26  
**Course:** Agile Development Methodologies

## Project purpose

Help retention managers explore cancellation patterns and organise proposed retention actions. All customer data will be synthetic. This is an educational project, not an official IVI product.

## Current sprint

**Sprint 2 — Reproducible synthetic data and validated import | October 19–November 1, 2026**

**Goal:** Generate reproducible synthetic customer-month data, validate CSV files and store valid records in PostgreSQL without duplicates.

**Board:** [Sprint planning and task tracking](https://github.com/users/KAMATE12/projects/3).
**Sprint plan:** [Sprint 2 tasks and acceptance criteria](docs/sprint-2-plan.md).
**Product backlog:** [Prioritised epics and tasks](docs/product-backlog.md).

## Current status

Sprint 1 is complete. The review, retrospective, reading takeaways
and demonstration were submitted to the course chat on October 18, 2026.
The instructor accepted the 13-minute demonstration.

The local application skeleton has been verified on Windows.
Angular communicates with FastAPI, and FastAPI executes a real
PostgreSQL query through the readiness endpoint.
Database availability, unavailability and recovery were checked.

E2-01: the reproducible synthetic data generator is implemented,
tested and published. A 100-observation example CSV is included.

E2-02: CSV validation is implemented and locally verified.
It checks file structure, field values and duplicate customer-month
pairs. Any detected error rejects the entire file.
Implementation and documentation are published.
GitHub Actions passed for commit 25da04a, and issue #15 is complete.

E2-03: PostgreSQL import, database duplicate handling and persistence
verification remain to be implemented.

The Angular interface still displays connection status only.
Customer analytics and retention-action management remain future work.

## Stack and structure

- `frontend/`: Angular 21 and TypeScript; a connection-checking page.
- `backend/`: Python and FastAPI; health and readiness endpoints, a synthetic data generator and a CSV validation command.
- `compose.yaml`: local PostgreSQL 17 service.
- `docs/`: sprint plan, backlog, data design, reading notes and demo checklist.
- `.github/workflows/checks.yml`: automated backend tests and frontend build.

SQLAlchemy and psycopg are already used for PostgreSQL connectivity.
The planned MVP will also use pandas, Chart.js and browser tests
when the corresponding features are developed.

## Run locally

Use Node.js 24, Python 3.12, Git, and Docker Desktop with Compose. Windows PowerShell commands are shown below. See [SETUP](docs/setup.md) for explanations and troubleshooting.

From the repository root:

```powershell
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Edit `.env`: replace the example password in BOTH `POSTGRES_PASSWORD` and `DATABASE_URL` with the same local password. For this exercise use letters and numbers to avoid URL-encoding issues.
The database is published at 127.0.0.1:5433 on Windows.
PostgreSQL inside the container uses port 5432.
Keep the host port in DATABASE_URL consistent with compose.yaml.
Restart FastAPI after changing .env.

```powershell
docker compose up -d db
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open a second terminal at the repository root:

```powershell
cd frontend
npm ci
npm start
```

Open http://localhost:4200 and click **Check connections**. API documentation: http://127.0.0.1:8000/docs.

## Verify

See the [verification history, results and limitations](docs/verification.md).

In a third terminal at the root:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
cd ../frontend
npm run build
```

The API tests mock PostgreSQL. Generator and CSV validation tests
exercise data generation, file handling and validation without a database.
Confirm real PostgreSQL connectivity separately through the UI
and `/api/readiness`.

Latest local backend result on October 28, 2026:
111 tests passed, with one Starlette TestClient deprecation warning.
See [CSV validation and verification details](docs/csv-validation.md).

There are no automated browser tests yet.

## Data design and evidence

See the [proposed data model and cancellation definition](docs/data-design.md).

A reproducible synthetic CSV dataset is available.
No customer tables or database import have been implemented yet.
The PostgreSQL service and real connectivity check are operational.

- [Synthetic data generation rules and usage](docs/synthetic-data-generation.md)
- [Example CSV: 100 customer-month observations](data/synthetic_customer_month_2026-09.csv)
- [CSV validation rules, usage and test results](docs/csv-validation.md)
- [S1-06 PostgreSQL verification report](docs/S1-06-postgresql-data-model.md)

To validate the example, run from the repository root:

```powershell
cd backend
..\.venv\Scripts\python.exe -m app.csv_validation ../data/synthetic_customer_month_2026-09.csv
```

Validation does not write records to PostgreSQL.
All customer data is synthetic and does not establish real IVI behaviour.

Local development only; public application deployment remains future work.

## Sprint reports

- [Sprint 1 completed review and retrospective](docs/sprint-1-report.md)
- [Sprint 1 demonstration — GitHub Release](https://github.com/KAMATE12/RtreamRetain/releases/tag/sprint-1-demo)
- [Sprint 2 plan](docs/sprint-2-plan.md)

The Sprint 1 submission was posted on October 18, 2026.
The instructor accepted the 13-minute demonstration.

The final semester demonstration remains planned for Sprint 5.