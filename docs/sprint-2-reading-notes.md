# Sprint 2 — Reading and learning notes

Student: Emmanuel Kamate
Group: M80-103CB-26
Project: StreamRetain
Sprint: October 19–November 1, 2026
Learning discussion recorded: October 29, 2026

## 1. Assigned reading and study scope

The course schedule assigns Robert C. Martin's Clean Code
to Sprint 2.

The initial Sprint 2 plan continued with Dan Olsen's
The Lean Product Playbook. After checking the course schedule,
Clean Code became the main focus of this learning activity.
The Olsen resources remain supplementary product learning.

The Clean Code activity focused on five topics relevant to
the generator, CSV validator and PostgreSQL importer:

- Meaningful names.
- Clear function responsibilities.
- Useful and accurate comments.
- Understandable error handling.
- Readable tests.

These topics were explored through an AI-assisted discussion
in French and Python examples related to StreamRetain.

This document does not claim that I read the entire book
or completed all chapters covering these topics.

## 2. Sources and reading status

### Main reference: Robert C. Martin — Clean Code

Official publisher information and original-edition contents:
https://www.informit.com/store/clean-code-a-handbook-of-agile-software-craftsmanship-9780136083221

Official accessible excerpt:
First Principles, from the second edition:
https://www.informit.com/articles/article.aspx?p=3222335

I read the official First Principles excerpt from the second
edition. Reading completion was recorded on October 30, 2026.

My main takeaway is that organizing code clearly helps a
programmer understand its structure and responsibilities.

In StreamRetain, separating CSV validation, database storage
and command coordination illustrates this organization.

This reading covers the accessible excerpt, not the entire book.

The original and second editions have different chapter
structures. This document does not treat their chapter
numbers as interchangeable.

The Python examples and exercises discussed during this
session were educational applications to StreamRetain,
not quotations from the book.

### Supplementary reference: Dan Olsen — The Lean Product Playbook

Author's public book overview and Lean Product Process:
https://dan-olsen.com/book/

Publisher's public Chapter 9 summary:
https://onlinelibrary.wiley.com/doi/10.1002/9781119154822.ch9

I read these public resources and discussed their application
to StreamRetain. This does not mean that I read the complete
book or the full Chapter 9.

## 3. Meaningful names

A name should help the reader understand what a value
or function represents.

For example, these names distinguish two import outcomes:

- inserted_observation_count: newly inserted observations.
- unchanged_observation_count: existing observations whose
  values already match the validated input.

Calling unchanged observations "errors" would be misleading:
an identical reimport is a successful operation.

Application to StreamRetain:

- validate_csv_file communicates a validation responsibility.
- store_validated_records indicates that its input should
  already have been validated.
- ObservationConflictError identifies a conflict rather than
  treating every existing observation as an error.

These observations explain existing code. No renaming change
is claimed as part of this learning session.

## 4. Clear function responsibilities

Validation and database storage have different responsibilities.

validate_csv_file checks the input and returns converted
observations or validation errors. It does not write to
PostgreSQL.

store_validated_records handles storage and existing
observations within a transaction supplied by its caller.

The command's main function coordinates validation,
the database transaction and user-facing results.

This separation allows someone to validate a CSV without
modifying the database or requiring a database connection.

A function may contain several steps serving one coherent
responsibility. Clear responsibilities do not mean that
every function must contain only one instruction.

## 5. Useful and accurate comments

Comments should explain useful context, assumptions or
reasons that are not obvious from the instruction alone.

For example, a comment can explain why existing observations
must never be silently overwritten.

A comment that merely repeats "add one" next to a counter
increment provides little additional information.

Detailed bilingual comments also support my learning.
They must remain accurate when the code changes.

During an exercise, I identified that:

    return value > 0

does not implement a rule that accepts zero.

For a numeric value, the intended comparison is:

    return value >= 0

The implementation must satisfy the intended rule.
A correct comment cannot compensate for incorrect code.

## 6. Error handling and transactions

The importer distinguishes these situations:

- A new customer-month pair is inserted.
- An existing pair with identical values is unchanged.
- An existing pair with different values causes a conflict.

The key contains both customer_id and observation_month.

Standard and Premium values for the same customer and month
conflict. Different plans in different months do not
automatically represent a conflict.

If an import encounters a conflict or database write failure,
the transaction rolls back all changes from that attempt.

An observation inserted earlier in the transaction is not
a successful permanent addition if the transaction later
rolls back.

Success is reported only after the transaction commits.
Error messages should explain the problem without exposing
database credentials.

## 7. Readable tests — my main takeaway

Readable tests helped me understand my code because they
showed what each function was expected to do.

Preparing an input, calling the function and checking the
result made its role clearer to me.

For example, the identical-reimport test showed that existing
observations should remain unchanged. The conflict test
showed that the entire import attempt must be rolled back.

I learned to identify three parts of a test:

1. Arrange: prepare the initial situation and input.
2. Act: execute the operation being tested.
3. Assert: check the expected result and relevant effects.

Checking an error message alone is insufficient for rollback.
The test must also check that no partial additions remain
and that existing observations are preserved.

For an identical reimport of the only 100 observations
already in the database, the expected result is:

- Inserted observations: 0.
- Unchanged observations: 100.
- Total stored observations: 100.

The stored values must also remain unchanged.

A test explains the scenario it covers. Understanding the
whole function requires reviewing other scenarios and its code.

## 8. Supplementary product learning

The product discussion helped me distinguish technical
verification from product validation.

Passing software tests provides evidence about implemented
behavior. It does not prove that the product meets a real
retention manager's needs.

The current import workflow is command-line based.
The Angular interface still displays connection status only.

We have not conducted interviews or usability tests with
real retention managers.

A proposed future interview question is:

"Can you tell me about the last time you compared subscription
cancellations across customer groups?"

This asks about actual experience without suggesting
StreamRetain's solution.

## 9. Application to Sprint 2 scope

Generating, validating and storing data provides a technical
foundation for later comparisons and indicators.

I compared this foundation to the support of a house:
the visible interface needs reliable underlying data.

However, interface mockups and user feedback can be explored
before all storage functionality is complete.
Technical work and learning about user needs can progress
together.

The Sprint 2 implementation delivers a reproducible generator,
CSV validation and transactional PostgreSQL import.

A dashboard and retention-action management remain future work.

All customer records are synthetic. A cancellation rate
calculated from them describes that fictional dataset,
not actual IVI customers.

## 10. Timing and limitations

This learning discussion took place after the implementation
of E2-01, E2-02 and E2-03.

It is a retrospective examination of existing decisions
and preparation for future work. It is not evidence that
these reading activities preceded implementation.

No complete-book reading, user research, dashboard
implementation or test-driven development history is claimed.

Direct reading of the official First Principles excerpt
has been completed. The broader learning discussion also
included guided explanations and StreamRetain exercises.

## 11. Next learning experiment

Before implementing a future function, I will describe:

- One representative input.
- Its expected result.
- One relevant error case.

I will use these examples to prepare understandable tests
and compare the implementation with the intended behavior.

This is a proposed improvement for future work, not a claim
that all existing tests were written before their implementation.

## 12. Related project evidence

- [Synthetic data generation](synthetic-data-generation.md)
- [CSV validation](csv-validation.md)
- [PostgreSQL import](postgresql-import.md)
- [Sprint 2 plan](sprint-2-plan.md)
- [S2-04 task](https://github.com/KAMATE12/RtreamRetain/issues/17)