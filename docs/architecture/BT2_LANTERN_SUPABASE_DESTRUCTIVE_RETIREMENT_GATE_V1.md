# Project Lantern Supabase Destructive-Retirement Gate V1

Status: ACTIVE SYSTEMS-ARCHITECTURE GATE / DELETE NOT YET SAFE

Date: 2026-09-11
Systems Architect: Two
Coordinator / Migration Owner: One
Source project: Supabase `agvhmutlrolbaijzlbqk` (Project Lantern)
Canonical replacement backend: WoWSQL `bt2-479e4ad9`

## 1. Decision

The Supabase Project Lantern project is **not safe to delete yet**, but destructive retirement does **not** need to wait for the entire BT2 migration.

It may be retired independently once the per-boundary gates in this document close.

## 2. What is already proven

### Lantern governed material cut — fresh stable read

Required B0 -> payload -> B1 sequence was executed against exact source target `agvhmutlrolbaijzlbqk`.

B0 and B1 were identical:
- profile digest: `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`
- predecessor: null
- policy digest: `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`
- material count: 2
- material IDs: `575acfa9-1274-5bbd-9a82-7e672af12e5d`, `e71548f3-3f09-49fd-9ed6-5d0179fd608c`

Payload rows exactly matched the B0 member tuples and profile/policy binding.

WoWSQL `bt2.material_cut_v1('PROJECT_LANTERN')` returned the exact same two members and canonical/semantic/source digests.

### Lantern durable rowset preservation

Exact source counts:
- accepted profiles: 1
- admission receipts: 2
- materials: 2
- producer grants: 3
- schema policies: 1
- seed import receipts: 0

Exact WoWSQL counts:
- material profiles: 1
- material receipts: 2
- materials: 2
- producer permits: 3
- material schema policy: 1
- seed receipts: 0

Deterministic normalized rowset SHA-256 digests are identical source -> target:
- profile: `bfc4606eddcb5b99707f3b4cc82a0498c12da1eeb86cdb0937786fc340f6c4df`
- receipt: `273f62374af1bc04b2d57d1d3500254a44398ccff84eaa14a86e6b6df2afdb57`
- material: `4d2b4a2693eddaf012423de56e8d19a54659bbd6a1a513bb57c2f5b81313cb4d`
- producer authorization history: `a0378236590d5ba447dd1cdbd0c8e77be5aff356feed4087bd51976ca2041d9a`
- schema policy: `4eabc5b6e0de4aeff21bb59ae6c05ddbf3849bcc18cec47f03e76fc744fa9573`

The normalized mapping is semantic only:
- source `grant_id` -> target `permit_id`
- source `revoked_at` -> target `invalidated_at`

All other compared values are exact.

Current producer authority is zero on both source and target.

Conclusion: **Lantern's own durable governed-material dataset is already preserved exactly enough for destructive-retirement consideration.**

## 3. State in the same Supabase project that is NOT yet preserved

Exact source counts outside Lantern material tables:

- `bug_ops.bug_reports`: 0
- `bug_ops.bug_events`: 0
- `bug_ops.dispatch_events`: 0
- `bug_ops.dispatch_events_v2`: 0
- `bug_ops.operation_receipts`: 0
- `bug_ops.role_registry`: 4
- `bug_ops.system_config`: 1
- `governance.project_notices`: 7
- `r9a0_coordination.events`: 3
- `r9a0_governance.migration_applications`: 1

Current canonical target readback:
- `bt2.governance_notices`: 0
- `bt2.coordination_events`: 0
- `bt2_legacy.source_rows`: 0

Therefore deleting the Supabase project today would destroy historical/governance evidence not yet preserved in the canonical migration record.

Deterministic source digests for the remaining nonempty source rowsets:
- BugOps role registry (4 rows): `f4c0ef4588f6c19d7a6291a6471de92b63b8f5fb4123a993d80ab67966da0055`
- BugOps system config (1 row): `3987cace3a570249a24305c3feaf75e5309bf4f8c751e0a4c8fb116b3faf7203`
- governance notices (7 rows): `a57ad620a1849fafe2426e0867d2119f75c553bd9829793665bafe79e7bdc0e0`
- R9A0 coordination events (3 rows): `5ea2b175f869cd38b58121fe0273305c2bf1595c534fad44108f0ae1fb4746c4`
- R9A0 migration applications (1 row): `b9e8cd36365aebfe4ae0a20d9c67e84c64e8fc63672e4a7fc71f97f59f963e8a`

Architectural classification:
- these rows are predominantly historical/provenance evidence, not current authority;
- the old BugOps role registry includes historical identity VOSS and must not be imported as current workforce state;
- governance notices include historical R9A0/Slack/planning authorization material and must not become active policy merely because preserved;
- R9A0 rows are historical implementation/review evidence, not canonical current coordination.

One should preserve them as historical source rows or exact archived evidence, with classification and digest verification, before destructive retirement.

## 4. Remaining deletion gates

### L-D1 — Historical source-row preservation

One preserves the nonempty non-Lantern rowsets above under an exact frozen source frontier. Preservation may be lossless `bt2_legacy.source_rows`, an exact source archive, or another canonical content-addressed form agreed by One/Two.

PASS requires exact membership/count/digest readback and explicit `HISTORICAL`/`SUPERSEDED` classification where appropriate. No row may become active authority by import side effect.

Current: **OPEN / HARD DELETE BLOCKER**.

### L-D2 — Replacement write-path qualification

WoWSQL must be shown to replace the source Lantern admission behavior for future legitimate use, not merely reproduce current reads.

Already proven:
- read equivalence;
- duplicate/canonicalization negative gates;
- lineage serialization correction;
- zero fabricated producer authority.

Still unproven:
- positive concurrent admission under legitimate authorization.

No test producer permit may be manufactured solely to make this test pass without current authority.

Current: **OPEN / DELETE BLOCKER IF LANTERN WILL ACCEPT FUTURE WRITES**.

If Patrick explicitly decides canonical Lantern becomes permanently read-only, this gate may instead be closed by an explicit architectural decision removing future admission as a required capability.

### L-D3 — Routing/dependency cutover

Before deletion, prove no current BT2 workflow, Project instruction, connector workflow, migration script, or runtime path still requires Supabase `agvhmutlrolbaijzlbqk` for current reads/writes/authority.

Required action:
- search canonical repo/current migration docs for live dependency references;
- reclassify remaining source-target references as historical or migration-only;
- route canonical current material reads/writes to WoWSQL;
- perform a bounded readback after routing switch.

Current: **OPEN / HARD DELETE BLOCKER**.

### L-D4 — Final freeze and destructive-retirement receipt

Immediately before deletion:
1. freeze source writes;
2. execute fresh B0 -> payload -> B1 stable cut;
3. recompute exact source row counts/digests for all preserved rowsets;
4. verify WoWSQL/archive equality against that final frontier;
5. verify zero current producer authorization;
6. record exact Supabase project ref, final source frontier, target package/integration subject, preservation digests, dependency-scan result, and rollback limitation;
7. mark Supabase Project Lantern logically retired;
8. only then may Patrick delete the Supabase project.

Deletion is irreversible source destruction, so the destructive-retirement receipt must exist before deletion, not be reconstructed afterward.

Current: **OPEN / FINAL DELETE GATE**.

## 5. When Patrick can delete Project Lantern

Patrick does **not** need to wait for full BT2 migration/cutover.

Deletion becomes architecturally safe when L-D1 through L-D4 are closed for this specific Supabase boundary.

Given current evidence, the data-migration portion for Lantern itself is already essentially complete. The remaining work is:
- preserve/classify the 16 non-Lantern historical rows in the same project;
- close or explicitly remove the future-write requirement;
- prove no current route still depends on the Supabase target;
- capture one final frozen source frontier and destructive-retirement receipt.

Until those are complete: **DO NOT DELETE `agvhmutlrolbaijzlbqk`.**
