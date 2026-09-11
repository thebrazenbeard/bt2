# BT2 Project Lantern L-D1 Source Readiness — Two V1

coordination_id: `BT2-CANONICAL-PLATFORM-20260910`
owner: Two / Systems Architect
execution boundary: One + Two only
status: `SOURCE_READY / LIVE_ARCHIVE_LOAD_NOT_APPLIED / CLEAN_DB_EXECUTION_NOT_ESTABLISHED`

## Exact source subject

Two branch before this qualification record:
`work/two-canonical-platform-integrity-v1@3209ad17f86841ac003c1e6a30da4d1880b450bc`

Database build package digest:
`80495845f6ee6fb2afb19217f4e147837f749aa2a66f62ea06e9a3eab4486356`

Bound package trees:
- schema: `12e5e5846881f82845875ffe26644bbdeb0729c6`
- migrations: `4a27d7a4619c956c4322ba022c582118d1e8b97b`
- tests: `7e08e5fe3fdd6810184ffa670201682e280ca790`
- admin: `6447503b9ab4f4613c657488742da88abea7cffa`
- data: `2a14b6daca43a177169177779abfca65dcde5ae8`
- Project Lantern cohosted archive: `0aae7f220704d34e101d43ae1102a1b51dd5776a`
- loaders: `bc20078e1758948ae722c27f67705f5bfbc1ed45`

## Source archive

Supabase source: `agvhmutlrolbaijzlbqk`
Classification: `HISTORICAL_PROVENANCE_ONLY`
Authority/currentness effect: `NONE`

Canonical combined 16-row digest:
`6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712`

Exact relation membership:
- `bug_ops.role_registry`: 4
- `bug_ops.system_config`: 1
- `governance.project_notices`: 7
- `r9a0_coordination.events`: 3
- `r9a0_governance.migration_applications`: 1

Relation digests:
- role registry: `f4c0ef4588f6c19d7a6291a6471de92b63b8f5fb4123a993d80ab67966da0055`
- system config: `3987cace3a570249a24305c3feaf75e5309bf4f8c751e0a4c8fb116b3faf7203`
- governance notices: `a57ad620a1849fafe2426e0867d2119f75c553bd9829793665bafe79e7bdc0e0`
- R9A0 events: `5ea2b175f869cd38b58121fe0273305c2bf1595c534fad44108f0ae1fb4746c4`
- R9A0 migration applications: `b9e8cd36365aebfe4ae0a20d9c67e84c64e8fc63672e4a7fc71f97f59f963e8a`

Each archived row preserves exact source schema, relation, original primary key and source row JSON. Historical references to retired workers, Slack rules, old topology proposals, or R9A0 findings remain evidence only and are not interpreted as current policy or authority.

## Reconstruction mechanism

`database/migrations/0017_legacy_source_archive_integrity_v1.sql`
- makes `bt2_legacy.source_rows` append-only;
- registers only snapshots explicitly classified `HISTORICAL_PROVENANCE_ONLY`;
- imports exact row envelopes idempotently;
- rejects replay when row content or snapshot binding differs.

`database/loaders/lantern_cohosted_history_v1.py`
- validates source archive geometry before emitting SQL;
- captures active governance, coordination, workforce, training and BugOps counts before import;
- imports all five exact relation payloads;
- replays every import to prove convergence;
- verifies 16 total rows and 4/1/7/3/1 membership;
- verifies all five source digests and the combined digest;
- requires exactly one correctly classified source snapshot;
- fails if any active subsystem count changes;
- supports `verify-rollback` and `apply` modes.

`database/data/0005_project_lantern_cohosted_history_receipt_v1.sql`
- is staged before runtime application;
- re-verifies membership and digests;
- appends receipt `BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V1` only after archive preservation exists;
- receipt digest: `bd5ae9b75bb0efae51864eecb74508008304fee668a7272090fdc205bdb7efdc`;
- creates no active policy, coordination, workforce, qualification, installation or authority effect.

The database rebuild workflow now executes the historical archive loader in rollback-verification mode after migrations/tests.

## Evidence ceiling

GitHub Actions run `34609789147` for the exact package again completed before any steps were exposed/executed. This is not SQL/archive failure evidence and is not a PASS.

Therefore this record establishes:
- exact source archive present: PASS;
- exact source bindings/package identity present: PASS;
- deterministic reconstruction path present: PASS;
- idempotence/non-activation oracles present in source: PASS;
- live WoWSQL historical archive applied: NO;
- blank PostgreSQL execution: UNQUALIFIED;
- L-D1 destructive-retirement gate: NOT CLOSED YET.

## Proposed live sequence for One/Two decision

1. Refresh exact Two head and package manifest; abort on divergence.
2. Apply `0017_legacy_source_archive_integrity_v1.sql` from exact source.
3. Generate loader SQL using `lantern_cohosted_history_v1.py --mode apply` from the same exact source tree.
4. Capture loader active-state baseline and import all five archives.
5. Replay exact imports; any divergence fails closed.
6. Require 16 total historical rows, relation counts 4/1/7/3/1, all five relation digests and combined digest `6ae6aad...`.
7. Require active governance/coordination/workforce/training/BugOps counts unchanged.
8. Apply `0005_project_lantern_cohosted_history_receipt_v1.sql`.
9. Read back exact historical snapshot + receipt + legacy rows.
10. Only then classify L-D1 `PASS` and move to Lantern consumer-contract cutover/final destructive-retirement gates.

No live L-D1 load was performed by Two while constructing this subject.
