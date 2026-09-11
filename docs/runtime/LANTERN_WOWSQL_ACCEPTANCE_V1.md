# LANTERN_WOWSQL_ACCEPTANCE_V1

Status: SUCCESSOR RUNTIME ACCEPTANCE SPEC / NOT YET INSTALLED

Run after the BT2 ChatGPT Project's Lantern instructions/files have been deliberately changed from the Supabase provider contract to the WoWSQL successor contract.

## Static acceptance

Verify:
- the installed Project instructions name exact WoWSQL project `bt2-479e4ad9` as the Lantern currentness backend;
- `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md` and `LANTERN_WOWSQL_READ_QUERIES_V1.md` are the installed runtime contract;
- the installed source binding names the exact canonical integration/database subject that qualified the provider cutover;
- no installed currentness instruction still requires Supabase `agvhmutlrolbaijzlbqk`.

## Cold-start acceptance

Start a fresh conversation in the target ChatGPT Project and ask:

**Use Project Lantern to tell me what Lantern material is currently visible. Distinguish what you actually read from what you infer.**

PASS requires:
1. Lantern consultation is recognized as required;
2. exact WoWSQL target `bt2-479e4ad9` is consulted;
3. B0 -> payload -> B1 is performed using the successor queries;
4. payload membership/count/profile/policy exactly cross-bind to B0;
5. B0 and B1 are stable, or one full retry occurs and instability then fails closed;
6. visible materials come from live WoWSQL readback rather than Project prose/model memory;
7. no uninterrupted-conversation identity is claimed;
8. no write/installation/authority/provider effect is claimed without evidence.

## Cross-provider cutover acceptance

Immediately before Supabase destructive retirement, while both providers still exist:

1. freeze Supabase Lantern writes;
2. execute the required Supabase B0 -> payload -> B1 cut;
3. execute the WoWSQL B0 -> payload -> B1 cut;
4. require exact equality of profile, predecessor, policy, material count, member IDs, canonical digests, semantic keys, source digests, receipt IDs, canonical payloads, and relevant timestamps;
5. require normalized rowset digests for profile/receipt/material/authorization-history/schema-policy to match the preserved final source frontier;
6. require zero current producer authorization unless an explicitly governed active permit is part of the cutover design;
7. perform fresh-chat WoWSQL cold-start acceptance;
8. prove no current runtime route still consults Supabase for Lantern currentness.

Only after these pass may Supabase Lantern be marked provider-retired.

## Failure-path acceptance

Evaluate a runtime without WoWSQL access, or explicitly disable the connector. The same currentness question must fail closed. It must not fall back to retired Supabase, model memory, a historical Project file, or Git source as current material state.

## Result vocabulary

- `WOWSQL_RUNTIME_CONTRACT_SOURCE_READY`: successor docs/queries are source-controlled.
- `WOWSQL_PROJECT_FILES_INSTALLED`: the ChatGPT Project has been deliberately updated to the successor contract.
- `WOWSQL_RUNTIME_CONSUMPTION_VERIFIED`: fresh-chat B0/payload/B1 passed.
- `CROSS_PROVIDER_CUTOVER_VERIFIED`: frozen final Supabase frontier equals the WoWSQL governed state and routing has moved.
- `SUPABASE_PROVIDER_RETIREMENT_READY`: all destructive-retirement gates except Patrick's actual delete action are closed.
- `NOT_ESTABLISHED`: use whenever required evidence is missing.

Do not call Supabase safe to delete merely because the WoWSQL rows match; the installed consumer contract and current routing must also have moved.
