# Sprint 2 — Reproducible synthetic data and validated import

Student: Emmanuel Kamate
Group: M80-103CB-26
Project: StreamRetain

Planned dates: October 19–November 1, 2026.
Confirm these dates against the GitHub Sprint 2 iteration.

Status: Planning. Implementation has not started.

## 1. Sprint goal

Generate reproducible synthetic customer-month data, validate CSV
files and store valid records in PostgreSQL without duplicates.

The result will provide a documented data foundation for later
cancellation analysis.

## 2. Capacity and estimates

Available time: 2 hours per day for 14 days, totalling 28 hours.

Plan 23 hours of work and reserve 5 hours for difficulties.
Estimates include learning, implementation and verification.

| Work item | Estimated hours |
|---|---:|
| Sprint planning, task issues and start message | 2 |
| E2-01 — Data rules, generator and tests | 6 |
| E2-02 — CSV validation and error tests | 5 |
| E2-03 — PostgreSQL import and integration tests | 7 |
| Documentation, reading, demo and retrospective | 3 |
| Buffer | 5 |
| Total | 28 |

Review estimates using actual progress.
Do not automatically add more work when time remains.

## 3. Scope

Included:

- A documented synthetic customer-month dataset.
- A reproducible Python generator.
- CSV structure and value validation.
- A command-line import into PostgreSQL.
- Duplicate handling and persistence checks.
- Tests, documentation and completion evidence.

Not included in this sprint commitment:

- An Angular CSV upload interface.
- Dashboard indicators and charts.
- Segment comparisons.
- Retention-action management.
- Machine-learning predictions.
- Public application deployment.

The first import will be demonstrated through a documented Python
command. A user-facing import interface can be planned separately.

## 4. Task identification and board rules

Parent epic:
[E2 — Synthetic customer data](https://github.com/KAMATE12/RtreamRetain/issues/10)

Sprint 2 task issues:

| Planning ID | Task | GitHub issue |
|---|---|---|
| E2-01 | Reproducible synthetic data generator | [#14](https://github.com/KAMATE12/RtreamRetain/issues/14) |
| E2-02 | CSV validation | [#15](https://github.com/KAMATE12/RtreamRetain/issues/15) |
| E2-03 | PostgreSQL import | [#16](https://github.com/KAMATE12/RtreamRetain/issues/16) |
| S2-04 | Reading, demonstration and sprint review | [#17](https://github.com/KAMATE12/RtreamRetain/issues/17) |

Planning identifiers are not GitHub issue numbers.

Assign these four task issues to Sprint 2 with priority P0.
Their initial status is Todo.

Keep the Sprint field on the E2 epic empty.
S2-04 is a sprint-level task, not an E2 implementation task.

Use Todo, In Progress, Testing and Done.
Keep at most two tasks across In Progress and Testing,
with one implementation task actively worked on at a time.

Creating an issue does not mean its functionality is implemented.

## 5. E2-01 — Reproducible synthetic data generator

### Objective

Generate fictional customer-month records using explicit,
documented rules and a fixed random seed.

### Work

- Review docs/data-design.md and confirm the CSV contract.
- Document fields, allowed values and generation assumptions.
- Define the observation period and cohort eligibility.
- Implement configurable generation with a fixed seed.
- Produce a small example CSV and automated tests.
- Document the command needed to reproduce the example.

### Acceptance criteria

- [ ] The same configuration and seed produce identical CSV
      content in the documented environment.
- [ ] Generation does not depend on the current date.
- [ ] The output contains the agreed required columns.
- [ ] Generated values obey the documented validation rules.
- [ ] Each customer-month pair is unique.
- [ ] Observation months are fully observed calendar months.
- [ ] Records represent customers eligible for the start-of-month
      cohort defined in docs/data-design.md.
- [ ] If customers appear across several months, their eligibility
      and subscription history follow documented rules.
- [ ] Generation assumptions and synthetic-data limitations
      are clearly documented.
- [ ] Tests and reproduction instructions are provided.

## 6. E2-02 — CSV schema and value validation

### Objective

Detect invalid input before writing customer records to PostgreSQL.

### Work

- Validate required columns and document the treatment of
  missing, additional or repeated column names.
- Validate identifiers, dates, categories and numeric values.
- Define accepted Boolean representations.
- Detect duplicate customer-month pairs within the input file.
- Report errors with the row, field and explanation.
- Test valid files and representative invalid cases.

### Acceptance criteria

- [ ] A valid sample passes validation.
- [ ] Missing required columns produce a clear error.
- [ ] Missing required values and invalid types are rejected.
- [ ] Observation months use the documented date format and
      the first day of the month.
- [ ] Plans belong to the documented allowed categories.
- [ ] Numeric values meet the documented constraints;
      non-finite values are rejected.
- [ ] Missing cancellation information is not interpreted as false.
- [ ] Duplicate customer-month pairs within a CSV are reported.
- [ ] Validation messages identify the relevant row or column.
- [ ] Validation tests cover both valid and invalid inputs.

## 7. E2-03 — PostgreSQL storage and import

### Objective

Store validated records reliably without creating duplicate
customer-month observations.

### Proposed import policy

Validate the complete file before writing records.
If validation fails, import no records.

Use a database transaction so a write failure does not leave
a partially imported dataset.

Enforce uniqueness on (customer_id, observation_month).

For an observation already stored:

- Identical values: skip the record and report it as unchanged.
- Different values: report a conflict and reject the import.
- Do not silently overwrite existing observations.

### Work

- Implement the required customer and customer-month tables.
- Document the command that creates the schema.
- Add database constraints consistent with the data contract.
- Implement the command-line import.
- Report inserted and unchanged record counts.
- Test repeat imports, conflicts and persistence.

### Acceptance criteria

- [ ] The database schema can be created using documented commands.
- [ ] A valid CSV is imported successfully.
- [ ] Imported values match the validated source records.
- [ ] The database enforces customer-month uniqueness.
- [ ] Reimporting an identical file creates no additional records.
- [ ] Conflicting existing observations produce clear errors.
- [ ] Invalid files and failed imports leave no partial additions.
- [ ] Import results report inserted and unchanged counts.
- [ ] Records remain available after restarting the application.
- [ ] Records remain available after stopping and starting the
      database container while preserving its named volume.
- [ ] Integration checks use an isolated test database or schema
      and do not delete the project's working data.

## 8. Verification strategy

Automated checks:

- Generator reproducibility and data-rule tests.
- CSV validation tests.
- Database import, duplicate and conflict tests.
- Existing backend tests.

Manual integration demonstration:

1. Generate the documented example dataset.
2. Validate and import it.
3. Query stored records and confirm expected counts and values.
4. Import the same file again and confirm no duplicates.
5. Try invalid input and show an understandable error.
6. Restart services and confirm that records remain available.

Run the frontend build if frontend files change and as part
of the final integrated regression check.

Record commands, dates, results and relevant screenshots.
Distinguish automated tests from manual integration checks.

## 9. Proposed schedule

- October 19: planning, task issues and sprint-start message.
- October 20–22: E2-01 — generator, rules and tests.
- October 23–25: E2-02 — validation and error cases.
- October 26–29: E2-03 — database import and integration checks.
- October 30: resolve remaining problems and rehearse the demo.
- October 31: final checks, review, retrospective and submission.
- November 1: board review and preparation for the next sprint.

The schedule is a planning assumption.
Use the buffer where necessary and report scope changes honestly.

## 10. Learning and reading

Continue studying relevant concepts from Dan Olsen's
The Lean Product Playbook using legally accessible publisher
excerpts and official author resources.

Focus on:

- Connecting data requirements to the target user's needs.
- Limiting the first implementation to a useful, testable scope.
- Making product and synthetic-data assumptions explicit.
- Preparing prototypes and questions for future user feedback.
- Working in small increments and recording what was learned.

Study a relevant concept before the implementation decision
it informs, then record the application after the work.

Create docs/sprint-2-reading-notes.md during the sprint.
For each reading session, record:

- The actual source and section studied.
- The main idea in the student's own words.
- Its concrete application to StreamRetain.
- Remaining uncertainties and the next learning step.

Explanations will be discussed in French.
Repository reading notes will be written in English.

Distinguish software verification from product validation.
Passing data tests does not prove that the product meets
real retention managers' needs.

Do not claim to have read full chapters when only an excerpt
or an author presentation was studied.

Confirm any additional assigned Sprint 2 reading against
the professor's semester plan.

## 11. Working habits from the Sprint 1 retrospective

### Short, regular sessions

Use the daily two-hour session for a small, explicit objective.
End by recording the next action.

### Immediate evidence capture

Record meaningful results immediately after verification.
Attach evidence before moving a task to Done.

If a task takes longer than expected, update the estimate
and review the remaining scope.

## 12. Definition of Done

A task is Done when:

- Its acceptance criteria are satisfied.
- Relevant tests and checks pass.
- The student can explain the implementation and results.
- Documentation and evidence are recorded.
- Changes are committed and pushed.
- The board reflects the actual status.

Close E2 only when all its required tasks are complete
and its acceptance criteria have been verified.

## 13. Review and delivery

Prepare:

- A short English demonstration, targeting 3–5 minutes.
- A factual sprint review.
- A retrospective with practical improvements.
- Reading takeaways from sources actually studied.
- Repository, board and evidence links.

The proposed submission target is October 31 in the evening,
subject to confirmation against the course schedule.

Record the actual submission date.
Do not mark unfinished work as complete.

## 14. Boundaries and interpretation

All customer records are synthetic.

Generated associations reflect modelling assumptions.
They do not establish real cancellation causes or retention
effectiveness at IVI.

The customer-month definition and cancellation metric must remain
consistent with docs/data-design.md.

E3 remains outside the current sprint commitment.
Any scope change must be explicitly documented.