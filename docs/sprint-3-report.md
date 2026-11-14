# Sprint 3 — Review and retrospective

Project: StreamRetain

Student: Kamate Emmanuel

Group: M80-103CB-26

Sprint: November 2–15, 2026

Report updated: November 14, 2026

Status: demonstration and documents submitted; issue #22 closed and Sprint 3 cards marked Done

## Sprint goal and outcome

The technical goal was to provide a dashboard for inspecting monthly
customer indicators and comparing subscription plans using the same
month and plan filters.

The delivered application provides:

- Read-only monthly indicator and available-month APIs.
- Angular summary indicators and explicit interface states.
- Observation-month and subscription-plan selectors.
- A subscription-plan comparison API and table.
- Coordinated summary and comparison loading.
- Current-selection retry and obsolete-request cancellation.

The English demonstration has been recorded and published on GitHub.
The student verified the downloaded archive and video playback.
The instructor approved the actual duration of 12 minutes 15 seconds.

The student confirmed submitting the demonstration, sprint review,
retrospective and reading notes in the course chat on November 14, 2026.

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
| Sprint 3 learning, review and demonstration | Completed; materials submitted, issue #22 closed and card marked Done |

Activity-based filtering remains deferred under epic #11.
Completion of this sprint does not automatically close the epic.

The additional Sprint 2 GitHub Release upload remains a separate
follow-up and is not part of this task.

## Verification evidence

Detailed definitions, API fields, tests and browser observations:
[Monthly indicators dashboard](monthly-indicators-dashboard.md).

### Local backend verification

Executed from `backend` with `STREAMRETAIN_DB_TESTS=1`:

```powershell
..\.venv\Scripts\python.exe -m pytest
```

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

Executed from `frontend`:

```powershell
npm.cmd test -- --watch=false
```

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

Executed from `frontend`:

```powershell
npm.cmd run build
```

Latest recorded result on November 12, 2026:

- Build succeeded in 4.276 seconds.
- Initial bundle total: 240.23 kB.
- Estimated transfer size: 65.77 kB.
- Output: `frontend/dist/frontend`.
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

- 38 + 19 + 43 = 100 customers.
- 7 + 3 + 9 = 19 requests.

The overall cancellation-request rate is calculated from combined counts:
19 / 100 × 100 = 19%.

It is not an unweighted average of the displayed plan rates.

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

- Only September 2026 was available for browser checks using the
  working synthetic dataset.
- Changing between two stored months was not manually demonstrated.
- The new comparison table has no recorded narrow-screen check.
- No separate manual network-timing experiment is claimed.
- Separate summary and comparison requests do not guarantee a shared
  database snapshot during concurrent imports.
- No user research or product validation was performed.
- No causation or statistical significance is established.
- Activity-based filtering remains deferred.
- Further reading on data models and analytical queries remains future work.
- The interface is a functional prototype and needs visual refinement.
- The demonstration and documents have been submitted.
  Final issue and board review completed on November 14, 2026.

Existing passing checks are retained as dated evidence.
Future implementation changes require appropriate verification.

### Proposed interface improvements

The project author identified presentation issues in the current interface:
a narrow content column on a large screen, substantial unused space,
and technical connection information appearing before the main dashboard.

Proposed improvements for future sprint planning include:

- Improve the use of available screen width.
- Make key indicators easier to identify and read.
- Improve the visual hierarchy of filters, summary values and comparisons.
- Move technical connection checks to a secondary area.
- Verify the revised layout on narrow screens and with keyboard navigation.

These are proposals, not completed improvements or a confirmed commitment
for a particular future sprint.

## Reading and learning

See [Sprint 3 reading notes](sprint-3-reading-notes.md).

The completed reading includes:

- Three sections of the official DDIA presentation:
  "Compare several designs", "Both theory and practice",
  and "Deeper understanding".
- The section "What are you using that lock for?" from Martin
  Kleppmann's article "How to do distributed locking".

The student confirms that both readings preceded implementation.
Exact reading dates have not been recorded.
Earlier AI-assisted drafts incorrectly described them as
post-implementation reading. This report corrects that chronology.

The main takeaways concern design trade-offs and the distinction
between correctness and efficiency.

For StreamRetain, a comparison table provides exact counts and rates
without requiring an additional visualization.

Preventing duplicate customer-month observations during an identical
reimport is a correctness requirement. Processing time and resource
consumption are separate efficiency questions.

The previously recorded import verification showed:

- Initial import: 100 inserted observations.
- Identical reimport: 0 inserted and 100 unchanged observations.

These results are not a performance benchmark or proof of all
concurrent-import cases.

Guided discussions also clarified:

- Waiting for both responses does not guarantee a shared database snapshot.
- Cancellation counts and cancellation rates answer different questions.
- An unavailable rate differs from a measured 0%.
- A customer may have observations in different months without duplication.
- Monthly calculations must select the requested observation month.
- Synthetic associations do not establish causation.

These discussions are distinguished from the source material actually read.
No complete book, full chapter or full article reading is claimed.

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

The delivered interface supports the required workflow, but I am not
satisfied with its visual presentation. Improving it should be planned
alongside the remaining product work.

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

## English demonstration

The recording is complete and published:

[StreamRetain — Sprint 3 demonstration](https://github.com/KAMATE12/RtreamRetain/releases/tag/sprint-3-demo)

Original target duration: 3–5 minutes unless another duration is accepted.

Actual duration: 12 minutes 15 seconds.

Duration exception: the student confirms that the instructor approved
this duration for Sprint 3.

The preparation plan covered:

1. Introduce StreamRetain, the retention manager and synthetic data.
2. Show a known month's summary and explain the beginning-of-month cohort.
3. Select Premium and compare its summary with the matching table row.
4. Return to All plans and explain counts, denominators and rates.
5. Demonstrate error handling and retry.
6. Explain empty data versus 0%, technical evidence and limitations.

The working dataset contains only one available month.
Multiple-month and empty-scope verification comes from controlled tests,
rather than a manual demonstration with multiple stored months.

All observations are synthetic. They do not establish causation,
statistical significance or proven retention effectiveness.

### Publication and playback verification

Published archive: `StreamRetain_Sprint3.zip`.

The student reported an approximate archive size of 639 MB.

The student confirmed:

- Listening to the complete local recording and finding the audio intelligible.
- Downloading the archive from the GitHub Release.
- Extracting the downloaded archive.
- Opening and successfully playing the published video.

These checks establish the student's successful access to the published
copy. Course-chat submission was separately confirmed by the student
on November 14, 2026.

## Submission record

Record updated: November 14, 2026.

The student confirmed submitting the demonstration, sprint review,
retrospective and reading takeaways in the course cha| Final issue and board review | Completed on November 14, 2026 |t on
November 14, 2026.

Final board review completed: November 14, 2026.
The board screenshot confirms that issues #18–#22 are closed and marked Done. Epic #11 remains open.

| Item | Status |
|---|---|
| Demonstration recording | Completed |
| Actual duration | 12 minutes 15 seconds |
| Accepted duration exception | Instructor approval confirmed by the student for Sprint 3 |
| Demonstration location | GitHub Release: sprint-3-demo |
| Published archive | StreamRetain_Sprint3.zip; approximately 639 MB, as reported by the student |
| Access and playback verification | Student downloaded the published ZIP, extracted it and successfully played the video |
| Course-chat submission | Completed; confirmed by the student |
| Actual course-chat submission date | November 14, 2026 |
| Submission message link | Not recorded |
| Initial publication of the two sprint documents | Commit 20e6ccd |
| Reading chronology corrections and demonstration evidence | Published in commit c14e6df |
| Final submission record | Added in this documentation update |
| Final issue and board review | Pending |

Demonstration:
[StreamRetain — Sprint 3](https://github.com/KAMATE12/RtreamRetain/releases/tag/sprint-3-demo)

Initial documentation publication:
[20e6ccd](https://github.com/KAMATE12/RtreamRetain/commit/20e6ccd)

Reading chronology corrections and demonstration evidence:
[c14e6df](https://github.com/KAMATE12/RtreamRetain/commit/c14e6df)

The duration approval, playback checks and course-chat submission
are recorded from the student's confirmation.
No written approval link or course-chat message link is included
in this record.

Task and board statuses must reflect the actual delivery state.
Epic #11 remains open while retained activity-filter work is deferred.