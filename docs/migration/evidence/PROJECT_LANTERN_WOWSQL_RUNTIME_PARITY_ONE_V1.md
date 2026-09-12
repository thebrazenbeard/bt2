# Project Lantern WoWSQL Runtime Parity — One V1

Status: BACKEND PARITY / SUCCESSOR READ CONTRACT QUALIFIED; PROJECT ROUTE NOT CUT OVER
Date: 2026-09-11
Coordinator / execution owner: One
Systems architect counterpart: Two
Execution boundary: One + Two only

## Exact subjects

- Current source provider: Supabase `agvhmutlrolbaijzlbqk`
- Successor provider: WoWSQL `bt2-479e4ad9`
- Successor branch subject before this evidence file: `0814c9a9eb6f6e4d929912b5360206ffb2bf0cec`
- Database package digest: `195a7546f508be23e95048682a2d2597eb3c67c44901450701ee17ada05d6e57`
- L-D3 acceptance contract: `docs/qualification/BT2_LANTERN_LD3_MINIMUM_FALSIFIABLE_ACCEPTANCE_TWO_V1.md`

## Supabase currentness handshake

The required Supabase B0 -> payload -> B1 sequence was performed against exact project `agvhmutlrolbaijzlbqk`.

Stable cut:
- facade: `LANTERN_MATERIAL_CUT_V1`
- profile: `99ad3bcb89fdb16c5eff9fc870fdf210c5eed03b23c650c6e96352c902fa77a1`
- predecessor: NULL
- policy: `ae3ced9107a5a1adff9b85879847bb8cc0f8f4f7417e182f4c72e47593075445`
- material count: 2
- exact member tuples: stable across B0/B1

Payload identities, canonical payloads, receipt IDs, timestamps, profile/policy bindings, schema versions, semantic keys, canonical digests, and source digests were read and cross-bound to the cut. B0 and B1 matched exactly.

## WoWSQL successor handshake

The successor B0 -> payload -> B1 sequence was performed against exact WoWSQL project `bt2-479e4ad9` using:

```sql
SELECT * FROM bt2.material_cut_v1('PROJECT_LANTERN');
```

and `bt2.runtime_visible_materials_v1`.

The WoWSQL cut was stable and exactly matched the Supabase profile, predecessor, policy, count, members, payloads, receipts, timestamps, schema versions, semantic keys, canonical digests, and source digests.

Normalized complete visible-material rowset SHA-256 was independently computed on both providers over material ID, project scope, schema version, semantic key, canonical digest, source digest, canonical payload, created timestamp, receipt ID, profile digest, and policy digest.

- Supabase: `8ecc199ece82f0551d70fe624fdd58d1a4f34ad6b9ee73fad5eb140b210c045b`
- WoWSQL: `8ecc199ece82f0551d70fe624fdd58d1a4f34ad6b9ee73fad5eb140b210c045b`

Result: exact equality for the current two-member visible frontier.

## Clean-room successor semantics test

`database/tests/0005_lantern_runtime_contract_smoke.sql` was corrected to be blank-database rebuildable rather than depending on migrated Project Lantern data.

Exact current blob: `78bca2f325480b9d8cc7649aa7fc3f13483dac51`.

The test creates a synthetic governed-material universe inside one transaction, validates:
- singular governed cut;
- expected facade;
- payload count == material count;
- exact sorted membership cross-binding;
- profile/policy cross-binding;
- canonical-payload digest integrity;
- stable B0/B1;
- unknown-scope fail-closed behavior;

then rolls the fixture back.

The exact checked-in test logic was executed against live WoWSQL in one transaction and completed without exception. Immediate readback confirmed zero synthetic profile, material, and permit rows remained.

## CI correction and ceiling

The rebuild workflow previously invoked superseded `lantern_cohosted_history_v1.py`. It now invokes corrected `lantern_cohosted_history_v2.py` and the generic test loop will execute the clean-room runtime test.

GitHub Actions run `34637947974` / run number 117 on commit `0814c9a9eb6f6e4d929912b5360206ffb2bf0cec` concluded `failure`, but the job reported zero steps. Therefore this run supplies no SQL/test execution result. Blank-database GitHub-hosted qualification remains NOT ESTABLISHED; this is still a pre-execution infrastructure failure, not a semantic failure of the database package.

## Claim ceiling

Established now:
- `L-D1_COHOSTED_HISTORICAL_DATA_PRESERVATION = VERIFIED_V2`
- successor WoWSQL backend is live-readable and stable for current Lantern currentness semantics;
- present Supabase and WoWSQL visible-material frontiers are exactly equal;
- clean-room successor cut semantics and fail-closed unknown-scope behavior pass;
- source package/CI bindings now point to corrected V2 artifacts.

Not established / still open:
- `P1` installed Project provider binding: current Project instructions still require Supabase;
- `P2` fresh-chat cold-start through the installed WoWSQL contract;
- `P4` fresh-runtime WoWSQL-unavailable/no-fallback behavior;
- post-install `P5` authority non-amplification;
- `P6` operational dependency zero;
- final frozen-frontier replay of `P3` immediately before retirement;
- GitHub-hosted blank-database qualification, because current Actions jobs still fail before step execution;
- merge, cutover, Supabase retirement/deletion, Project instruction mutation, producer authorization, or any other protected effect.

Therefore the dominant Lantern blocker is no longer backend capability or data parity. It is deliberate installation/routing of the Project consumer contract followed by the fresh-runtime acceptance sequence defined by Two.
