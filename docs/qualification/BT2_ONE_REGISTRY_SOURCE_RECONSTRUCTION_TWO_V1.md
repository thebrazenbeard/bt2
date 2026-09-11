# BT2 One Registry Source Reconstruction — Two V1

Coordination: `BT2-CANONICAL-PLATFORM-20260910`
Reviewer/implementer: Two
Date: 2026-09-11
Scope: source-code reconstruction of One v1.0.0 preserved training-source registration under `one-0163`.

## Disposition

`PASS_FOR_SOURCE_RECONSTRUCTION_AND_LIVE_REPLAY`

This is not a blank-database rebuild PASS, qualification import, runtime installation/activation, merge, cutover, or retirement decision.

## Independently reproduced source and preservation bindings

One v1.0.0 source:
- repository: `thebrazenbeard/build-team-2.0`
- ref: `training/one-role-v1.0.0`
- commit: `ed1f2c5515425deab4c77c2f4fd291a1086191d4`
- commit tree: `0cd6bca8a3d1aaab9e47f3f8b23d3a18a6f4d40a`
- package path: `training/roles/one/v1.0.0`
- package tree: `e27ce67b67159fb445347ae9a8888fe3c480cdd1`

Preserved target subject on PR #3 exact head `692b72e423077ad47fc2f8c3f104742ce7216c5f`:
- path: `archive/training-sources/build-team-2.0/one/v1.0.0`
- package tree: `e27ce67b67159fb445347ae9a8888fe3c480cdd1`
- manifest path: `archive/training-sources/build-team-2.0/one/v1.0.0/TRAINING_MANIFEST.yaml`
- manifest blob: `e6d8e6b4a8139d8073b08fe7f346107f66a16458`

The source and preserved package trees are exactly identical.

## Independently reproduced WoWSQL target state

Project: `bt2-479e4ad9`

Observed One package row:
- package id: `5b359bba-c29e-4c64-8268-dced670c3d0a`
- status: `REGISTERED`
- source binding: `BYTE_PRESERVED_VERIFIED`
- compatibility: `UNASSESSED`
- source repository/ref/commit/tree: exact match to the source subject above
- package tree: `e27ce67b67159fb445347ae9a8888fe3c480cdd1`
- manifest blob: `e6d8e6b4a8139d8073b08fe7f346107f66a16458`
- preservation receipt id: `9b664dc3-7d88-4767-a839-8601521f5cf4`

Observed preservation receipt:
- key: `BT2-TRAINING-ONE-V1.0.0-BYTE-PRESERVATION-V1`
- result: `VERIFIED`
- source package tree = target package tree = `e27ce67b67159fb445347ae9a8888fe3c480cdd1`
- `qualification_effect = NONE`
- `runtime_installation_effect = NONE`

Registry readback before replay:
- package rows: 8
- qualification rows: 0
- installation-event rows: 0

## Source implementation

Updated:
- `database/data/0001_verified_training_source_registry_v1.sql`

The data load now contains One plus the previously registered seven exact preserved package subjects. One is registered only through `bt2.register_preserved_training_package_v1` and remains bounded to preserved-source registration.

Added:
- `database/tests/0003_training_source_registry_reconstruction_smoke.sql`

The test seeds only synthetic VERIFIED preservation evidence, invokes the real data load twice, and requires:
- exact eight-package subject set;
- every package `REGISTERED / BYTE_PRESERVED_VERIFIED / UNASSESSED`;
- One appears exactly once;
- replay leaves package count at eight;
- no qualification rows;
- no installation-event rows.

## Live replay qualification

A rollback-contained WoWSQL probe replayed all eight exact `register_preserved_training_package_v1` calls twice against the live eight-row registry.

Assertions passed before the deliberate rollback marker:
- package UUID mapping unchanged from pre-replay snapshot;
- package count remained exactly 8;
- every package remained `REGISTERED / BYTE_PRESERVED_VERIFIED / UNASSESSED`;
- qualification count remained 0;
- installation-event count remained 0.

Terminal marker: `REGISTRY_REPLAY_ROLLBACK_PASS`.
The deliberate exception rolled back all replay-side timestamp/update effects.

## Bound database package

Manifest source head before manifest update: `4396e8412a48d01b5f2905680aa26d29e17cd69c`

Package trees:
- schema: `12e5e5846881f82845875ffe26644bbdeb0729c6`
- migrations: `2c9aa4f2fcb2879e52c148dfa196f25c622a9a44`
- tests: `df278e7f6ebf3c10273846e53992fe87e6fe34b3`
- admin: `6447503b9ab4f4613c657488742da88abea7cffa`
- data: `6efe2e963a1e06b7242fe9a08868a40cb71df7d7`

Package digest SHA-256:
`9f28548c95b8884b2a2193d4dfd94064f32a3dbd15cb424ed49c1290cec9aaca`

## Remaining gate

`BLANK_DATABASE_REBUILD = PENDING_EXTERNAL_EXECUTION`

The GitHub Actions rebuild workflow remains registered but repeatedly fails before runner allocation/step execution. Therefore this record does not claim that a fresh PostgreSQL instance has executed the ordered schema/migration/data/test package.

## Effect ceiling

No qualification import/promotion, compatibility promotion, runtime installation/activation, assignment/authority effect, merge, cutover, legacy retirement, producer authorization, Vera mutation, or ongoing-project repository absorption is authorized or claimed by this record.
