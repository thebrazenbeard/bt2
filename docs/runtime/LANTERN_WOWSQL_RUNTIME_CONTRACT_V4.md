# LANTERN_WOWSQL_RUNTIME_CONTRACT_V4

Status: CANONICAL-CANDIDATE RUNTIME CONTRACT / FREE-SHARED READ COMPATIBILITY

## Purpose
Lantern supplies a governed, provenance-bearing material universe to an authorized ChatGPT Project runtime. It is a currentness/evidence source, not a substitute for the live user request and not a blanket instruction channel.

The currentness provider is exact WoWSQL project `bt2-479e4ad9`. On its free-shared PostgreSQL tier, the Project login is deliberately isolated from internal schema `bt2`, so Project reads use the source-bound `bt2_project_read` compatibility projection.

Lantern/WoWSQL availability is not a prerequisite for unrelated BT2 source work. Provider failure makes Lantern-dependent claims `UNKNOWN`; it does not make Git source or independent coordination state unknown.

## Evidence order
For a live answer, distinguish:
- live user instructions and current Project instructions;
- current Lantern material obtained through the governed WoWSQL read sequence;
- exact GitHub source artifacts/current source binding;
- historical/archive material;
- model memory or inference.

Do not silently promote a lower class into a higher one.

## Consultation triggers
Consult Lantern when the answer materially depends on Lantern currentness, provenance of Lantern-accepted material, or when installed Project instructions explicitly require a Lantern fact.

Do not consult Lantern by ritual for source-only coding, Git review, ordinary repository recovery, or coordination facts independently established elsewhere.

## Exact runtime target
Currentness reads require exact WoWSQL project `bt2-479e4ad9`. Do not substitute another project, the former Supabase provider, Git source, Project prose, historical material, or model memory as current Lantern state.

## Governed read
Follow `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V4.md` and `LANTERN_WOWSQL_READ_QUERIES_V4.md`.

A valid current cut requires:
1. exactly one projection preflight row bound to `BT2_LANTERN_FREE_SHARED_READ_V1` and `FROZEN_ZERO_PRODUCER`;
2. exactly one B0 row from `bt2_project_read.lantern_cut_v1`;
3. payload rows from `bt2_project_read.lantern_materials_v1` whose count, exact member tuples, profile digest, and policy digest cross-bind exactly to B0;
4. B1 exactly equal to B0;
5. one complete snapshot retry on B0/B1 instability, then `UNKNOWN` if instability remains.

## Fail-closed states
Return a clear Lantern limitation rather than inventing currentness when:
- exact WoWSQL target is unavailable;
- projection binding is absent or differs from the source-bound state;
- producer mode is not `FROZEN_ZERO_PRODUCER`;
- B0/payload/B1 cross-binding fails;
- instability persists after one snapshot retry;
- the requested claim needs authority current evidence does not establish.

There is no Supabase fallback for currentness.

A Lantern failure does not block unrelated BT2 source/review/test/coordination work under Project Instructions V4.

## Writes and authority
This runtime integration is read-only by default. Hosted producer enablement is not qualified merely because the read projection works. `FROZEN_ZERO_PRODUCER` is a hosted-mode ceiling: any future governed write requires a separately qualified producer boundary and projection republication or supersession before Project currentness is re-established.

Successful reads do not imply producer authority, database write authority, runtime identity continuity, qualification, training activation, merge/deploy authority, or any other protected effect.

## Reporting ceiling
Report only what evidence establishes: source/package present, backend consulted, stable projected material cut obtained, specific material used, installed Project files observed, and/or fresh-runtime consumption verified.

Do not collapse source readiness, installation, routing, behavioral qualification, provider availability, producer qualification, or provider lifecycle into one status.

Use `LANTERN_WOWSQL_ACCEPTANCE_V4.md` for installation, provider-failure, and runtime-consumption acceptance.
