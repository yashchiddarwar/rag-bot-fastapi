# Caching Strategies in Backend Systems (caching_strategies_backend.md)

## Overview
Caching is one of those tools that feels like a silver bullet until it starts lying to you. Early on, I added caches to “make things fast” and felt good when latency dropped. In production, I learned caching mostly **moves problems around**. You trade CPU and DB load for consistency issues, stale data, and harder debugging.

Most caching incidents I’ve seen weren’t because cache was missing—they were because it was **incorrectly scoped**, **never invalidated**, or **used as a band-aid** for deeper problems. This document reflects how my thinking around caching evolved after dealing with stale dashboards, ghost data, and bugs that only reproduced after cache expiry.

## Core Concepts
Only what actually matters when caches are live.

- **Caching is a consistency trade**
  - You’re explicitly accepting stale data.
  - The question is not *if* data is stale, but *how stale is acceptable*.

- **What you cache matters more than where**
  - Caching raw DB rows vs derived responses changes invalidation complexity.
  - Higher-level caches are faster but harder to invalidate correctly.

- **Read-heavy vs write-heavy behavior**
  - Caches shine when reads dominate.
  - In write-heavy systems, cache churn can cost more than it saves.

- **Cache lifetime defines system behavior**
  - TTL too short → cache useless.
  - TTL too long → data lies confidently.
  - TTL selection is a product decision, not a technical one.

## Common Problems
Issues I’ve personally hit or seen teams struggle with.

- **Stale data causing business bugs**
  - User updates profile.
  - API still returns old data.
  - Support ticket raised, logs show “correct” DB state.

- **Cache masking bad queries**
  - Slow query hidden by cache.
  - Query never fixed.
  - Cache miss during spike brings system down.

- **Over-caching**
  - Every endpoint cached “just in case”.
  - Invalidation logic explodes.
  - No one knows what’s safe to clear.

- **Cache stampede**
  - Popular key expires.
  - Many requests hit DB at once.
  - DB load spikes suddenly.

- **Environment-specific cache bugs**
  - Local cache disabled.
  - Staging partially enabled.
  - Prod behaves differently, debugging becomes guesswork.

## Best Practices
What I actually recommend today.

- **Cache only proven hot paths**
  - Identify endpoints that are slow *and* frequently hit.
  - Don’t pre-emptively cache everything.

- **Prefer simple invalidation**
  - Time-based invalidation over event-based unless required.
  - Fewer rules mean fewer bugs.

- **Cache read models, not write paths**
  - Writes should go straight to DB.
  - Reads can tolerate controlled staleness.

- **Fail open on cache issues**
  - If cache is down, fall back to DB.
  - Cache outages shouldn’t become system outages.

- **Log cache behavior**
  - Hits, misses, evictions.
  - Helps distinguish cache problems from DB problems.

- **Treat cache as disposable**
  - Clearing cache should never break correctness.
  - If it does, cache is holding business state it shouldn’t.

## Real-World Example
A realistic production issue I’ve debugged.

We cached user account summaries for performance.
TTL was set to 10 minutes.

What went wrong:
- Users updated bank account details.
- UI continued showing old data.
- DB was correct, cache was not.
- Support escalations increased.

Root cause:
- Cache key was user ID.
- No invalidation on update.
- TTL chosen arbitrarily without business alignment.

What we changed:
- Reduced TTL for sensitive fields.
- Split cache: static profile vs dynamic financial data.
- Explicit cache eviction on critical updates.

Result:
- Slightly higher DB load.
- Much fewer correctness complaints.
- Predictable behavior under updates.

## Trade-offs & Limitations
Caching always comes with costs.

- **Increased complexity**
  - Invalidation logic is harder than caching itself.
  - Bugs are subtle and time-dependent.

- **Debugging becomes non-deterministic**
  - Bug appears only for some users.
  - Cache state differs per node or region.

- **Consistency guarantees weaken**
  - Strong consistency and caching don’t coexist easily.
  - Business must accept eventual correctness.

- **Operational overhead**
  - Cache sizing, eviction policies, monitoring.
  - Another moving part to maintain.

- **Not all data should be cached**
  - Financial, authorization, and transactional data need caution.
  - Wrong cache here causes real damage.

## Summary
- Caching is a performance optimization with correctness cost.
- Most issues come from stale or incorrectly scoped caches.
- Cache hot reads, not critical writes.
- Simple invalidation beats clever invalidation.
- If clearing cache breaks your system, the design is wrong.

Caching doesn’t make systems better by default. Used carefully, it buys you performance. Used blindly, it buys you subtle bugs that show up at the worst time.
