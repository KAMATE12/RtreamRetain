# Local setup and command explanations

Use Windows PowerShell at the repository root. Prerequisites: Git, Node.js 24, Python 3.12, and running Docker Desktop. The frontend uses Angular 21, compatible with Node.js 24. On macOS/Linux use `python3.12` instead of `py -3.12` and `.venv/bin/python` instead of the Windows executable path.

## A. Local configuration and database

```powershell
Copy-Item .env.example .env
```

This copies example settings into your local configuration. Edit .env and replace the example password in BOTH POSTGRES_PASSWORD and DATABASE_URL with the same local alphanumeric password. .env stays on your computer; .env.example is shared.

```powershell
docker compose up -d db
docker compose ps
```

Compose reads compose.yaml. `up` creates/starts the database service, `-d` keeps it in the background, and `db` selects it. `ps` shows whether it is running and healthy. The named volume preserves database files across container restarts. Port 5432 is bound to your local computer only.

If port 5432 is already used by another PostgreSQL installation, change the left-hand port in compose.yaml, for example 127.0.0.1:5433:5432, and use localhost:5433 in DATABASE_URL. The container still uses its internal port 5432.

## B. Backend in terminal 1

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- `py -3.12` selects Python 3.12.
- `-m venv .venv` creates an isolated Python environment. Packages for this project do not modify other projects.
- The explicit `.venv` executable avoids needing to activate the environment or change PowerShell execution policy.
- `-m pip install -r ...` installs the versions listed in requirements.txt.
- `cd backend` puts the shell where Python can import the app package.
- `uvicorn` is the process that listens for HTTP requests.
- `app.main:app` means “load the app variable from app/main.py”.
- `--reload` restarts the server when Python source changes; use it for development.
- `--host 127.0.0.1 --port 8000` makes the server available locally on port 8000.

Open http://127.0.0.1:8000/api/health: expect status ok. Open http://127.0.0.1:8000/docs to explore the two routes. `/api/readiness` returns ready only when PostgreSQL accepts a query. HTTP 503 means the database connection is not ready; check Docker and .env.

## C. Frontend in terminal 2

Open another terminal at the repository root:

```powershell
cd frontend
npm ci
npm start
```

`npm ci` installs exactly the versions in package-lock.json. `npm start` runs the start script in package.json, which launches Angular with the API proxy. Open http://localhost:4200. Click Check connections. Both statuses should say Connected when the two services are ready.

On Windows, if PowerShell blocks npm.ps1, use `npm.cmd ci`, `npm.cmd start`, and `npm.cmd run build` instead. No execution-policy change is necessary.

## D. Checks in terminal 3

From the repository root:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
cd ../frontend
npm run build
```

pytest checks successful and failed responses using a mocked connection. The frontend build checks that Angular and TypeScript compile. Neither proves that your local PostgreSQL server works: verify the readiness route and UI separately.

Manual integration scenarios:

1. Start all services: both UI checks say Connected.
2. Stop PostgreSQL with `docker compose stop db` from the root; check again: API stays Connected, database reports Not ready.
3. Restart with `docker compose start db`; wait for readiness and check again.
4. Stop the backend with Ctrl+C in terminal 1; check again: the frontend must not claim the backend or database is connected.
5. Restart the backend for your screenshot and demo.

The browser dev server may print proxy errors during the deliberate failure checks. Those are expected evidence of the stopped service.

## E. Stop work

Ctrl+C stops frontend/backend terminal processes. At the root, `docker compose stop db` stops the database while keeping its data. Do not add `-v` to removal commands if you want to retain database files.

## Files and boundaries

No customer tables exist yet. compose.yaml provisions PostgreSQL, while the readiness query checks connectivity. docs/data-design.md is a proposal for Sprint 2. CI verifies tests/build; the screenshot and live checks document your actual local setup. Commit fixes and test results after verifying them.
