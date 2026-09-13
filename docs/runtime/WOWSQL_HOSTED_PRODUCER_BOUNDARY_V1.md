# WOWSQL HOSTED PRODUCER BOUNDARY V1

Status: HOSTED-RUNTIME COMPATIBILITY CONTRACT

## Purpose

`database/migrations/0018_lantern_producer_boundary_v1.sql` defines the strict reconstruction target for ordinary PostgreSQL 16: the Lantern producer function is owned by `postgres`, is `SECURITY DEFINER`, has fixed `search_path=pg_catalog, bt2, pg_temp`, grants execute to `postgres`, and removes PUBLIC function execute.

Hosted WoWSQL currently rejects `REVOKE` through both its MCP/control API and dashboard SQL Editor as a dangerous operation. Its session-pooler login also maps to a restricted project role rather than the owning `postgres` role.

That provider limitation does not by itself establish a security failure. PostgreSQL function invocation requires both schema `USAGE` and function `EXECUTE`, and a `SECURITY DEFINER` search path is trustworthy only while untrusted reachable roles cannot create objects in its writable schemas.
The trusted path also names `pg_temp` explicitly last. Omitting it would let PostgreSQL implicitly search the caller's temporary schema before trusted relations, allowing temp-object shadowing of unqualified table references inside the definer function.

## Hosted acceptance rule

For exact hosted target `bt2-479e4ad9`, the producer boundary is accepted only when all of the following are true:

1. exact `bt2.append_material_v1(uuid,text,text,text,text,text)` exists exactly once;
2. owner is `postgres`;
3. `SECURITY DEFINER` is true;
4. `proconfig` is exactly `search_path=pg_catalog, bt2, pg_temp`;
5. the query in `tools/qualification/verify_wowsql_effective_producer_boundary_v1.sql` returns successfully;
6. zero non-owner login identities can reach any role state, either directly or through a transitive `SET ROLE` path permitted by `pg_auth_members.set_option`, that has both schema `USAGE` on `bt2` and function `EXECUTE` on the producer;
7. zero non-owner login identities can reach any role state with schema `CREATE` on `bt2`.

A non-owner login becoming able to invoke the producer, or becoming able to create objects in the trusted `bt2` search-path schema, is a hard FAIL even if no material write has yet occurred.

## Observed installation evidence — 2026-09-12

Live WoWSQL readback established:
- PostgreSQL `16.15`;
- exact producer signature exists once;
- owner `postgres`;
- `SECURITY DEFINER=true`;
- observed live `search_path=pg_catalog, bt2` (without explicit `pg_temp`);
- therefore the observed live function does **not** satisfy the corrected hosted acceptance rule until its function-local search path is tightened to `pg_catalog, bt2, pg_temp`;
- PUBLIC function execute remains true because WoWSQL blocks `REVOKE`;
- PUBLIC schema `USAGE=false` and `CREATE=false`;
- project pooler role `u_bt2_479e4ad9` has no schema `USAGE` or `CREATE`;
- no non-owner login role had the combined privileges required to invoke the producer at observation time;
- the only non-owner roles with both schema `USAGE` and function `EXECUTE` were `pg_read_all_data` and `pg_write_all_data`, and no observed login membership reached them;
- no non-owner role had schema `CREATE` on `bt2` at observation time.

## Reconstruction and future tightening

Do not weaken migration 0018 or rollback qualification 0008. Blank PostgreSQL 16 rebuilds must continue to prove the stricter ACL with PUBLIC function execute removed.

If WoWSQL exposes an owner-capable path for function configuration, first tighten the live function-local search path to `pg_catalog, bt2, pg_temp` and verify it by readback. If WoWSQL later permits the strict `REVOKE`, also apply the source-defined ACL and retire this hosted exception after readback. Until both applicable controls are verified, do not label the hosted producer boundary accepted merely because no non-owner login is currently reachable.
