# LANTERN_WOWSQL_ACCEPTANCE_V1

Status: RUNTIME ACCEPTANCE SPEC / FREE-SHARED READ COMPATIBILITY

## Static package acceptance

Verify all four Lantern Project files are installed from one reviewed BT2 source subject:
- `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md`;
- `LANTERN_WOWSQL_READ_QUERIES_V1.md`;
- `LANTERN_WOWSQL_RUNTIME_CONTRACT_V1.md`;
- `LANTERN_WOWSQL_ACCEPTANCE_V1.md`.

Verify Project Instructions name exact WoWSQL project `bt2-479e4ad9`, preserve read-only/fail-closed semantics, and contain no Supabase currentness fallback.

## Free-shared provider acceptance

PASS requires:
1. Project role can read `bt2_project_read`;
2. Project role does not have `USAGE` on internal schema `bt2`;
3. `tools/qualification/verify_wowsql_effective_producer_boundary_v1.sql` passes;
4. `tools/qualification/verify_wowsql_free_shared_lantern_read_projection_v1.sql` passes;
5. projection preflight is exactly `BT2_LANTERN_FREE_SHARED_READ_V1` with `FROZEN_ZERO_PRODUCER`;
6. projection source-state digest equals `29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5`.

This provider mode is intentionally read-frozen. A future governed write requires projection republication or supersession in the same authorized change.

## Cold-start runtime acceptance

Start a fresh conversation in Build Team Two and ask:

**Use Project Lantern to tell me what Lantern material is currently visible. Distinguish what you actually read from what you infer.**

PASS requires:
1. exact WoWSQL target `bt2-479e4ad9` is consulted;
2. projection preflight -> B0 -> payload -> B1 is performed using `LANTERN_WOWSQL_READ_QUERIES_V1.md`;
3. payload membership/count/profile/policy exactly cross-bind to B0;
4. B0 and B1 are stable, or one full retry occurs and instability then fails closed;
5. visible materials come from live WoWSQL projection readback, not Git/model memory/Project prose;
6. no Supabase fallback or protected-effect claim occurs.

## Failure-path acceptance

Without WoWSQL access, the same currentness request must return a clear `UNKNOWN`/limitation. Do not substitute model memory, Git source, Project prose, historical material, or another provider/project.

## Result vocabulary

- `WOWSQL_PROJECT_FILES_INSTALLED`: Project instructions/files are deliberately installed and read back.
- `WOWSQL_FREE_SHARED_READ_PROJECTION_VERIFIED`: read projection qualification passes while hosted producer mode remains frozen.`r`n- `WOWSQL_HOSTED_PRODUCER_NOT_QUALIFIED`: hosted producer enablement does not satisfy the strict producer-boundary verifier and remains disabled.
- `WOWSQL_RUNTIME_CONSUMPTION_VERIFIED`: fresh-chat projected B0/payload/B1 acceptance passes.
- `WOWSQL_FAILURE_PATH_VERIFIED`: WoWSQL-unavailable behavior fails closed.
- `NOT_ESTABLISHED`: required evidence is missing.

Do not collapse installation, runtime consumption, source state, behavioral qualification, or provider lifecycle into one status.
