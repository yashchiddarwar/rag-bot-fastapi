# Microservice Deployment Failures (microservice_deployment_failures.md)

## Overview
Microservice deployment failures are rarely caused by one big mistake. Almost every serious incident I’ve seen was a combination of small, “harmless” changes deployed together under time pressure. Port changes, config tweaks, dependency bumps—each one safe in isolation—end up creating a chain reaction when deployed across multiple services.

Early on, I assumed deployments fail because of bad code. In reality, most failures come from coordination issues: config drift, partial rollouts, incompatible versions, or assumptions that worked in one service but not in another. This document captures how I now think about deployment failures after dealing with broken releases, emergency rollbacks, and production outages caused by seemingly trivial changes.

## Core Concepts
Only the concepts that actually matter during real deployments.

- **Microservices fail independently**
  - Each service has its own config, runtime, and failure modes.
  - “One change” is actually many changes multiplied by service count.

- **Deployments are distributed events**
  - Not all services deploy at the same time.
  - For a window of time, multiple versions coexist.
  - Backward compatibility matters more than correctness.

- **Configuration is part of deployment**
  - Code deploys are often safe.
  - Config deploys are where things break.
  - Ports, URLs, credentials, and feature flags are common culprits.

- **Rollback is a first-class feature**
  - If rollback is slow or risky, deployment is unsafe.
  - A deployment without a rollback plan is gambling.

## Common Problems
Failures I’ve personally seen or realistically could.

- **Bulk deployments**
  - Deploying many services together “because the change is small”.
  - When something breaks, root cause becomes unclear.
  - Blast radius increases massively.

- **Config drift across environments**
  - Dev works.
  - Staging partially works.
  - Prod fails because config sources differ.
  - Root cause hides in precedence or missing variables.

- **Incompatible service versions**
  - One service expects a new field.
  - Another still sends the old payload.
  - Errors appear only at runtime.

- **Hidden dependency changes**
  - Minor library upgrade.
  - Transitive behavior changes.
  - Multiple services break in different ways.

- **Health checks lying**
  - Service starts successfully.
  - Health endpoint returns OK.
  - Core functionality is broken.

## Best Practices
What I actively recommend today.

- **Deploy in small batches**
  - 2–3 services at a time.
  - Validate before moving forward.
  - Damage control becomes manageable.

- **Separate config changes from code**
  - Deploy config changes independently where possible.
  - Observe behavior before code rollout.
  - Makes rollback faster and safer.

- **Design for version overlap**
  - New versions should handle old inputs.
  - Additive changes before breaking ones.
  - Assume mixed versions during deployment.

- **Automate sanity checks**
  - Verify DB connectivity.
  - Verify downstream calls.
  - Not just “app is up”.

- **Always know what changed**
  - Track exactly what went into a deployment.
  - Avoid “misc fixes” releases.
  - Small diff, clear intent.

## Real-World Example
A deployment failure pattern I’ve personally experienced.

We needed to change a database port due to infrastructure migration.
The change itself was trivial.

What happened:
- About 15 microservices needed redeployment.
- Change was merged quickly across branches.
- Deployment was done in one go.

Result:
- ~9 services came up fine.
- Remaining services failed to start.
- Root cause varied:
  - Missing config updates.
  - Old environment variables still overriding values.
  - Minor unrelated changes slipped into some merges.

Why it hurt:
- Failures looked unrelated.
- Rollback was messy.
- Debugging under pressure led to more mistakes.

What I changed after that:
- Deploy in batches.
- Lock branches during infra changes.
- Verify config source per service before deploy.

That single change in process reduced deployment stress dramatically.

## Trade-offs & Limitations
There’s no perfect deployment strategy.

- **Slower deployments**
  - Batch deployments take more time.
  - But reduce risk significantly.

- **More discipline required**
  - Engineers must respect version compatibility.
  - “Quick fixes” become harder.

- **Operational overhead**
  - Monitoring and validation add work.
  - But save time during incidents.

- **Microservices amplify mistakes**
  - What’s trivial in a monolith becomes risky.
  - Requires mindset shift, not just tooling.

## Summary
- Most microservice deployment failures are process failures, not code failures.
- Small changes become dangerous when multiplied across services.
- Config is as risky as code, sometimes more.
- Batch deployments drastically reduce blast radius.
- If rollback feels scary, the deployment is already unsafe.

Microservices don’t forgive sloppy deployments. The system will work—until it very suddenly doesn’t.
