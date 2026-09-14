# LANTERN_WOWSQL_RUNTIME_CONTRACT_V3

Status: CANONICAL RUNTIME CONTRACT / FREE-SHARED READ COMPATIBILITY

## Purpose

Lantern supplies a governed, provenance-bearing material universe to an authorized ChatGPT Project runtime. It is a currentness/evidence source, not a substitute for the live user request and not a blanket instruction channel.

The currentness provider is exact WoWSQL project `bt2-479e4ad9`. On its free-shared PostgreSQL tier, the Project login is deliberately isolated from internal schema `bt2`, so Project reads use the source-bound `bt2_project_read` compatibility projection.

## Evidence order

For a live answer, distinguish:
- live user instructions and current Project instructions;
- current Lantern material obtained through the governed WoWSQL read sequence;
- exact GitHub source artifacts/current source binding;
- historical/archive material;
- model memory or inference.

Do not silently promote a lower class into a higher one.

## Consultation triggers

Consult Lantern when the answer materially depends on durable project state, recovery/currentness, provenance of accepted material, or when installed Project instructions explicitly require it. Skip Lantern when the live turn already supplies everything needed or the task is unrelated.

## Exact runtime target

Currentness reads require exact WoWSQL project `bt2-479e4ad9`. Do not substitute another project, the former Supabase provider, Git source, Project prose, historical material, or model memory as current Lantern state.

## Governed read

Follow `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V3.md` and `LANTERN_WOWSQL_READ_QUERIES_V3.md`.

A valid current cut requires:
1. exactly one projection preflight row bound to `BT2_LANTERN_FREE_SHARED_READ_V1` and `FROZEN_ZERO_PRODUCER`;
2. exactly one B0 row from `bt2_project_read.lantern_cut_v1`;
3. payload rows from `bt2_project_read.lantern_materials_v1` whose count, exact member tuples, profile digest, and policy digest cross-bind exactly to B0;
4. B1 exactly equal to B0;
5. one complete retry on instability, then `UNKNOWN` if instability remains.

## Fail-closed states

Return a clear limitation rather than inventing currentness when:
- exact WoWSQL target is unavailable;
- projection binding is absent or differs from the installed source-bound state;
- producer mode is not `FROZEN_ZERO_PRODUCER`;
- B0/payload/B1 cross-binding fails;
- instability persists after one retry;
- the requested claim needs authority current evidence does not establish.

There is no Supabase fallback for currentness.

## Writes and authority

This runtime integration is read-only by default. Hosted producer enablement is NOT QUALIFIED on free-shared WoWSQL while the strict producer-boundary verifier fails. `FROZEN_ZERO_PRODUCER` is a hosted-mode ceiling: any future governed write requires a separately qualified producer boundary and projection republication or supersession before Project currentness is re-established.

Successful reads do not imply producer authority, database write authority, runtime identity continuity, qualification, training activation, merge/deploy authority, or any other protected effect.

## Reporting ceiling

Report only what evidence establishes: source/package present, backend consulted, stable projected material cut obtained, specific material used, installed Project files observed, and/or fresh-runtime consumption verified.

Do not collapse source readiness, installation, routing, behavioral qualification, or provider lifecycle into one status.

Use `LANTERN_WOWSQL_ACCEPTANCE_V3.md` for installation and runtime-consumption acceptance.
