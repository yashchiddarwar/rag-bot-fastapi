# Spring Transaction Management (spring_transaction_management.md)

## Overview
Transaction management in Spring is one of those things that feels trivial until it breaks in production. On paper, `@Transactional` looks like a magic switch. In reality, it’s a set of rules layered on top of proxies, database behavior, and call patterns that can silently fail if you don’t respect them.

I’ve seen transactions fail not because Spring is “buggy”, but because we misunderstood *where* the transaction actually starts, *what* it rolls back on, and *who* owns the connection. Most issues surfaced only after partial writes, inconsistent data, or support tickets saying “payment deducted but order missing”.

This doc captures how I now think about Spring transaction management after breaking it a few times.

## Core Concepts
Only the concepts that matter in practice.

- **Transactions are proxy-based**
  - `@Transactional` works through Spring proxies.
  - If a method is not called through the proxy, the transaction does not exist.
  - Internal method calls (`this.method()`) bypass transactions completely.

- **Rollback is exception-driven**
  - By default, Spring rolls back only on unchecked exceptions (`RuntimeException`).
  - Checked exceptions *do not* trigger rollback unless explicitly configured.
  - This single detail causes most “why did it commit?” incidents.

- **Transaction scope = connection scope**
  - One transaction = one DB connection.
  - If you call an external service inside a transaction, that DB connection stays open and locked.
  - Long transactions kill throughput.

- **Propagation defines boundaries**
  - `REQUIRED` joins or creates a transaction.
  - `REQUIRES_NEW` suspends the current one.
  - Most systems misuse propagation without realizing the side effects.

## Common Problems
Things I’ve personally seen or could realistically happen.

- **`@Transactional` on private methods**
  - Looks fine in code review.
  - Does nothing at runtime.
  - Result: partial commits with no rollback.

- **Internal method calls**
  - `serviceA.method1()` calls `method2()` inside the same class.
  - `method2()` has `@Transactional`.
  - No transaction is created. Ever.

- **Checked exception leakage**
  - Business validation throws a checked exception.
  - DB writes already happened.
  - Transaction commits.
  - Data corruption masked as “expected flow”.

- **Over-scoped transactions**
  - Transaction starts → API call → Kafka publish → email send → DB write.
  - If email blocks, DB connection blocks.
  - Seen this cause pool exhaustion under load.

- **Misused `REQUIRES_NEW`**
  - Used to “be safe”.
  - Actually creates hidden commits even when parent fails.
  - Leads to orphan records and audit nightmares.

## Best Practices
What I actually recommend today.

- **Keep transactions small and boring**
  - Only DB reads/writes.
  - No network calls.
  - No message publishing.

- **Fail fast, then write**
  - Validate inputs *before* opening a transaction.
  - Do not rely on rollback for validation logic.

- **Be explicit about rollback rules**
  - If a failure must rollback, make it a runtime exception.
  - Avoid mixing checked exceptions with transactional logic.

- **One transaction per business state change**
  - “Create order” is one transaction.
  - “Send notification” is not part of it.

- **Split orchestration and persistence**
  - Orchestrator service (non-transactional)
  - Persistence service (transactional)
  - Makes boundaries obvious and testable.

## Real-World Example
A production issue I’ve seen variants of.

We had an order creation flow:
1. Save order
2. Save order items
3. Call payment service
4. Update order status

Everything sat inside a single `@Transactional` method.

What went wrong:
- Payment service latency spiked.
- DB connections stayed open during API calls.
- Connection pool exhausted.
- New requests started failing.
- Worse: some orders were saved but never paid.

What we changed:
- Transaction only wrapped steps 1 and 2.
- Payment call moved outside.
- Order status update handled in a separate transaction.
- Idempotency added at the payment boundary.

Result:
- Shorter transactions.
- Predictable rollback behavior.
- Easier recovery for partial failures.

## Trade-offs & Limitations
Transaction management is not free.

- **Complexity leaks**
  - Propagation rules are hard to reason about.
  - Debugging nested transactions is painful.

- **Does not solve distributed consistency**
  - Transactions stop at the database.
  - They do not protect you from partial failures across services.

- **Overuse reduces scalability**
  - High contention tables + long transactions = slow system.
  - Sometimes eventual consistency is the better trade-off.

- **Testing gaps**
  - Unit tests rarely catch transactional bugs.
  - Most issues appear only under real concurrency.

## Summary
- `@Transactional` is not magic; it’s a proxy with rules.
- Most bugs come from misunderstanding call paths and rollback behavior.
- Keep transactions short, explicit, and database-only.
- Never mix orchestration logic with transactional persistence.
- If you can’t clearly explain where a transaction starts and ends, it’s probably wrong.

This is one of those areas where being boring and explicit beats clever abstractions every time.
