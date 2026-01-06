# REST API Design Principles (rest_api_design_principles.md)

## Overview
I used to think REST API design was mostly about naming endpoints cleanly and returning JSON. In production, I learned that bad API design doesn’t usually crash systems—it slowly poisons them. Clients misuse endpoints, teams become afraid to change anything, and every bug fix risks breaking consumers you didn’t even know existed.

Most real problems I’ve seen came from unclear contracts: APIs that didn’t clearly say what they do, what they guarantee, or how clients are expected to behave. This document reflects how my understanding of REST API design changed after maintaining and evolving APIs under real production pressure.

## Core Concepts
Only the concepts that actually matter once APIs are live.

- **APIs are long-term contracts**
  - Once clients integrate, you don’t control their usage.
  - Breaking changes hurt trust more than bugs.

- **Resources over actions**
  - URLs represent nouns (orders, users, payments).
  - HTTP methods express actions.
  - If your URL contains verbs everywhere, the design will age badly.

- **HTTP semantics are non-negotiable**
  - Status codes communicate intent to clients, gateways, retries, and caches.
  - Method choice affects idempotency and safety.
  - Ignoring HTTP rules creates invisible bugs.

- **Consistency beats correctness**
  - A consistent API is easier to use than a perfectly modeled but inconsistent one.
  - Predictability reduces client-side defensive code.

## Common Problems
Mistakes I’ve made or seen repeatedly.

- **Action-based endpoints**
  - `/createOrder`, `/cancelOrder`, `/doPayment`
  - Logic leaks into URLs.
  - Versioning and extension become painful.

- **Overloaded endpoints**
  - One endpoint behaving differently based on flags.
  - Hard to document, harder to debug.
  - Clients misuse it accidentally.

- **Incorrect status codes**
  - Returning 200 for validation errors.
  - Returning 500 for client mistakes.
  - Retries and alerts become meaningless.

- **Tight coupling to frontend needs**
  - APIs shaped around one UI screen.
  - Another client arrives and everything breaks.
  - Backend becomes a UI-specific adapter.

- **Silent breaking changes**
  - Renaming fields.
  - Changing enum values.
  - Removing response fields assumed to be “unused”.

## Best Practices
What I would actively recommend today.

- **Design APIs as products**
  - Clear purpose per endpoint.
  - Explicit behavior on success and failure.
  - Stable response shapes.

- **Use HTTP properly**
  - GET is safe and idempotent.
  - POST creates.
  - PUT replaces.
  - PATCH updates partially.
  - DELETE does exactly what it says.

- **Be explicit about failures**
  - Use correct status codes.
  - Return structured, predictable error responses.
  - Don’t hide errors inside 200 responses.

- **Version consciously**
  - Version only when contract breaks.
  - Prefer additive changes over breaking ones.
  - Deprecate before removal.

- **Keep responses boring**
  - Avoid dynamic keys.
  - Avoid polymorphic responses unless unavoidable.
  - Clients should not need custom logic per response.

## Real-World Example
A real pattern I’ve seen fail.

We had an endpoint:
`POST /order/process`

It:
- Created an order
- Reserved inventory
- Initiated payment
- Sent notifications

Problems that surfaced:
- Partial failures created ghost orders.
- Clients didn’t know which step failed.
- Retrying caused duplicate side effects.
- Fixing one step broke others.

What we changed:
- Split into resource-based endpoints:
  - `POST /orders`
  - `POST /orders/{id}/payments`
  - `POST /orders/{id}/confirm`
- Clear ownership per step.
- Explicit idempotency on critical operations.

Result:
- Failures became isolated.
- Retries were safe.
- Debugging stopped being guesswork.

## Trade-offs & Limitations
REST is not perfect.

- **More endpoints, more thinking**
  - Fine-grained APIs require discipline.
  - Initial design effort is higher.

- **Strict REST can feel rigid**
  - Some workflows don’t map cleanly to resources.
  - Pragmatism sometimes wins over purity.

- **Backward compatibility slows change**
  - You can’t “just fix” things.
  - Requires planning and communication.

- **Over-abstraction hurts**
  - Overengineering REST purity creates friction.
  - Simple systems don’t need complex modeling.

## Summary
- REST APIs are contracts, not just transport layers.
- Most pain comes from ambiguity, not logic bugs.
- HTTP semantics exist for a reason—use them.
- Consistency and clarity matter more than clever designs.
- If changing an API feels scary, the contract was probably weak.

Good REST design doesn’t make APIs faster—but it makes systems survivable.
