# S1-05 — Run the Angular page and connect it to the API

Student: Emmanuel Kamate
Sprint: 1 — October 5–18, 2026
Verification date: October 12, 2026

## Objective

Run the Angular frontend locally and demonstrate communication
with the FastAPI backend.

## Files reviewed

- frontend/package.json: startup and build commands.
- frontend/src/app/app.ts: connection-check logic and state.
- frontend/src/app/app.html: page content, button, and results.
- frontend/src/app/app.config.ts: HttpClient and other providers.
- frontend/proxy.conf.json: development proxy configuration.

## Startup commands

Backend, from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Frontend, in a separate terminal from the repository root:

```powershell
Set-Location frontend
npm.cmd start
```

The start script runs:

```text
ng serve --host 127.0.0.1 --proxy-config proxy.conf.json
```

Observed frontend address: http://127.0.0.1:4200

Backend address: http://127.0.0.1:8000

## Page content

The page opened successfully and displayed:
- StreamRetain and Sprint 1.
- The project purpose: exploring customer cancellations
  on a fictional streaming platform inspired by IVI.
- Separate FastAPI and PostgreSQL status fields.
- A Check connections button.
- Planned features clearly identified as not yet implemented.
- A statement that no customer data has been loaded.

Both connection fields initially displayed Not checked.

## From a click to a visible result

1. The button click calls checkConnections().
2. Angular sets the status fields to Checking.
3. HttpClient sends two HTTP GET requests:
   - /api/health
   - /api/readiness
4. The development proxy forwards the requests to FastAPI
   at http://127.0.0.1:8000.
5. Successful responses or errors update the api and database signals.
6. The template displays the updated values separately.

The proxy is part of the local development setup.
A production build alone does not configure production API routing.

## Connection results with FastAPI running

After clicking Check connections, the page displayed:

| Field | Observed result |
|---|---|
| FastAPI backend | Connected |
| PostgreSQL database | Not ready — check the API and PostgreSQL |

The backend logs confirmed:

```text
GET /api/health HTTP/1.1       200 OK
GET /api/readiness HTTP/1.1    503 Service Unavailable
```

The health request succeeded.
The database readiness check failed.

These separate results demonstrate that an available API
does not necessarily have an available database connection.
The 503 response alone does not identify the exact cause.

## Backend unavailable test

FastAPI was stopped using Ctrl+C while Angular remained running.
The Check connections button was clicked again.

Observed results:

| Field | Observed result |
|---|---|
| FastAPI backend | Unavailable — start the backend |
| PostgreSQL database | Not ready — check the API and PostgreSQL |

The page remained accessible and clearly reported backend
unavailability.

With FastAPI stopped, the frontend cannot obtain a database
readiness result from it. This display does not establish
whether PostgreSQL itself is running.

## Recovery test

FastAPI was restarted using the original startup command.
After another button click:
- The API field returned to Connected.
- The database field remained Not ready.
- FastAPI logged HTTP 200 for health and HTTP 503 for readiness.

Communication recovered without restarting Angular.

## Production build

Command executed from the repository root:

```powershell
npm.cmd --prefix frontend run build
```

Observed result:

```text
Application bundle generation complete.
```

Build duration: 6.983 seconds.
Initial raw bundle total: 211.52 kB.
Estimated transfer total: 57.55 kB.
Output directory: frontend/dist/frontend.

The build completed successfully.

After verification, git status --short produced no output.
No tracked source changes or untracked files were reported
before this document was created.

## Observations and limitations

- Punctuation displayed correctly in the browser despite
  garbled characters in earlier PowerShell file output.
- No source-code changes were required for these checks.
- API and database results are displayed independently.
- The current checking flag is reset when the readiness request
  finishes; it does not explicitly wait for both requests.
- A successful real PostgreSQL connection remains to be verified.
- The application has been tested locally, not deployed.

## Evidence

Browser screenshots captured during this task show:
- The initial page with both fields set to Not checked.
- API Connected with database Not ready.
- Backend Unavailable after stopping FastAPI.
- API Connected again after restarting FastAPI.

Attach the connected and backend-unavailable screenshots
to the S1-05 issue as completion evidence.

## Verification summary

- Angular page opens successfully.
- The page identifies StreamRetain and its purpose.
- The connection-check button sends requests to FastAPI.
- API health and database readiness are displayed separately.
- Backend unavailability is clearly reported.
- Communication recovers after the backend restarts.
- The frontend production build succeeds.
- The click, HTTP requests, proxy, responses, and visible
  status updates were reviewed and explained.