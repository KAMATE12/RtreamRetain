# Monthly indicators dashboard — Implementation and verification

Project: StreamRetain

Tasks:
- E3-02 — Angular monthly indicators dashboard, issue #19.
- E3-03 — Observation-month and subscription-plan selectors, issue #20.
- E3-04 — Subscription-plan comparisons, issue #21.

Parent epic: #11 — Customer analysis dashboard.

Sprint: Sprint 3 — November 2–15, 2026.

## Purpose and scope

Display backend-calculated monthly indicators for a retention manager
and allow selection of an observation month and subscription plan.

All customer data is synthetic. Technical verification does not
establish product usefulness, causation or actual IVI customer behavior.

The dashboard displays:

- Beginning-of-month cohort size.
- Customers who requested cancellation during the selected month.
- Monthly cancellation-request rate.
- Average viewing hours per cohort customer.

Angular displays API results without recalculating the indicators.
The cohort is assumed to contain customers active at the beginning
of the month, including customers who requested cancellation during it.

E3-04 adds a subscription-plan comparison table using the same active
month and plan selection as the summary indicators.

The current E3-04 behavior and verification results are documented below.
E3-02 and E3-03 test counts and browser observations remain historical
evidence for those implementation stages.
Activity filters, CSV upload and retention actions are outside this scope.

## Implementation

- `indicators.models.ts` defines API response types, subscription plans,
  the combined month-plan selection and display states.
- `indicators.service.ts` retrieves available months and indicators,
  with an optional plan parameter.
- `indicators-panel.ts` manages available months, active selection,
  request cancellation, loading, empty results, errors and retry.
- `indicators-panel.html` displays labelled selectors, the active scope,
  indicator values and interpretation guidance.
- `indicators-panel.css` styles indicators, filters and interface states.
- `app.ts` and `app.html` integrate the panel into the application.

TypeScript interfaces describe the expected API contract.
They do not perform runtime response validation.

## Selection and filtering rules

### Initial selection

The dashboard requests `GET /api/observation-months`.

The API returns months from newest to oldest.
The first available month is initially selected with All plans.

The latest available month is a display default, not evidence that
the observation period is complete.

### Subscription plans

The selector offers:

- All plans.
- Basic.
- Standard.
- Premium.

Internally, All plans is represented by `null`.
For this selection, the service omits the API's `plan` parameter.

A specific plan is sent using its exact API value:
`Basic`, `Standard` or `Premium`.

Examples:

```text
/api/indicators?observation_month=2026-09-01
/api/indicators?observation_month=2026-09-01&plan=Basic
```

### Consistent scope

Every indicator request contains exactly one observation month
and, optionally, one subscription plan.

The same request returns all four indicators for that scope.
Angular does not combine indicators from separate filter selections.

Changing the month preserves the selected plan.
Changing the plan preserves the selected month.

A combination without observations remains selected.
The application does not silently switch to another plan.

The active month and plan remain visible while loading
and after an indicator request fails.

## Display precision

Counts are displayed as integers.

The API already expresses the cancellation-request rate as a percentage.
Angular appends the percent sign without multiplying the value.

Rates and average viewing hours use Angular DecimalPipe with
`digitsInfo` set to `1.0-2`: up to two fractional digits,
rounded for display. The underlying API values are not changed.

| API value | Display |
|---|---|
| `cancellation_rate: 19` | 19% |
| `cancellation_rate: 0` | 0% |
| `average_viewing_hours: 57.1351` | 57.14 hours |
| `average_viewing_hours: 0` | 0 hours |
| Null rate or average | No data |

The observation month is displayed as `YYYY-MM`.
Average viewing hours is labelled per cohort customer.

## Interface states and request behavior

### Loading

The dashboard displays "Loading monthly indicators…" while retrieving
available months or the indicators for the current selection.

Previous indicator values are cleared before requesting new results.
Missing results are not presented as measured zeros.

Once available months have loaded, the selectors remain visible
and usable while an indicator request is pending.

### Rapid selection changes

A Subject carries indicator-request selections.
RxJS `switchMap` replaces the previous indicator subscription
when a new selection is requested.

Unsubscribing cancels the obsolete Angular HTTP request.
Its response cannot subsequently update the displayed indicators.

Subscriptions are also cleaned up when the component is destroyed.

### Empty data

If the months endpoint returns an empty list, the dashboard displays:

"No observation months are available."

It does not send an indicator request with an invalid month.

If the selected month-plan combination has an empty cohort,
the dashboard displays:

"No observations are available for this month and plan selection."

Both empty cases display zero counts and "No data" for unavailable
rate and average values.

A non-empty cohort with no cancellation requests displays 0%.
An unavailable rate is never converted to a measured zero.

### API errors and retry

An error displays:

"Unable to load the indicators. Please try again."

Raw server error details are not displayed.
Previous indicator values remain hidden.

If an indicator request fails, the selected month and plan are preserved.
"Try again" requests indicators for that same current selection
without reloading the available-month list.

If initial month discovery fails, no valid selection exists yet.
In that case, "Try again" requests the available-month list again.

Errors are handled inside the indicator request stream so that
a failed request does not prevent later selections from working.

### Change from E3-02

E3-02 initially displayed the latest month and all plans without selectors.
Its retry behavior fetched the months again.

E3-03 preserves the active filters during indicator failures and retries.
It also replaces obsolete requests instead of blocking filter changes
until an earlier request completes.

## Automated verification — E3-03

Command, executed from `frontend`:

```powershell
npm.cmd test -- --watch=false
```

Observed on November 11, 2026:

- 2 test files passed.
- 20 tests passed.
- Service tests: 6 passed.
- Component tests: 14 passed.
- Vitest duration: 4.16 seconds.

### Service coverage

The six service tests verify:

- Available-months endpoint and response order.
- Default all-plans request and preservation of null indicators.
- Month and Basic plan forwarding.
- Month and Standard plan forwarding.
- Month and Premium plan forwarding.
- Explicit return to All plans after a filtered request,
  without retaining the previous plan parameter.

### Component coverage

The fourteen component tests verify:

- Loading without measured values during both initial requests.
- Available months, four plan choices and documented defaults.
- Display rounding without changing API values.
- Month changes and removal of previous values during loading.
- Plan changes and restoration of all-plans results.
- Preservation of Basic across month changes and measured zeros.
- Known Premium results for September.
- Empty results with Standard preserved across month changes.
- No indicator request when no observation months exist.
- Retry after an initial available-months failure.
- Preserved filters and current-selection retry after indicator failure.
- Selection changes after an indicator request fails.
- Cancellation of obsolete requests during rapid selection changes.
- Cancellation of a pending request when the panel is destroyed.

### Controlled dataset

Expected responses represent the following synthetic observations:

| Month | Plan | Viewing hours and cancellation request |
|---|---|---|
| September 2026 | Basic | 10 hours, yes; 30 hours, no |
| September 2026 | Premium | 40 hours, no; 40 hours, no |
| October 2026 | Basic | 0 hours, no |
| October 2026 | Premium | 20 hours, yes |
| Both months | Standard | No observations |

Expected results:

| Month | Plan | Customers | Requests | Rate | Average hours |
|---|---|---:|---:|---:|---:|
| September | All plans | 4 | 1 | 25% | 30 |
| September | Basic | 2 | 1 | 50% | 20 |
| September | Premium | 2 | 0 | 0% | 40 |
| September | Standard | 0 | 0 | No data | No data |
| October | All plans | 2 | 1 | 50% | 10 |
| October | Basic | 1 | 0 | 0% | 0 |
| October | Premium | 1 | 1 | 100% | 20 |
| October | Standard | 0 | 0 | No data | No data |

Responses are explicitly supplied using Angular HttpTestingController.
No records are inserted into PostgreSQL for these frontend tests.

These checks verify request parameters and rendered responses.
They do not independently verify backend aggregation calculations.

### Obsolete-request test

The rapid-selection test starts requests for:

1. October, All plans.
2. October, Basic.
3. September, Basic.

It verifies that the first two requests are cancelled.
The newest request completes and its September Basic values are displayed.

Attempts to flush the cancelled requests are rejected by the HTTP
testing backend. The displayed values remain unchanged.

This verifies cancellation-based protection against outdated responses.
It does not simulate successful delivery of cancelled network requests
or measure real-network timing.

## Production build — E3-03

Command, executed from `frontend`:

```powershell
npm.cmd run build
```

Observed on November 11, 2026:

- Production build succeeded.
- Build duration: 4.067 seconds.
- Initial bundle total: 236.36 kB.
- Estimated transfer size: 64.93 kB.
- Output: `frontend/dist/frontend`.
- No warning appeared in the recorded build output.

## Manual browser observations — E3-03

Browser: Microsoft Edge on Windows.

Application address: http://127.0.0.1:4200.

### Available data and API comparison

The real available-months endpoint returned:

```json
{"observation_months":["2026-09-01"]}
```

Only September 2026 was available in the working database.

Read-only requests to the indicators endpoint returned:

| Plan | Customers | Requests | API rate | API average hours |
|---|---:|---:|---:|---:|
| All plans | 100 | 19 | 19.0 | 57.1351 |
| Basic | 38 | 7 | 18.421052631578945 | 55.773421052631576 |
| Standard | 19 | 3 | 15.789473684210526 | 58.55736842105263 |
| Premium | 43 | 9 | 20.930232558139537 | 57.71 |

Expected display after rounding:

| Plan | Customers | Requests | Displayed rate | Displayed average |
|---|---:|---:|---:|---|
| All plans | 100 | 19 | 19% | 57.14 hours |
| Basic | 38 | 7 | 18.42% | 55.77 hours |
| Standard | 19 | 3 | 15.79% | 58.56 hours |
| Premium | 43 | 9 | 20.93% | 57.71 hours |

The recorded All plans screenshot matches the corresponding API values.

The previous independent CSV-to-API comparison is documented in
[Monthly indicators](monthly-indicators.md).

### Read-only verification command

The following PowerShell command was used to inspect the available month
and each plan's API response:

```powershell
$apiBase = "http://127.0.0.1:8000/api"

$monthsResponse = Invoke-RestMethod "$apiBase/observation-months"
$monthsResponse | ConvertTo-Json -Depth 3

if ($monthsResponse.observation_months.Count -gt 0) {
    $selectedMonth = $monthsResponse.observation_months[0]

    $results = foreach ($plan in @("", "Basic", "Standard", "Premium")) {
        $uri = "$apiBase/indicators?observation_month=$selectedMonth"

        if ($plan -ne "") {
            $uri += "&plan=$plan"
        }

        $result = Invoke-RestMethod $uri

        [PSCustomObject]@{
            Month         = $result.observation_month
            Plan          = $(if ($plan -eq "") { "All plans" } else { $plan })
            Customers     = $result.cohort_size
            Cancellations = $result.cancellation_count
            Rate          = $result.cancellation_rate
            AverageHours  = $result.average_viewing_hours
        }
    }

    $results | Format-Table -AutoSize
}
```

A PSReadLine paste exception appeared before the command ran.
The subsequent command completed and returned the results recorded above.

### Error with preserved filters and recovery

The browser verification sequence stopped FastAPI and selected Premium.

The error-state screenshot shows:

- Observation month: September 2026.
- Subscription plan: Premium.
- Matching active-selection labels.
- A generic error message.
- A "Try again" button.
- No previous indicator values.

After restarting FastAPI and following the retry procedure,
the supplied recovery screenshot shows Premium still selected with:

- 43 customers.
- 9 cancellation requests.
- 20.93% cancellation-request rate.
- 57.71 average viewing hours.

These values match the Premium API response after display rounding.

### Manual-verification limits

The working database contains only one available month.
Switching between two real stored months was therefore not checked.

All three real subscription plans have observations in September.
An empty month-plan combination was verified using controlled
component responses rather than by changing the working database.

The automated tests cover rapid changes and cancellation.
A separate manual network-timing check has not been recorded.

The supplied E3-03 screenshots show desktop All plans, Premium error
and Premium recovery states. They do not independently document every
plan's rendered values or the return from Premium to All plans.

A narrow-screen check of the new selectors has not yet been recorded.
Earlier E3-02 responsive evidence concerns the indicator layout.

Screenshots show visible states, not calculation correctness.
No product-user validation or physical-phone testing is claimed.

## Historical verification — E3-02

### Local tests and build

Recorded on November 9, 2026:

- 2 frontend test files passed.
- 10 tests passed.
- Vitest duration: 4.43 seconds.
- Production build succeeded in 4.087 seconds.
- Initial bundle total: 227.57 kB.
- Estimated transfer size: 62.59 kB.
- No bundle-budget warning appeared in the recorded output.

These are historical E3-02 results.
The current E3-03 local results are recorded separately above.

### Browser checks

E3-02 browser checks recorded:

- September 2026 all-plans values:
  100 customers, 19 requests, 19% and 57.14 hours.
- Generic error and hidden results when FastAPI was unavailable.
- Keyboard navigation to "Try again" and activation with Enter.
- Recovery after restarting FastAPI without reloading the page.
- Desktop indicator layout.
- Responsive emulation at 390 × 844, with readable stacked values
  and no horizontal overflow visible in the captured area.
- No-available-months state using an Edge local response override:
  `{"observation_months":[]}`.
- Zero counts and "No data" for that simulated empty state.

The empty-state check did not modify PostgreSQL.
Responsive emulation was not a physical-phone test.

A manual loading screenshot was not recorded.
Loading behavior was covered by automated tests.

### Publication and completion

- [Implementation commit 9517cb4](https://github.com/KAMATE12/RtreamRetain/commit/9517cb4)
- [Verification documentation commit bdf6e1e](https://github.com/KAMATE12/RtreamRetain/commit/bdf6e1e)
- [Issue #19](https://github.com/KAMATE12/RtreamRetain/issues/19)

The project author confirmed that completion evidence was added,
issue #19 was closed, its board card was moved to Done,
and the parent epic was updated.

## Dependency maintenance

During E3-02, framework and compiler packages were aligned to 21.2.26.
Angular CLI and Angular Build were updated to 21.2.29.

The resolved build dependencies included:

- Vite 7.3.7.
- Undici 7.30.1.

The recorded audit following that update reported:

- 16 moderate vulnerabilities.
- No high or critical vulnerabilities in that report.

The remaining findings involved glob, minimatch and the Angular CLI
dependency chain. They remain documented maintenance work.

The suggested forced remediation would upgrade Angular CLI to 22.
That major migration was not performed.

Installation-script warnings were also reported.
Subsequent tests and production builds succeeded.

The dependency files were committed in `9517cb4`.
No dependency-file change appears in the E3-03 status output reviewed
for this document. No new E3-03 audit result is claimed.

## Continuous integration

The frontend job in `.github/workflows/checks.yml` runs:

1. `npm ci`
2. `npm test -- --watch=false`
3. `npm run build`

The backend job remains unchanged by E3-03.

### Historical E3-02 CI evidence

GitHub Actions passed on November 10, 2026, for commit `9517cb4`.

- [Successful run](https://github.com/KAMATE12/RtreamRetain/actions/runs/42732797814)
- [Frontend logs](https://github.com/KAMATE12/RtreamRetain/actions/runs/42732797814/job/129554718031)

| Verification | Observed result |
|---|---|
| Overall workflow | Success, 31 seconds |
| Backend job | Success, 14 seconds |
| Frontend job | Success, 26 seconds |
| Dependency installation | npm ci succeeded |
| Frontend test files | 2 passed |
| Frontend tests | 10 passed |
| Vitest duration | 1.15 seconds |
| Production build | Succeeded |
| Angular build duration | 3.810 seconds |
| Initial bundle total | 227.57 kB |
| Estimated transfer size | 62.59 kB |

The summary confirms backend success.
No backend test count is inferred from those screenshots.

Dependency installation reported 16 moderate vulnerabilities
and installation-script warnings. The workflow also displayed
action-runtime deprecation annotations.

A successful workflow does not resolve these maintenance findings.

### E3-03 CI evidence

The implementation and documentation were committed and pushed
in commit `f2b36ad`:

`feat: filter monthly indicators by month and subscription plan`

Evidence:

- [Implementation commit](https://github.com/KAMATE12/RtreamRetain/commit/f2b36ad)
- [Successful CI run](https://github.com/KAMATE12/RtreamRetain/actions/runs/43123414181)
- [Frontend logs](https://github.com/KAMATE12/RtreamRetain/actions/runs/43123414181/job/130869320621)

The recorded frontend logs are dated November 11, 2026, in UTC.
The screenshots were reviewed on November 12, 2026.

| Verification | Observed result |
|---|---|
| Frontend job | Success, 23 seconds |
| Backend job | Success, 14 seconds |
| Dependency installation | npm ci succeeded |
| Frontend test files | 2 passed |
| Service tests | 6 passed |
| Component tests | 14 passed |
| Total frontend tests | 20 passed |
| Vitest duration | 1.43 seconds |
| Production build | Succeeded |
| Angular build duration | 4.380 seconds |
| Initial bundle total | 236.36 kB |
| Estimated transfer size | 64.93 kB |

The backend screenshot confirms successful pytest execution.
Its test breakdown is not expanded, so no backend test count
is inferred from this evidence.

The screenshots do not establish a new dependency-audit result
or resolution of previously documented maintenance findings.

## E3-04 — Subscription-plan comparisons

### Implementation and API contract

The dashboard now displays a comparison table below the summary.
Both sections reuse the panel's active `IndicatorSelection`.
No application-wide selection service is introduced.

Backend aggregation is implemented in `backend/app/indicators.py`.
The read-only route is implemented in `backend/app/main.py`:

GET /api/plan-comparisons

Query parameters:

| Parameter | Required | Meaning |
|---|---|---|
| observation_month | Yes | ISO date representing the first day of the selected month |
| plan | No | Basic, Standard or Premium, with exact capitalization |

Omitting `plan` includes all represented subscription plans.
The frontend omits this parameter when All plans is selected.

Example response for a controlled test fixture:

```json
{
  "observation_month": "2026-09-01",
  "plan": null,
  "comparisons": [
    {
      "plan": "Basic",
      "cohort_size": 80,
      "cancellation_count": 8,
      "cancellation_rate": 10.0
    },
    {
      "plan": "Premium",
      "cohort_size": 20,
      "cancellation_count": 4,
      "cancellation_rate": 20.0
    }
  ]
}

```

The response identifies the requested month and plan filter.
A null plan means All plans.

Each comparison contains:

- `plan`: subscription plan at the beginning of the month.
- `cohort_size`: beginning-of-month cohort customer count.
- `cancellation_count`: customers who requested cancellation during the month.
- `cancellation_rate`: cancellation count divided by cohort size, multiplied by 100.

Cohort assumptions match those used for the summary indicators.

Groups follow the stable order Basic, Standard, Premium.
Only represented plans are returned.
An empty scope returns `comparisons: []`, without invented zero-rate groups.

Invalid month or plan parameters return HTTP 422.
Configuration or database failures return HTTP 503 with a generic message.
Raw database details and credentials are not exposed.

Backend rates are not rounded for presentation.
Angular displays up to two decimal places and appends the percent sign.

### Coordinated loading, errors and retry

This section supersedes the earlier single-indicator-request behavior.

Each selection triggers two requests with identical month and plan filters:
one for summary indicators and one for plan comparisons.

RxJS `forkJoin` waits for both responses before displaying either section.
Previous summary values and comparison rows are cleared during loading.

If either request fails, both result sections remain hidden.
The selected filters remain visible.
Try again repeats both requests for the current selection.

If initial month discovery fails, no selection exists yet.
Retry therefore reloads the available months first.

RxJS `switchMap` cancels the previous request pair when the selection changes.
Obsolete responses cannot replace results for the current selection.
Pending subscriptions are also cancelled when the panel is destroyed.

An empty scope displays zero summary counts and "No data" for unavailable
indicators, together with an explanatory comparison message and no rows.

The two endpoints use separate database requests.
Coordinated rendering does not guarantee a shared database snapshot
if an import changes the data between those requests.

### Known-dataset verification

Isolated PostgreSQL fixtures use unequal group sizes:

| Scope | Cohort size | Cancellation requests | Rate |
|---|---:|---:|---:|
| Basic | 80 | 8 | 10% |
| Premium | 20 | 4 | 20% |
| All plans | 100 | 12 | 12% |

The overall rate is 12 / 100 × 100 = 12%.
It is not the unweighted average of the two plan rates, which would be 15%.

Integration tests verify grouped calculations and real HTTP responses,
different months, single-plan filters, empty results and stable ordering.

Group counts reconcile with the corresponding summary.
Stored table contents are checked before and after the read operations.
Database tests use isolated schemas and preserve working data.

### Automated verification — November 12, 2026

The complete backend suite was run from `backend` with
`STREAMRETAIN_DB_TESTS=1`:

```powershell
..\.venv\Scripts\python.exe -m pytest
```

Observed result:

- 202 tests passed.
- No tests skipped.
- Duration: 5.03 seconds.
- One Starlette TestClient deprecation warning concerning httpx.

A later run without the integration-test flag reported:

- 170 tests passed.
- 32 PostgreSQL tests skipped.
- Duration: 2.53 seconds.
- The same deprecation warning.

The skipped tests in the later run do not replace the earlier
successful verification with PostgreSQL enabled.

Frontend command, executed from `frontend`:

```powershell
npm.cmd test -- --watch=false
```

Observed result:

- 2 test files passed.
- 8 service tests passed.
- 15 component tests passed.
- Total: 23 tests passed.
- The first complete E3-04 run reported a Vitest duration of 4.76 seconds.
- A subsequent run also reported 23 passing tests.

Frontend coverage includes:

- Summary and comparison request parameters.
- Available months and default selections.
- Known counts, rates and display rounding.
- Single-plan filtering and return to All plans.
- Preservation of the selected plan across month changes.
- Empty results and measured zeros.
- Waiting for both responses, whichever arrives first.
- Failures from either endpoint and current-selection retry.
- Removal of both result sections during loading and errors.
- Cancellation of obsolete request pairs and destruction cleanup.

Frontend tests use controlled HttpTestingController responses.
They do not contact PostgreSQL or independently verify backend calculations.

The testing backend rejects attempts to flush cancelled requests.
This verifies cancellation-based protection rather than successful
delivery of cancelled network responses.

### Production build — November 12, 2026

Command, executed from `frontend`:

```powershell
npm.cmd run build
```

Latest recorded result:

- Production build succeeded.
- Angular build duration: 4.276 seconds.
- Initial bundle total: 240.23 kB.
- Estimated transfer size: 65.77 kB.
- Output: `frontend/dist/frontend`.
- No warning appeared in the recorded build output.

The earlier E3-04 build also succeeded, in 5.903 seconds,
with the same recorded bundle sizes.

### Browser observations — November 12, 2026

Browser: Microsoft Edge on Windows.
Application address: http://127.0.0.1:4200.

For September 2026 with All plans selected, the table displayed:

| Plan | Cohort size | Cancellation requests | Displayed rate |
|---|---:|---:|---:|
| Basic | 38 | 7 | 18.42% |
| Standard | 19 | 3 | 15.79% |
| Premium | 43 | 9 | 20.93% |

The summary displayed 100 customers, 19 requests, 19% and 57.14 hours.

The counts reconcile:

- Cohort sizes: 38 + 19 + 43 = 100.
- Cancellation requests: 7 + 3 + 9 = 19.
- Overall rate: 19 / 100 × 100 = 19%.

With Premium selected, the table displayed only the Premium row.
Both sections displayed 43 customers, 9 requests and 20.93%.
The summary also displayed 57.71 average viewing hours.

A subsequent All plans capture showed all three groups again,
in the documented order.

Error-state screenshots show:

- An initial failure without a selection or displayed results.
- A failure with September 2026 and Premium still selected.
- The generic error message and Try again button.
- Both summary values and comparison rows hidden.

The recovery screenshot shows Premium selected with matching summary
and comparison results: 43 customers, 9 requests and 20.93%.

Screenshots document visible states.
Button-based retry and current-selection request behavior are also
verified by automated tests.

### Verification and interpretation limits

Only September 2026 was available in the working database.
Multiple months and empty scopes were verified using controlled fixtures.

A separate manual network-timing check and a narrow-screen check
of the new comparison table have not been recorded.

Earlier E3-02 responsive evidence concerns the indicator layout,
not the newly added comparison table.

Group sizes are displayed alongside rates.
A higher rate is a reason for investigation, not proof that
the subscription plan caused cancellations.

No statistical significance testing is implemented.
All data is synthetic.
These results do not establish actual IVI behavior, proven retention
effectiveness or product usefulness.

## E3-04 publication and CI evidence

The implementation, tests and verification documentation were committed
and pushed in commit `766ef96`:

`feat: compare subscription plans with coordinated dashboard filters`

Evidence:

- [Implementation commit](https://github.com/KAMATE12/RtreamRetain/commit/766ef96)
- [Successful CI run](https://github.com/KAMATE12/RtreamRetain/actions/runs/43151108867)
- [Backend logs](https://github.com/KAMATE12/RtreamRetain/actions/runs/43151108867/job/130960193939)
- [Frontend logs](https://github.com/KAMATE12/RtreamRetain/actions/runs/43151108867/job/130960194233)

The recorded build logs are dated November 12, 2026, in UTC.

| Verification | Observed result |
|---|---|
| Backend job | Success, 14 seconds |
| Frontend job | Success, 22 seconds |
| Frontend dependency installation | npm ci succeeded |
| Frontend test files | 2 passed |
| Service tests | 8 passed |
| Component tests | 15 passed |
| Total frontend tests | 23 passed |
| Production build | Succeeded |
| Angular build duration | 3.676 seconds |
| Initial bundle total | 240.23 kB |
| Estimated transfer size | 65.77 kB |

The backend CI log shows 202 collected tests and skipped PostgreSQL
tests. This CI run must not be presented as a PostgreSQL integration run.

The separate local execution with STREAMRETAIN_DB_TESTS=1 passed
all 202 tests without skips, as documented above.

The CI screenshots also show deprecation warnings, including the
Starlette TestClient httpx warning and a Node.js punycode warning
during action cleanup. These did not fail the jobs.

No new dependency-audit result or resolution of existing maintenance
findings is claimed.

## Completion status

E3-02 and E3-03 were published.
The project author confirmed completion of their issue and board updates.

E3-03 CI documentation was published in commit `6576041`,
following implementation commit `f2b36ad`.

E3-04 implementation, tests and documentation were published in `766ef96`.
Local backend and frontend tests, production compilation and the
corresponding GitHub Actions checks passed.

Browser observations and verification limitations are recorded above.

Remaining E3-04 completion work:

- Publish this documentation update containing the CI evidence.
- Add implementation, documentation and browser evidence to issue #21.
- Review acceptance criteria against the recorded evidence.
- Update issue #21, the project board and parent epic #11.

Technical verification does not establish product validation.