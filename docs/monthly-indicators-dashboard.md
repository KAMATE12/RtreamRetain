# Monthly indicators dashboard — Implementation and verification

Project: StreamRetain
Task: E3-02 — Angular monthly indicators dashboard
Issue: #19
Sprint: Sprint 3 — November 2–15, 2026

## Purpose and scope

Display backend-calculated monthly indicators for a retention manager
without requiring terminal commands.

All customer data is synthetic. Technical verification does not
establish product usefulness, causation or actual IVI customer behavior.

The initial view selects the first month returned by
GET /api/observation-months, whose documented order is newest first.
It then requests GET /api/indicators with observation_month.

The plan parameter is omitted, so all subscription plans are included.
Interactive month and plan selectors belong to E3-03.
Plan comparisons belong to E3-04.

The latest available month is a display default, not evidence that
the observation period is complete.

## Implementation

- indicators.models.ts defines the API response types and display states.
- indicators.service.ts performs the two read-only HTTP requests.
- indicators-panel.ts selects the latest month and manages loading,
  ready, empty and error states.
- indicators-panel.html displays values and interpretation guidance.
- indicators-panel.css provides desktop and narrow-screen layouts.
- app.ts and app.html integrate the panel into the existing application.

TypeScript interfaces describe the expected API contract.
They do not perform runtime response validation.

Angular displays the API results without recalculating the indicators.
The cohort is assumed to contain customers active at the beginning
of the month, including customers who requested cancellation during it.

## Display precision

Counts are displayed as integers.

The cancellation-request rate is already expressed as a percentage
by the API. Angular appends the percent sign without multiplying it.

Rates and average viewing hours use Angular DecimalPipe with
digitsInfo set to 1.0-2: up to two fractional digits, rounded for display.
The underlying API values are not changed.

Examples:

| API value | Display |
|---|---|
| cancellation_rate: 19 | 19% |
| cancellation_rate: 0 | 0% |
| average_viewing_hours: 57.1351 | 57.14 hours |
| average_viewing_hours: 0 | 0 hours |
| null rate or average | No data |

The observation month is displayed as YYYY-MM.
Average viewing hours is labelled per cohort customer.

## Interface states

### Loading

Display "Loading monthly indicators…" while retrieving months
and then indicators. Do not display missing results as measured zeros.

Previous results and the previous month are cleared before a new load.
Overlapping loading attempts are prevented.

### Empty data

If the months endpoint returns an empty list, display
"No observation months are available."
Do not request monthly indicators.

If the selected month has an empty cohort, display
"No observations are available for this month."

Both empty cases display zero counts and "No data" for unavailable
rate and average values.

### API error and retry

An error from either endpoint displays:
"Unable to load the indicators. Please try again."

The interface exposes a "Try again" button and hides previous results.
Raw server error details are not displayed.

Retry requests the available months again and then the latest month's
indicators. A successful retry restores the indicator display.

## Automated frontend verification

Command, executed from frontend:

    npm.cmd test -- --watch=false

Observed on November 9, 2026, after styling:

- 2 test files passed.
- 10 tests passed.
- Vitest duration: 4.43 seconds.

The service tests verify:

- Available-months endpoint and response order.
- Selected-month forwarding, omitted plan filter and preserved nulls.

The component tests verify rendered content for:

- Loading during both requests without measured values.
- Latest-month selection, known values and display rounding.
- Measured zero rate and zero viewing hours.
- Empty cohort with null indicators.
- No available months and no unnecessary indicator request.
- Months-endpoint failure followed by retry through the button.
- Indicators-endpoint failure followed by retry through the button.
- Removal of previous results during reload and after failure.

HTTP responses are controlled using Angular HttpTestingController.
These tests do not contact FastAPI or PostgreSQL and do not verify
backend calculations or visual layout.

## Production build

Command, executed from frontend:

    npm.cmd run build

Observed on November 9, 2026, after styling:

- Production build succeeded.
- Build duration: 4.087 seconds.
- Initial bundle total: 227.57 kB.
- Estimated transfer size: 62.59 kB.
- Output: frontend/dist/frontend.
- No bundle-budget warning appeared in the recorded output.

## Manual browser observations

Browser: Microsoft Edge on Windows.
Application address: http://127.0.0.1:4200.

### Real API data

The dashboard displayed September 2026 with:

- Cohort size: 100.
- Cancellation-request count: 19.
- Cancellation-request rate: 19%.
- Average viewing hours: 57.14 hours.

These displayed values match the previously verified API response:
100, 19, 19.0 and 57.1351 respectively, with display rounding applied.

The independent CSV-to-API comparison is recorded in
[Monthly indicators](monthly-indicators.md).

### API unavailable and restored

With FastAPI stopped and the page reloaded, the dashboard displayed
the generic error and retry button without indicator values.

After FastAPI restarted, the indicator values were displayed again.
Screenshots record both states.

The button-based retry behavior is also covered by automated tests.

### Layout

The desktop screenshot shows labels beside values.

An Edge responsive-mode check at 390 × 844 shows values below their
labels, wrapped text and all four indicators readable.
No horizontal overflow is visible in the captured area.

This is browser device emulation, not a physical-phone test.

### Remaining manual checks

On November 10, 2026, the no-available-months state was manually
verified in Microsoft Edge using a local response override:
{"observation_months":[]}.

The interface displayed "No observation months are available.",
zero counts and "No data" for the rate and average.
A screenshot records the result. PostgreSQL data was not modified.

Loading behavior is covered by automated tests; a manual loading
screenshot has not yet been recorded.

On November 10, 2026, keyboard navigation to "Try again" and
activation with Enter were manually checked. After restarting
FastAPI, retry restored the indicators without reloading the page.

## Dependency maintenance

The installed framework and compiler packages were aligned to 21.2.26.
Angular CLI and Angular Build were updated to 21.2.29.

The resolved build dependencies include:

- Vite 7.3.7.
- Undici 7.30.1.

After the update and clean dependency installation, npm audit reported:

- 16 moderate vulnerabilities.
- No high or critical vulnerabilities in that recorded report.

The remaining findings involve glob, minimatch and the Angular CLI
dependency chain. They remain unresolved maintenance work.

The suggested forced remediation would upgrade Angular CLI to 22.
That major migration was not performed as part of this task.

Installation-script warnings were also reported.
The subsequent tests and production build succeeded.

The regenerated package-lock.json must be committed with package.json.

## Continuous integration

The frontend workflow is configured to run:

1. npm ci
2. npm test -- --watch=false
3. npm run build

The backend workflow remains unchanged.

The updated workflow has not yet been verified by a published CI run.
Local success must not be presented as GitHub Actions success.

## Completion status

Pending:

- Remaining manual browser checks and screenshot links.
- Final change review.
- Implementation and documentation commit.
- Push and successful CI evidence.
- Issue acceptance checklist and project-board update.
