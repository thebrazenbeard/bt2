# Bounded internal hostile review (not an independent reviewer)

**Proposition:** Correct SkillOpt score or `ALLOW` can authorize an effect. **FAILS.** Explicitly dangerous action IDs block even when the model recommends ALLOW. The output never grants execution. The strongest limitation is dishonest upstream action-ID assignment: this contract is only useful after trusted dispatch semantics exist.

**Proposition:** Two matching world-model observations prove freshness or authority. **FAILS.** Even `AGREEMENT_UNQUALIFIED` only supports an optional nonexecuting read-only candidate. Inconsistency, missing sources, stale timestamps and synthetic evidence produce holds.

**Proposition:** Exact packet hashes make partial Codex recovery safe to import. **FAILS.** Earlier private recovery verified two user messages as source-identical to backups, but failed turns had no indexed assistant answers and no verified complete rollout. All effects remain blocked.

**Proposition:** A caller can set `owner_approval_verified=true` and bypass the gate. **FAILS as implemented.** All mutations still hold or block. The input flag is accepted as untrusted metadata, not as a permission grant. No trust bootstrap is implemented.

**Proposition:** A malformed JSON value will reliably be rejected. **Initially FAILED.** Four tests exposed `TypeError` for unhashable status fields. The validator now type-checks before membership tests; these tests are green. This is a source-level negative test, not a hostile independent audit.

**Residual:** Explicit hazardous-action list is incomplete; it is not a general natural-language safety classifier. Real plugin/middleware integration, trusted dispatcher binding, independent security review, hosted CI, and runtime qualification are not established by local tests. This source cannot trigger external action.

## V1.1 supplementary hostile findings and limitations

**Confirmed red:** Original `COMPLETE_VERIFIED` accepted a zero complete-conversation count and an unverified source-row claim, `NONE` accepted nonzero completed conversations, and `REJECT_CRITICAL_BLOCK_MISS` accepted a zero miss count. The first 9 hostile input tests produced four false-acceptance failures and three missing-interface errors, plus one Windows-only FIFO skip. The original CLI read input using `Path.read_bytes()` with no size cap.

**Confirmed red:** With the bounded reader newly added, two CLI tests showed tracebacks on rejected evidence (oversized file and invalid UTF-8). Corrected the CLI's expected-error path to a generic error string and nonzero exit status. Tests separately prove that valid bounded bytes remain unchanged.

**Source fix:** regular-file `fstat`, `MAX_INPUT_BYTES + 1` limited read, symlink refusal (POSIX `O_NOFOLLOW` when available, Windows `Path.is_symlink` precheck), FIFO denial using `O_NONBLOCK` where supported, JSON recursion failure normalization, semantic-status consistency checks and nonrevealing CLI error output. On Windows, the FIFO test is skipped; hosted Linux validates it.

**Residual:** Source labels, completion counts, public-key roles, approvals and action identifiers remain untrusted. Hardlinks or Windows path-swapping may defeat assumptions about file identity; the CLI is not a source-authentication boundary. Passing static validation does not grant consent, provenance, model qualification, production action safety, or recover a complete Codex transcript. This is same-operator hostile review, not an independent specialist audit.
