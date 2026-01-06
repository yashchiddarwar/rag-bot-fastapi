# Exception Handling Patterns (exception_handling_patterns.md)

## Overview
Exception handling is where backend systems quietly rot if you’re not deliberate. Early in my experience, I treated exceptions as something you “catch and log”. In production, I learned that exceptions actually define how reliable your system feels to users and how recoverable it is for engineers.

I’ve seen cases where data was partially written, APIs returned 200 with error messages inside JSON, and logs were full of stack traces that meant nothing. Almost every one of those incidents traced back to poor exception boundaries. This document reflects how I now reason about exceptions after breaking things and being on-call for them.

## Core Concepts
Only what actually matters in practice.

- **Exceptions represent responsibility boundaries**
  - Controller layer decides *what the client sees*.
  - Service layer decides *business failure vs system failure*.
  - Repository layer should mostly surface technical failures, not interpret them.

- **Runtime exceptions work better with Spring**
  - They propagate cleanly.
  - They trigger transaction rollback by default.
  - Checked exceptions often create more harm than safety in Spring-based systems.

- **An exception must have a single meaning**
  - Client mistake
  - Business rule violation
  - System failure
  - Mixing these leads to incorrect HTTP status codes and bad retries.

- **Logging is not handling**
  - Logging an exception and continuing is often worse than failing fast.
  - Exceptions should either be translated or propagated, not swallowed.

## Common Problems
Mistakes I’ve seen repeatedly.

- **Swallowing exceptions**
  - `try-catch` with just a log statement.
  - Application continues in an invalid state.
  - Data inconsistencies show up days later.

- **Generic `Exception` catch blocks**
  - Everything becomes “something went wrong”.
  - No differentiation between client errors and server failures.
  - Monitoring and alerting become useless.

- **Returning error info with HTTP 200**
  - “status”: false in response body.
  - Clients treat it as success.
  - Retries, caches, and gateways all behave incorrectly.

- **Throwing exceptions from deep layers without context**
  - Raw SQL or NullPointer exceptions bubbling to controller.
  - No business meaning attached.
  - Debugging requires digging through logs instead of reading the error.

- **Checked exceptions inside transactional flows**
  - Business validation throws checked exception.
  - Transaction commits anyway.
  - Silent data corruption.

## Best Practices
What I would recommend today, based on pain.

- **Define exception ownership**
  - Repository: throw technical exceptions.
  - Service: translate to business/system exceptions.
  - Controller: map to HTTP responses.

- **Prefer unchecked custom exceptions**
  - Explicit naming communicates intent.
  - Works naturally with Spring transactions.
  - Easier to reason about rollback behavior.

- **Fail fast and loudly**
  - If a state is invalid, throw immediately.
  - Don’t try to “recover” silently unless you’re very sure.

- **Centralize HTTP error mapping**
  - One place decides status codes and response format.
  - Keeps controllers clean and predictable.

- **Log once, at the boundary**
  - Log where context is richest (usually controller or global handler).
  - Avoid logging the same exception multiple times.

## Real-World Example
A realistic production scenario.

We had an order creation API:
- Validate input
- Save order
- Save order items
- Call downstream inventory service

What went wrong:
- Inventory service timed out.
- Exception was caught and logged inside service layer.
- API returned success with partial order saved.
- Users saw orders that could never be fulfilled.

Why it happened:
- Exception was treated as “non-critical”.
- No clear rule on when to fail vs continue.
- Controller had no idea something went wrong.

What we changed:
- Inventory failure treated as system exception.
- Exception propagated up.
- Transaction rolled back.
- API returned 503 with clear message.

Result:
- Fewer “ghost” orders.
- Easier retries.
- Cleaner recovery path.

## Trade-offs & Limitations
Exception handling isn’t free.

- **More custom exceptions = more classes**
  - Needs discipline to avoid explosion.
  - Naming becomes important.

- **Fail-fast can feel harsh**
  - Some teams prefer partial success.
  - Requires clear business alignment.

- **Over-handling reduces clarity**
  - Too many translations hide root cause.
  - Sometimes letting an exception bubble is better.

- **Testing exception paths is work**
  - Often skipped.
  - Bugs appear only under failure conditions.

## Summary
- Exceptions define system behavior under failure, not just error cases.
- Most production bugs come from swallowed or misclassified exceptions.
- Runtime exceptions align better with Spring and transactions.
- Each layer must know whether to handle, translate, or propagate.
- If an exception surprises you in logs, your boundaries are wrong.

Clean exception handling doesn’t make systems perfect—but it makes failures predictable and recoverable.
