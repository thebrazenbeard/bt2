# BT2 Training Source-State Qualification — Two V1

Date: 2026-09-10
Coordination: `BT2-CANONICAL-PLATFORM-20260910`
Owner: Two
Target: WoWSQL `bt2-479e4ad9`

## Purpose

Prove that exact training-source preservation can become canonical source provenance without being silently promoted into compatibility, qualification, runtime installation, assignment, or authority.

## Source basis

One's current `training_source_recovery_v1.json` represents package/source state, qualification state, and runtime-installation state as separate evidence axes. The live canonical `bt2.training_packages` registry was empty before this change, and `bt2.training_qualifications` was also empty.

WoWSQL contained VERIFIED byte-preservation migration receipts for Two, Three, Seven, and Eight. Those receipts explicitly state `qualification_effect = NONE` and `runtime_installation_effect = NONE`.

## Implemented contract

Migration:
`database/migrations/0014_training_source_state_separation_v1.sql`

The migration adds:

- explicit `source_binding_state` separate from package lifecycle status;
- explicit `compatibility_state` defaulting to `UNASSESSED`;
- source package path and exact Git package-tree / manifest-blob identities;
- linkage to the preservation migration receipt;
- a guard requiring VERIFIED byte-preservation state to match a VERIFIED receipt and exact package tree;
- a guard preventing `QUALIFIED_BASE` unless compatibility is separately `COMPATIBLE` and an agent/package-bound PASS qualification exists;
- `register_preserved_training_package_v1`, which registers exact preserved source as `REGISTERED / BYTE_PRESERVED_VERIFIED / UNASSESSED` and creates no qualification or installation effect.

## Behavioral qualification

A rollback-contained probe used the real VERIFIED Two v1.0.0 byte-preservation receipt.

Verified:

1. first preserved-source registration succeeds;
2. exact registration replay converges to the same `training_package_id`;
3. registered state remains `REGISTERED`;
4. source binding is `BYTE_PRESERVED_VERIFIED`;
5. compatibility remains `UNASSESSED`;
6. qualification row count remains zero;
7. changing the package tree away from the receipt-bound tree is rejected with `PRESERVATION_RECEIPT_PACKAGE_TREE_MISMATCH`;
8. attempting `QUALIFIED_BASE` with compatibility marked compatible but without PASS qualification evidence is rejected with `QUALIFIED_BASE_REQUIRES_COMPATIBLE_PASS_EVIDENCE`.

The probe reached deliberate marker `TRAINING_SOURCE_ROLLBACK_PASS`. Post-probe readback showed:

- `training_packages = 0`
- `training_qualifications = 0`

No real package registration or qualification was manufactured by qualification testing.

## Rebuild coverage

`database/tests/0001_rebuild_smoke.sql` now includes an isolated synthetic preservation receipt and verifies the same non-promotion boundary on a future blank rebuild.

GitHub Actions still fails before runner step 1 for this repository, so blank-database execution of that smoke test remains uncredited. This is not classified as a SQL failure.

## Integration seam with One

At the checked heads, Two's PR #2 and One's source-preservation PR #3 have no overlapping changed paths. One owns archived training bytes/provenance; Two owns the database registry/integrity contract.

The registry is now structurally ready to accept VERIFIED preserved-package source records after coordination. Package registration alone must not be interpreted as compatibility, qualification, runtime installation, current assignment, or authority.

## Current database package binding

Current database package digest after migration `0014` and the extended smoke test:

`a52993748be926133398410f2c95cafe4d2683283a486b168c7aa3fcd075d32f`

No merge, cutover, qualification import, runtime training installation, legacy retirement, producer authorization, or Vera-Supabase mutation is asserted by this record.
