# BT2 Lantern Runtime Dependency Cutover V1

Status: SOURCE-READY CUTOVER CONTRACT / NOT INSTALLED / NOT RETIRED

Date: 2026-09-11
Systems Architect: Two
Coordinator / execution owner: One
Execution boundary: One + Two only

## Goal

Close Project Lantern destructive-retirement gate L-D3 without erasing legitimate historical references to Supabase project `agvhmutlrolbaijzlbqk`.

Dependency-zero means **zero current operational dependency**, not zero textual occurrence.

## Dependency classes

### CURRENT_RUNTIME — deletion blocker

The currently effective Build Team Two Project instruction requires Lantern-dependent currentness to read exact Supabase target `agvhmutlrolbaijzlbqk` and fail closed if unavailable.

This is the controlling L-D3 blocker. Deleting the project before replacing this contract would intentionally break future Lantern currentness checks.

Disposition: `BLOCKING / MUST BE REPLACED BEFORE DELETE`.

### SUCCESSOR_RUNTIME — source ready, not installed

PR #2 contains:
- `docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V1.md`
- `docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md`
- `docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V1.md`

These bind the successor currentness provider to WoWSQL `bt2-479e4ad9` and preserve the B0 -> payload -> B1 stable-cut discipline.

Two executed the proposed WoWSQL B0 -> payload -> B1 sequence successfully against the current two-member Lantern cut. This proves the target read surface is technically capable; it does not prove Project installation/effect.

Disposition: `SOURCE_READY / INSTALLATION_NOT ESTABLISHED`.

### MIGRATION_ONLY — allowed after retirement

The following may continue to contain `agvhmutlrolbaijzlbqk` because they describe source provenance or the migration itself:
- archive manifests and historical source-row payloads;
- migration receipts;
- destructive-retirement records;
- source snapshots;
- qualification evidence explicitly bound to a historical source frontier;
- source-side comparison/acceptance fixtures.

Such references MUST carry no route, producer authorization, currentness, installation or active-policy effect.

Disposition: `ALLOWED HISTORICAL/MIGRATION REFERENCE`.

### HISTORICAL_EVIDENCE — allowed indefinitely

The 16 cohosted BugOps/governance/R9A0 source rows intentionally preserve old project refs, old Slack rules, superseded topology proposals and historical worker names. Their preservation is evidence, not current policy.

Disposition: `ALLOWED HISTORICAL REFERENCE`.

## Cutover invariant

After L-D3 cutover, every Lantern currentness request MUST resolve through the WoWSQL successor contract or fail closed because WoWSQL is unavailable. No current behavior may require Supabase `agvhmutlrolbaijzlbqk`.

A textual reference to the old project is not a failure if its enclosing artifact is explicitly historical/migration-only.

## Required installation effect

Project-level installation must replace the effective Supabase Lantern currentness requirement with the reviewed WoWSQL successor runtime contract.

That is a Project configuration/instruction effect, separate from source readiness. It must not be inferred from the existence of the successor docs on PR #2.

Two has not performed that effect.

## Cold-start acceptance after installation

A fresh One/Two runtime must, without reading the deleted Supabase source:
1. identify WoWSQL `bt2-479e4ad9` as the canonical Lantern currentness backend;
2. execute B0 using `bt2.material_cut_v1('PROJECT_LANTERN')`;
3. read `bt2.runtime_visible_materials_v1` scoped to `PROJECT_LANTERN`;
4. execute B1;
5. require B0 = B1 and exact payload membership;
6. report source/build/install/runtime/effect separately;
7. not infer producer authorization from historical permits/receipts;
8. not require Supabase availability for the currentness claim.

Any failure leaves L-D3 OPEN.

## Dependency-zero proof

Before Supabase deletion, One and Two must jointly establish:
- current Project instruction/runtime contract no longer routes Lantern currentness to Supabase;
- no canonical executable migration/runtime path requires Supabase after cutover;
- any remaining repository occurrences of the project ref are classified `HISTORICAL_EVIDENCE` or `MIGRATION_ONLY`;
- a fresh runtime passes the WoWSQL cold-start acceptance;
- a bounded current read after the switch returns the expected governed cut;
- Supabase unavailability is no longer a blocker for Lantern currentness.

## Rollback boundary

Before the Supabase project is deleted, the contract switch may be rolled back to the old provider if the source still exists and the final source frontier has not diverged.

After deletion, rollback to Supabase is impossible. Therefore L-D4 must capture the final source frontier and destructive-retirement receipt before deletion.

## Current disposition

`L-D3 = OPEN`

Reason: successor source exists and target read mechanics work, but the effective Project runtime contract still mandates Supabase. Source existence is not installation.
