# WOWSQL HOSTED PRODUCER BOUNDARY V1

Status: HOSTED-RUNTIME COMPATIBILITY CONTRACT

## Purpose

`database/migrations/0018_lantern_producer_boundary_v1.sql` defines the strict reconstruction target for ordinary PostgreSQL 16: the Lantern producer function is owned by `postgres`, is `SECURITY DEFINER`, has fixed `search_path=pg_catalog, bt2`, grants execute to `postgres`, and removes PUBLIC function execute.

Hosted WoWSQL currently rejects `REVOKE` through both its MCP/control API and dashboard SQL Editor as a dangerous operation. Its session-pooler login also maps to a restricted project role rather than the owning `postgres` role.

That provider limitation does not by itself establish a security failure. PostgreSQL function invocation requires both schema `USAGE` and function `EXECUTE`.

## Hosted acceptance rule

For exact hosted target `bt2-479e4ad9`, the producer boundary is accepted only when all of the following are true:

1. `bt2.append_material_v1(uuid,text,text,text,text,text)` exists exactly once;
2. owner is `postgres`;
3. `SECURITY DEFINER` is true;
4. `proconfig` is exactly `search_path=pg_catalog, bt2`;
5. the query in `tools/qualification/verify_wowsql_effective_producer_boundary_v1.sql` returns successfully;
6. therefore zero non-owner roles with `rolcanlogin=true` have both schema `USAGE` on `bt2` and function `EXECUTE` on the producer.

A non-owner login becoming reachable is a hard FAIL even if no material write has yet occurred.

## Observed installation evidence — 2026-09-12

Live WoWSQL readback established:
- owner `postgres`;
- `SECURITY DEFINER=true`;
- `search_path=pg_catalog, bt2`;
- PUBLIC function execute remains true because WoWSQL blocks `REVOKE`;
- PUBLIC schema `USAGE=false` and `CREATE=false`;
- project pooler role `u_bt2_479e4ad9` has no schema `USAGE` or `CREATE`;
- no non-owner login role had the combined privileges required to invoke the producer;
- no login role was a member of the predefined `pg_read_all_data` or `pg_write_all_data` roles at observation time.

## Reconstruction and future tightening

Do not weaken migration 0018 or rollback qualification 0008. Blank PostgreSQL 16 rebuilds must continue to prove the stricter ACL with PUBLIC function execute removed.

If WoWSQL later exposes an owner-capable path that permits the strict `REVOKE`, apply the source-defined ACL and retire this hosted exception after readback. Until then, this contract records the provider-specific effective-access equivalence rather than pretending an impossible ACL mutation occurred.
