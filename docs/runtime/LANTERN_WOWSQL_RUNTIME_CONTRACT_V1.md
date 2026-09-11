# LANTERN_WOWSQL_RUNTIME_CONTRACT_V1

Status: CANONICAL-CANDIDATE SUCCESSOR RUNTIME CONTRACT / NOT YET INSTALLED IN CHATGPT PROJECT

## Purpose

Lantern supplies a governed, provenance-bearing material universe to an authorized ChatGPT Project runtime. It is a currentness/evidence source, not a substitute for the live user request and not a blanket instruction channel.

This successor contract changes the Lantern currentness provider from the retired-target Supabase subject to exact WoWSQL project `bt2-479e4ad9`. It does not change Lantern's evidence semantics or authority ceiling.

## Evidence order

For a live answer, distinguish:
- live user instructions and current Project instructions;
- current Lantern material obtained through the governed WoWSQL read sequence;
- exact GitHub source artifacts/current source binding;
- historical/archive material;
- model memory or inference.

Do not silently promote a lower class into a higher one.

## Consultation triggers

Consult Lantern when the answer materially depends on:
- durable project state or continuation/recovery;
- what Lantern currently recognizes as visible material;
- provenance/currentness of project material;
- reconciling potentially stale project evidence;
- a task whose installed Project instructions explicitly require Lantern.

Normally skip Lantern for:
- ordinary conversation with no project-state dependency;
- creative generation;
- information completely supplied in the current turn;
- unrelated projects/domains.

## Exact runtime target

Currentness reads require read access to exact WoWSQL project `bt2-479e4ad9`.

Do not substitute another WoWSQL project, the former Supabase project, Git source, Project prose, historical material, or model memory as current Lantern state.

## Governed read

Follow `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md` and `LANTERN_WOWSQL_READ_QUERIES_V1.md`.

A valid current cut requires:
1. exactly one B0 row from `bt2.material_cut_v1('PROJECT_LANTERN')`;
2. payload rows from `bt2.runtime_visible_materials_v1` whose count, exact member tuples, profile digest, and policy digest cross-bind exactly to B0;
3. B1 exactly equal to B0;
4. one complete retry on B0/B1 instability, then `UNKNOWN` if instability remains.

## Fail-closed states

Return a clear limitation rather than inventing currentness when:
- exact WoWSQL target `bt2-479e4ad9` is unavailable;
- `bt2.material_cut_v1('PROJECT_LANTERN')` is absent, non-singular, or invalid;
- payload rows do not exactly cross-bind to B0 membership/profile/policy;
- B0 and B1 do not match after one complete retry;
- the requested claim needs authority that current evidence does not establish.

There is no fallback to the former Supabase provider for currentness after this contract is installed.

## Writes and authority

This runtime integration is read-only by default. A Lantern read never authorizes a Lantern write.

Provider mutation, producer grants, material admission, database writes, Project Settings mutation, Project-file replacement, merge/deploy, qualification, training installation/activation, canonical-memory effects, or destructive provider retirement require separate current authority.

Successful reads do not imply runtime identity continuity or any protected effect.

## Reporting ceiling

Report only what evidence establishes: source/package present, backend consulted, stable material cut obtained, specific material used, installed Project files observed, and/or fresh-runtime consumption verified.

Do not collapse source readiness, installation, routing, behavioral qualification, or provider retirement into one status.

Use `LANTERN_WOWSQL_ACCEPTANCE_V1.md` for installation and runtime-consumption acceptance.