# S1-04 — Run and explain the FastAPI skeleton

Student: Emmanuel Kamate
Sprint: 1 — October 5–18, 2026
Verification date: October 12, 2026

## Objective

Run the FastAPI backend locally, understand its basic endpoints,
and verify its behavior with automated tests.

## Backend structure

- app/main.py: creates the FastAPI application and defines its endpoints.
- app/__init__.py: identifies app as a Python package.
- requirements.txt: lists backend dependencies.
- pytest.ini: configures the test runner.
- tests/test_health.py: contains four automated tests.

The application object is named app in app/main.py.
Its title is StreamRetain API and its version is 0.1.0.

## Local startup

Command executed from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Observed result:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Uvicorn serves the FastAPI application.
The --reload option enables automatic reload during development.

## Health endpoint

Request:

```http
GET /api/health
```

Observed HTTP status: 200 OK.

Observed response:

```json
{"status":"ok","service":"streamretain-api"}
```

This endpoint responds without checking PostgreSQL.
Its success does not prove that the database is available.

## Interactive documentation

The documentation was accessible at:

http://127.0.0.1:8000/docs

It displayed both GET endpoints:
- /api/health
- /api/readiness

Both endpoints were called using Try it out and Execute.
Their actual status codes and response bodies were inspected
in the Server response section.

## Database readiness endpoint

Request:

```http
GET /api/readiness
```

Observed HTTP status: 503 Service Unavailable.

Observed response:

```json
{"detail":"Database is not ready"}
```

The implementation reads DATABASE_URL from the environment,
with local settings loaded from the root .env file.
It attempts to connect through SQLAlchemy and execute SELECT 1.

A successful check would return HTTP 200 with:

```json
{"status":"ready","database":"connected"}
```

The observed 503 means that the database check did not succeed.
It does not establish the exact cause: the database may be
unavailable or the connection settings may be incorrect.

A successful real PostgreSQL connection has not yet been verified.

The documentation displayed 503 as Undocumented because this
response is not explicitly declared in the route's OpenAPI metadata.
The Python implementation does handle this response.

## Automated tests

Commands executed from the repository root in a second terminal:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest -v
```

Observed environment:
- Python: 3.12.10
- pytest: 9.1.1
- Configuration: backend/pytest.ini

Observed result:

```text
4 passed, 1 warning in 1.32s
```

Tests and their scope:

1. test_health_does_not_depend_on_database
   Verifies HTTP 200 and the exact health response.
   It also verifies that health does not call get_engine.

2. test_readiness_reports_database_failure_without_exposing_credentials
   Simulates a database error and verifies HTTP 503 with a
   generic response instead of connection details.

3. test_readiness_checks_database
   Uses a mock engine and verifies HTTP 200,
   database = connected, and one call to execute.
   It does not verify the exact SQL text.

4. test_readiness_handles_missing_configuration
   Simulates missing configuration and verifies HTTP 503.

## Mocked checks versus a real database connection

The tests use patch and MagicMock to replace database interactions.
TestClient calls the application without requiring a running
Uvicorn server.

Passing these tests verifies application behavior under the
simulated conditions. It does not prove that a real PostgreSQL
server is reachable or accepts the configured credentials.

The browser readiness check used the actual application
configuration and returned 503.

## Warning observed

The test run reported StarletteDeprecationWarning:
using httpx with starlette.testclient is deprecated,
and the warning suggests httpx2.

This warning did not fail the tests.
No dependency changes were made to resolve it during this task.
It remains a dependency-maintenance follow-up.

## Key concepts reviewed

- Request: an HTTP message sent by a client, such as GET /api/health.
- Response: the status, headers, and body returned by the server.
- Endpoint: an API access point identified here by a method and path.
- JSON: the format used for the response data.
- HTTP 200: the request succeeded.
- HTTP 503: the readiness check reports an unavailable dependency.
- Health: the application can respond.
- Database readiness: the application can connect to the database
  and execute the check query.

## Verification summary

Verified:
- FastAPI starts locally.
- GET /api/health returns HTTP 200 and the expected JSON.
- Interactive documentation is accessible at /docs.
- GET /api/readiness returns a handled HTTP 503 response.
- All four backend tests pass locally.

Remaining follow-up:
- Establish and verify a successful real PostgreSQL connection.
- Review the test-client deprecation warning.