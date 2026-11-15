# Sprint 4 plan

Project: StreamRetain
Student: Kamate Emmanuel
Group: M80-103CB-26

Sprint: November 16–29, 2026
Planning date: November 15, 2026
Status: scope agreed; implementation not started

## Sprint goal

Enable the retention manager to review transparent, rule-based
suggestions, record proposed follow-up actions for a selected month
and subscription plan, and track their status in a clearer interface.

Also verify that historical observations can be imported through
the existing command-line workflow and selected in the dashboard.

All customer data remains synthetic.

## Capacity

The student confirmed an available capacity of 26 hours.

| Task | Estimated effort |
|---|---:|
| E4-01 — Define, implement and test transparent suggestion rules | 4 hours |
| E4-02 — Create and list proposed retention actions | 7 hours |
| E4-03 — Update action statuses and verify persistence | 4 hours |
| S4-04 — Improve dashboard and action-interface presentation | 4 hours |
| S4-05 — Verify historical import and multiple-month selection | 1 hour |
| S4-06 — Reading, integrated verification and sprint delivery | 3 hours |
| Contingency | 3 hours |
| Total | 26 hours |

Implementation estimates include task-level tests and documentation.
S4-06 covers final integrated verification and sprint-level delivery.

These are estimates, not recorded working hours.
Record actual effort and replan if necessary.

## Starting point

Sprint 3 delivered:

- Monthly indicators and a read-only API.
- Angular loading, empty-data and error states.
- Observation-month and subscription-plan filters.
- Subscription-plan comparisons with counts and rates.
- Tests, documentation and a published demonstration.

Issues #18–#22 were closed and their cards marked Done.

Epic #11 remains open because activity-based filtering is deferred.
Epic #12 groups the retention-action work planned for this sprint.

## Planned tasks

### E4-01 — Transparent suggestion rules

Define and implement a small set of deterministic rules.

For each rule, document:

- Identifier and version.
- Required inputs.
- Trigger condition.
- Suggested investigation or follow-up.
- Rationale and limitations.

Verify examples where each condition is met and not met.
Document any thresholds as educational assumptions.
Do not present them as statistically validated boundaries.

A missing rate must not be treated as a measured 0%.
Suggestions must identify the selected month and plan scope.

### E4-02 — Create and list proposed actions

Allow the manager to review a suggestion before saving an action.

Each saved action must retain:

- Observation month.
- Subscription-plan scope, including All plans.
- Proposed action text.
- Rationale.
- Source rule identifier and version when applicable.
- Status.
- Creation date.

New actions start as Proposed.

Changing dashboard filters must not rewrite saved actions.
Viewing a suggestion must not automatically create an action.

Validate inputs and display understandable save errors.
Retain user input after a failed save.
Prevent repeated clicks while a save is pending.

### E4-03 — Status updates and persistence

Support these statuses:

- Proposed.
- In Progress.
- Completed.
- Dismissed.

Define permitted transitions before implementation.
Validate status changes in the backend.

Verify that actions and status changes remain available after:

- Reloading the page.
- Restarting the application.
- Restarting PostgreSQL without deleting its persistent volume.

Completed means workflow progress.
It does not demonstrate improved retention.

### S4-04 — Interface improvements

Improve the delivered interface without changing indicator meanings.

Work includes:

- A content width appropriate for desktop screens.
- Clearer visual hierarchy for indicators.
- Readable comparison tables.
- Consistent presentation of suggestions and actions.
- Less prominence for technical connection information.
- Readable loading, empty-data, error and save states.
- Keyboard focus and labelled controls.
- Verification at desktop and narrow-screen widths.

Record before-and-after screenshots.
Visual improvements do not establish product validation.

### S4-05 — Historical import and month selection

Use the existing command-line importer with a controlled synthetic
dataset for an earlier observation month.

Verify:

- Importing the earlier month succeeds.
- The imported month appears among available months.
- Selecting either month updates indicators and comparisons.
- Monthly calculations do not combine observations across months.
- Reimporting the same file creates no duplicate observations.
- Existing working observations remain unchanged.

The observation month is distinct from the import date.
Do not relabel an existing month's records as historical evidence.

Inspect current validation rules before preparing the dataset.
Do not erase working data.

The one-hour estimate covers verification.
Any substantial defect requires explicit replanning.

### S4-06 — Reading and sprint delivery

Confirm the assigned Sprint 4 reading against the course schedule.

Record exact sources, sections actually studied, personal takeaways
and their application to project decisions.

Study relevant material before the decision it informs where possible.
Record the actual chronology without inventing dates.

Review the Sprint 3 improvement experiments:

- Allow time for unexpected work.
- Choose a small, clear priority for each session.
- Capture commands, results and screenshots immediately.

Prepare the sprint review, retrospective and English demonstration.
Target 3–5 minutes unless the instructor accepts another duration
for this sprint.

Verify access and playback before submission.
Submit the required materials in the course chat.
Record the actual submission date and available evidence.

## Integrated acceptance criteria

- [ ] Suggestions identify their rule, scope and rationale.
- [ ] Triggering and non-triggering rule examples pass.
- [ ] The manager reviews a suggestion before creating an action.
- [ ] Saved actions retain their original context.
- [ ] Actions can be listed and their statuses updated.
- [ ] Persistence survives reload and restart checks.
- [ ] Invalid input and failed saves produce understandable messages.
- [ ] The interface clearly labels suggestions as proposals.
- [ ] Dashboard and action views are readable at checked screen sizes.
- [ ] Historical import and selection between two months are verified.
- [ ] Relevant backend and frontend tests pass.
- [ ] The frontend production build passes.
- [ ] Local PostgreSQL integration evidence is distinguished from CI.
- [ ] Documentation and implementation are committed and pushed.
- [ ] Demonstration and course submission evidence are recorded.
- [ ] Issues and board statuses reflect actual completion.

## Scope boundaries and deferred work

This sprint does not include:

- CSV upload through Angular.
- Activity-based filtering.
- Machine-learning predictions.
- Automatic customer messaging.
- Payment or subscription changes.
- Claims of proven retention effectiveness.

Angular CSV upload must remain visible as a backlog task.
Estimate and prioritise it during Sprint 5 planning alongside
remaining MVP requirements and final-delivery work.
It is not yet a Sprint 5 delivery commitment.

Activity-based filtering remains under epic #11.
It must not disappear from the MVP backlog.

## Tracking and replanning

The six task issues are listed in the Sprint 4 task issues section.
Planning identifiers are not GitHub issue numbers.

Keep the Sprint field empty on epic summary issues.
Assign Sprint 4 to its task issues.

Do not mark planned work as implemented.
Do not close epic #12 until its acceptance criteria are verified.

Use contingency for unexpected work.
If capacity is exceeded, record the scope decision and update
the plan, backlog and board.

## Communication

Post the agreed sprint goal, task list and board link in the course
chat at sprint start. Record the actual posting date.

Final review target: November 29, 2026.
Confirm submission timing against the instructor's instructions.

## References

- [Project board](https://github.com/users/KAMATE12/projects/3)
- [E4 — Retention action workflow](https://github.com/KAMATE12/RtreamRetain/issues/12)
- [E3 — Customer analysis dashboard](https://github.com/KAMATE12/RtreamRetain/issues/11)
- [Product backlog](product-backlog.md)
- [Sprint 3 report](sprint-3-report.md)
- [Dashboard documentation](monthly-indicators-dashboard.md)

## Completion evidence

To be added as work is completed.

## Sprint 4 task issues

- [E4-01 — Transparent suggestion rules](https://github.com/KAMATE12/RtreamRetain/issues/23)
- [E4-02 — Action creation and listing](https://github.com/KAMATE12/RtreamRetain/issues/24)
- [E4-03 — Status updates and persistence](https://github.com/KAMATE12/RtreamRetain/issues/25)
- [S4-04 — Interface improvements](https://github.com/KAMATE12/RtreamRetain/issues/26)
- [S4-05 — Historical import and multiple-month verification](https://github.com/KAMATE12/RtreamRetain/issues/27)
- [S4-06 — Reading, integrated verification and sprint delivery](https://github.com/KAMATE12/RtreamRetain/issues/28)

These issues describe planned work.
Their creation does not establish implementation or completion.
