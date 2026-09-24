# BT2 Database ChatGPT Plugin V1

Status: design candidate / not installed / no runtime authority

## Purpose

Provide ChatGPT a first-party BT2 database interface instead of depending on a database vendor's ChatGPT connector.

The plugin is a client of the BT2 control service. It MUST NOT embed database owner credentials or connect arbitrary user prompts directly to PostgreSQL.

## Tool surface

V1 SHOULD expose:

### Read tools

- `platform_health`
  - exact platform version;
  - backing provider adapter;
  - database server version;
  - migration head;
  - runtime identity digest.

- `database_schema`
  - schemas, tables, views, functions, extensions and roles;
  - optional bounded object filter.

- `query_readonly`
  - SELECT/EXPLAIN only;
  - read-only transaction;
  - row/byte/time limits;
  - exact subject and transaction receipt.

- `lantern_current_cut`
  - one repeatable-read transaction;
  - accepted profile/policy;
  - exact material membership;
  - payload or bounded projection;
  - currentness receipt.

- `migration_status`
  - canonical migration list vs applied ledger;
  - drift without mutation.

- `backup_status`
  - latest backup identity and latest qualified restore evidence.

### Protected write tools

- `apply_migrations`
- `execute_governed_sql`
- `lantern_append_material`
- `create_or_rotate_service_role`
- `restore_database`

Protected writes require explicit live authority, preflight currentness, bounded target, transaction/effect receipt, and post-effect readback.

Plugin installation or connection NEVER grants database write authority by itself.

## Safety model

The service, not the model, is the final enforcement boundary.

Enforce:
- deny-by-default capabilities;
- separate read and write credentials;
- SQL parser/statement-class checks;
- transaction timeout and result limits;
- schema allowlists for ordinary reads;
- no secret values in tool responses;
- append-only audit/effect receipts;
- idempotency keys for retriable writes;
- exact database identity on every response;
- post-write verification.

An `execute arbitrary SQL as owner` tool is explicitly out of scope for V1.

## Plugin packaging

The ChatGPT plugin can be a private first-party plugin owned by Patrick.

Its package should contain:
- plugin metadata and interface description;
- BT2 database operating skill/instructions;
- the MCP/app binding to the BT2 control service once that HTTPS/MCP endpoint exists.

The existing private `lappy-operator` plugin demonstrates that Patrick's account can own private plugins. The DB plugin must be a separate capability surface with its own permissions and must not inherit Lappy filesystem authority.

## Provider independence

The plugin speaks the BT2 platform protocol, not Aiven, WoWSQL, Supabase or another provider API.

Changing the backing Postgres provider must not require changing ordinary plugin tools or Lantern semantics.

## Minimum end-to-end qualification

1. provision blank PostgreSQL;
2. reconstruct BT2;
3. start BT2 control service;
4. call `platform_health`;
5. call `database_schema`;
6. call `lantern_current_cut`;
7. prove a write tool is denied without authority;
8. authorize one bounded test write;
9. verify exact post-effect state;
10. rotate/revoke the test credential and prove the old credential fails.

Only then classify the plugin runtime as qualified.
