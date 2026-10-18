# StreamRetain

Customer churn analysis for a fictional streaming platform inspired by IVI.

**Student:** Emmanuel Kamate | **Group:** M80-103CB-26  
**Course:** Agile Development Methodologies

## Project purpose

Help retention managers explore cancellation patterns and organise proposed retention actions. All customer data will be synthetic. This is an educational project, not an official IVI product.

## Current sprint

**Sprint 1 — Product and foundation | October 5–18, 2026**

**Goal:** Establish the product backlog and development environment, and demonstrate an Angular application connected to a FastAPI backend and PostgreSQL database.

**Board:** [Sprint planning and task tracking](https://github.com/users/KAMATE12/projects/3).  
**Sprint plan:** [Tasks and acceptance criteria](docs/sprint-1-plan.md)  
**Product backlog:** [Prioritised epics and tasks](docs/product-backlog.md)

## Current status

The local application skeleton has been verified on Windows.
Angular communicates with FastAPI, and FastAPI executes a real
PostgreSQL query through the readiness endpoint.

Database availability, unavailability and recovery were checked
during S1-06. The interface displays connection status, not
customer statistics.

S1-01 through S1-07 are complete.
S1-08 is in progress: reading notes and the sprint report are
prepared, and a 13-minute demo has been recorded.
Course-chat submission is pending. The demo exceeds the requested
3–5 minutes; a shorter version or instructor acceptance is pending.
Customer data import, analytics and retention-action management
remain future work.

## Stack and structure

- `frontend/`: Angular 21 and TypeScript; a connection-checking page.
- `backend/`: Python and FastAPI; health and database readiness endpoints.
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

These automated backend tests mock PostgreSQL. Confirm the real database connection separately in the UI and `/api/readiness`. There are no browser tests yet; they belong to the feature implementation work.

## Data design and evidence

See the [proposed data model and cancellation definition](docs/data-design.md).

No customer tables or customer datasets have been implemented yet.
The PostgreSQL service and real connectivity check are operational.

See the [S1-06 verification report](docs/S1-06-postgresql-data-model.md)
and [issue #6 with completion evidence](https://github.com/KAMATE12/RtreamRetain/issues/6).

Local development only; public application deployment remains future work.

## Sprint reports

[Sprint 1 report template](docs/sprint-1-report.md). Post the demo, retrospective, and reading takeaways by Saturday evening, October 17. Review the board on Sunday, October 18. The final semester demo link will be added here in Sprint 5.
