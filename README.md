# StreamRetain

Customer churn analysis for a fictional streaming platform inspired by IVI.

**Student:** Emmanuel Kamate | **Group:** M80-103CB-26  
**Course:** Agile Development Methodologies

## Project purpose

Help retention managers explore cancellation patterns and organise proposed retention actions. All customer data will be synthetic. This is an educational project, not an official IVI product.

## Current sprint

**Sprint 1 — Product and foundation | October 5–18, 2026**

**Goal:** Establish the product backlog and development environment, and demonstrate an Angular application connected to a FastAPI backend and PostgreSQL database.

**Board:** Add the real public GitHub Projects URL here after creating the board.  
**Sprint plan:** [Tasks and acceptance criteria](docs/sprint-1-plan.md)  
**Product backlog:** [Prioritised epics and tasks](docs/product-backlog.md)

## Current status

This repository contains a starter skeleton and proposed sprint plan. The application displays connection status, not customer statistics. Importing data, analytics, and retention actions are future work. A supplied starter is not evidence that the student has completed every task: issues are closed after local verification and explanation.

## Stack and structure

- `frontend/`: Angular 21 and TypeScript; a connection-checking page.
- `backend/`: Python and FastAPI; health and database readiness endpoints.
- `compose.yaml`: local PostgreSQL 17 service.
- `docs/`: sprint plan, backlog, data design, reading notes and demo checklist.
- `.github/workflows/checks.yml`: automated backend tests and frontend build.

The planned MVP will also use pandas, SQLAlchemy, Chart.js, and browser tests. These are added when their features are developed.

## Run locally

Use Node.js 24, Python 3.12, Git, and Docker Desktop with Compose. Windows PowerShell commands are shown below. See [SETUP](docs/setup.md) for explanations and troubleshooting.

From the repository root:

```powershell
Copy-Item .env.example .env
```

Edit `.env`: replace the example password in BOTH `POSTGRES_PASSWORD` and `DATABASE_URL` with the same local password. For this exercise use letters and numbers to avoid URL-encoding issues.

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

In a third terminal at the root:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
cd ../frontend
npm run build
```

These automated backend tests mock PostgreSQL. Confirm the real database connection separately in the UI and `/api/readiness`. There are no browser tests yet; they belong to the feature implementation work.

## Data design and evidence

[Proposed data model and cancellation definition](docs/data-design.md). No database tables or datasets are implemented yet. Add a screenshot after verifying the application on your computer. Local development only; public application deployment is future work.

## Sprint reports

[Sprint 1 report template](docs/sprint-1-report.md). Post the demo, retrospective, and reading takeaways by Saturday evening, October 17. Review the board on Sunday, October 18. The final semester demo link will be added here in Sprint 5.
