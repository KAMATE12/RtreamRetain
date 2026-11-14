# Sprint 3 — Reading and learning notes

Project: StreamRetain
Student: Kamate Emmanuel
Group: M80-103CB-26
Sprint: November 2–15, 2026
Document prepared: November 13, 2026

## Assigned reading and actual scope

The Sprint 3 task identifies Martin Kleppmann's
Designing Data-Intensive Applications as the assigned book.

The completed reading includes three sections of the book's official
presentation website and one section of a public article by the author.
The exact scope of each session is recorded below.

No complete book, chapter or edition-specific excerpt is claimed.

## Reading record 1 — Official DDIA presentation

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

The student confirms that this reading was completed before implementation.
The exact reading date has not been recorded.

An earlier AI-assisted draft incorrectly described the reading as occurring
after implementation. This record corrects that chronology.

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

The reading helped me consider design trade-offs.
The comparison table illustrates choosing a solution that meets the
current need and remains understandable and maintainable.

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
The figures alone do not justify removing a subscription plan or asserting
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

A second technical reading session is recorded below.
Further reading on data models and analytical query patterns remains pending.

## Reading record 2 — Efficiency and correctness

Source: [How to do distributed locking](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

Author: Martin Kleppmann.
Publication date: February 8, 2016.
Resource type: public article on the author's website.
Book edition: not applicable.

Confirmed reading scope:
the complete section "What are you using that lock for?",
ending before "Protecting a resource with a lock".

Full-article or book-chapter reading is not claimed.

### Main idea and understanding

The section distinguishes efficiency from correctness by examining
the consequences of a lock failing.

Efficiency concerns unnecessary work and resource use.
Correctness concerns whether the system preserves the required behavior
and produces valid results.

During the guided discussion, I initially used "efficiency" to describe
an import that creates duplicates. I then understood that incorrect
duplication is a correctness problem, while unnecessary processing time
with correct results is an efficiency problem.

This summary was prepared with AI assistance from the student's answers.

### Application to StreamRetain

Reimporting the same CSV must not insert the same customer-month
observations again.

The previously recorded import verification showed:

- Initial import: 100 inserted observations.
- Identical reimport: 0 inserted and 100 unchanged observations.

This is evidence about the correctness of repeated identical imports.
It is not a performance benchmark or proof of all concurrent-import cases.

A slow import with correct stored results would raise a separate
efficiency question.

This application is a project analogy. The article discusses distributed
locks; it does not establish that StreamRetain needs such a lock.

### Chronology and next steps

The student confirms that this reading was completed before implementation.
The exact reading date has not been recorded.

The later guided discussion clarified the distinction between correctness
and efficiency. The date of that discussion is not the reading date.

No distributed locking feature was added.

For future processing changes, identify correctness requirements before
considering optimizations, then measure performance separately.

Further reading on data models and analytical query patterns remains
pending. No unread sections are claimed.
