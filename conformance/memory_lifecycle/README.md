# BT2 Memory Lifecycle Conformance V1

**Status:** source-only, synthetic test candidate; no host/runtime or protected-memory integration. Designed to sit beside existing systems, not supersede them.

The records and results use a deterministic JSON interface. This prototype **does not authenticate sources**, grant privileges, write memories, query personal data, or schedule work. Every selected claim retains the status `MATCHES_SUPPLIED_HEAD_UNAUTHENTICATED`; a caller-provided "authenticated" flag is ignored. A trusted native host verifier and governed memory admission operation are separate and not implemented here.

Run without dependencies (Python >=3.11):

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python memory_lifecycle.py fixtures/synthetic_current.json
```

## Reuse map and compatibility ceilings

- `thebrazenbeard/stm` already provides a bounded, exact-session working set, privacy-filtered read grants and correction-version checks. Source: `docs/architecture.md`. It cannot self-authenticate the actor, prove KV reuse, or import the DMS archive as current memory.
- `thebrazenbeard/deepmemorystorage` already preserves historical tranches, provenance amendments and correction overlays. Source: `architecture/DEEP_MEMORY_INTEGRATION_CONTRACT_V1.md`. Historical canonicity and source timestamps are **not** present currentness.
- `thebrazenbeard/vera-mono` already has a SQLite CAS/operation-id ledger for governed revisions, and a separate read-only historical-evidence boundary. Source: `packages/vera_memory/src/vera_memory/{ledger,historical_evidence}.py`. A reference to authority is **not** verified authority.
- `thebrazenbeard/bt2` source state `docs/runtime/CURRENTNESS_BACKEND_STATUS_V1.json` explicitly reports Lantern runtime currentness UNKNOWN. Do not relabel that source file as an active provider.
- Connected Supabase **Vera** project already has `public.vera_memory_epoch_*` tables (RLS) and `semantic_atlas` objects (RLS). Never create a competing current-memory schema or import its private rows for these tests. Supabase **Tattler** is a separate review/webhook project; no automatic copy of Vera's memory schema is justified. `supabase_metadata_probe.sql` is a read-only, metadata-only query. Project-specific migration or permission changes need review and release authorization.
- BT2's separate `signal_ingest` Draft PR #123 produces candidate observations; do not convert its events into authenticated memory without an independently verified admission bridge.

## Representation and extraction

Input shape: `CONTRACT_V1.json` (`BT2_MEMORY_LIFECYCLE_INPUT_V1`). A record uses immutable ID, exact subject/head, explicit `supersedes`, source reference/class, privacy scope, observation time, record time, extraction confidence, TTL, and opaque claimed actor. UTF-8 content is limited to 2 KiB. This system **only consumes supplied extracted candidates**; it does not generate, mine, train, or automatically persist facts. Extraction requires a confidence score and named source. A host should quarantine uncertain/injected candidates and never treat extracted text as instructions.

## Retrieval goal, algorithm, and budgets

Every invocation requires a nonempty `goal.query`, bounded `goal.purpose`, caller-authorized privacy scopes and a caller-supplied `expected_heads` map. Filtering precedes lexical relevance: privacy, expiration, historical-only, injection flags, explicit supersession and exact head matching. Unauthorized records are **not included in rejection diagnostics or structural-head output**; a hidden successor can still invalidate the visible predecessor without disclosing the hidden ID. Relevance is deterministic lexical-token overlap; default threshold **0.4**. Candidate cap **5**, input cap **256**, selected UTF-8 serialized bytes default **800**, max **4096**. Designed target **200 ms**/invocation on a small input, but no actual latency promise: `measured_latency_ms = null` until instrumented. External cost target **$0** because the pure function makes no model/network calls; output `measured_cost_usd = null` until host accounting. Model-token cost is NOT equal to UTF-8 bytes. If empty/stale/conflicted, returns no selected current record; it does not fabricate a replacement.

## Maintenance and stability

No mutation here. Corrections use an explicit linked `supersedes` chain; forks and unrelated contradictory heads result in `null` current structural head. A restatement of an already superseded head cannot revive it merely by changing the record timestamp. Divergent reuse of a record ID is a hard provenance conflict. Original source records stay available for independent historical lookup and audit. There is no global rewrite, automatic condensation, deletion, canonical-memory admission, or learned-weight update. This is a localized projection, not a database migration.

## Source-only evaluation

`RED_LOG.txt` shows the original naive timestamp-based selector failing to reject an old head. `PRIVACY_RED_LOG.txt` records two additional real assertion failures exposing private record IDs and private head projections. `GREEN_LOG.txt` contains both corrected tests plus adversarial cases for privacy, cross-subject edges, forks, duplicate IDs, spoofed reviewers, unsupported runtime claims, prompt-injection, TTL, costs, budgets, and side effects. The suite is a synthetic regression, **not** independent host/runtime proof, continuous memory, or subjective experience.

### Integration requirements (not implemented)

1. An authenticated host must supply **independent** current heads and identity/privacy receipts. A caller-provided `expected_heads` map never suffices for authority.
2. STM, DMS and vera-mono owners must independently review adapter translations before wiring the output to any current memory admission API.
3. A current Supabase project owner must approve an exact read-only query or reviewed migration. Do not assume database-admin technical access constitutes authorization to read private content.
4. Record retrieval latency, model-token budget, cost, recall@k, stale-revival count, privacy leaks and update correctness under repeated seeded streams; add independent negative reviewers and sealed evaluation holdouts.
5. Only after source reviews and provider-bound real probes should the separate decision policy consider qualified evidence. This module never grants action authority.