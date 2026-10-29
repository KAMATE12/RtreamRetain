# Data design and cancellation definition

The customer and customer_month tables were implemented during
Sprint 2, task E2-03, together with transactional CSV import.

No customer tables were created during Sprint 1.
The original design proposal became the basis for this implementation.

Retention actions remain a proposal for future implementation.

See [PostgreSQL import and verification](postgresql-import.md)
for commands, database constraints, storage limits and test results.

## One row and one time window

Use one row per synthetic customer per calendar month, with a unique pair (customer_id, observation_month). The initial dataset will represent a cohort of customers active at the start of that month. A customer who cancels during that month is counted once. New mid-month customers are outside this initial cohort definition.

## Implemented customer_month fields

| Field | Meaning | Rule |
|---|---|---|
| customer_id | Synthetic identifier | Required; no personal names |
| observation_month | Calendar month | First day of month |
| plan | Subscription plan | Allowed category list |
| tenure_months | Tenure at month start | Non-negative integer |
| viewing_hours | Viewing during the month | Non-negative number |
| payment_failures | Failures during the month | Non-negative integer |
| support_requests | Requests during the month | Non-negative integer |
| cancelled_in_month | Cancelled during the month | Boolean |

Cancellation rate = customers in the start-of-month cohort who cancel during the month / customers in the start-of-month cohort. A zero denominator yields “No data”, not a made-up percentage.

Example: 20 cancellations among 100 customers present at the start of the month gives 20%. This example is illustrative, not a project result.

## Interpretation

Lower viewing may be associated with cancellation; it does not establish the cause. Same-month viewing may fall because the customer cancelled. A future prediction model must use only information available before the prediction date. Synthetic patterns reflect generator assumptions, not verified IVI behaviour.

## Proposed retention_action fields

id, segment_description, proposed_action, rationale, status, created_at. Initial statuses: Proposed, In Progress, Completed. Marking an action Completed describes the workflow; it does not prove that retention improved.

## Entities, identifiers and relationships

Customer and customer_month are implemented in PostgreSQL.
The retention_action entity remains a proposal.

### Customer

A customer represents a fictional subscriber.
The implemented primary key is customer_id: a required synthetic
identifier that remains stable across observation months.

No real names, email addresses or other personal identifiers
are required.

### Customer month

A customer_month record describes one eligible customer during
one calendar month.

The implemented composite primary key is:
(customer_id, observation_month).

customer_id references customer.customer_id through a foreign key.
One customer can have many monthly observations.
Each monthly observation belongs to exactly one customer.

The same customer must not appear twice for the same month.
observation_month includes the year and is stored as the first
day of the month, for example 2026-10-01.

### Retention action

A retention_action record describes a proposed action for a
customer segment.

Its proposed primary key is id.
segment_description explains which group the action targets.

In this initial design, the segment is described in text.
There is no foreign-key relationship between retention_action
and individual customers or monthly observations.

A future version may introduce structured segments and explicit
relationships if the product requires them.


## Churn definition and observation period

### Initial operational definition

For this educational project, cancelled_in_month is true when
a customer in the start-of-month cohort submits at least one
subscription cancellation request during the observation month.

This measures cancellation requests, not necessarily the end
of paid access. A request counts in the month it is submitted,
even if access ends later.

Repeated requests by the same customer in the same month count
once. A later withdrawal of the request does not erase the
event from this initial metric.

Payment failures or low viewing activity alone do not count
as cancellation. Automatic termination due to non-payment is
outside this initial definition.

### Observation window and cohort

Use calendar months with UTC boundaries:
month start is included; next month start is excluded.

For October 2026, the window is:
2026-10-01 00:00:00 UTC <= event time < 2026-11-01 00:00:00 UTC.

The cohort contains customers with an active subscription at
the start of the month. Customers joining during the month
are excluded from that month's initial cohort.

For the initial synthetic dataset, assume at most one active
subscription per customer at a time.

Only fully observed months are used for the final monthly rate.
Missing cancellation information must not be treated as false.

### Calculation

Monthly cancellation rate (%) =
100 * distinct cohort customers who requested cancellation
during the month / distinct customers in the start-of-month cohort.

If the cohort is empty, display "No data".
Do not replace an undefined rate with 0%.

Example: 20 cancelling customers in a cohort of 100 gives 20%.
This is an illustrative example, not an observed project result.

### Synthetic data scope

The current customer records are artificially generated
for this educational project. Future datasets must remain synthetic.

They are not real IVI customer records. Patterns in these data
reflect generation assumptions and cannot establish actual
cancellation causes or retention effectiveness at IVI.

## Additional field definitions and validation rules

Monthly observation validation is implemented in the CSV validator.
PostgreSQL additionally enforces required values, primary and foreign
keys, allowed plans, first-day dates and non-negative numeric values.
Special numeric values such as NaN and Infinity are rejected.

The CSV validator enforces the canonical synthetic customer ID format.
The database customer ID constraint only checks that the value is
non-empty after trimming ordinary spaces.

Database storage limits also apply; see the PostgreSQL import guide.

Cohort eligibility, fully observed months and cross-month subscription
history remain dataset assumptions rather than database guarantees.

Retention-action rules below remain proposed and are not implemented.

### Monthly observations

All fields listed in customer_month are required in the initial
dataset. Reject missing values rather than silently replacing
them with zero or false.

| Field | Definition and validation |
|---|---|
| customer_id | Non-empty synthetic identifier referencing an existing customer. |
| observation_month | Valid date representing the first day of the observed month. |
| plan | Plan at month start. Initial fictional categories: Basic, Standard, Premium. |
| tenure_months | Completed months since the current subscription period began, measured at month start; integer >= 0. |
| viewing_hours | Total viewing hours during the observation month; finite number >= 0. |
| payment_failures | Number of failed payment attempts during the month; integer >= 0. |
| support_requests | Number of distinct support tickets opened during the month; integer >= 0. |
| cancelled_in_month | Boolean indicating a cancellation request, using the operational definition above. |

Plan categories are project assumptions, not verified IVI plans.
A plan change during the month does not change the recorded
start-of-month plan.

Monthly activity totals cover the observation window, including
activity after a cancellation request if access remains active.

The pair (customer_id, observation_month) must be unique.

Repeated pairs inside one CSV file cause whole-file validation failure.

When importing a valid file into PostgreSQL:
- A new pair is inserted.
- An existing pair with identical validated values is counted as unchanged.
- An existing pair with different values causes a conflict and rolls back
  the entire import.

Missing customer identities are created within the same transaction.
Existing observations are never silently overwritten.

### Retention actions

| Field | Proposed definition and validation |
|---|---|
| id | Unique, non-empty action identifier. |
| segment_description | Required text describing the target customer group. |
| proposed_action | Required text describing the suggested intervention. |
| rationale | Required text explaining why the action is proposed; assumptions must be distinguished from evidence. |
| status | One of: Proposed, In Progress, Completed. Initial value: Proposed. |
| created_at | Required creation timestamp recorded in UTC. |

Completed means the action workflow is complete.
It does not establish that the action reduced cancellations.
