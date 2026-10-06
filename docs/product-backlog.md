# Product backlog

## Product goal

Help a retention manager inspect cancellation patterns in synthetic streaming data and organise possible retention actions.

## Target user and need

Our initial user is a retention manager who needs to see which subscriber groups cancel more frequently. This is a hypothesis for an educational project, not a finding from an interview with IVI. The expected benefit is faster, more transparent investigation and follow-up.

## Priority order

P0 = necessary for the core workflow; P1 = important after the foundation. Sprint allocation after S1 is provisional and will be reviewed with feedback.

### E1 Product and foundation

Priority: P0. Planned: S1. Value: Board, product scope, environment and a connected skeleton.

- [ ] Create the public repository and sprint board
- [ ] Define the target user and prioritise the product backlog
- [ ] Set up and understand the local development environment
- [ ] Run and explain the FastAPI skeleton
- [ ] Run the Angular page and connect it to the API
- [ ] Connect PostgreSQL and document the proposed data model
- [ ] Document setup and verify the integrated skeleton
- [ ] Read selected product chapters and submit the sprint review

### E2 Synthetic customer data

Priority: P0. Planned: S2. Value: Import trustworthy educational records.

- [ ] Specify a reproducible synthetic data generator
- [ ] Implement CSV schema validation and error messages
- [ ] Store valid customer-month records and test duplicate handling

### E3 Customer analysis dashboard

Priority: P0. Planned: S2–S3. Value: Make cancellation patterns visible.

- [ ] Calculate and test the defined cancellation rate
- [ ] Display subscriber and activity indicators
- [ ] Add subscription and activity filters
- [ ] Compare segments and document the limits of interpretation

### E4 Retention action workflow

Priority: P1. Planned: S3. Value: Turn findings into proposed follow-up actions.

- [ ] Document transparent suggestion rules
- [ ] Create and list proposed actions
- [ ] Update action status and test persistence

### E5 Delivery and final review

Priority: P1. Planned: S4–S5. Value: Make the project reproducible and explain its results.

- [ ] Expand integration and browser scenario tests
- [ ] Improve local delivery and continuous integration
- [ ] Polish documentation and screenshots
- [ ] Record final demo and write the one-page Agile reflection

## Scope boundaries

The approved MVP has data import, a dashboard, segment comparisons, and retention suggestions with action tracking. No real IVI data access, payment processing, streaming service, automated customer messaging, or distributed Big Data infrastructure is included. Machine learning is an optional future learning extension after the MVP.
