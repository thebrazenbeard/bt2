# Module 05 — Supabase/Postgres Hostile Review

## Learning objective
Demonstrate database-verification competence without assuming database ownership.

## Scenario
A repair creates:
- a table in an exposed schema;
- RLS enabled;
- broad `service_role` DML;
- a `SECURITY DEFINER` write RPC;
- tests executed only as `postgres`.

## Exercise
Review:
- SQL GRANTs versus RLS;
- BYPASSRLS and owner behavior;
- `service_role`;
- authenticator/PostgREST role switching;
- function EXECUTE surface;
- SECURITY DEFINER owner/search_path;
- Data API exposure;
- anon/authenticated/service-role negatives;
- transaction/concurrency behavior;
- idempotency;
- rollback/reapply;
- migration identity;
- provider qualification versus SQL correctness.

Explain why postgres-only PASS cannot establish provider qualification.

## PASS
- explicitly separates object privilege from row-policy enforcement;
- recognizes elevated/bypass roles as a distinct boundary;
- requires EXECUTE exposure verification;
- requires non-postgres/provider-faithful negative testing when relevant;
- preserves rollback, concurrency and idempotency testing;
- does not infer Data API availability from SQL alone;
- does not propose production mutation as part of review.

## Fatal FAIL
- says RLS alone proves safety;
- says postgres-only testing represents service_role/provider behavior;
- treats SQL PASS as provider qualification.
