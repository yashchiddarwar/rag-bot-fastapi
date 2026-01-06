# SQL Indexes and Trade-offs (sql_indexes_and_tradeoffs.md)

## Overview
Indexes were one of those things I thought I “knew” early on: add an index, queries get faster. In production, I learned that indexes are closer to a tax system than a free optimization. Every index you add speeds up some reads and quietly slows down writes, deployments, and sometimes even recovery.

Most real issues I’ve seen around indexes weren’t about missing indexes—they were about *wrong* indexes, too many indexes, or indexes added without understanding actual query patterns. This document captures how my mental model around SQL indexes evolved after debugging slow APIs, write bottlenecks, and unexpected DB load.

## Core Concepts
Only the parts that matter when systems are under load.

- **Indexes optimize access paths, not queries**
  - The database uses indexes to find rows faster.
  - A fast query is usually one that touches fewer rows, not one that’s “well written”.

- **Every index is a data structure**
  - It needs storage.
  - It needs maintenance on every insert, update, and delete.
  - Indexes are not free, even if reads are faster.

- **Composite index order matters**
  - `(A, B)` is not the same as `(B, A)`.
  - Index usage depends on leading columns.
  - Wrong order = index exists but is never used.

- **Indexes reflect query patterns**
  - You index for `WHERE`, `JOIN`, and `ORDER BY`.
  - Indexing columns that are never filtered is useless.

## Common Problems
Issues I’ve either seen directly or could realistically happen.

- **Indexing everything “just in case”**
  - Tables with 10+ indexes.
  - Writes slow down.
  - Developers stop understanding which index does what.

- **Indexes added based on assumptions**
  - Indexing columns that “seem important”.
  - Actual production queries filter differently.
  - Index never gets used.

- **Ignoring write-heavy workloads**
  - Index added to speed up one dashboard.
  - Inserts and updates slow across the system.
  - Latency spikes under load.

- **Composite indexes with wrong order**
  - Query filters by `STATUS` then `CREATED_AT`.
  - Index built as `(CREATED_AT, STATUS)`.
  - Database scans anyway.

- **Indexes masking bad queries**
  - N+1 queries hidden by indexes.
  - System works until data grows.
  - Failure is delayed, not prevented.

## Best Practices
What I actually recommend after seeing pain.

- **Index only after observing queries**
  - Use real query logs.
  - Don’t index based on intuition.
  - Optimize what actually runs in production.

- **Design indexes around access patterns**
  - Start with `WHERE` clauses.
  - Then `JOIN` columns.
  - Then `ORDER BY` if needed.

- **Be deliberate with composite indexes**
  - Put the most selective column first.
  - Match the common filter order.
  - Avoid wide composite indexes unless justified.

- **Review indexes as part of schema changes**
  - Every new feature adds queries.
  - Old indexes might become useless.
  - Periodic cleanup matters.

- **Measure both read and write impact**
  - Faster reads don’t help if writes become the bottleneck.
  - Balance matters more than raw speed.

## Real-World Example
A pattern I’ve seen multiple times.

We had an orders table powering:
- Order creation
- User order history
- Admin dashboards

Problem:
- User history API was slow.
- An index was added on `USER_ID`.

What went wrong:
- Admin dashboards filtered by `STATUS` and `CREATED_AT`.
- Writes slowed because multiple indexes were being maintained.
- Insert latency increased under peak traffic.

What fixed it:
- Removed unused single-column indexes.
- Added a composite index aligned to actual queries.
- Left write-heavy paths with minimal indexing.

Result:
- User history became fast.
- Writes stabilized.
- Overall DB load reduced.

## Trade-offs & Limitations
Indexes always involve compromise.

- **Indexes speed reads but slow writes**
  - This is unavoidable.
  - High-write systems must be conservative.

- **More indexes = more maintenance**
  - Disk usage increases.
  - Backups and migrations slow down.

- **Indexes can hide design issues**
  - Poor query design may appear “fine” initially.
  - Problems resurface as data grows.

- **Not all queries benefit**
  - Low-selectivity columns may not gain much.
  - Sometimes a full scan is cheaper.

## Summary
- Indexes are powerful but expensive.
- Most problems come from over-indexing or misaligned indexes.
- Always index for real query patterns, not assumptions.
- Composite index order matters more than people expect.
- If writes slow down unexpectedly, indexes are a prime suspect.

Indexes don’t fix bad data access patterns—they only delay the pain if misused.
