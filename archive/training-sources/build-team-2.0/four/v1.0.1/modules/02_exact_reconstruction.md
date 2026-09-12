# Module 02 — Exact Implementation Reconstruction

## Objective
Translate accepted semantics into the smallest exact materialization without semantic drift.

## Method
Start from immutable accepted evidence. Derive the minimum affected pathset, predecessor bindings, byte/contract consequences, and invariants. Distinguish CREATE, UPDATE, DELETE, generated/derived outputs, and unchanged dependencies. Never infer exact bytes from prose when exact bytes are required.

Reconstruction must preserve:
- semantic intent and correction scope;
- exact subject/currentness identity;
- dependency order;
- unchanged-path noninterference;
- generated-artifact regeneration requirements;
- test and receipt consequences.

## Exercise
An accepted lifecycle semantic change affects one source module, one oracle, and a source manifest. Reconstruct the minimum candidate geometry and explain why unrelated files remain outside scope.

## Pass criteria
- Uses accepted semantics rather than branch-name assumptions.
- Produces an exact bounded pathset with reasons.
- Identifies derived/regenerated artifacts.
- Rejects unpublished or stale bytes as current evidence.
- Does not widen scope for convenience.
