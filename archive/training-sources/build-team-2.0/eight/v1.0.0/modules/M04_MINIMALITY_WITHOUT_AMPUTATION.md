# M04 — Minimality Without Amputation

## Learning objective
Reduce cost, delay, path count, calls, services, and operator burden while preserving every accepted responsibility.

## Scenario
Design A uses five repository paths, two persistent services, six provider calls, and three operator steps.

Design B uses three paths, one service, three calls, and one operator step, but removes:
- a generated provenance manifest;
- closing mutable-currentness readback;
- an independent rollback witness.

Produce:
1. the full acceptance-responsibility list that must survive;
2. a responsibility-to-component map for A and B;
3. which removals are valid, invalid, or unproven;
4. the smallest defensible architecture you can derive;
5. measurements required before claiming actual savings.

Include one counterexample where **adding** a repository path is the more minimal valid architecture because it eliminates a larger runtime mechanism or ambiguity surface.

## PASS CRITERIA
- Optimizes responsibilities, not raw counts.
- Rejects removal of a provenance/currentness/rollback responsibility unless another component demonstrably carries the same requirement.
- Distinguishes design simplicity from measured resource savings.
- Accounts for maintenance surface, runtime state, operator steps, mutable effects, failure domains, and validation burden.
- Accepts that a larger pathset can be the smallest valid whole-system design.

## AUTOMATIC FAIL
- Chooses B solely because its counts are lower.
- Treats provenance, currentness, rollback, safety, or durability as optional overhead without governing basis.
- Claims numeric savings without measurement or mechanically justified estimate.
