# BT2 NATIVE PROJECT INSTALL V1

## Goal
Install Build Team Two as a native ChatGPT Project runtime using canonical Git source plus WoWSQL durable state.

## Project Instructions
Replace the active BT2 Project Instructions with the complete contents of:
`native/project/PROJECT_INSTRUCTIONS_V1.md`

Do not append the new contract below stale Supabase-bound Lantern instructions. Replace obsolete instructions so there is one active provider/runtime model.

## Project files
Remove the old Supabase-bound Lantern runtime files from active Project-file use:
- `LANTERN_OPERATOR_HANDSHAKE_V1.md`
- `LANTERN_READ_QUERIES_V1.md`
- `LANTERN_RUNTIME_CONTRACT_V1.md`
- `LANTERN_ACCEPTANCE_V1.md`

Install these canonical files from `bt2/main`:
- `native/project/BT2_NATIVE_RUNTIME_V1.md`
- `native/project/BT2_CODING_OPERATIONS_V1.md`
- `native/project/BT2_RECOVERY_AND_STATE_V1.md`
- `docs/runtime/LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md`
- `docs/runtime/LANTERN_WOWSQL_READ_QUERIES_V1.md`
- `docs/runtime/LANTERN_WOWSQL_RUNTIME_CONTRACT_V1.md`
- `docs/runtime/HYPERCONNECTOME_RUNTIME_MODEL.md`
- `docs/runtime/PLASTICITY_AND_STATE_GOVERNANCE.md`

Optional acceptance reference:
- `docs/runtime/LANTERN_WOWSQL_ACCEPTANCE_V1.md`

## Acceptance after installation
Use a fresh chat in Build Team Two. Confirm it can:
1. identify `thebrazenbeard/bt2@main` as canonical source;
2. consult WoWSQL `bt2-479e4ad9` for runtime state;
3. perform Lantern B0 -> payload -> B1 through WoWSQL with no Supabase fallback;
4. explain current source/runtime state without relying on prior-chat memory;
5. execute a small coding task using branch/worktree -> implementation -> test -> review/integration discipline.

Record failures as installed-BT2 bugs. Do not reopen the completed consolidation merely because acceptance finds a defect.
