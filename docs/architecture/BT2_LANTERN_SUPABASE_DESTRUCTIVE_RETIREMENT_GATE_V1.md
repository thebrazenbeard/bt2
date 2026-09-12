# Project Lantern Supabase Destructive-Retirement Gate V1

Status: ACTIVE SYSTEMS-ARCHITECTURE GATE / DELETE NOT YET SAFE

Date: 2026-09-11
Systems Architect: Two
Coordinator / Migration Owner: One
Source project: Supabase `agvhmutlrolbaijzlbqk` (Project Lantern)
Canonical replacement backend: WoWSQL `bt2-479e4ad9`

## 1. Decision

The Supabase Project Lantern project is **not safe to delete yet**, but it does **not** need to survive until global BT2 migration completion. It may be destructively retired as its own legacy boundary once L-D1 through L-D4 below close.

## 2. What is already proven

### Lantern governed material cut

A fresh required Supabase B0 -> payload -> B1 sequence passed against exact source target `agvhmutlrolbaijzlbqk`:
- profile `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`;
- predecessor null;
- policy `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`;
- exactly 2 materials.

WoWSQL `bt2.material_cut_v1('PROJECT_LANTERN')` returns the exact same two member IDs and canonical/semantic/source digest tuples.

A WoWSQL B0 -> payload -> B1 successor read sequence was also executed in this session and was stable with exact payload cross-binding.

### Lantern durable rowset preservation

Source and target counts match exactly:
- profiles 1;
- receipts 2;
- materials 2;
- producer authorization-history rows 3;
- schema policies 1;
- seed receipts 0.

Deterministic normalized rowset SHA-256 digests match source -> target exactly:
- profile `bfc4606eddcb5b99707f3b4cc82a0498c12da1eeb86cdb0937786fc340f6c4df`;
- receipt `273f62374af1bc04b2d57d1d3500254a44398ccff84eaa14a86e6b6df2afdb57`;
- material `4d2b4a2693eddaf012423de56e8d19a54659bbd6a1a513bb57c2f5b81313cb4d`;
- producer authorization history `a0378236590d5ba447dd1cdbd0c8e77be5aff356feed4087bd51976ca2041d9a`;
- schema policy `4eabc5b6e0de4aeff21bb59ae6c05ddbf3849bcc18cec47f03e76fc744fa9573`.

Normalized naming only:
- source `grant_id` -> target `permit_id`;
- source `revoked_at` -> target `invalidated_at`.

Current producer authority = 0 on both source and target.

Conclusion: **Lantern's own durable governed-material dataset is already preserved.**

## 3. Co-resident Supabase state still requiring preservation

Exact nonempty rowsets outside Lantern material tables:
- `bug_ops.role_registry`: 4;
- `bug_ops.system_config`: 1;
- `governance.project_notices`: 7;
- `r9a0_coordination.events`: 3;
- `r9a0_governance.migration_applications`: 1.

Operational BugOps reports/events/dispatch/operation-receipt tables are currently empty.

Canonical readback at this cut:
- `bt2.governance_notices = 0`;
- `bt2.coordination_events = 0`;
- `bt2_legacy.source_rows = 0`.

Deleting Supabase today would therefore destroy 16 rows of historical/configuration/provenance evidence not yet preserved canonically.

Source rowset digests:
- BugOps role registry `f4c0ef4588f6c19d7a6291a6471de92b63b8f5fb4123a993d80ab67966da0055`;
- BugOps system config `3987cace3a570249a24305c3feaf75e5309bf4f8c751e0a4c8fb116b3faf7203`;
- governance notices `a57ad620a1849fafe2426e0867d2119f75c553bd9829793665bafe79e7bdc0e0`;
- R9A0 coordination events `5ea2b175f869cd38b58121fe0273305c2bf1595c534fad44108f0ae1fb4746c4`;
- R9A0 migration applications `b9e8cd36365aebfe4ae0a20d9c67e84c64e8fc63672e4a7fc71f97f59f963e8a`.

These are predominantly historical/provenance subjects. Preservation must not activate VOSS, Slack/R9A0 authority, historical notices, or old coordination state.

## 4. Installed consumer contract is still Supabase-bound

Current Lantern runtime package/Project contract explicitly says:
- currentness requires exact Supabase target `agvhmutlrolbaijzlbqk`;
- unavailability of that target is a fail-closed state;
- cold-start acceptance requires Supabase B0 -> payload -> B1.

Therefore deleting Supabase before changing and qualifying the consumer contract would intentionally break future Lantern currentness even though WoWSQL holds the data.

Successor runtime contract is now source-controlled on PR #2:
- `docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V1.md`;
- `docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md`;
- `docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V1.md`.

These bind exact WoWSQL project `bt2-479e4ad9` and preserve the same stable-cut/cross-binding/fail-closed discipline.

Current state: `WOWSQL_RUNTIME_CONTRACT_SOURCE_READY` only. It is **not** yet installed into this ChatGPT Project and has not received fresh-chat cold-start acceptance.

## 5. Remaining deletion gates

### L-D1 — Historical source-row preservation

One preserves/classifies the 16 non-Lantern historical/configuration rows above under an exact frozen source frontier. PASS requires exact membership/count/digest readback and historical/superseded classification where appropriate, with no active-authority side effect.

Current: **OPEN / HARD DELETE BLOCKER**.

### L-D2 — Replacement capability qualification

If canonical Lantern must accept future writes, WoWSQL positive concurrent admission must be qualified under legitimate authorization. No permit may be manufactured only to make a test pass.

If Patrick explicitly decides Lantern becomes permanently read-only, this gate can instead close by an explicit architecture decision removing future admission from required capability.

Current: **OPEN / DELETE BLOCKER FOR FUTURE-WRITE LANTERN**.

### L-D3 — Consumer/routing cutover

Before deletion:
1. deliberately replace the installed Supabase-bound Project instructions/files with the WoWSQL successor runtime contract;
2. run fresh-chat WoWSQL cold-start acceptance;
3. prove no current BT2 workflow, Project instruction, connector path, migration script, or runtime still depends on Supabase for current reads/writes/authority;
4. route canonical current Lantern reads/writes to WoWSQL;
5. perform bounded post-route readback.

Current: **SOURCE CONTRACT READY / INSTALLATION + COLD-START + DEPENDENCY-ZERO OPEN / HARD DELETE BLOCKER**.

### L-D4 — Final freeze and destructive-retirement receipt

Immediately before deletion:
1. freeze Supabase writes;
2. fresh Supabase B0 -> payload -> B1;
3. fresh WoWSQL B0 -> payload -> B1;
4. recompute exact source row counts/digests for Lantern plus co-resident preserved rowsets;
5. require target/archive equality to the final frozen frontier;
6. require zero unintended current producer authority;
7. record exact Supabase ref, final frontier, integrated target subject, preservation digests, consumer-contract acceptance result, dependency-zero result, and rollback limitation;
8. mark Supabase provider logically retired;
9. only then may Patrick perform deletion.

Current: **OPEN / FINAL DELETE GATE**.

## 6. When Patrick can delete Project Lantern

Patrick does **not** need to wait for full BT2 cutover.

The Lantern data itself is already migrated. The remaining path is bounded:
- preserve/classify 16 co-resident historical rows;
- qualify future writes or explicitly choose read-only Lantern;
- install/cold-start-qualify the WoWSQL consumer contract and prove dependency zero;
- execute one final frozen cross-provider comparison and destructive-retirement receipt.

Until those close: **DO NOT DELETE `agvhmutlrolbaijzlbqk`.**
