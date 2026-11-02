# Sprint 3 — Verified indicators and customer comparisons

Student: Emmanuel Kamate
Group: M80-103CB-26
Project: StreamRetain

Dates: November 2–15, 2026.
Status: Planning. Implementation has not started.

## 1. Sprint goal

Enable the retention manager to view verified monthly
indicators and compare cancellation rates across subscription
plans using stored synthetic customer-month observations.

## 2. Capacity and estimates

Planned availability: approximately two hours per day.
Total planning capacity: 28 hours.

Estimates include learning, implementation and task-level tests.

| Work | Estimated hours |
|---|---:|
| E3-01 — Indicator definitions, calculations, tests and API | 6 |
| E3-02 — Angular indicators and interface states | 7 |
| E3-03 — Month and subscription-plan filters | 3 |
| E3-04 — Subscription-plan comparisons | 4 |
| S3-05 — Reading, final verification, demo and retrospective | 3 |
| Buffer | 5 |
| Total | 28 |

These are planning estimates, not recorded working hours.
Review scope if implementation or learning takes longer.

## 3. Dependencies and starting point

E2 provides the synthetic generator, CSV validator and
transactional PostgreSQL importer.

The current example contains 100 customer-month observations
for September 2026.

The Angular interface currently displays connection status.
The analytical dashboard is not implemented yet.

Parent epic:
https://github.com/KAMATE12/RtreamRetain/issues/11

## 4. Included scope

- Documented monthly indicator definitions.
- Backend calculations and a read-only API.
- Customer counts and cancellation-request counts.
- Monthly cancellation rates.
- Average monthly viewing hours per cohort customer.
- Angular display of the indicators.
- Observation-month and subscription-plan filters.
- Subscription-plan comparisons with counts and rates.
- Loading, empty-data and API-error states.
- Known-dataset tests and integration verification.
- Reading notes, demonstration and sprint review.

A clear comparison table is sufficient for the first version.
Charts are not required to demonstrate correct comparisons.

## 5. Deferred and excluded work

The activity filter remains part of E3 but is deferred.
Its category definitions and implementation require later planning.

E3 must remain open while this retained requirement is unfinished.

Retention-action management under E4 is outside this sprint.
Its previous Sprint 3 allocation must be revised in the backlog.

The following are also outside this sprint:

- An Angular CSV upload interface.
- Subscription-history schema changes.
- Individual cancellation prediction.
- Machine learning.
- Public application deployment.

The command-line import remains available.

## 6. Cohort and metric definitions

Each observation for a selected month is assumed to represent
a customer active at the beginning of that month.

Customers joining later in the month must be excluded during
dataset preparation.

The current schema cannot independently verify eligibility:
it has no subscription start date or explicit eligibility field.

Do not use tenure_months > 0 as an eligibility rule.
An eligible customer can have zero completed months of tenure.

Only fully observed months should be used for final monthly rates.
Observation-period completeness remains a dataset assumption.

For the selected month and plan scope:

- Cohort size: number of distinct represented customers.
- Cancellation count: cohort customers with
  cancelled_in_month = true.
- Cancellation rate (%): 100 × cancellation count / cohort size.
- Average viewing hours: total viewing_hours / cohort size.

A customer who requests cancellation remains in the denominator.

Average viewing hours includes all selected cohort customers,
including those who requested cancellation.

When the cohort is empty:

- Counts are zero.
- Rate and average are unavailable.
- The API represents unavailable values as null.
- Angular displays "No data" for those values.

A non-empty cohort with no cancellations has a rate of 0%.
This differs from an empty cohort.

Rounding is for display. Calculation and test expectations
must document precision and rounding rules.

## 7. Filtering and comparisons

Select one observation month at a time.

The subscription-plan selector offers:
All plans, Basic, Standard and Premium.

The same month and plan scope must apply to the summary
indicators and comparison results.

With All plans selected, show each plan represented in that
month's data.

With a single plan selected, show only that plan and calculate
the summary for the same selected group.

A group without observations must not be presented as having
a measured cancellation rate of 0%.

Changing a filter must not leave values labelled with the new
selection while still showing results from the old selection.

Document the behavior when no months or matching records exist.

## 8. Task breakdown

### E3-01 — Verified indicators and API

Document definitions, response fields and precision rules.
Implement the calculations and read-only API.
Provide the observation months available in stored data.

Acceptance examples:

- 100 eligible customers and 12 cancellations produce 12%.
- Eligible customers with tenure_months = 0 remain included.
- A non-empty cohort with no cancellations produces 0%.
- An empty cohort produces null rate and average.
- Average viewing hours matches a manually calculated example.
- Different observation months are not mixed.
- Invalid filter inputs produce understandable API errors.
- Database errors do not expose credentials.

### E3-02 — Angular indicators

Display the selected month's cohort size, cancellation count,
cancellation rate and average viewing hours.

Label units and explain that the rate measures cancellation
requests among the beginning-of-month cohort.

Provide understandable loading, empty-data and error states.
Show that all data is synthetic.

### E3-03 — Month and plan filters

Connect the selectors to the API.
Apply consistent scope to indicators and comparisons.
Verify changes between selections and no-match cases.

Activity filtering remains deferred and must not be marked done.

### E3-04 — Plan comparisons

Display each selected plan's cohort size, cancellation count
and cancellation rate.

Verify results using plans with different customer counts.
Do not compare raw cancellation counts without their denominators.

Explain that associations are not proof of causation.

### S3-05 — Learning and sprint delivery

Record actual reading sources and takeaways.
Run final regression checks.
Prepare and rehearse an English demonstration.
Write the review and retrospective.
Submit the required materials and record actual evidence.

## 9. Verification strategy

Use small, known datasets with expected results calculated
before running the implementation.

The generated example is useful for demonstration, but is not
a substitute for a controlled calculation test.

Include multiple months and plans in isolated test fixtures.
Do not require modifying the project's working dataset.

Database integration tests must use isolated schemas or databases.
Cleanup must preserve working data.

Run relevant existing backend tests and the frontend build.
Check browser behavior against known API results.

Record commands, dates and observed outcomes.
Distinguish local database integration results from CI checks.

## 10. Reading and learning

The course schedule assigns Martin Kleppmann's
Designing Data-Intensive Applications to Sprint 3.

Select legally accessible author or publisher resources
before the implementation decisions they inform.

Topics to investigate:

- Reliability and correctness of data processing.
- Maintainability and understandable responsibilities.
- Data models and query patterns for descriptive analysis.
- Aggregation and the distinction between transactional
  operations and analytical queries.

Record the exact source, edition, section and actual reading scope.
Do not claim full chapters or complete-book reading when only
an excerpt was studied.

For each session, record:

- The idea in the student's own words.
- Its application to a StreamRetain decision.
- Remaining uncertainty.
- A concrete next step.

Use French for discussion and English for repository notes.

Planned file: docs/sprint-3-reading-notes.md.

## 11. Working habits and board rules

Continue short, regular sessions and immediate evidence capture.

Before implementing a function, describe its responsibility,
one representative input, the expected result and an error case.

Split functions when doing so improves clarity.
Do not use line count alone as the criterion.

Keep at most two tasks across In Progress and Testing,
with one implementation task actively worked on at a time.

Assign Sprint 3 to task issues.
Keep the Sprint field on the parent epic empty.

Task issue links will be added after creation.
Planning identifiers are not GitHub issue numbers.

## 12. Proposed schedule

- November 2: planning, task issues, sprint announcement and reading.
- November 3–5: indicator definitions, calculations and API.
- November 6–9: Angular indicators and interface states.
- November 10–11: filters.
- November 12: comparisons.
- November 13: integration checks, corrections and demo rehearsal.
- November 14: sprint review and proposed evening submission.
- November 15: board review and next-sprint preparation.

Confirm submission timing against the professor's instructions.
Report the actual submission date.

## 13. Definition of Done

Each task meets its acceptance criteria and can be explained
by the student.

Relevant tests pass, evidence is recorded, documentation is
updated and changes are committed and pushed.

Do not close the entire E3 epic merely because Sprint 3 ends.
Deferred retained requirements remain visible.

The final demonstration must show implemented behavior.
Target 3–5 minutes unless the instructor accepts another duration.

## 14. Risks and interpretation limits

The available project example covers only one month.
Multiple-month behavior must therefore be verified with
controlled test data.

Synthetic data does not establish real IVI behavior,
cancellation causes or retention effectiveness.

Same-month viewing may be affected by cancellation.
It must not be presented as proof of a cause or as a validated
predictive feature.

Product assumptions have not been validated with real
retention managers.

## 15. Separate follow-up from Sprint 2

The Sprint 2 demonstration was submitted in the course chat.
An additional GitHub Release copy remains pending.

This upload follow-up is separate from Sprint 3 functionality.