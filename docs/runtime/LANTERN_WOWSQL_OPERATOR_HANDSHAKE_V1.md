# LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1

Status: CANONICAL-CANDIDATE SUCCESSOR RUNTIME CONTRACT / NOT YET INSTALLED IN CHATGPT PROJECT

Use this handshake when a fresh BT2 Project runtime must consult Lantern after the WoWSQL provider cutover.

1. Session boundary: treat the current conversation as a replaceable terminal; do not claim uninterrupted runtime/subjective continuity.
2. Target binding: require read access to exact WoWSQL project `bt2-479e4ad9`. Do not substitute the retired Supabase project, another WoWSQL project, or model memory.
3. Source binding: preserve the exact canonical BT2 integration/database subject that installs this contract. GitHub source provenance and WoWSQL runtime state remain separate evidence.
4. B0 cut: execute the B0 query from `LANTERN_WOWSQL_READ_QUERIES_V1.md`.
5. Payload: read `bt2.runtime_visible_materials_v1` for `PROJECT_LANTERN` and cross-bind count/membership/profile/policy exactly to B0.
6. B1 cut: execute the same cut again.
7. Stability: B0 and B1 must match exactly. Retry the complete sequence once on mismatch. Second mismatch => `UNKNOWN`.
8. Use: only a stable cut is current Lantern material evidence.
9. Report ceiling: distinguish package/source present, backend consulted, stable material cut obtained, and specific material used. Do not collapse those into installation/effectiveness or authority.

## Fail closed

Return a clear limitation rather than inventing currentness when:
- exact WoWSQL target `bt2-479e4ad9` is unavailable;
- `bt2.material_cut_v1('PROJECT_LANTERN')` does not yield exactly one authoritative cut;
- B0/payload cross-binding fails;
- B0/B1 remains unstable after one complete retry;
- requested action requires authority not established by current governance.

## Writes

The runtime integration is read-only by default. A governed read never authorizes a write. Producer permits, material admission, database/provider mutation, Project settings/files mutation, merge/deploy, qualification, installation, or other protected effects require separate current authority.

## Supabase retirement condition

This handshake may replace the Supabase-bound Lantern operator contract only after:
- exact source-to-WoWSQL durable preservation is verified;
- historical co-resident Supabase state required for provenance is preserved/classified;
- the ChatGPT Project instructions/files are deliberately updated to reference this WoWSQL contract;
- a fresh-chat cold-start acceptance passes against `bt2-479e4ad9`;
- no current workflow still requires Supabase `agvhmutlrolbaijzlbqk`.
