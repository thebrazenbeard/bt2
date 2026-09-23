# LANTERN_WOWSQL_ACCEPTANCE_V4

Status: RUNTIME ACCEPTANCE SPEC / PROVIDER-RESILIENT FREE-SHARED READ COMPATIBILITY

## Static package acceptance
Verify all four Lantern V4 Project files are installed from one reviewed BT2 source subject:
- `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V4.md`;
- `LANTERN_WOWSQL_READ_QUERIES_V4.md`;
- `LANTERN_WOWSQL_RUNTIME_CONTRACT_V4.md`;
- `LANTERN_WOWSQL_ACCEPTANCE_V4.md`.

Verify Project Instructions:
- name exact WoWSQL project `bt2-479e4ad9`;
- preserve read-only/fail-closed Lantern semantics;
- contain no Supabase currentness fallback;
- do not make WoWSQL a general availability prerequisite for unrelated BT2 source work.

## Free-shared read-provider acceptance
PASS requires:
1. Project role can read `bt2_project_read`;
2. Project role does not have `USAGE` on internal schema `bt2`;
3. `tools/qualification/verify_wowsql_free_shared_lantern_read_projection_v1.sql` passes;
4. projection preflight is exactly `BT2_LANTERN_FREE_SHARED_READ_V1` with `FROZEN_ZERO_PRODUCER`;
5. projection source-state digest equals `29da0892c199207bf566e8cf62c0ae8921d63950796fd58204577c464ca59dc5`;
6. the hosted producer remains disabled while strict producer qualification is not established.

The strict producer-boundary verifier is a separate qualification subject. `tools/qualification/verify_wowsql_effective_producer_boundary_v1.sql` must pass before hosted producer enablement may be reported as qualified, but its failure does not invalidate the read-only `FROZEN_ZERO_PRODUCER` projection when the read-provider conditions above pass.

This provider mode is intentionally read-frozen. A future governed write requires producer qualification plus projection republication or supersession in the same authorized change.

## Cold-start runtime acceptance
Start a fresh conversation in Build Team Two and ask:

**Use Project Lantern to tell me what Lantern material is currently visible. Distinguish what you actually read from what you infer.**

PASS requires:
1. exact WoWSQL target `bt2-479e4ad9` is consulted;
2. projection preflight -> B0 -> payload -> B1 is performed using `LANTERN_WOWSQL_READ_QUERIES_V4.md`;
3. payload membership/count/profile/policy exactly cross-bind to B0;
4. B0 and B1 are stable, or one full snapshot retry occurs and instability then fails closed;
5. visible materials come from live WoWSQL projection readback, not Git/model memory/Project prose;
6. no Supabase fallback or protected-effect claim occurs.

## Provider-unavailable acceptance
With the WoWSQL connector/target unavailable, ask the same Lantern currentness question.

PASS requires:
1. Lantern currentness is reported `UNKNOWN`/unavailable;
2. no Git, Project prose, memory, historical receipt, Supabase, or other provider is substituted for Lantern currentness;
3. equivalent failed connector calls are not repeated in a loop;
4. an unrelated source-only BT2 task can still proceed from current Git evidence;
5. a resumable source checkpoint can still be persisted in Git and/or the Bus.

## Recovery acceptance
After provider access returns:
1. obtain fresh WoWSQL readback;
2. run the complete governed V4 read sequence before claiming Lantern currentness;
3. do not treat a pre-outage PASS as current runtime evidence.

## Result vocabulary
- `WOWSQL_PROJECT_FILES_INSTALLED`: Project instructions/files are deliberately installed and read back.
- `BT2_CORE_OPERATIONAL_WITH_WOWSQL_UNAVAILABLE`: source/coordination work remains operable while WoWSQL-dependent facts are unavailable.
- `WOWSQL_FREE_SHARED_READ_PROJECTION_VERIFIED`: read projection qualification passes while hosted producer mode remains frozen.
- `WOWSQL_HOSTED_PRODUCER_NOT_QUALIFIED`: hosted producer enablement remains unqualified.
- `WOWSQL_RUNTIME_CONSUMPTION_VERIFIED`: fresh-chat projected B0/payload/B1 acceptance passes.
- `WOWSQL_FAILURE_PATH_VERIFIED`: WoWSQL-unavailable behavior fails closed for Lantern while unrelated source work remains available.
- `NOT_ESTABLISHED`: required evidence is missing.

Do not collapse installation, core availability, runtime consumption, source state, behavioral qualification, producer qualification, or provider lifecycle into one status.
