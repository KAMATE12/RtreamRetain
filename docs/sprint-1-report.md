# Sprint 1 — Review and retrospective

Student: Emmanuel Kamate
Group: M80-103CB-26
Course: Agile Development Methodologies
Project: StreamRetain
Sprint: October 5–18, 2026
Report prepared: October 16, 2026

Status: Prepared for submission — course-chat posting pending.
The recorded demo is 13 minutes long, exceeding the requested
3–5 minutes. A shorter version or instructor acceptance is pending.

## 1. Sprint goal and outcome

The sprint goal was to establish the product backlog and development
environment, and demonstrate an Angular application connected to
FastAPI and PostgreSQL.

The technical foundation and planning goal have been achieved.
The local application communicates with the API and a real PostgreSQL
database. The backlog, setup instructions and proposed data model
are documented.

Sprint closure is still in progress: S1-08 requires the demo video
and submission of the review, retrospective and reading takeaways.

## 2. Project links

- Repository: https://github.com/KAMATE12/RtreamRetain
- Board: https://github.com/users/KAMATE12/projects/3
- Verification history: [verification.md](verification.md)
- Reading notes: [reading-notes.md](reading-notes.md)
- Demo video: Recorded, 13 minutes.
  GitHub Release upload is pending; its download link will be
  added after publication.
  A ZIP copy is also prepared for direct course-chat submission.
  The requested 3–5 minute duration is not yet met.

## 3. Completed work

### S1-01 — Repository and board

The public repository and sprint board were set up to organise
the work and make progress reviewable.

### S1-02 — Target user and backlog

The project targets a retention manager who needs to investigate
cancellation patterns and organise proposed actions.

The backlog identifies the technical foundation, synthetic data,
segment analysis and retention-action work.

These product needs remain hypotheses, not validated IVI findings.

### S1-03 — Development environment

The local Windows environment was prepared for Git, Angular,
Python, FastAPI and Docker-based PostgreSQL development.

### S1-04 — FastAPI skeleton

The API provides separate health and database readiness endpoints.

Four automated tests verify successful and failed responses
using a mocked database connection.

Evidence: [S1-04 report](S1-04-fastapi-skeleton.md)

### S1-05 — Angular and API connection

The Angular page sends requests through the development proxy
and displays separate API and database connection results.

The production build passed.

Evidence: [S1-05 report](S1-05-angular-api-connection.md)

### S1-06 — PostgreSQL and proposed data model

PostgreSQL runs through Docker Compose.
FastAPI successfully executed SELECT 1 against the real database.

Database availability, unavailability and recovery were verified.
When PostgreSQL was stopped, API health remained HTTP 200 while
database readiness returned HTTP 503. Restarting PostgreSQL
restored readiness to HTTP 200.

The proposed data model and monthly cancellation definition
were documented. No customer tables were created.

Evidence: [S1-06 report](S1-06-postgresql-data-model.md)

### S1-07 — Documentation and integrated verification

The README and verification history were updated.
Backend tests, the frontend production build and live connection
checks succeeded.

Evidence: [Verification history](verification.md)

## 4. Verification results

Checks recorded on October 15, 2026:

- Backend: 4 tests passed, with 1 deprecation warning.
- Frontend: production build completed successfully.
- PostgreSQL: Docker Compose reported the service as healthy.
- GET /api/health: HTTP 200.
- GET /api/readiness: HTTP 200 with database connected.

The backend tests mock the database.
Real connectivity was checked separately.

Failure and recovery evidence from S1-06 complements these checks.
A successful build does not prove browser behavior or analytical
correctness.

## 5. Incomplete work and current limitations

S1-08 remains in progress until the demo and submission are complete.

The following are future product features, not completed
Sprint 1 functionality:

- Synthetic customer data import.
- Cancellation indicators and segment comparisons.
- Retention-action management.

The current application displays connection status only.
There are no customer tables, customer datasets or automated
browser tests.

No public application deployment or fresh installation on
another computer has been verified.

The product assumptions have not been tested with real retention
managers. Synthetic data cannot establish actual cancellation
causes or retention effectiveness at IVI.

## 6. Retrospective — what went well

Explanations before running commands helped me understand
the purpose of each step.

Tests after each stage helped me check the result before
continuing and identify problems more clearly.

The GitHub board helped me organise tasks and follow progress.

## 7. Retrospective — difficulty and resolution

The main technical difficulty was a PostgreSQL port conflict.

An existing local PostgreSQL process occupied port 5432,
preventing Docker from publishing the database on that port.

We identified the process and changed the project mapping to:

127.0.0.1:5433:5432

The application configuration was updated to use host port 5433.
PostgreSQL inside the container still uses port 5432.

The database then started successfully and the readiness check
confirmed a working connection.

This taught me to inspect the existing environment before changing
configuration and to distinguish host ports from container ports.

The port conflict is resolved.

## 8. Two improvements for the next sprint

### Improvement 1 — Work in short, regular sessions

At the start of each session, choose one small task or acceptance
criterion from the board.

At the end, record the result and the next action.
Review whether this helped maintain progress during the retrospective.

### Improvement 2 — Record evidence immediately

After each meaningful check, record the command, result and date
in the relevant task notes.

Add screenshots when they help demonstrate behavior.
Before moving a task to Done, check that its evidence is linked
and its acceptance criteria are satisfied.

## 9. Reading takeaways and application

I studied the publicly available Chapter 1 excerpt of
Dan Olsen's The Lean Product Playbook, focusing on the
Product-Market Fit Pyramid and the Lean Product Process.

I learned to identify the target user and problem before
selecting features.

For StreamRetain, this means starting with the retention manager's
need to investigate cancellation patterns, then selecting
appropriate indicators, comparisons and action-tracking features.

The reading clarified the reasoning behind the existing backlog.
It did not validate the product assumptions.

I also learned to distinguish a working technical foundation
from a product that provides value to its intended users.

Detailed scope, sources and uncertainties:
[Reading notes](reading-notes.md)

## 10. Proposed next-sprint focus

Refine the synthetic data and import work into small, testable
tasks, using the proposed data model and cancellation definition.

Confirm the scope during Sprint 2 planning.
Do not treat all remaining product features as committed work.

## 11. Remaining submission checklist

## 11. Submission checklist

- [x] Record the demonstration: 13 minutes.
- [ ] Meet the requested 3–5 minute duration, or obtain explicit
      instructor acceptance of the 13-minute version.
- [ ] Upload the video as a GitHub Release asset.
- [ ] Add the actual GitHub Release link to this report.
- [ ] Verify that the video can be downloaded while signed out.
- [ ] Attach the ZIP containing the video to the course chat.
- [ ] Post the GitHub video link, sprint review, retrospective
      and reading takeaways in the course chat.
- [ ] Record the actual submission date and the course-chat
      message link, if available.
- [ ] Commit and push the final documentation updates.
- [ ] Add completion evidence to S1-08.
- [ ] Review the acceptance criteria and update the board
      to reflect the actual completion status.

Planned submission deadline: October 17, 2026, in the evening.
Actual submission date: Pending.
GitHub video link: Pending upload.
Course-chat message link: Pending, if available.