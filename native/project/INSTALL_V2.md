# BT2 NATIVE PROJECT INSTALL V2

## Status
SOURCE INSTALLATION CANDIDATE. Presence in Git does not establish native Project installation, runtime binding, or behavioral effectiveness.

## Exact installation subject
Install only the immutable Project Instructions and file identities recorded by `native/project/PROJECT_FILES_MANIFEST_V2.json`.

## Project Instructions
Replace the active BT2 Project Instructions with the exact `native/project/PROJECT_INSTRUCTIONS_V2.md` subject recorded by the manifest. Do not append it beneath an older contract.

## Project files
Install every required native Project file listed in `PROJECT_FILES_MANIFEST_V2.json`. The four Lantern WoWSQL V2 files use distinct `_V2.md` filenames and the free-shared `bt2_project_read` projection. Keep existing `_V1.md` Project files untouched; do not delete, overwrite, or re-upload a same-named file. Project Instructions V2 designate the `_V2.md` files as active.

## Runtime binding
The target remains WoWSQL `bt2-479e4ad9`. Project Lantern currentness reads use projection preflight -> B0 -> payload -> B1. There is no Supabase fallback. The internal `bt2` schema remains inaccessible to the Project role.
