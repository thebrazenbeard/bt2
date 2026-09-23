# BT2 Runtime Provider Degradation Contract V1

Status: source contract candidate

## Purpose
BT2 must remain useful when an external runtime provider is unavailable. This contract prevents WoWSQL or any future runtime provider from becoming an accidental single point of failure for source recovery, coding, review, coordination, or continuation.

It does not create a substitute source for runtime-only truth.

## Claim-domain model
Before reading a provider, classify the fact:

| Domain | Authoritative surface | Behavior when unavailable |
| --- | --- | --- |
| SOURCE | canonical Git repository/ref | use Git; independent of WoWSQL |
| COORDINATION | Chat Communication Bus or owning durable repository handoff | use that surface; independent of WoWSQL |
| PROJECT_INSTALL | installed Project instructions/files | inspect Project state; independent of WoWSQL |
| RUNTIME_ONLY | exact provider that owns the runtime fact | `UNKNOWN` until fresh live readback |
| LANTERN_CURRENTNESS | exact governed WoWSQL Lantern route | `UNKNOWN`; no fallback |

A fact from one domain must not be silently promoted into another.

## Availability states
Use these provider states when they matter:
- `AVAILABLE`: the required live operation returned valid evidence.
- `UNAVAILABLE`: the provider or connector returned a bounded failure for the required operation.
- `UNKNOWN`: no current live determination exists.
- `DEGRADED`: some required operations work but the requested operation or evidence class does not.

Do not infer `AVAILABLE` from an old successful call.

## Degradation behavior
When WoWSQL is `UNAVAILABLE` or the connector fails internally:
1. Contain the failure to WoWSQL-dependent claims/effects.
2. Continue Git, PR, code-review, static/test, Bus, documentation, and checkpoint work whose semantics are independent.
3. Report WoWSQL-dependent state as `UNKNOWN` rather than reconstructing it from Git, memory, Project prose, screenshots, or historical receipts.
4. Never fall back to Supabase for Lantern currentness.
5. Do not loop on equivalent provider calls in the same bounded operation. A retry must have a materially different route, changed provider state, or new evidence.
6. Persist resumable work outside WoWSQL before ending the session.

## No sole-copy rule
WoWSQL may own runtime-only facts, but it must not be the sole location of information required to:
- identify the canonical source head;
- identify an active branch or PR;
- understand a source change;
- resume a coding task;
- recover authority boundaries;
- know the next executable source action.

Those must be reconstructible from Git and/or the Chat Communication Bus.

## Runtime-only exceptions
Some facts cannot be truthfully mirrored as source truth, such as a live row, receipt, active permit, runtime registration, current material cut, or current database effect.

For these facts, the correct degraded result is `UNKNOWN`, not a stale mirror pretending to be current.

## Lantern
Lantern retains stricter semantics:
- exact target `bt2-479e4ad9`;
- V3 projection preflight -> B0 -> payload -> B1;
- no Supabase fallback;
- no Git/Project/memory substitution for Lantern currentness;
- failure is local to Lantern-dependent claims and must not halt unrelated BT2 source work.

## Recovery after outage
When provider access returns:
1. perform a fresh read for the exact required fact;
2. re-establish any cross-binding or stability sequence required by that provider contract;
3. compare with source only for source/runtime divergence, not as a substitute for runtime truth;
4. update checkpoints with the newly verified state.

## Design test
A conforming BT2 runtime must pass both of these statements:
- "WoWSQL is down, so I cannot establish current Lantern/runtime-only state."
- "WoWSQL is down, but I can still inspect/fix/test/review the repository and persist a resumable checkpoint."

If either statement is false, provider failure containment is incomplete.
