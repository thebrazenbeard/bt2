# Module 08 — Incident Records and Resumable Operational State

**Objective:** Preserve evidence for correct resumption without manufacturing continuity.

## Exercise
Create two templates. A debug/incident record must include finding ID, exact subject, provider observation/time, reproduction, timeline, trigger, root cause, invariant, severity/blast radius, falsifiers, dedup/supersession, oracle/test identity, limitations, handoffs, blockers. A Masa operational checkpoint must include training version, current governance evidence loaded during reorientation, roster, coordination high-water, assignment states, exact artifacts/refs/hashes, timed provider observations, active leases/absence, open H/M findings, terminal/superseded work, dependencies/owners, handoff receipts, and `OBSERVED/INFERRED/HISTORICAL/UNKNOWN` classes. Explain why training source != operational state, frozen base != currentness, and checkpoint != uninterrupted runtime/subjective continuity.

## PASS
Clean separation of training source, frozen base, operational state; checkpoint is sufficient for evidence-based resumption.

**Critical fail:** today's mutable work is baked into frozen training source.
