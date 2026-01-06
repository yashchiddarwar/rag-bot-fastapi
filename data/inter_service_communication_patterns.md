# Inter-Service Communication Patterns (inter_service_communication_patterns.md)

## Overview
Inter-service communication is where microservices stop being clean boxes on a diagram and start behaving like a real system. Early on, I thought choosing REST over messaging (or vice versa) was the main decision. In production, I learned the real problems come from *when* services talk, *how long they wait*, and *what happens when the other side is slow, down, or partially broken*.

Most incidents I’ve seen weren’t caused by a service being completely down, but by it being *slow*, *inconsistent*, or *returning unexpected responses*. Inter-service communication defines your system’s failure modes. This doc captures how my understanding evolved after debugging timeouts, cascading failures, and “why is everything slow?” incidents.

## Core Concepts
Only what actually matters in practice.

- **Synchronous vs asynchronous is a failure decision**
  - Sync calls couple uptime and latency.
  - Async decouples availability but complicates flow.
  - The choice defines how failures propagate.

- **Latency compounds**
  - One service calling three others adds their latencies.
  - P95 becomes your new normal.
  - Slow dependencies silently degrade the whole system.

- **Retries are dangerous by default**
  - Retrying failed calls multiplies traffic.
  - Under load, retries often make outages worse.
  - Retry logic must be intentional and bounded.

- **Contracts matter more than transport**
  - REST, messaging, or gRPC doesn’t matter if payloads are unstable.
  - Versioning and backward compatibility are non-negotiable.

## Common Problems
Failures I’ve personally seen or realistically could.

- **Cascading failures**
  - One downstream service slows.
  - Upstream threads block.
  - Connection pools exhaust.
  - Entire system appears down.

- **Overuse of synchronous calls**
  - Every operation becomes a chain of REST calls.
  - One slow service delays everything.
  - Debugging turns into tracing spaghetti.

- **Missing or misconfigured timeouts**
  - Default timeouts are often too high.
  - Threads wait far longer than they should.
  - Failures surface late and violently.

- **Blind retries**
  - Client retries immediately on failure.
  - Downstream gets hammered.
  - Recovery takes longer.

- **Tight coupling through shared assumptions**
  - One service expects fields that aren’t guaranteed.
  - Another service changes behavior “safely”.
  - Runtime failures appear without compile-time signals.

## Best Practices
What I would recommend today, based on experience.

- **Be intentional about sync vs async**
  - User-facing, immediate response → sync.
  - Background, eventual consistency → async.
  - Don’t default to sync just because it’s easier.

- **Always set timeouts**
  - Every outbound call.
  - Shorter than you think.
  - A fast failure is better than a slow one.

- **Fail fast and propagate clearly**
  - If a dependency is unhealthy, surface it.
  - Don’t hide failures behind partial success unless explicitly required.

- **Design APIs for backward compatibility**
  - Add fields, don’t remove.
  - Tolerate unknown fields.
  - Assume mixed versions in production.

- **Isolate dependencies**
  - Separate thread pools or clients per dependency.
  - Prevent one slow service from blocking everything else.

## Real-World Example
A realistic failure I’ve debugged.

We had an order service that synchronously called:
- Inventory service
- Pricing service
- Payment service

Symptoms:
- Order API latency slowly increased.
- No service showed obvious errors.
- Eventually, requests started timing out.

Root cause:
- Inventory service had increased latency due to DB load.
- Order service threads waited on inventory responses.
- Connection pool exhausted.
- New requests blocked, even though other dependencies were fine.

What we changed:
- Added strict timeouts on inventory calls.
- Moved pricing recalculation to async.
- Returned partial failure explicitly when inventory was unavailable.

Result:
- System degraded gracefully.
- Orders failed fast instead of hanging.
- Debugging became straightforward.

## Trade-offs & Limitations
There’s no perfect pattern.

- **Synchronous calls are simpler**
  - Easier to reason about.
  - Easier to debug.
  - But fragile under load.

- **Asynchronous flows add complexity**
  - Harder to trace.
  - Event ordering issues.
  - Requires idempotency and replay handling.

- **More isolation means more configuration**
  - Multiple clients.
  - Multiple thread pools.
  - Operational overhead increases.

- **Failure transparency can hurt UX**
  - Users see errors sooner.
  - But silent failures are worse long-term.

## Summary
- Inter-service communication defines how failures spread.
- Most outages are caused by slowness, not total downtime.
- Synchronous calls amplify latency and risk.
- Timeouts and isolation are mandatory, not optional.
- If one service can take down many others, the communication pattern is wrong.

Microservices don’t fail cleanly. How they talk to each other decides how badly they fail.
inter_service_communication_patterns.md