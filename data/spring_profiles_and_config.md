# Spring Profiles and Configuration (spring_profiles_and_config.md)

## Overview
Spring profiles look simple until you deploy the wrong config to the wrong environment and spend your evening firefighting. For me, profiles became important not when I learned them, but when I *misused* them—hardcoded values slipping into prod, secrets committed accidentally, or services behaving differently locally vs staging with no clear reason why.

Profiles are essentially how Spring decides *which reality your application is living in*. If you don’t control that explicitly, the application will choose for you—and it rarely chooses correctly in production.

This doc captures how I now think about profiles after dealing with broken deployments, misconfigured ports, and “works on my machine” incidents.

## Core Concepts
Only what actually matters in day-to-day backend work.

- **A profile is just a conditional switch**
  - Spring loads beans and config based on active profiles.
  - Nothing magical—just conditional wiring.

- **Config precedence matters more than profiles**
  - Order (high to low):
    1. Command-line args
    2. Environment variables
    3. `application-{profile}.yml`
    4. `application.yml`
  - Most bugs happen because we assume the wrong source is winning.

- **Profiles decide *what* loads, not *how***
  - Profiles don’t validate config correctness.
  - Spring will happily boot with wrong values if they exist.

- **One app, multiple personalities**
  - Same artifact runs everywhere.
  - Only config changes.
  - If code changes per environment, something is already wrong.

## Common Problems
Things I’ve actually seen break systems.

- **Prod running with `default` profile**
  - No `spring.profiles.active` set.
  - App boots using fallback config.
  - Wrong DB, wrong ports, wrong credentials.

- **Overloaded `application.yml`**
  - One massive file with commented prod/stage/dev configs.
  - Human error waiting to happen.
  - Someone uncomments the wrong block.

- **Secrets mixed with environment config**
  - DB passwords inside profile files.
  - Git history becomes a security liability.
  - Rotation becomes painful.

- **Profile-specific beans abused**
  - Business logic split across profiles.
  - “Dev-only” shortcuts leaking into prod behavior.
  - Debugging becomes impossible.

- **Local != staging**
  - Local uses `.yml`
  - Staging uses env vars
  - Prod uses Kubernetes config maps
  - Three sources, one confused engineer.

## Best Practices
What I now do consistently.

- **Always set the active profile explicitly**
  - Local: IDE or `.env`
  - Server: startup args or env var
  - Never rely on defaults.

- **Thin profile files**
  - Only environment-specific values.
  - No logic, no duplication.

- **One responsibility per config source**
  - Profiles → environment differences
  - Env vars → secrets
  - Base config → shared defaults

- **Fail fast on missing config**
  - If a required value isn’t present, app should not boot.
  - Silent fallbacks are dangerous.

- **Document expected config**
  - A sample config file or README per service.
  - New devs shouldn’t reverse-engineer prod behavior.

## Real-World Example
A realistic deployment failure.

We migrated DB ports across environments.
Change was trivial—just port numbers.

What went wrong:
- Dev profile updated correctly.
- Staging picked values from environment variables.
- Prod still used old port via `application.yml`.
- 9 out of ~15 services failed post-deployment.

Why it hurt:
- Config source precedence wasn’t documented.
- Everyone assumed profile files were the source of truth.
- Rollback took longer than the change itself.

What I changed afterward:
- Removed DB connection details from base config.
- Forced all DB credentials via environment variables.
- Added a startup log printing active profile and DB host (not password).

That one log line saved hours later.

## Trade-offs & Limitations
Profiles are useful, but not perfect.

- **Too many profiles increase mental load**
  - `dev`, `local`, `test`, `staging`, `preprod`, `prod`
  - People stop knowing which does what.

- **Profiles don’t enforce safety**
  - Spring won’t stop you from pointing prod to test DB.
  - Discipline matters more than tooling.

- **Complexity grows with microservices**
  - Each service = its own config surface.
  - Centralized config helps but adds infra dependency.

- **Debugging config is not straightforward**
  - You often discover issues only at runtime.
  - Logs become critical.

## Summary
- Profiles decide *which config loads*, not whether it’s correct.
- Most production issues come from config precedence confusion.
- Be explicit about active profiles everywhere.
- Keep profile files small and boring.
- If config behavior surprises you, it’s already too complex.

Profiles don’t make systems safer by default. Clear ownership and predictable rules do.
