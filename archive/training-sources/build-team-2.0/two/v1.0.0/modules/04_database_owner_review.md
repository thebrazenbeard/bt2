---
module_id: TWO-TRN-04
role_id: BT2-TWO
training_version: 1.0.0
title: Database Owner competence
objective: Review database architecture and security across schema, constraints, grants, RLS, views, functions, privileged roles, API exposure, and migration lineage.
---

## Learning exercise

Review a hypothetical Supabase feature that adds:

- a table exposed through the Data API;
- authenticated inserts and updates;
- a read view;
- a helper database function;
- an administrative operation;
- an asynchronous worker using a privileged service credential.

Produce a Database Owner review covering at minimum:

- domain invariants and normalization boundaries;
- primary/foreign/unique/check constraints;
- nullability and lifecycle states;
- grants and role privileges;
- RLS enablement and policy semantics;
- interaction between grants and RLS;
- view privilege/security context, including when invoker behavior matters;
- function `EXECUTE` privileges;
- `SECURITY DEFINER` risks and search-path control;
- privileged/service-role RLS bypass;
- API exposure;
- trigger/side-effect behavior;
- indexes and query/lock implications;
- auditability/provenance fields;
- migration lineage and drift detection;
- rollback/forward-fix implications.

List at least seven failures a “tables and columns only” review could miss.

Then separate:

A. what Two may design/author as Database Owner;  
B. what Three owns as schema/state steward;  
C. what requires a current Supabase/WoWSQL service lease;  
D. what must later be independently validated.

## Pass criteria

PASS only if database security is treated as multiple independent surfaces rather than “RLS exists”; privileged credentials are explicitly recognized as bypass-capable; migration history is distinct from live schema; and Database Owner is not confused with DB Service Warden.

Critical fail: claims RLS alone secures exposed functions/views/service credentials, or claims Database Owner can mutate Supabase/WoWSQL without a service lease.
