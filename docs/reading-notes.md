# Sprint 1 — Product reading notes

Student: Emmanuel Kamate
Group: M80-103CB-26
Date: October 16, 2026
Book: Dan Olsen, The Lean Product Playbook

## 1. Reading scope and sources

This study focused on the publicly available Chapter 1 excerpt,
particularly the Product-Market Fit Pyramid and the Lean Product
Process. I discussed these concepts and applied them to StreamRetain
with AI-assisted explanations.

Official publisher excerpt:
https://catalogimages.wiley.com/images/db/pdf/9781118960875.excerpt.pdf

Official author overview and table of contents:
https://dan-olsen.com/book/

The relevant topics are developed further in Chapters 3–6:
target customers, underserved needs, value proposition and MVP
feature scope. I do not claim to have read those chapters in full.

## 2. Main takeaway in my own words

Before proposing a solution, I need to understand the problem
and the people who experience it.

The Product-Market Fit Pyramid connects two parts:
the market and the product.

The market includes target customers and their underserved needs.
The product includes the value proposition, feature set and
user experience.

A technically working application is not enough. Its features
must help the intended user address an important need.

## 3. Application to StreamRetain

### Target user

Our target user is a retention manager at a streaming platform.

Subscribers are represented in the future synthetic dataset.
The retention manager is the person who would use StreamRetain
to investigate that dataset.

### Need hypothesis

The manager needs to identify customer groups with higher
cancellation rates and decide which groups to investigate.

This is a hypothesis. We have not interviewed real retention
managers or established how well their current tools meet this need.

### Proposed value

StreamRetain aims to make cancellation patterns understandable
and help the manager organise proposed follow-up actions.

We have not demonstrated that the application reduces cancellations.

### Planned MVP scope

The proposed scope includes:

- Importing synthetic customer data.
- Calculating clearly defined cancellation indicators.
- Comparing customer groups.
- Recording proposed retention actions and their status.

These features are planned, not implemented in Sprint 1.

### User experience

The interface should make the observation period, group sizes
and cancellation rates easy to understand.

It should distinguish missing data from a zero cancellation rate
and clearly explain the limits of the results.

## 4. Concrete implications for the backlog

The reading supports keeping the backlog focused on the
retention manager's investigation workflow:

- E2: synthetic data provides the basis for the investigation.
- E3: indicators and segment comparisons support group analysis.
- E4: action tracking records proposed responses.

These items already existed in the backlog. The reading clarified
why they belong together; it did not prove that users need them.

When refining the comparison feature, I should include both
group sizes and cancellation rates, rather than showing only
cancellation counts.

For example, 100 cancellations among 1,000 customers represent
10%, while 20 among 100 represent 20%.

This is an illustrative example, not a project result.
A higher rate helps direct investigation but does not establish
the cause of cancellation.

## 5. MVP and learning process

The process starts with target customers and their needs,
then defines the value proposition and minimum feature scope.
A prototype is created and tested with target users.

A prototype can be a mockup before it becomes working software.

The process is iterative: feedback may require revising the
assumed need, proposed value or selected features.

Following the steps helps structure learning; it does not
guarantee product-market fit.

## 6. What Sprint 1 actually demonstrates

The current application verifies communication between Angular,
FastAPI and PostgreSQL.

The Check connections button supports technical verification.
It does not yet help a retention manager analyse cancellations.

Backend tests, the frontend build and real database checks
provide evidence of the technical foundation.

They do not validate customer needs, analytical correctness
or retention effectiveness.

## 7. Remaining uncertainties and next learning step

We still need to investigate:

- Whether the proposed need is important to retention managers.
- Which comparisons would help them make decisions.
- Whether they can correctly interpret the planned indicators.
- Whether the proposed MVP scope is small enough and useful.

A proposed future learning activity is to show a simple comparison
mockup to a target user and ask them to identify which group they
would investigate and explain why.

This user test has not yet been conducted.

All customer data will be synthetic. The project does not establish
actual cancellation causes or retention effectiveness at IVI.