# LANTERN_POSTGRESQL_OPERATOR_HANDSHAKE_V4

Status: SOURCE CANDIDATE / PROVIDER-NEUTRAL POSTGRESQL READ ROUTE

Use this handshake when a fresh BT2 Project runtime must consult Lantern after the WoWSQL runtime is retired.

1. Treat the current chat as a replaceable execution terminal.
2. Require a qualified SQL Connectome/PostgreSQL runtime. A provider name, service name, or successful TCP connection is not enough.
3. Require PostgreSQL runtime evidence showing the canonical BT2 `bt2` schema, `bt2.runtime_visible_materials_v1`, and `bt2.material_cut_v1(text)` are installed from the accepted BT2 source subject.
4. Prefer the SQL Connectome `lantern_cut` tool because it performs the cut and payload read inside one `REPEATABLE READ READ ONLY` transaction.
5. If direct PostgreSQL access is used instead, execute the complete V4 transaction in `LANTERN_POSTGRESQL_READ_QUERIES_V4.md` without splitting it across independent snapshots.
6. Require exactly one cut for `PROJECT_LANTERN`.
7. Cross-bind payload row count, exact member tuples, profile digest, and policy digest to that cut.
8. Treat only a qualified, cross-bound transaction result as current Lantern evidence.
9. Preserve source/build/install/runtime/effect as separate states.
10. A governed read never grants producer, database-write, Project-settings, merge, deploy, or installation authority.

## Fail closed

Return `UNKNOWN` for Lantern currentness when:
- the qualified SQL Connectome/PostgreSQL runtime is unavailable;
- the canonical `bt2` schema/functions/views are absent or drifted;
- `material_cut_v1('PROJECT_LANTERN')` returns zero or more than one row;
- payload count or exact membership does not match the cut;
- any payload row differs from the cut profile/policy digests;
- the runtime identity/migration subject cannot be established;
- the requested effect requires authority not established by current governance.

Do not substitute WoWSQL, Supabase, another provider, Git source, Project prose, historical material, or model memory as current Lantern state.

## Provider boundary

The PostgreSQL provider is infrastructure, not Lantern semantics. Cloud vendor, region, and service identifier may change without changing this contract, provided the new runtime is reconstructed from canonical source and independently re-qualified.

A free-tier provider-assigned region is not part of Lantern identity.

## Writes

Producer authorization and material admission are separate qualification subjects. Do not infer write authority from a successful V4 read.
