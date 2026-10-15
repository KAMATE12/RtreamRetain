# S1-06 — PostgreSQL connection and proposed data model

## Objective

Connect FastAPI to a real local PostgreSQL database and document
the proposed structure of the future synthetic dataset.

Sprint: October 5–18, 2026.
Local verification date: October 15, 2026.

## Configuration and port conflict

The first Docker Compose startup failed because host port 5432
was already occupied.

PowerShell identified process 6056 as postgres.
No listener was found on port 5433, and that port was not in
the displayed Windows IPv4 TCP exclusion ranges.

The project was configured to use:
- Host address: 127.0.0.1
- Host port: 5433
- Container port: 5432
- Compose service: db
- Image: postgres:17
- Persistent named volume: postgres_data

The existing PostgreSQL installation was left running.

compose.yaml and .env.example were updated to use host port 5433.
The local DATABASE_URL was updated accordingly.
FastAPI was restarted to reload its configuration.

## Real database verification

The following command started the database:

```powershell
docker compose up -d db
docker compose ps
```

Observed container: rtreamretain-db-1.
Observed status: healthy.
Observed port mapping: 127.0.0.1:5433->5432/tcp.

The readiness endpoint was checked with:

```powershell
curl.exe -i http://127.0.0.1:8000/api/readiness
```

Observed HTTP status: 200 OK.

```json
{"status":"ready","database":"connected"}
```

The endpoint opens a real database connection and executes
SELECT 1. This verifies connectivity and query execution;
it does not verify customer tables or imported data.

After clicking Check connections, Angular displayed:
- FastAPI backend: Connected
- PostgreSQL database: Connected

## Database unavailable scenario

PostgreSQL was stopped while FastAPI and Angular remained running:

```powershell
docker compose stop db
curl.exe -i http://127.0.0.1:8000/api/health
curl.exe -i http://127.0.0.1:8000/api/readiness
```

Observed health response: HTTP 200 OK.

```json
{"status":"ok","service":"streamretain-api"}
```

Observed readiness response: HTTP 503 Service Unavailable.

```json
{"detail":"Database is not ready"}
```

After clicking Check connections, Angular displayed:
- FastAPI backend: Connected
- PostgreSQL database: Not ready — check the API and PostgreSQL

This demonstrates that API availability and database readiness
are reported separately. The error response contains no credentials.

## Recovery scenario

The existing database container was restarted:

```powershell
docker compose start db
docker compose ps
curl.exe -i http://127.0.0.1:8000/api/readiness
```

The container returned to healthy.
Readiness returned HTTP 200 with database connected.

After clicking Check connections, Angular again displayed
Connected for both services.

The screenshots captured during these checks show the available,
unavailable and recovered states. They should be attached to
the S1-06 issue as visual evidence.

## Proposed data model

See [Proposed data design](data-design.md).

The document describes:
- A fictional Customer entity with a stable synthetic identifier.
- Monthly observations identified by the composite key
  (customer_id, observation_month).
- A one-to-many relationship from Customer to monthly observations.
- Retention actions targeting segments described in text.
- Field meanings, proposed categories and validation rules.

No customer tables or data import were implemented in this task.
The model remains a proposal for future implementation.

## Cancellation metric and observation window

The initial metric counts customers in the start-of-month cohort
who submit a cancellation request during that calendar month.

It measures requests, not necessarily the end of paid access.
Each eligible customer is counted at most once per month.

UTC month boundaries are used: month start is included and
next month start is excluded. Mid-month joiners are excluded
from that month's initial cohort.

An empty cohort produces "No data", not 0%.
Missing cancellation information must not be treated as false.

All future customer records will be synthetic.
They will not represent real IVI customers or establish actual
causes of cancellation at IVI.

## Credential handling

Database credentials remain in the local .env file.
compose.yaml references environment variables.

The following checks were performed:

```powershell
git check-ignore -v .env
git ls-files -- .env
```

The first command confirmed that .gitignore excludes .env.
The second returned no output, confirming that .env was not
tracked in the current Git index.

.env.example must contain example values only.

## Documentation and scope

[Local setup](setup.md) now explains the host/container ports,
the port conflict, and the need to restart FastAPI after
changing .env.

Its configuration-copy command preserves an existing .env file.

Earlier mocked backend tests are documented in S1-04.
The real database checks in this report provide separate
integration evidence; mocked tests alone do not prove
PostgreSQL connectivity.