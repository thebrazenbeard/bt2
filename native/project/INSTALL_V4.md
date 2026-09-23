# BT2 NATIVE PROJECT INSTALL V4

## Status
SOURCE INSTALLATION CANDIDATE. Presence in Git does not establish native Project installation, runtime binding, or behavioral effectiveness.

## Why V4 exists
V3 correctly fails closed for Lantern currentness but still makes WoWSQL appear in ordinary BT2 bootstrap/recovery paths strongly enough that provider instability can become an operational bottleneck.

V4 separates provider-specific truth from core BT2 availability:
- Git remains canonical for source and resumable source state;
- the Chat Communication Bus carries non-PR coordination/handoffs;
- WoWSQL is consulted only when a claim or acceptance criterion actually requires live runtime state;
- WoWSQL failure makes those runtime facts `UNKNOWN` without blocking unrelated source/review/test/recovery work;
- Lantern V4 remains fail-closed with no Supabase fallback.

## Project Instructions
Replace the active BT2 Project Instructions only when separately authorized, using exact `native/project/PROJECT_INSTRUCTIONS_V4.md` from the reviewed V4 source subject.

## Core Project files
V4 introduces:
- `BT2_NATIVE_RUNTIME_V2.md`
- `BT2_CODING_OPERATIONS_V2.md`
- `BT2_RECOVERY_AND_STATE_V2.md`
- `RUNTIME_PROVIDER_DEGRADATION_V1.md`

V4 introduces a coherent four-file Lantern V4 contract. V1/V2/V3 Lantern files remain historical/inactive when the corresponding V4 files are installed.

## Lantern V4 files
Add exactly the reviewed V4 set:
- `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V4.md`
- `LANTERN_WOWSQL_READ_QUERIES_V4.md`
- `LANTERN_WOWSQL_RUNTIME_CONTRACT_V4.md`
- `LANTERN_WOWSQL_ACCEPTANCE_V4.md`

All four must come from the one exact source subject recorded by `PROJECT_FILES_MANIFEST_V4.json`.

## Installation boundary
Creating or merging this source package does not install it into ChatGPT Project settings/files. Project installation is a distinct protected effect and requires separate live authority plus readback.

## Acceptance target
A fresh BT2 Project runtime should be able to:
1. recover and execute source work while WoWSQL is unavailable;
2. state `UNKNOWN` for WoWSQL-only/Lantern-currentness facts during that outage;
3. avoid Supabase fallback;
4. persist a resumable Git/Bus checkpoint;
5. obtain fresh WoWSQL readback after provider recovery before making current runtime claims.

See `PROJECT_FILES_MANIFEST_V4.json` for the exact reviewed payload binding once populated.
