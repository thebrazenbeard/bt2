# BT2 Project Lantern L-D2 Concurrency Attempt — Two V1

Status: CONCURRENCY_NOT_ESTABLISHED / SYNTHETIC_FIXTURE_FULLY_REMOVED
Date: 2026-09-12
Systems Architect: Two
Coordinator counterpart: One
Execution boundary: One + Two only

## Purpose

Attempt the minimum genuine two-session admission falsification defined in `BT2_LANTERN_LD2_MINIMUM_CONCURRENCY_FALSIFICATION_TWO_V1.md` without touching real `PROJECT_LANTERN` authority or materials.

## Synthetic subject

- project scope: `BT2_LD2_CONCURRENCY_V1`
- schema version: `BT2_LD2_CONCURRENCY_SCHEMA_V1`
- producer principal: `bt2-ld2-concurrency`
- exact synthetic permit id: `77777777-7777-4777-8777-777777777777`

A committed synthetic policy/profile/permit fixture was created only to make cross-session overlap observable. No real `PROJECT_LANTERN` row was changed.

## Observed execution

One admission query used an in-query three-second gate and returned:

- backend pid: `3014455`
- started_at: `2026-09-12T13:40:48.307122+00:00`
- finished_at: `2026-09-12T13:40:51.314833+00:00`
- receipt id: `0ee798b7-1251-4fda-9a02-31f84d8110f3`

This proves the connector executed the statement in a PostgreSQL backend and that the synthetic admission path itself remained functional. It does **not** prove a two-session race.

The available conversation tool interface serialized Two's calls rather than allowing Two to dispatch two WoWSQL `execute_sql` requests simultaneously. WoWSQL documentation search exposed no supported multi-session/concurrency facility. `dblink` and `postgres_fdw` are available extension packages but not installed; no extension or other infrastructure was installed merely to manufacture a concurrency result.

Therefore the four required race cases remain `UNKNOWN`, not PASS and not database FAIL:

1. same semantic subject;
2. distinct semantic subjects;
3. profile-lineage mutation versus admission;
4. permit invalidation versus admission.

## Cleanup/readback

Cleanup order was receipt -> material -> permit -> profile -> schema policy.

Final readback after cleanup:

- synthetic policy rows: 0
- synthetic profile rows: 0
- synthetic permit rows: 0
- synthetic material rows: 0
- synthetic receipt rows: 0
- real `PROJECT_LANTERN` profiles: 1
- real current `PROJECT_LANTERN` permits: 0
- real `PROJECT_LANTERN` materials: 2
- real `PROJECT_LANTERN` receipts: 2

Result: `ZERO_SYNTHETIC_RESIDUE / REAL_LANTERN_UNCHANGED`.

## Architectural disposition

Single-session authorized admission remains qualified for the executed rollback-only scope. True concurrency/serialization remains an explicit L-D2 open gate.

No producer authority, material, Project cutover, Supabase retirement, privilege migration, extension installation, or merge is authorized or implied by this attempt.
