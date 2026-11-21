# Memory Lifecycle V1 — sanitized source and provider audit

## Actual source inspection

- STM: bounded session and privacy governance; historical bridge read-only; source docs inspected from GitHub.
- DeepMemoryStorage: historical evidence union with append-only corrections, distinct record/event/effective/read times; source docs inspected.
- vera-mono: SQLite memory CAS/supersession ledger and historical projection boundary, with no self-certified authority; source inspected.
- BT2 main: source-only currentness status reports `lantern_currentness: UNKNOWN` and no qualified active replacement; separate signal_ingest Draft PR #123 owns candidate observations.
- Connected Supabase projects: **Vera** (active) contains RLS-enabled memory epoch subject/event/provider/archive tables, `semantic_atlas` runtime objects and read functions; **Tattler** (active) has service-role-limited webhook/review/usage tables, no Vera memory tables in its public schema. Read-only metadata and security advisors observed. No private row contents, auth identities or credentials read; no migration applied.

## TDD and verification

- RED: naive timestamp-last selector returned record `C` (old head `111` restated late) instead of corrected record `B` (head `222`). The exact test failed with `AssertionError: 'C' != 'B'`, exit **1**.
- GREEN: replace last-timestamp selection with explicit rooted supersession lineage, stale-head restatement suppression and conflict holding. Identical test passes.
- Additional privacy **RED**: two assertions failed when unauthorized private record IDs and a private terminal head leaked through `rejected` / `structural_heads`. New fix omits unauthorized records from all diagnostics, while keeping hidden successors active for anti-revival decisions.
- Full synthetic `unittest` suite: **30 passed** (plus a CLI subprocess repro test), no external network/tools used.
- Exact fixture and report files are public-safe synthetic examples; no private identity/relational/journal content.

## Evidence ceilings

The evaluator's exact-head check compares against *supplied* heads; it does not independently authenticate GitHub, Supabase, provider receipt, or model identity. `independently_authenticated=false` always. Supabase live project metadata is real but does not mean any memory retrieval, admission, repair, release, or installation happened.

## Risk

Biggest correctness failure: an archived or stale record, a forged Bus reviewer, or a model-generated memory claim being promoted to current authority. Biggest cost failure: repeated global extraction/reindexing and unconstrained candidate/context growth. The prototype uses bounded, localized projection and no paid infrastructure.