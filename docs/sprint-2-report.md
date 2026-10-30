# Sprint 2 — Review and retrospective

Student: Emmanuel Kamate
Group: M80-103CB-26
Course: Agile Development Methodologies
Project: StreamRetain
Sprint: October 19–November 1, 2026
Report prepared: October 30, 2026

Status: Draft — demonstration and course-chat submission pending.

## 1. Sprint goal and outcome

The sprint goal was to generate reproducible synthetic
customer-month data, validate CSV files and store valid
observations in PostgreSQL without duplicates.

The technical goal has been achieved and locally verified.

The delivered workflow is command-line based:
generate a dataset, validate it and import it into PostgreSQL.

Sprint delivery is not yet complete. The English demonstration
has not been recorded, and the review package has not yet
been submitted to the course chat.

## 2. Project and evidence links

- [Repository](https://github.com/KAMATE12/RtreamRetain)
- [Project board](https://github.com/users/KAMATE12/projects/3)
- [Sprint 2 plan](sprint-2-plan.md)
- [Reading and learning notes](sprint-2-reading-notes.md)
- [Synthetic data generation](synthetic-data-generation.md)
- [CSV validation](csv-validation.md)
- [PostgreSQL import](postgresql-import.md)

Demonstration link: Pending recording and publication.
Demonstration duration: Not yet available.

## 3. Completed implementation

### E2-01 — Reproducible synthetic data generator

Issue: https://github.com/KAMATE12/RtreamRetain/issues/14

Implemented a configurable generator with a fixed random seed,
documented generation rules and CSV output.

The same configuration and seed reproduce the same dataset
in the verified environment.

The generator refuses to overwrite an existing output file.

A 100-observation example is included in the repository.

Implementation commit:
https://github.com/KAMATE12/RtreamRetain/commit/45bdc6f

### E2-02 — CSV validation

Issue: https://github.com/KAMATE12/RtreamRetain/issues/15

Implemented validation of file structure, required values,
data formats, allowed categories and customer-month uniqueness.

Valid text values are converted to appropriate Python types.

Any detected validation error rejects the entire file.
Validation does not modify the source file or write to PostgreSQL.

Implementation commit:
https://github.com/KAMATE12/RtreamRetain/commit/25da04a

### E2-03 — Transactional PostgreSQL import

Issue: https://github.com/KAMATE12/RtreamRetain/issues/16

Implemented the customer and customer_month tables,
database constraints and a documented import command.

The importer validates the complete CSV before database access.

Each import uses one transaction:

- New observations are inserted.
- Identical existing observations are counted as unchanged.
- Different values for an existing customer-month pair
  cause a conflict and reject the entire import.
- A database write failure rolls back the entire attempt.

Existing observations are never silently overwritten.

Implementation commit:
https://github.com/KAMATE12/RtreamRetain/commit/4132977

## 4. Verification results

### Automated checks

The complete local backend suite passed 134 tests with
PostgreSQL integration enabled.

The checks covered generation, CSV validation, API behavior,
database constraints, import behavior and transaction rollback.

The database tests used isolated test schemas.
Their cleanup did not target the project's working tables.

The known Starlette TestClient deprecation warning remains
a maintenance item.

Commands executed from backend:

```powershell
$env:STREAMRETAIN_DB_TESTS = "1"

try {
    ..\.venv\Scripts\python.exe -m pytest -v
}
finally {
    Remove-Item Env:\STREAMRETAIN_DB_TESTS -ErrorAction SilentlyContinue
}

```

GitHub Actions passed for implementation commit 4132977:

https://github.com/KAMATE12/RtreamRetain/actions/runs/40802569986

Both backend and frontend jobs succeeded.
The run lasted 27 seconds.

Action runtime deprecation warnings remain a maintenance item.

The CI summary alone does not establish that PostgreSQL
integration tests ran on GitHub. The 134-test result above
is the recorded local result.

### Initial import and identical reimport

The example CSV was imported using the command-line importer.

First import:

- Inserted observations: 100.
- Unchanged observations: 0.
- Exit code: 0.

Identical reimport:

- Inserted observations: 0.
- Unchanged observations: 100.
- Exit code: 0.

A separate database connection found:

- Customers: 100.
- Monthly observations: 100.
- Observations matching all validated CSV fields: 100.

### PostgreSQL restart persistence

On October 29, PostgreSQL was stopped and started using
docker compose stop db and docker compose start db.

The existing data volume was preserved.

Before any reimport, a new connection found 100 customers
and 100 monthly observations.

Reimporting the example then reported 0 inserted and
100 unchanged observations, with exit code 0.

Detailed commands, test scenarios and limitations:
[PostgreSQL import guide](postgresql-import.md).

## 5. Incomplete work and current limitations

S2-04 remains in progress.

The English demonstration has not yet been recorded.
The review package has not yet been submitted to the course chat.

The current workflow is command-line based.
The Angular interface displays connection status only.

An Angular CSV upload interface, analytical dashboards,
segment comparisons and retention-action management
are not implemented.

There are no automated browser tests or public application
deployment.

All customer records are synthetic. Their patterns do not
establish actual IVI cancellation behavior or causes.

No interviews or usability tests with real retention managers
have been conducted.

Concurrent imports and large-file performance have not
been established by the current verification.

## 6. Retrospective — What went well

Dan Olsen's Product-Market Fit Pyramid helped me connect
the retention manager's needs with the proposed features.

We chose to prepare the data workflow before developing
the analytical dashboard. This was our technical sequencing
decision, not a requirement of the pyramid.

Interface prototypes can also be explored before storage
implementation is complete.

The Clean Code learning activity helped me understand how
to organize code, separate responsibilities and make the
relationships between functions easier to follow.

It also encouraged me to consider how another developer
would understand my code.

Readable tests were particularly helpful: concrete inputs
and expected results made each function's role clearer.

## 7. Retrospective — Main difficulty

My main difficulty was deciding how to divide the code
into small, clear and effective functions.

I initially focused on making functions as short as possible.

I learned that fewer lines do not automatically make code
clearer or more efficient. A function needs a coherent
responsibility, an understandable name and testable behavior.

Further decomposition should improve understanding.
No performance improvement is claimed without measurement.

## 8. Review of the Sprint 1 improvements

### Short, regular sessions

I maintained regular work sessions, following my planned
allocation of approximately two hours per day.

This describes my working habit, not a measured total
of actual sprint hours.

### Immediate evidence capture

I recorded results immediately after verification.

This helped preserve the commands and observed outcomes
needed for documentation and completion evidence.

## 9. Reading takeaways

The course assigns Robert C. Martin's Clean Code to Sprint 2.

I read the official First Principles excerpt from the second
edition. Reading completion was recorded on October 30, 2026.

My main takeaway was the importance of organizing code
so its structure and responsibilities are understandable.

The guided learning discussion also covered meaningful names,
comments, error handling and readable tests using StreamRetain
examples.

I also read the public Dan Olsen resources recorded in
the reading notes as supplementary product learning.

The initial reading plan was corrected after checking
the professor's course schedule.

These activities examined existing implementation decisions
retrospectively. They are not evidence that the reading
preceded implementation.

I do not claim to have read either complete book.

Sources and detailed personal reflections:
[Reading notes](sprint-2-reading-notes.md).

## 10. Improvements for the next sprint

1. Before implementing a function, describe its responsibility,
   one representative input, the expected result and an error case.
   Use these examples to prepare understandable tests.

2. Before splitting a function further, check whether doing so
   clarifies its responsibilities and execution flow.
   Avoid using line count alone as the reason for decomposition.

Continue regular sessions and immediate evidence capture.

## 11. Proposed next-sprint focus

During Sprint 3 planning, refine the analytical work into
small, testable tasks using the stored synthetic observations.

Potential work includes verifying cancellation calculations
against a known dataset and presenting understandable indicators.

Confirm priorities and capacity before committing to tasks.

The professor's schedule assigns Martin Kleppmann's
Designing Data-Intensive Applications to Sprint 3.
Select relevant accessible reading during planning.

## 12. Submission checklist

- [x] Implement and verify the generator.
- [x] Implement and verify CSV validation.
- [x] Implement and verify PostgreSQL import.
- [x] Publish implementation and technical documentation.
- [x] Record reading sources, scope and takeaways.
- [x] Reflect on the two Sprint 1 improvements.
- [ ] Review and finalize this report.
- [ ] Prepare and rehearse an English demonstration.
- [ ] Record the demonstration, targeting 3–5 minutes.
- [ ] Publish the demonstration and record its actual duration.
- [ ] Verify demonstration access.
- [ ] Submit the demo, review, retrospective and reading takeaways.
- [ ] Record the actual submission date and available evidence.
- [ ] Commit and push the finalized report.
- [ ] Add completion evidence to S2-04.
- [ ] Review acceptance criteria and update the board.

Planned submission target: October 31, 2026, in the evening,
subject to the professor's course schedule.

Actual submission date: Not yet submitted.
Demonstration link: Pending recording and publication.
Demonstration duration: Not yet available.
Course-chat message link: Not yet available.