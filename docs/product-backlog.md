# Product backlog

## Product goal

Help a retention manager explore cancellation patterns in synthetic streaming data, compare customer segments and organise proposed retention actions.

StreamRetain is an educational project inspired by a fictional streaming-platform scenario. It is not an official IVI product.

## Target user, problem and proposed value

### Target user

A retention manager at a fictional streaming platform.

The manager uses StreamRetain to inspect customer information and organise follow-up actions. Subscribers are the subjects of the analysis, not the primary users of this application.

### Problem

The manager has subscription and activity records but struggles to identify which customer groups cancel more frequently and organise the actions to investigate next.

Reviewing individual records alone makes it difficult to compare groups and maintain a clear record of proposed follow-up actions.

### Proposed value

StreamRetain brings indicators, segment comparisons and action tracking into one workflow.

The expected benefit is clearer investigation and better-organised follow-up. A reduction in real customer cancellations is not an established result of this project.

### Assumptions

This user profile and problem statement are hypotheses for an educational project. They are not findings from interviews with IVI employees.

All customer records will be synthetic. Patterns in generated data do not establish the real causes of customer cancellations at IVI.

## MVP features

The minimum viable product contains four features.

### F1 — Data import

Import a CSV file containing synthetic customer-month records, validate its structure and values, and store valid records in PostgreSQL.

Expected behaviour:
- Valid records can be imported.
- Invalid records produce understandable validation messages.
- Repeated imports do not create duplicate customer-month records.

Main epic: [E2 Synthetic customer data](https://github.com/KAMATE12/RtreamRetain/issues/10).

### F2 — Customer dashboard

Display customer counts, cancellation counts, cancellation rates and clearly labelled activity indicators for a selected observation month.

Expected behaviour:
- Calculations match a known test dataset.
- The monthly cancellation rate uses customers active at the beginning of the month as its cohort.
- Customers joining during that month are excluded from that month's starting cohort.
- A zero denominator displays "No data".
- Loading, empty-data and error states are understandable.

Main epic: [E3 Customer analysis dashboard](https://github.com/KAMATE12/RtreamRetain/issues/11).

### F3 — Segment comparisons

Filter and compare customer groups by subscription plan and activity using documented grouping rules.

Expected behaviour:
- Filters update indicators and comparisons consistently.
- Comparisons show rates and the customer counts used to calculate them.
- Observed associations are presented as investigation leads, not proof of causation.

Main epic: [E3 Customer analysis dashboard](https://github.com/KAMATE12/RtreamRetain/issues/11).

### F4 — Retention suggestions and action tracking

Present suggestions based on documented rules and allow the manager to record proposed actions, their rationale and their status.

Expected behaviour:
- Suggestions explain the rule and reasoning behind them.
- The manager reviews a suggestion before recording an action.
- Saved actions and status updates persist.
- Action statuses are Proposed, In Progress, Completed and Dismissed.
- Completing an action does not imply that its effectiveness has been demonstrated.

Main epic: [E4 Retention action workflow](https://github.com/KAMATE12/RtreamRetain/issues/12).

## Priority order and rationale

- P0: necessary for the core workflow and its foundations.
- P1: follows the foundations but remains required for the planned MVP or final delivery.

P1 does not mean optional.

E1 establishes the product scope and technical foundation. E2 provides validated data. E3 makes that data understandable. E4 organises proposed follow-up actions. E5 strengthens verification and prepares the final delivery.

Testing and documentation begin in Sprint 1 and continue throughout development.

Sprint allocation after Sprint 1 is provisional and will be reviewed using progress and feedback.

## Epics and task breakdown

### E1 — Product and foundation

Epic issue: [#9](https://github.com/KAMATE12/RtreamRetain/issues/9)

Priority: P0. Planned delivery: Sprint 1.

Value: Establish project organisation, product scope, the development environment and a connected application skeleton.

Existing task issues:
- [S1-01 — Create the public repository and sprint board](https://github.com/KAMATE12/RtreamRetain/issues/1)
- [S1-02 — Define the target user and prioritise the product backlog](https://github.com/KAMATE12/RtreamRetain/issues/2)
- [S1-03 — Set up and understand the local development environment](https://github.com/KAMATE12/RtreamRetain/issues/3)
- [S1-04 — Run and explain the FastAPI skeleton](https://github.com/KAMATE12/RtreamRetain/issues/4)
- [S1-05 — Run the Angular page and connect it to the API](https://github.com/KAMATE12/RtreamRetain/issues/5)
- [S1-06 — Connect PostgreSQL and document the proposed data model](https://github.com/KAMATE12/RtreamRetain/issues/6)
- [S1-07 — Document setup and verify the integrated skeleton](https://github.com/KAMATE12/RtreamRetain/issues/7)
- [S1-08 — Read selected product chapters and submit the sprint review](https://github.com/KAMATE12/RtreamRetain/issues/8)

Use the linked issues and project board to review current task status.

### E2 — Synthetic customer data

Epic issue: [#10](https://github.com/KAMATE12/RtreamRetain/issues/10)

Priority: P0. Planned delivery: Sprint 2.

Value: Provide reproducible, validated educational records for analysis.

Planned tasks:
- E2-01 — Specify and implement a reproducible synthetic data generator with documented rules and a fixed random seed.
- E2-02 — Implement CSV schema and value validation with clear error messages.
- E2-03 — Store valid customer-month records and test duplicate handling.

### E3 — Customer analysis dashboard

Epic issue: [#11](https://github.com/KAMATE12/RtreamRetain/issues/11)

Priority: P0. Planned delivery: Sprints 2–3.

Value: Make cancellation patterns and differences between customer groups visible.

Dependency: Validated synthetic data from E2.

Planned tasks:
- E3-01 — Calculate and test the documented monthly cancellation rate.
- E3-02 — Display customer, cancellation and activity indicators in Angular.
- E3-03 — Add observation-month, subscription-plan and activity filters.
- E3-04 — Compare segments, show their sample sizes and document interpretation limits.

### E4 — Retention action workflow

Epic issue: [#12](https://github.com/KAMATE12/RtreamRetain/issues/12)

Priority: P1. Planned delivery: Sprint 3.

Value: Turn observations into documented follow-up proposals.

Dependencies: Validated data from E2 and segment analysis from E3.

Planned tasks:
- E4-01 — Document and test transparent suggestion rules.
- E4-02 — Implement the creation and listing of proposed retention actions.
- E4-03 — Implement action-status updates and test persistence.

### E5 — Delivery and final review

Epic issue: [#13](https://github.com/KAMATE12/RtreamRetain/issues/13)

Priority: P1. Planned delivery: Sprints 4–5.

Value: Make the project reproducible, verify its main workflow and explain its results.

Dependencies: Builds on E1–E4.

Planned tasks:
- E5-01 — Expand integration and browser scenario tests.
- E5-02 — Verify fresh local setup and improve continuous integration.
- E5-03 — Update documentation, screenshots, data definitions and known limitations.
- E5-04 — Record the final demo and write the one-page Agile reflection.

## Tracking rules

Project board: [StreamRetain — Semester Project](https://github.com/users/KAMATE12/projects/3).

- Sprint 1 runs from October 5 to October 18, 2026.
- The Sprint 1 task set consists of S1-01 to S1-08.
- Future work under E2–E5 must remain outside Sprint 1.
- Epic issues group work; they are not additional implementation tasks.
- Keep the Sprint field on epic summary issues empty to avoid counting the same work twice. Their planned delivery is documented above.
- E2-01 to E5-04 are planning identifiers, not GitHub issue numbers. These tasks are currently described within their epics.
- Create separate task issues when refining future sprint work, then add their links here.
- Close an epic only when its required tasks meet their acceptance criteria and completion evidence has been reviewed.
- Creating an issue or writing a plan does not mean the planned functionality is implemented.

## Scope boundaries

The MVP includes data import, a dashboard, segment comparisons, and retention suggestions with action tracking.

The following are excluded:
- Access to real IVI customer data or internal systems.
- Video streaming.
- Payment processing or subscription changes.
- Automated customer messaging.
- Distributed Big Data infrastructure.
- A mandatory machine-learning prediction model.

Machine learning is an optional future learning extension after the MVP.

Public application hosting is not assumed to be complete. Delivery documentation must explain how the application can actually be accessed.

See [Data design](data-design.md) for the proposed data model and cancellation definition, and [Sprint 1 plan](sprint-1-plan.md) for the initial sprint plan.
