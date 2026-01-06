# Rate Limiting and Throttling (rate_limiting_and_throttling.md)

## Overview
Rate limiting is one of those things you usually add *after* something breaks. In my case, it showed up after APIs that worked perfectly in testing started falling over in production—CPU spikes, DB connection exhaustion, and one client accidentally taking down a shared service. The system wasn’t buggy; it was just too permissive.

What I learned the hard way is that rate limiting isn’t about security or fairness alone. It’s about **protecting system capacity** and **controlling blast radius**. Without it, every downstream dependency is exposed to the worst-behaved client. This document reflects how I now think about rate limiting and throttling after seeing real incidents, not theoretical abuse cases.

## Core Concepts
Only the concepts that actually matter in real systems.

- **Rate limiting protects capacity, not endpoints**
  - It’s not about stopping users.
  - It’s about preventing resource exhaustion (threads, DB connections, queues).

- **Throttling vs hard limiting**
  - Hard limit: requests are rejected immediately.
  - Throttling: requests are slowed down or delayed.
  - Most backend systems benefit more from hard limits than polite throttling.

- **Limits must align with bottlenecks**
  - CPU-bound service → CPU protection.
  - DB-heavy service → connection and query protection.
  - Rate limits that ignore bottlenecks are cosmetic.

- **Where you apply limits matters**
  - Gateway-level limits protect the entire system.
  - Service-level limits protect local resources.
  - DB-level limits are a last line of defense.

## Common Problems
Failures I’ve personally seen or could realistically happen.

- **No rate limiting at all**
  - One misconfigured client loops requests.
  - DB pool exhausts.
  - All users see timeouts.

- **Global limits only**
  - One noisy client consumes the entire quota.
  - Well-behaved clients get penalized.
  - Hard to debug because “limits exist”.

- **Limits too high to matter**
  - Configured generously “to be safe”.
  - Doesn’t actually protect anything.
  - Failure still happens under spikes.

- **Limits applied too late**
  - Rate limiting after auth, DB lookup, or heavy validation.
  - Resources already consumed.
  - Protection is ineffective.

- **Inconsistent limits across services**
  - One service is protected.
  - Downstream services are not.
  - Failures just move deeper into the system.

## Best Practices
What I would recommend today based on experience.

- **Start with simple, conservative limits**
  - It’s easier to increase limits than recover from outages.
  - Most systems don’t need high throughput per user.

- **Limit early in the request lifecycle**
  - As close to the edge as possible.
  - Before DB access or expensive computation.

- **Use per-client or per-key limits**
  - API key, user ID, or IP.
  - Prevents one client from starving others.

- **Fail fast and clearly**
  - Return explicit rate-limit errors.
  - Don’t let requests hang or timeout silently.

- **Align limits with downstream capacity**
  - If DB can handle 100 concurrent operations, don’t allow 500 requests/sec.
  - Rate limiting should reflect weakest dependency.

- **Log and monitor limit hits**
  - Rate limit events are signals.
  - They often reveal bugs, not abuse.

## Real-World Example
A realistic production scenario.

We had a reporting API used by internal dashboards.
It queried multiple tables and aggregated data.

What went wrong:
- A frontend bug triggered polling every second.
- Each user opened multiple tabs.
- Request rate multiplied quickly.
- DB connections maxed out.
- Entire service became unresponsive.

Why it was bad:
- No rate limiting.
- Each request was expensive.
- Failure impacted unrelated APIs sharing the DB.

What we changed:
- Added per-user rate limits at the gateway.
- Added stricter limits on the reporting endpoint itself.
- Cached responses for short durations.

Result:
- Bug still existed, but impact was contained.
- Other services stayed healthy.
- Debugging happened without production fire.

## Trade-offs & Limitations
Rate limiting is not free.

- **Too strict limits hurt UX**
  - Legitimate users get blocked.
  - Needs tuning and feedback loops.

- **Stateful limits add complexity**
  - Distributed rate limiting requires shared state.
  - Adds operational overhead.

- **Limits don’t fix inefficient APIs**
  - Bad queries remain bad.
  - Limits only delay failure, not remove it.

- **Edge cases are hard**
  - Bursts vs sustained traffic.
  - Background jobs vs user traffic.
  - One-size-fits-all limits rarely work.

## Summary
- Rate limiting is about protecting system capacity, not punishing users.
- Most outages happen because limits are missing or meaningless.
- Apply limits early, based on real bottlenecks.
- Prefer failing fast over slow degradation.
- If one client can hurt everyone, rate limiting is insufficient.

Rate limiting doesn’t make systems faster—but it keeps them alive long enough for you to fix the real problem.
