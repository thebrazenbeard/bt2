# LANTERN_POSTGRESQL_ACCEPTANCE_V4

Status: SOURCE CANDIDATE / PROVIDER-NEUTRAL RUNTIME ACCEPTANCE

## Static package acceptance

PASS requires the V4 Project Instructions and the four V4 Lantern files to come from one reviewed BT2 source subject.

Historical WoWSQL V1-V3 files remain present but inactive once V4 is installed.

## Database reconstruction acceptance

PASS requires a blank supported PostgreSQL database to be reconstructed from canonical BT2 source using the accepted build manifest or its reviewed successor.

At minimum verify:
1. required extensions, including `pgcrypto`;
2. canonical `bt2` schemas/tables/views/functions;
3. ordered schema + migration application;
4. canonical seeds/data/loaders needed for `PROJECT_LANTERN`;
5. migration/build receipts and reconstruction oracle;
6. no WoWSQL-only projection is required for ordinary currentness reads.

Object presence alone is not parity.

## Lantern state acceptance

PASS requires:
1. exactly one accepted `PROJECT_LANTERN` profile lineage;
2. exactly one `BT2_MATERIAL_CUT_V1` cut;
3. payload count and exact members cross-bind to the cut;
4. payload profile/policy digests cross-bind to the cut;
5. the reconstructed state matches the accepted source-controlled Lantern state subject;
6. current producer authority is independently reported and not inferred from read success.

The historical source-controlled migrated state includes two governed visible materials and zero current producer authority. A different accepted state requires a new reviewed source subject and qualification rather than silent drift.

## SQL Connectome acceptance

PASS requires:
1. `platform_status` returns the expected database/runtime identity;
2. `migration_state` reports the expected SQL Connectome migration head;
3. `lantern_cut(PROJECT_LANTERN)` returns one cross-bound governed cut;
4. two consecutive calls on an unchanged runtime return the same governed subject;
5. the MCP surface contains no protected write tool unless a separately reviewed write contract has been authorized.

## Recovery acceptance

PASS requires a provider-independent backup and blank-target restore qualification of the exact runtime subject or an equivalent reviewed recovery mechanism. Provider snapshots alone are insufficient.

## Cold-start Project acceptance

After installation, start a fresh Build Team Two chat and ask:

**Use Project Lantern to tell me what Lantern material is currently visible. Distinguish what you actually read from what you infer.**

PASS requires:
1. the qualified SQL Connectome/PostgreSQL runtime is consulted;
2. V4 currentness is obtained from a one-snapshot governed read;
3. exact membership/count/profile/policy cross-binding passes;
4. visible materials come from live runtime readback;
5. no WoWSQL/Supabase/memory fallback occurs;
6. no protected-effect authority is inferred.

## Failure path

If the V4 runtime is unavailable, unqualified, drifted, or incomplete, return `UNKNOWN` for Lantern currentness.

## Result vocabulary

- `V4_SOURCE_READY`
- `V4_DATABASE_RECONSTRUCTED`
- `V4_RUNTIME_QUALIFIED`
- `V4_PROJECT_FILES_INSTALLED`
- `V4_PROJECT_INSTRUCTIONS_INSTALLED`
- `V4_RUNTIME_CONSUMPTION_VERIFIED`
- `V4_FAILURE_PATH_VERIFIED`
- `NOT_ESTABLISHED`

Do not collapse these states.
