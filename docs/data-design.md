# Proposed data design

Design proposal for later implementation. No customer tables are created in Sprint 1.

## One row and one time window

Use one row per synthetic customer per calendar month, with a unique pair (customer_id, observation_month). The initial dataset will represent a cohort of customers active at the start of that month. A customer who cancels during that month is counted once. New mid-month customers are outside this initial cohort definition.

## Proposed customer_month fields

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
