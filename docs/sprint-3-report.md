# Sprint 3 — Review and retrospective

Project: StreamRetain
Student: Kamate Emmanuel
Group: M80-103CB-26
Sprint: November 2–15, 2026
Report date: November 13, 2026
Status: draft — demonstration and course submission pending

## Sprint goal and outcome to date

The technical goal was to provide a dashboard for inspecting monthly
customer indicators and comparing subscription plans using consistent
month and plan filters.

The delivered application provides:

- Read-only monthly indicator and available-month APIs.
- Angular summary indicators and explicit interface states.
- Observation-month and subscription-plan selectors.
- A subscription-plan comparison API and table.
- Coordinated summary and comparison loading.
- Current-selection retry and obsolete-request cancellation.

All observations are synthetic.
Technical success does not establish product usefulness or actual
IVI customer behavior.

## Task status

| Task | Status |
|---|---|
| #18 — Monthly indicators and API | Completed; closure confirmed by project author |
| #19 — Angular indicators and interface states | Completed; closure confirmed by project author |
| #20 — Month and subscription-plan filters | Completed; closure confirmed by project author |
| #21 — Subscription-plan comparisons | Completed; closure confirmed by project author |
| Sprint 3 learning, review and demonstration | In progress |

Activity-based filtering remains deferred under epic #11.
Completion of this sprint does not automatically close the epic.

The additional Sprint 2 GitHub Release upload remains a separate
follow-up and is not part of this task.

## Verification evidence

Detailed definitions, API fields, tests and browser observations:
[Monthly indicators dashboard](monthly-indicators-dashboard.md).

### Local backend verification

Executed from backend with STREAMRETAIN_DB_TESTS=1:

    ..\.venv\Scripts\python.exe -m pytest

Recorded on November 12, 2026:

- 202 tests passed.
- No tests skipped.
- Duration: 5.03 seconds.
- One Starlette TestClient deprecation warning concerning httpx.

PostgreSQL tests used isolated schemas.
The working dataset was not replaced to satisfy tests.

A later run without the integration-test flag reported:

- 170 tests passed.
- 32 PostgreSQL tests skipped.
- Duration: 2.53 seconds.

These are different test configurations.
The later run does not replace the successful integration run.

### Local frontend verification

Executed from frontend:

    npm.cmd test -- --watch=false

Recorded on November 12, 2026:

- 2 test files passed.
- 8 service tests passed.
- 15 component tests passed.
- Total: 23 tests passed.
- The first complete E3-04 run reported 4.76 seconds.
- A subsequent run also passed all 23 tests.

Coverage includes filter forwarding, known results, empty scopes,
measured zeros, coordinated loading, errors, retry and cancellation
of obsolete requests.

Controlled frontend responses do not independently verify
backend calculations.

### Local production compilation

Executed from frontend:

    npm.cmd run build

Latest recorded result on November 12, 2026:

- Build succeeded in 4.276 seconds.
- Initial bundle total: 240.23 kB.
- Estimated transfer size: 65.77 kB.
- Output: frontend/dist/frontend.
- No warning appeared in the recorded build output.

### GitHub Actions

Implementation commit:
[766ef96](https://github.com/KAMATE12/RtreamRetain/commit/766ef96)

Verification documentation commit:
[c0a87f4](https://github.com/KAMATE12/RtreamRetain/commit/c0a87f4)

Implementation CI:
[Run 43151108867](https://github.com/KAMATE12/RtreamRetain/actions/runs/43151108867)

Observed results:

| Check | Result |
|---|---|
| Backend job | Success, 14 seconds |
| Frontend job | Success, 22 seconds |
| Frontend tests | 23 passed across 2 files |
| Production compilation | Success, 3.676 seconds |
| Initial bundle total | 240.23 kB |
| Estimated transfer size | 65.77 kB |

PostgreSQL tests were skipped in this CI configuration.
Database integration evidence comes from the separate local run.

Deprecation warnings remain documented maintenance work.
Successful CI does not resolve those warnings or previously recorded
dependency-audit findings.

## Integrated dashboard observations

Browser: Microsoft Edge on Windows.
Application: http://127.0.0.1:4200.
Recorded on November 12, 2026.

### All plans — September 2026

| Plan | Cohort size | Cancellation requests | Displayed rate |
|---|---:|---:|---:|
| Basic | 38 | 7 | 18.42% |
| Standard | 19 | 3 | 15.79% |
| Premium | 43 | 9 | 20.93% |

The summary displayed 100 customers, 19 requests, 19% and 57.14 hours.

Group counts reconcile with the summary:
38 + 19 + 43 = 100 customers;
7 + 3 + 9 = 19 requests.

### Single plan and return to All plans

Premium displayed one comparison row and matching summary values:
43 customers, 9 requests and 20.93%.

The summary displayed 57.71 average viewing hours.

Returning to All plans restored Basic, Standard and Premium
in the documented order.

### Errors and recovery

Screenshots document:

- An initial failure without results.
- An error with September / Premium still selected.
- Hidden summary values and comparison rows.
- A generic error message and Try again button.
- Recovery with matching Premium summary and comparison values.

Button-based retry is also covered by automated tests.

### Controlled verification

Isolated backend fixtures verify:

- Basic: 80 customers, 8 requests, 10%.
- Premium: 20 customers, 4 requests, 20%.
- Combined summary: 100 customers, 12 requests, 12%, not 15%.

Multiple months and empty selections are covered by controlled tests.
Frontend tests verify loading and cancellation-based protection
against outdated responses.

## Limitations and remaining work

- Only September 2026 was available for real-data browser checks.
- Changing between two stored months was not manually demonstrated.
- The new comparison table has no recorded narrow-screen check.
- No separate manual network-timing experiment is claimed.
- Separate summary and comparison requests do not guarantee a shared
  database snapshot during concurrent imports.
- No user research or product validation was performed.
- No causation or statistical significance is established.
- Activity-based filtering remains deferred.
- Further technical reading remains pending.
- The demonstration has not yet been recorded or submitted.

Existing passing checks will be retained as dated evidence.
Relevant checks must be repeated if implementation changes before delivery.

## Reading and learning

See [Sprint 3 reading notes](sprint-3-reading-notes.md).

On November 12, the student confirmed reading three sections of
the official DDIA presentation website.

The reading occurred after implementation.
It supported reflection on trade-offs and existing design decisions.

No complete book or chapter reading is claimed.
Guided explanations about data consistency and indicator interpretation
are recorded separately from the reading itself.

## Retrospective

### What went well

- Describing responsibilities, inputs, expected results and error cases
  before implementation helped me understand what to verify.
- Distinguishing 0% from "No data" was a particularly useful example.
- Separating backend calculations, Angular HTTP requests and interface
  behavior helped me understand where to intervene.
- Saving screenshots and test outputs during the work helped me prepare
  the review without repeating every verification.

### Difficulties

I tried to respect the planned working time, but unexpected requests
from other courses disrupted my organization.

I adapted my sessions to continue the project and complete the
technical tasks.

No precise actual-hours total is available, so compliance with every
task estimate is not claimed.

During implementation, a test was temporarily placed in the application
module. Inspection and test discovery identified the placement problem;
it was moved to the test file and the integration tests passed.

Copying nested Markdown blocks also interrupted documentation work.
The incomplete document was identified and completed before publication.

### Review of Sprint 2 improvement experiments

| Experiment | Observed outcome |
|---|---|
| Describe responsibilities, inputs, outputs and errors before coding | Helpful, especially for 0% versus unavailable data |
| Split by responsibility rather than line count | Helped identify where to change calculations, requests and interface behavior |
| Work in regular sessions | Difficult to sustain because of unexpected coursework; sessions were adapted |
| Capture evidence immediately | Helpful for preparing the sprint review |

### Practical improvements for the next sprint

1. Reserve time for unexpected coursework and define one small priority
   task for each work session.
2. Continue capturing evidence immediately, using descriptive filenames
   and recording the relevant command or scenario with each result.

## English demonstration plan

Target duration: 3–5 minutes, unless the instructor accepts another duration.

Planned sequence:

1. Introduce StreamRetain, the retention manager and synthetic data.
2. Show a known month's summary and explain the beginning-of-month cohort.
3. Select Premium and compare its summary with the matching table row.
4. Return to All plans and explain counts, denominators and rates.
5. Demonstrate error handling and retry.
6. Explain empty data versus 0%, technical evidence and limitations.

The working database currently has only one available month.
The demo must acknowledge this rather than imply a manual multi-month check.

Any simulated empty state must be identified as simulated.
Working data must not be erased for the demonstration.

The demo should explain that synthetic associations do not establish
causation, statistical significance or proven retention effectiveness.

## Submission record

Proposed submission: November 14, 2026, in the evening.
Confirmation against the instructor's instructions: pending.

Final board review target: November 15, 2026.

| Item | Status |
|---|---|
| Demonstration recording | Pending |
| Actual duration | Not recorded yet |
| Accepted duration exception | Not recorded |
| Demonstration location | Pending |
| Access and playback verification | Pending |
| Course-chat submission | Pending |
| Actual submission date | Not submitted yet |
| Submission message link | Not available |
| Publication of these two sprint documents | Pending |

The review, retrospective, reading takeaways and demonstration must
be submitted before completion is claimed.

Task and board statuses must reflect the actual delivery state.
Epic #11 remains open while retained activity-filter work is deferred.