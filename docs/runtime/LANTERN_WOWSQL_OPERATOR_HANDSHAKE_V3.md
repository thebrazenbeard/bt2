# LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V3

Status: CANONICAL RUNTIME HANDSHAKE / FREE-SHARED READ ROUTE

Use this handshake when a fresh BT2 Project runtime must consult Lantern.

1. Session boundary: treat the current conversation as a replaceable terminal; do not claim uninterrupted runtime/subjective continuity.
2. Target binding: require read access to exact WoWSQL project `bt2-479e4ad9`. Do not substitute Supabase, another WoWSQL project, Git source, Project prose, or model memory.
3. Route binding: execute the projection preflight from `LANTERN_WOWSQL_READ_QUERIES_V3.md`. On WoWSQL free-shared PostgreSQL, the Project role reads `bt2_project_read`; it is intentionally denied direct `bt2` schema access.
4. B0 cut: execute the B0 query from `LANTERN_WOWSQL_READ_QUERIES_V3.md`.
5. Payload: read `bt2_project_read.lantern_materials_v1` for `PROJECT_LANTERN` and cross-bind count/membership/profile/policy exactly to B0.
6. B1 cut: execute the same cut again.
7. Stability: B0 and B1 must match exactly. Retry the complete preflight -> B0 -> payload -> B1 sequence once on mismatch. Second mismatch => `UNKNOWN`.
8. Use: only a stable, correctly bound projection is current Lantern material evidence.
9. Report ceiling: distinguish source/package present, backend consulted, stable material cut obtained, and specific material used. Do not collapse those into unrelated authority or qualification.

## Fail closed

Return a clear limitation rather than inventing currentness when:
- exact WoWSQL target `bt2-479e4ad9` is unavailable;
- projection preflight is absent, non-singular, or not `FROZEN_ZERO_PRODUCER`;
- B0 is absent or non-singular;
- B0/payload cross-binding fails;
- B0/B1 remains unstable after one complete retry;
- requested action requires authority not established by current governance.

## Writes and free-shared projection ceiling

The runtime integration is read-only by default. A governed read never authorizes a write.

`BT2_LANTERN_FREE_SHARED_READ_V1` is valid only while producer mode is `FROZEN_ZERO_PRODUCER`. Any future governed write must republish or supersede the projection in the same authorized change before Project currentness can be claimed again.

Protected effects still require current authority.

## Provider fallback

There is no Supabase currentness fallback. If the WoWSQL projection cannot establish a stable cut, Lantern currentness is `UNKNOWN`.
