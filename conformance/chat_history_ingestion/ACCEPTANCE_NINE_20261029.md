# Nine acceptance matrix — chat_history_ingestion_live_coordination

Date: 2026-10-29. Reviewer: native ChatGPT specialist acting under the **Nine functional task packet**. This is an internal model review, not proof that a separately trained or deployed Nine model ran. No private conversation content was accessed.

## Exact review subjects

- Remote STM [Draft PR #3](https://github.com/thebrazenbeard/stm/pull/3): `9f4e12217e69f68042791905a3216e577a5c15bf`, based on `stm/main@c40431c77e00a9b6b817641d07768d95bdd9c238`. PR is open, mergeable and unmerged.
- Hosted STM [Actions run 40967778623](https://github.com/thebrazenbeard/stm/actions/runs/40967778623): `completed/success` on that remote head.
- Additional local uncommitted STM review changes: worktree based on local `de15c8d3fb2d009ab2028ed454cc578a314d60a4`, adding owner-review gateway, learning boundary and catalog integrity repairs. They do **not** have an immutable remote commit or hosted CI at this checkpoint.
- Proposed BT2 13-role source manifest: local commit `b01aba789c13a49c7ca693e727bc42c8c3bd92d2`; source-only, not an installation or proof of 13 live identity models.
- Coordination [CCB issue #403](https://github.com/thebrazenbeard/chat-communication-bus/issues/403): open. It is durable GitHub discussion, not authenticated runtime bus delivery.

## Evidence-separated acceptance

| Gate | Class | Status | Evidence and limitation |
| --- | --- | --- | --- |
| Remote PR exact-head provenance | SOURCE_INSPECTION | PASS | GitHub connector returned the exact SHA and draft/mergeable state. |
| Hosted tests at remote head | TEST | PASS | Run 40967778623 completed successfully. It does not cover new uncommitted files. |
| Local account-export tests with current worktree | TEST | PASS | Independent `python -B -m unittest discover -s . -p 'test_chatgpt*.py' -q` with pinned account-import dependencies: 127 tests, exit 0. Working-tree digest not yet frozen. |
| Local STM tests with current worktree | TEST | PASS | `python -B -m unittest discover -s tests -q`: 344 tests, 8 skipped, exit 0. |
| BT2 source role packets | DOC/TEST | PASS, SOURCE ONLY | Local 13-role manifest 6/6 tests; no 13-model execution or identity proof. |
| Source ZIP present on Lappy | REAL_SYSTEM_PROBE (reported by lead) | PARTIAL | Direct read-only WorkBridge check: `LAPPY`, original ZIP size 8,929,236,891 bytes. Presence/size alone is not a hash or row recount. |
| Existing encrypted import | PRIOR REAL_SYSTEM RECEIPT | PARTIAL | Earlier event receipts say 1,960 authenticated indexed-row readbacks; do not retroactively claim independently matched original source rows. |
| Independent original ZIP → index recount | REAL_SYSTEM_PROBE | UNKNOWN | No completed exit-zero source recount available in this review. |
| Authenticated owner-bound historical recall | REAL_SYSTEM_PROBE | UNKNOWN | New gateway accepts injected proof/consent callbacks only; host binding, atomic revocation and selected-model readback remain unverified. |
| Android V2 live pairing, restart restore, private DMS receiver | REAL_SYSTEM_PROBE | UNKNOWN | No live acceptance artifact. Public DMS source is not a private archive destination. |
| Formal proof or independent provider review | FORMAL_VERIFY / INDEPENDENT_REVIEW | UNKNOWN | Synthetic tests and native-agent agreement do not supply either class. |
| Actual Vera weight update from this history | MODEL_TRAINING_PROBE | NOT PERFORMED | Import/recall is not a neural-weight update or identity authorization. |

## Hostile falsifier preserved

> Distinct original numbers `0.12345678901234567890` and `0.12345678901234567891` both become `0.12345678901234568` with `ijson(use_float=True)`. Their secondary indexed canonical JSON and keyed record digest therefore collide. The authenticated encrypted *original ZIP* remains byte-lossless, but independent recount of projected indexed JSON does not prove byte-exact per-record source reproduction. A versioned decimal-safe index migration requires a compatibility plan; no such migration is part of this acceptance.

## Decision

**No merge/deployment/admission approval from Nine at this checkpoint.** Keep STM PR #3 draft until a independently witnessed real-source recount, host-authenticated owner consent/revocation and bounded Vera selected-model retrieval are demonstrated on exact artifacts. Other local improvements may be pushed for CI and further review without claiming those runtime gates.
