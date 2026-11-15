# Product backlog

Project: StreamRetain
Planning update: November 15, 2026

## Product goal

Help a retention manager explore cancellation patterns in synthetic
streaming data, compare customer segments and organise proposed
retention actions.

StreamRetain is an educational project inspired by a fictional
streaming-platform scenario. It is not an official IVI product.

## Target user, problem and proposed value

### Target user

A retention manager at a fictional streaming platform.

The manager uses StreamRetain to inspect customer information and
organise follow-up actions. Subscribers are the subjects of the
analysis, not the primary users of this application.

### Problem

The manager has subscription and activity records but struggles to
identify which customer groups cancel more frequently and organise
the actions to investigate next.

Reviewing individual records alone makes it difficult to compare
groups and maintain a clear record of proposed follow-up actions.

### Proposed value

StreamRetain brings indicators, segment comparisons and action
tracking into one workflow.

The expected benefit is clearer investigation and better-organised
follow-up. A reduction in real customer cancellations is not an
established result of this project.

### Assumptions

This user profile and problem statement are hypotheses for an
educational project. They are not findings from interviews with
IVI employees.

All customer records are synthetic. Patterns in generated data do
not establish the real causes of customer cancellations at IVI.

## MVP features

### F1 — Data import

Import synthetic customer-month records from CSV, validate their
structure and values, and store valid records in PostgreSQL.

Expected behaviour:

- Valid records can be imported.
- Invalid records produce understandable validation messages.
- Repeated identical imports do not create duplicate observations.
- Conflicting observations reject the import according to the
  documented rules.
- Importing a historical observation month does not mix that
  month's records with another month's calculations.

Delivered interface: command-line import.

Historical import and selection between two stored months will
receive an additional integrated check during Sprint 4.

CSV upload through Angular is a separate usability enhancement
that has not yet been implemented or committed to a sprint.

Main epic:
[E2 Synthetic customer data](https://github.com/KAMATE12/RtreamRetain/issues/10).

### F2 — Customer dashboard

Display cohort sizes, cancellation-request counts, cancellation-request
rates and clearly labelled activity indicators for a selected
observation month.

Expected behaviour:

- Calculations match controlled test datasets.
- The monthly cohort represents customers active at the beginning
  of the observation month.
- Customers joining during the month are excluded from that
  month's starting cohort.
- Customers requesting cancellation during the month remain
  in the starting cohort and its denominator.
- A zero denominator produces an unavailable rate displayed
  as No data.
- Loading, empty-data and error states are understandable.

Current implementation assumes that imported observations represent
the beginning-of-month cohort. This is a modelling assumption;
it is not evidence of independently verified real subscription history.

Main epic:
[E3 Customer analysis dashboard](https://github.com/KAMATE12/RtreamRetain/issues/11).

### F3 — Segment comparisons

Filter and compare customer groups by subscription plan and activity
using documented grouping rules.

Expected behaviour:

- Filters update indicators and comparisons for the selected scope.
- Comparisons show rates and the counts used to calculate them.
- The overall rate uses combined counts.
- Observed associations are presented as investigation leads,
  not proof of causation.

Delivered in Sprint 3:

- Observation-month and subscription-plan selection.
- Subscription-plan comparisons.
- Coordinated loading and display of summary and comparisons.

Remaining requirement:

- Activity-based filtering and comparisons using documented rules.

Using the same filters and displaying responses together does not
guarantee that separate database reads share one transactional snapshot.

Main epic:
[E3 Customer analysis dashboard](https://github.com/KAMATE12/RtreamRetain/issues/11).

### F4 — Retention suggestions and action tracking

Present suggestions based on documented rules and allow the manager
to record proposed actions, their rationale and their status.

Expected behaviour:

- Suggestions identify their rule, selected scope and rationale.
- The manager reviews a suggestion before recording an action.
- Saved actions retain their observation month and plan scope.
- Saved actions and status updates persist.
- New actions start as Proposed.
- Available statuses are Proposed, In Progress, Completed and Dismissed.
- Invalid input and failed saves produce understandable messages.
- Completing an action does not imply proven retention effectiveness.

Planned implementation: Sprint 4.

Main epic:
[E4 Retention action workflow](https://github.com/KAMATE12/RtreamRetain/issues/12).

## Priority order and rationale

- P0: necessary for the core workflow and its foundations.
- P1: follows the foundations but remains required for the planned
  MVP or final delivery.

P1 does not mean optional.

E1 establishes the product scope and technical foundation.
E2 provides validated data.
E3 makes that data understandable.
E4 organises proposed follow-up actions.
E5 strengthens verification and prepares final delivery.

Testing and documentation continue throughout development.

Sprint allocations are planning decisions and may be revised using
actual progress and available capacity. Record scope changes explicitly.

## Epics and task breakdown

### E1 — Product and foundation

Epic:
[#9](https://github.com/KAMATE12/RtreamRetain/issues/9)

Priority: P0.
Delivered during Sprint 1.

Tasks:

- [S1-01 — Public repository and sprint board](https://github.com/KAMATE12/RtreamRetain/issues/1)
- [S1-02 — Target user and prioritised backlog](https://github.com/KAMATE12/RtreamRetain/issues/2)
- [S1-03 — Local development environment](https://github.com/KAMATE12/RtreamRetain/issues/3)
- [S1-04 — FastAPI skeleton](https://github.com/KAMATE12/RtreamRetain/issues/4)
- [S1-05 — Angular page and API connection](https://github.com/KAMATE12/RtreamRetain/issues/5)
- [S1-06 — PostgreSQL connection and data model](https://github.com/KAMATE12/RtreamRetain/issues/6)
- [S1-07 — Setup documentation and integrated verification](https://github.com/KAMATE12/RtreamRetain/issues/7)
- [S1-08 — Reading and sprint review](https://github.com/KAMATE12/RtreamRetain/issues/8)

### E2 — Synthetic customer data

Epic:
[#10](https://github.com/KAMATE12/RtreamRetain/issues/10)

Priority: P0.
Implementation delivered during Sprint 2.

Tasks:

- [E2-01 — Reproducible synthetic data generator](https://github.com/KAMATE12/RtreamRetain/issues/14)
- [E2-02 — CSV validation](https://github.com/KAMATE12/RtreamRetain/issues/15)
- [E2-03 — PostgreSQL import and duplicate handling](https://github.com/KAMATE12/RtreamRetain/issues/16)

The command-line importer validates the complete file before writing.
Identical observations remain unchanged.
Conflicting observations reject the import.

Sprint-level reading and delivery:
[S2-04](https://github.com/KAMATE12/RtreamRetain/issues/17).

Any remaining Sprint 2 distribution follow-up is tracked separately
and must not be confused with Sprint 4 implementation.

### E3 — Customer analysis dashboard

Epic:
[#11](https://github.com/KAMATE12/RtreamRetain/issues/11)

Priority: P0.
Core dashboard delivered during Sprint 3.
Epic remains open for deferred activity-based filtering.

Dependency: validated synthetic data from E2.

Completed task issues:

- [E3-01 — Monthly indicators and read-only API](https://github.com/KAMATE12/RtreamRetain/issues/18)
- [E3-02 — Angular indicators and interface states](https://github.com/KAMATE12/RtreamRetain/issues/19)
- [E3-03 — Observation-month and subscription-plan filters](https://github.com/KAMATE12/RtreamRetain/issues/20)
- [E3-04 — Subscription-plan comparisons](https://github.com/KAMATE12/RtreamRetain/issues/21)

The completed E3-03 scope includes month and plan filters.
It does not include activity filtering.

Remaining work:

- Define activity-grouping rules.
- Implement and test activity-based filtering and comparisons.
- Keep denominators and interpretation limitations visible.

This remaining requirement is outside the Sprint 4 commitment.
Review and estimate it during planning of the remaining delivery.
Do not close E3 or silently remove the requirement.

Sprint-level reading and delivery:
[S3-05](https://github.com/KAMATE12/RtreamRetain/issues/22).

### E4 — Retention action workflow

Epic:
[#12](https://github.com/KAMATE12/RtreamRetain/issues/12)

Priority: P1.
Planned delivery: Sprint 4 — November 16–29, 2026.

The earlier tentative Sprint 3 allocation was revised after
delivery of the dashboard foundations.

Value: turn observations into documented follow-up proposals.

Dependencies:

- Validated data from E2.
- Monthly indicators and subscription-plan analysis from E3.

Planned tasks:

- E4-01 — Define, implement and test transparent suggestion rules.
- E4-02 — Create and list proposed retention actions.
- E4-03 — Update action statuses and verify persistence.

Estimated implementation effort:

- E4-01: 4 hours.
- E4-02: 7 hours.
- E4-03: 4 hours.

These estimates include task-level tests and documentation.
Implementation issue links are listed in the Sprint 4 task issues section.

### E5 — Delivery and final review

Epic:
[#13](https://github.com/KAMATE12/RtreamRetain/issues/13)

Priority: P1.
Planned delivery: Sprints 4–5, subject to capacity review.

Value: make the project reproducible, verify its main workflow
and explain its results.

Dependencies: builds on E1–E4.

Planned tasks:

- E5-01 — Expand integration and browser scenario tests.
- E5-02 — Verify fresh local setup and improve continuous integration.
- E5-03 — Update documentation, screenshots, definitions and limitations.
- E5-04 — Record the final demo and write the one-page Agile reflection.

Existing task-level tests do not automatically complete these
final-delivery tasks.

## Sprint 4 commitment

Sprint dates: November 16–29, 2026.
Confirmed capacity: 26 hours.

| Task | Estimated effort |
|---|---:|
| E4-01 — Transparent suggestion rules | 4 hours |
| E4-02 — Action creation and listing | 7 hours |
| E4-03 — Status updates and persistence | 4 hours |
| S4-04 — Interface improvements | 4 hours |
| S4-05 — Historical import and multiple-month verification | 1 hour |
| S4-06 — Reading, integrated verification and sprint delivery | 3 hours |
| Contingency | 3 hours |
| Total | 26 hours |

S4-04 improves layout, readability and the presentation of indicators,
suggestions and actions.

S4-05 checks the existing command-line import workflow and the
dashboard using an additional historical observation month.
Its estimate covers verification; substantial defects require replanning.

S4-06 covers sprint-level learning and delivery.
Confirm the assigned reading against the course schedule.

See the [Sprint 4 plan](sprint-4-plan.md) for detailed acceptance criteria.

## Additional usability backlog

### CSV upload through Angular

Status: proposed enhancement; not implemented.
Priority relative to other remaining work: to be decided.

Possible scope:

- Select a CSV file in the interface.
- Submit it through a documented API.
- Reuse existing validation and transactional import rules.
- Display validation errors and import results.
- Refresh available observation months after successful import.
- Test file limits, failed requests and repeated submissions.

Estimate this work before committing it to a sprint.
Review it during Sprint 5 planning alongside remaining MVP
requirements and final-delivery work.

The existing command-line importer remains the delivered import path.
The Angular upload is not yet a Sprint 5 delivery commitment.

## Tracking rules

Project board:
[StreamRetain — Semester Project](https://github.com/users/KAMATE12/projects/3)

Sprint dates:

- Sprint 1: October 5–18, 2026.
- Sprint 2: October 19–November 1, 2026.
- Sprint 3: November 2–15, 2026.
- Sprint 4: November 16–29, 2026.

Rules:

- Epic issues group work; they are not additional implementation tasks.
- Keep the Sprint field empty on epic summary issues.
- Assign the relevant sprint to task issues.
- Planning identifiers such as E4-01 are not GitHub issue numbers.
- Create separate issues when refining committed work.
- Add actual task links after issue creation.
- Do not double-count work across implementation and delivery tasks.
- Close tasks only after reviewing their acceptance evidence.
- Close an epic only when all required work is complete.
- Creating a plan or issue does not mean the feature is implemented.
- Record actual work and scope changes rather than rewriting history.

## Scope boundaries

The MVP includes data import, a dashboard, segment comparisons,
and rule-based retention suggestions with action tracking.

Excluded:

- Access to real IVI customer data or internal systems.
- Video streaming.
- Payment processing or subscription changes.
- Automated customer messaging.
- Distributed Big Data infrastructure.
- A mandatory machine-learning prediction model.

Machine learning remains an optional future learning extension
after the MVP.

Public application hosting is not assumed complete.
A downloadable demonstration video is not a hosted application.

Delivery documentation must explain how the application can
actually be accessed.

## References

- [Data design and cancellation definition](data-design.md)
- [Sprint 1 plan](sprint-1-plan.md)
- [Sprint 2 plan](sprint-2-plan.md)
- [Sprint 3 plan](sprint-3-plan.md)
- [Sprint 3 report](sprint-3-report.md)
- [Sprint 4 plan](sprint-4-plan.md)
- [Dashboard documentation](monthly-indicators-dashboard.md)
- [PostgreSQL import](postgresql-import.md)

## Sprint 4 task issues

- [E4-01 — Transparent suggestion rules](https://github.com/KAMATE12/RtreamRetain/issues/23)
- [E4-02 — Action creation and listing](https://github.com/KAMATE12/RtreamRetain/issues/24)
- [E4-03 — Status updates and persistence](https://github.com/KAMATE12/RtreamRetain/issues/25)
- [S4-04 — Interface improvements](https://github.com/KAMATE12/RtreamRetain/issues/26)
- [S4-05 — Historical import and multiple-month verification](https://github.com/KAMATE12/RtreamRetain/issues/27)
- [S4-06 — Reading, integrated verification and sprint delivery](https://github.com/KAMATE12/RtreamRetain/issues/28)

These issues describe planned work.
Their creation does not establish implementation or completion.
