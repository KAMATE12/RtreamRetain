# Verification history and current limitations



## 1. Starter preparation — October 6, 2026

The original package preparation notes reported:
- Four backend pytest tests passed with a mocked database.
- The Angular production build passed.
- Required files and local Markdown links were checked.

The preparation environment did not verify real PostgreSQL
connectivity, browser interactions, execution on the student's
Windows computer or GitHub Actions in the student's repository.

These were initial limitations, not the current verification status.

## 2. Student verification before S1-07

### Backend and frontend

During S1-04, four backend tests passed on Windows.
These tests used a mocked database connection.

During S1-05, the Angular production build passed.
The interface was also checked with FastAPI running, stopped
and restarted.

See:
- [S1-04 report](S1-04-fastapi-skeleton.md)
- [S1-05 report](S1-05-angular-api-connection.md)

### Real PostgreSQL integration — October 15, 2026

During S1-06:
- PostgreSQL started through Docker Compose and became healthy.
- The published database address was 127.0.0.1:5433.
- FastAPI executed SELECT 1 through a real database connection.
- GET /api/readiness returned HTTP 200 when the database was available.
- After stopping the database, GET /api/health remained HTTP 200
  while GET /api/readiness returned HTTP 503.
- Angular displayed API Connected and database Not ready.
- Restarting PostgreSQL restored readiness HTTP 200.
- Angular again displayed both connections as Connected.

See:
- [S1-06 report](S1-06-postgresql-data-model.md)
- [Issue #6 and visual evidence](https://github.com/KAMATE12/RtreamRetain/issues/6)

### Automated checks on GitHub

Starter checks #12 passed for commit aa7805e.
Both backend and frontend jobs succeeded.

[GitHub Actions run](https://github.com/KAMATE12/RtreamRetain/actions/runs/38779261090)

The workflow displayed a Node runtime deprecation warning
for some GitHub Actions. It did not fail the run.
Updating those action versions remains a maintenance item.

CI results complement the local integration checks.
They do not, by themselves, prove real PostgreSQL connectivity.

## 3. S1-07 verification — completed

The README was updated to describe the verified local application,
current dependencies, database port and existing evidence.
The configuration-copy command now preserves an existing .env.

### Backend tests — October 15, 2026

Command executed from backend:

`..\.venv\Scripts\python.exe -m pytest -v`

Result: 4 passed, 1 warning in 1.37 seconds.

The warning was a StarletteDeprecationWarning concerning
httpx usage in TestClient. It did not fail the tests.
Reviewing this dependency compatibility remains a maintenance item.

The tests use a mocked database connection.

### Frontend production build — October 15, 2026

Command executed from the repository root:

`npm.cmd --prefix frontend run build`

Result: successful production build in 6.469 seconds.
Initial bundle total: 211.52 kB.
Estimated transfer size: 57.55 kB.
Output directory: frontend/dist/frontend.

This verifies compilation, not browser behavior or API connectivity.

### Integration evidence

Real database availability, unavailability and recovery were
verified during S1-06 on October 15, as recorded above.

### Final integrated-state check — October 15, 2026

During S1-07, the current application state was checked:
- docker compose ps showed PostgreSQL healthy.
- The published port mapping was 127.0.0.1:5433->5432/tcp.
- GET /api/health returned HTTP 200 with status ok.
- GET /api/readiness returned HTTP 200 with database connected.
- After clicking Check connections, Angular displayed Connected
  for both FastAPI and PostgreSQL.
- A screenshot was captured for the S1-07 issue.

Failure-state evidence is reused from the earlier checks:
- Backend unavailable and recovery: S1-05.
- Database unavailable and recovery: S1-06.

These failure scenarios were not repeated during S1-07.

### Documentation review

The README describes the project purpose, fictional scenario,
technology stack and project board link.

The setup guide documents prerequisites, local configuration,
startup commands and manual verification scenarios.
.env.example provides example values without real credentials.

Known limitations and maintenance items are recorded below.
The documentation was committed and pushed in commit db027f8.
S1-07 was subsequently closed and moved to Done.

## 4. Current scope and limitations

- The application displays connection status only.
- No customer tables or customer datasets are implemented.
- Data import, analytics and retention-action management are future work.
- The data model is a proposal; its validation rules are not implemented.
- All future customer data will be synthetic.
- Backend automated tests mock the database.
- No automated browser tests are implemented.
- Connection labels refresh when Check connections is clicked;
  the page does not continuously monitor services.
- Local Windows operation has been checked.
- A fresh installation on another computer has not been verified.
- Public application deployment has not been implemented.
- Successful connectivity does not establish analytical correctness
  or real-world retention effectiveness.

## 5. Local configuration

The personal .env file is ignored and was not tracked in the
Git index during the S1-06 checks.

.env.example contains example configuration.
The setup instructions preserve an existing .env file.

See [Local setup](setup.md) and
[Proposed data design](data-design.md).