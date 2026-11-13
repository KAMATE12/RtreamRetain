# Sprint 3 — Reading and learning notes

Project: StreamRetain
Student: Kamate Emmanuel
Group: M80-103CB-26
Sprint: November 2–15, 2026
Document prepared: November 13, 2026

## Assigned reading and actual scope

The Sprint 3 task identifies Martin Kleppmann's
Designing Data-Intensive Applications as the assigned book.

The reading actually completed for the session recorded here was
limited to the book's official presentation website.

No complete book, chapter or edition-specific excerpt is claimed.

## Reading session — November 12, 2026

Source: [Official DDIA presentation](https://dataintensive.net/)

Author: Martin Kleppmann.

Resource type: book presentation webpage.

Edition: not applicable to the webpage itself; no specific book
edition was studied during this session.

Sections read:

- Compare several designs.
- Both theory and practice.
- Deeper understanding.

The student confirmed reading these three sections.

### Chronology

This reading took place after implementation of the Sprint 3
dashboard tasks #18–#21.

It supported retrospective evaluation of existing decisions.
It is not presented as the original basis for those decisions.

### Personal takeaway

I learned that I should compare possible solutions and understand
their trade-offs before choosing one. A popular or complex technology
is not necessarily the best fit for my project.

For StreamRetain, I should start with the retention manager's needs
and choose a solution that I can explain, test and maintain.

This wording was prepared with AI assistance and accepted by the
student as close to his own understanding.

### Concrete application to StreamRetain

Looking back at Sprint 3, a comparison table meets the current need
to inspect subscription-plan counts and rates.

Charts were not required for this task. The table shows exact values
and denominators without introducing an additional visualization.

The reading helped me evaluate this scope decision after implementation.
I do not claim that it originally guided the choice.

### Remaining questions and next steps

The presentation does not provide a detailed study of reliability,
data models or analytical query design.

Further reading should use legally accessible author or publisher
material on these topics and record the exact sections actually read.

Before a future technical decision, record:

- The user need.
- The alternatives considered.
- Expected benefits and limitations.
- How the chosen behavior will be verified.

## Guided project discussion

The following learning came from discussion of StreamRetain.
It is not attributed to unread sections of DDIA.

### Complete display and consistent data

The dashboard waits for summary and comparison responses before
displaying either result section.

This prevents partial display, but does not prove data correctness.

Both requests use the same month and plan filters.
However, if an import changes the database between the two reads,
the responses can describe different database states.

A shared snapshot would be needed to avoid that particular mismatch.
A single endpoint alone would not automatically guarantee it.

This is a documented limitation, not an observed production incident.
A future snapshot design remains outside the delivered Sprint 3 scope.

### Counts and rates answer different questions

In the controlled example:

| Plan | Cohort size | Cancellation requests | Rate |
|---|---:|---:|---:|
| Basic | 80 | 8 | 10% |
| Premium | 20 | 4 | 20% |

Basic has more cancellation requests.
Premium has a higher proportion of customers requesting cancellation.

Showing cohort size, request count and rate together prevents
confusing absolute counts with proportions.

### No data is different from zero percent

With 20 customers and no cancellation requests, the rate is 0%.

With no customers matching the filters, a rate cannot be calculated.
The API represents the unavailable rate as null.
The interface displays "No data".

Displaying 0% for an empty group would be misleading.

### Observation does not establish causation

A higher observed rate does not prove that a subscription plan
caused cancellations.

The appropriate response is to investigate possible explanations.
The figures alone do not justify removing an abonnement or asserting
that a retention action will work.

All StreamRetain observations are synthetic.
They do not establish actual IVI customer behavior.

### Beginning-of-month cohort

The cohort contains customers assumed active at the beginning
of the observation month.

A customer who requests cancellation during that month remains
in the cohort and its denominator.

For 100 beginning-of-month customers and 19 cancellation requests,
the rate is 19 / 100 × 100 = 19%.

## Evidence and limitations

The learning record combines:

- Three confirmed sections of an official presentation webpage.
- Student responses during guided discussion.
- AI-assisted formulation reviewed by the student.
- Concrete examples from the implemented dashboard.

No full-chapter reading, user research, statistical significance
testing or product validation is claimed.

Further substantive reading on the assigned technical topics remains
to be completed and recorded before final submission.