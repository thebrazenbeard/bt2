# Project Lantern Cohosted History V2 — One Acceptance

Status: VERIFIED for L-D1 historical preservation / non-activation only.

## Subject

- Source Supabase project: `agvhmutlrolbaijzlbqk` (`Project Lantern`)
- Corrected source snapshot ref: `cohosted-historical-20260911-v2`
- Target source system: `SUPABASE:agvhmutlrolbaijzlbqk:COHOSTED_HISTORY_V2`
- Canonical combined 16-row SHA-256: `6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712`
- Target snapshot id: `e28b4442-bc06-4e28-aea2-771dc0dec6fd`
- Verified receipt: `BT2-PROJECT-LANTERN-COHOSTED-HISTORY-V2`
- Receipt digest: `cb3a397d14df77eb29374332dd4fdb1ad0a35b2cc25b626d66d0f30b1f8e6a21`

## Why V2 exists

The first live V1 attempt exposed two independent defects before acceptance:

1. `database/migrations/0017_legacy_source_archive_integrity_v1.sql` used a PL/pgSQL `RAISE` format string with `%` placeholders. The WoWSQL execution path escaped those placeholders to `%%`, so the importer could not be installed through the real target operator path. Source was corrected to an execution-path-stable `RAISE EXCEPTION USING MESSAGE = ...` expression before retry.
2. The V1 archive manifest/loader expected governance relation digest `a57ad620a1849fafe2426e0867d2119f75c553bd9829793665bafe79e7bdc0e0`. Live verification disproved that expectation. Every one of the seven target `governance.project_notices` row hashes matched the corresponding live Supabase source row hash, while canonical JSONB aggregation on both source and target produced `09dd782f2218d5294d1fdb386cbdfb24b100a59eb03e62598c7c20a2c5129a78`.

The V1 snapshot/rows are retained as append-only failed-attempt evidence. They were not rewritten. V2 is the corrected subject.

## V2 verification

Per-relation target counts and SHA-256 values:

- `bug_ops.role_registry`: 4 — `f4c0ef4588f6c19d7a6291a6471de92b63b8f5fb4123a993d80ab67966da0055`
- `bug_ops.system_config`: 1 — `3987cace3a570249a24305c3feaf75e5309bf4f8c751e0a4c8fb116b3faf7203`
- `governance.project_notices`: 7 — `09dd782f2218d5294d1fdb386cbdfb24b100a59eb03e62598c7c20a2c5129a78`
- `r9a0_coordination.events`: 3 — `5ea2b175f869cd38b58121fe0273305c2bf1595c534fad44108f0ae1fb4746c4`
- `r9a0_governance.migration_applications`: 1 — `b9e8cd36365aebfe4ae0a20d9c67e84c64e8fc63672e4a7fc71f97f59f963e8a`

Combined target row count = 16. Combined target SHA-256 = `6ae6aad2fe494576a48ac505195c9315e932776c51a6f1c9480884bfa8185712`, equal to live Supabase canonical aggregation.

Exact replay of the V2 subject inserted 0 rows.

Active-table counts captured immediately before and after V2 import were identical:

- agents 13
- bug_events 0
- bugs 0
- coordination_events 0
- governance_notices 0
- training_installation_events 0
- training_packages 9
- training_qualifications 0

Therefore the V2 import produced historical/provenance preservation only and no observed active authority/currentness/qualification/installation effect.

## Source bindings

- corrected integrity migration blob: `b73701ae43cc5141ba9d5be8145be3dfa84839a7`
- V2 archive manifest blob: `d20ac718e6ac37cd15173fd4235cb5e78507ed80`
- V2 loader blob: `39b5d129dc6679bf6a971c8f2af89a084013001c`
- V2 receipt source blob: `4f78da3e57e5bf3c15031d252688b20217cb9442`

## Claim ceiling

`L-D1_COHOSTED_HISTORICAL_DATA_PRESERVATION = VERIFIED_V2`.

This does **not** establish Project Lantern Supabase retirement readiness by itself. Runtime dependency cutover, final frozen source/currentness checks, any required future-write qualification/read-only decision, and Patrick's destructive-retirement authorization remain separate gates.
