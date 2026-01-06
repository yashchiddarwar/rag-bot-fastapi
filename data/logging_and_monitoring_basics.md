# Logging and Monitoring Basics (logging_and_monitoring_basics.md)

## Overview
Logging and monitoring were things I treated as “ops problems” early on. I logged a few errors, printed stack traces, and moved on. In production, I learned that when something breaks at 2 AM, logs and metrics are the *only* story you have. If that story is vague, noisy, or incomplete, recovery takes longer than the bug deserved.

Most incidents I’ve been part of weren’t hard to fix technically. They were hard to *understand*. Requests timing out with no context, services marked healthy while core flows were broken, or logs full of stack traces with no correlation to user actions. This document reflects how my approach changed after debugging real production failures where better logs and basic monitoring would have saved hours.

## Core Concepts
Only the parts that actually matter in practice.

- **Logs answer “what happened”**
  - They are forensic evidence.
  - If you can’t reconstruct a request’s journey, your logs are insufficient.

- **Metrics answer “how bad is it”**
  - Counts, latencies, error rates.
  - Logs tell stories; metrics show trends.

- **Monitoring is about signals, not dashboards**
  - A pretty dashboard that no one watches is useless.
  - Alerts should point to action, not noise.

- **Context matters more than volume**
  - One good log line with context beats ten stack traces.
  - Without identifiers, logs are just text.

## Common Problems
Mistakes I’ve personally made or seen repeatedly.

- **Logging too much**
  - Every method logs entry and exit.
  - Logs become unreadable.
  - Real issues get buried.

- **Logging too little**
  - Only stack traces.
  - No request data, no IDs, no parameters.
  - Impossible to reproduce issues.

- **Missing correlation**
  - One user request spans multiple services.
  - Logs can’t be tied together.
  - Debugging becomes guesswork.

- **Health checks lying**
  - App is “UP”.
  - DB is disconnected or downstream is failing.
  - Monitoring says green while users are blocked.

- **No distinction between expected and unexpected errors**
  - Validation failures logged as errors.
  - Real failures lost in noise.
  - Alerts trigger for normal behavior.

## Best Practices
What I would recommend today, based on experience.

- **Log at boundaries**
  - Incoming requests.
  - Outgoing calls.
  - Error boundaries.
  - Avoid logging every internal step.

- **Always include context**
  - Request ID or correlation ID.
  - User or entity identifiers where safe.
  - Operation name and outcome.

- **Use log levels deliberately**
  - INFO for business-relevant events.
  - WARN for abnormal but recoverable situations.
  - ERROR for failures requiring attention.
  - DEBUG only for local or targeted debugging.

- **Monitor the basics first**
  - Request rate.
  - Error rate.
  - Latency (especially p95/p99).
  - Resource usage (CPU, memory, DB connections).

- **Alert on symptoms, not causes**
  - Alert on error rate spikes, not individual errors.
  - Alert on sustained latency, not single slow requests.
  - Alerts should wake someone up *only when action is required*.

- **Make logs searchable**
  - Structured logs over plain text.
  - Consistent field names.
  - Predictable formats.

## Real-World Example
A realistic incident I’ve debugged.

We had a checkout API intermittently timing out.
Users complained, but metrics showed only a slight latency increase.

What went wrong:
- Logs showed stack traces with no request context.
- No way to tell which user or flow failed.
- Health checks showed service as healthy.

What we discovered later:
- A downstream service was slow for specific inputs.
- Requests piled up, threads blocked.
- No logs captured request IDs or downstream latency.

What we changed:
- Added request correlation IDs across services.
- Logged outbound call durations and failures.
- Added latency alerts on the checkout endpoint.

Result:
- Next incident was identified in minutes.
- Root cause was obvious from logs.
- Fix was straightforward instead of frantic.

## Trade-offs & Limitations
Logging and monitoring aren’t free.

- **More logs cost money**
  - Storage and ingestion add up.
  - Logging everything is expensive and useless.

- **Too many alerts cause fatigue**
  - People start ignoring alerts.
  - Real incidents get missed.

- **Privacy and security concerns**
  - Logging sensitive data is dangerous.
  - Redaction and discipline are required.

- **Monitoring doesn’t replace testing**
  - It tells you something broke, not why it was built that way.
  - Design flaws still surface in production.

## Summary
- Logs are for understanding *what happened*.
- Metrics are for understanding *how bad it is*.
- Most production pain comes from missing context, not missing data.
- Fewer, better logs beat noisy verbosity.
- If debugging relies on reproducing locally, your observability is weak.

Logging and monitoring don’t prevent failures. They decide whether failures are short and controlled—or long and chaotic.
