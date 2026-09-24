# LANTERN_POSTGRESQL_RUNTIME_CONTRACT_V4

Status: SOURCE CANDIDATE / SUPERSEDES WOWSQL RUNTIME SEMANTICS WHEN INSTALLED AND QUALIFIED

## Purpose

Lantern supplies governed, provenance-bearing durable material to Build Team Two. PostgreSQL is the persistence substrate; SQL Connectome is the preferred governed ChatGPT/MCP interface.

The runtime contract is provider-neutral. Aiven, another managed PostgreSQL provider, or a self-hosted PostgreSQL instance may host the database without becoming part of Lantern semantics.

## Current migration state

The SQL Connectome development PostgreSQL substrate has been provisioned and its SQL Connectome control schema installed and read back.

The canonical BT2 `bt2` runtime schema, governed Lantern seed/data state, V4 read qualification, and fresh-chat Project consumption have not yet been established on that substrate.

Therefore:

`LANTERN_CURRENTNESS = UNKNOWN`

until V4 runtime acceptance passes.

## Evidence order

1. current live user instruction;
2. current installed Project Instructions;
3. exact current canonical Git source and reviewed branch/PR evidence;
4. current qualified SQL Connectome/PostgreSQL runtime state obtained by live readback;
5. installed Project files and historical evidence;
6. conversation/model memory or inference.

Never silently promote a lower class into a higher one.

## Governed read

Follow `LANTERN_POSTGRESQL_OPERATOR_HANDSHAKE_V4.md` and `LANTERN_POSTGRESQL_READ_QUERIES_V4.md`.

A valid current cut requires one repeatable-read snapshot containing:
- runtime/object preflight;
- exactly one `bt2.material_cut_v1('PROJECT_LANTERN')` row;
- payload from `bt2.runtime_visible_materials_v1`;
- exact count/membership/profile/policy cross-binding.

The SQL Connectome `lantern_cut` tool is the preferred implementation because it encapsulates those requirements in one governed call.

## Provider retirement

WoWSQL-specific V1-V3 files and `database/provider/wowsql/**` remain historical/source evidence. They are not deleted by V4.

Once V4 is installed and runtime-qualified:
- WoWSQL is not a currentness provider;
- `bt2_project_read` is not a current read contract;
- `FROZEN_ZERO_PRODUCER` is not a permanent Lantern semantic;
- Supabase remains superseded and is not a fallback.

## Writes and authority

Reads are read-only by default. Producer permits, material admission, migrations, restore, provider changes, plugin installation, Project settings, merges, and deployments are separately authorized effects.

A successful read never grants any of those authorities.

## Reporting

Report exact state separately:
- source package readiness;
- database reconstruction;
- runtime qualification;
- Project installation;
- fresh-chat behavioral consumption;
- protected effects.

Do not collapse them into a single PASS.
