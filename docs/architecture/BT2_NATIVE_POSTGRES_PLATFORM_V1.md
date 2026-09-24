# BT2 Native Postgres Platform V1

Status: architecture candidate / source-only / no deployment authority

## Decision

Build a BT2-owned Postgres platform around standard PostgreSQL rather than creating a PostgreSQL fork or binding BT2 to another proprietary database control plane.

The platform MUST keep the database reconstructible from source and MUST allow the backing PostgreSQL provider to be replaced without changing BT2/Lantern semantics.

## Supabase-derived lessons

The reviewed `supabase/supabase` architecture confirms that the useful product boundary is not a custom database engine. It is a composition of standard PostgreSQL with independently replaceable services:

- PostgreSQL as the authoritative database;
- PostgREST for generated REST APIs;
- postgres-meta for schema/role/query administration;
- an auth service for identity/JWT when human application auth is needed;
- a pooler for connection pressure;
- optional realtime, storage, functions, dashboard and gateway services.

BT2 should adopt the compositional pattern, not clone the entire product.

## V1 architecture

### 1. PostgreSQL substrate

Support ordinary PostgreSQL 16/17 with no BT2 semantic dependence on a specific cloud vendor.

Initial development target: an Aiven PostgreSQL free service once separately provisioned and qualified.

Provider-specific configuration belongs under an adapter boundary. The canonical schema, migrations, qualification and recovery path remain source-controlled in BT2.

### 2. Canonical database source

The existing BT2 PostgreSQL baseline and migrations remain the reconstruction authority.

Provider provisioning is never the source of truth for schema.

Every accepted runtime must be reproducible from:
1. canonical baseline;
2. ordered migrations;
3. source-controlled seed/provenance data;
4. exact qualification tooling.

### 3. Data API

Use PostgREST where a generated REST surface is useful.

Authorization remains PostgreSQL-role/RLS based. Public exposure of arbitrary tables is forbidden by default; expose governed schemas/views only.

### 4. Administrative API

Use postgres-meta only behind an authenticated BT2 control boundary.

postgres-meta explicitly provides no standalone security and MUST NOT be internet-exposed directly.

A BT2 control service wraps administrative operations and enforces:
- project identity;
- capability grants;
- currentness;
- read/write separation;
- effect receipts;
- explicit authorization for protected writes.

### 5. Connection management

V1 does not need a cloud-scale multi-tenant pooler.

Use the provider's normal connection endpoint or PgBouncer-compatible pooling first. Supavisor remains a future option only if measured connection pressure justifies it.

### 6. Auth

V1 machine access uses explicit service identities, PostgreSQL roles and scoped platform credentials.

Do not add GoTrue/Auth merely because Supabase uses it. Add human-user OAuth/JWT auth only when a real consumer requires it.

### 7. Realtime

Deferred.

Lantern/currentness does not require websocket fan-out. Realtime may be admitted later for coordination/event consumers after delivery semantics and replay requirements are defined.

### 8. Backups and recovery

A valid platform needs provider-independent recovery:
- logical `pg_dump` artifact;
- migration replay;
- seed/provenance replay;
- checksum/digest verification;
- periodic restore qualification to a blank PostgreSQL instance.

Provider snapshots are additional recovery evidence, never the only recovery path.

## Lantern currentness

Replace the WoWSQL-specific `bt2_project_read` projection route.

For a provider we control normally, Lantern reads SHOULD use one read-only REPEATABLE READ transaction:
1. establish exact database/runtime identity;
2. begin read-only repeatable-read transaction;
3. read accepted profile/cut;
4. read payload;
5. cross-bind count, membership, profile and policy;
6. commit/rollback;
7. emit an exact read receipt.

The transaction snapshot replaces the provider workaround that required WoWSQL preflight -> B0 -> payload -> B1.

## WoWSQL retirement

WoWSQL-specific source becomes historical/provider evidence after replacement qualification.

Retire from the active runtime contract:
- exact target `bt2-479e4ad9`;
- `database/provider/wowsql/**`;
- WoWSQL-only producer-boundary exceptions;
- WoWSQL-only qualification scripts;
- `LANTERN_WOWSQL_*_V3.md` as current runtime files;
- `FROZEN_ZERO_PRODUCER` as a provider-imposed runtime mode.

Do not delete historical commits or qualification evidence.

## Acceptance gates

A replacement backend is not current until all are true:

1. blank database reconstructs from canonical BT2 source;
2. all migrations pass;
3. required extensions and functions are present;
4. privilege/role qualification passes without provider exceptions;
5. Lantern source/seed material is loaded and exact-member digests match;
6. repeatable-read Lantern currentness test passes;
7. backup and blank restore qualification passes;
8. ChatGPT plugin read path returns exact runtime identity and currentness receipt;
9. write path remains separately authority-gated;
10. WoWSQL is absent from every effective runtime/config/instruction path.

Source/build/install/runtime/effect remain separate states.
