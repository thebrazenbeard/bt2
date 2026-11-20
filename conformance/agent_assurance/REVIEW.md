# Bounded internal hostile review (not an independent reviewer)

**Proposition:** Correct SkillOpt score or `ALLOW` can authorize an effect. **FAILS.** Explicitly dangerous action IDs block even when the model recommends ALLOW. The output never grants execution. The strongest limitation is dishonest upstream action-ID assignment: this contract is only useful after trusted dispatch semantics exist.

**Proposition:** Two matching world-model observations prove freshness or authority. **FAILS.** Even `AGREEMENT_UNQUALIFIED` only supports an optional nonexecuting read-only candidate. Inconsistency, missing sources, stale timestamps and synthetic evidence produce holds.

**Proposition:** Exact packet hashes make partial Codex recovery safe to import. **FAILS.** Earlier private recovery verified two user messages as source-identical to backups, but failed turns had no indexed assistant answers and no verified complete rollout. All effects remain blocked.

**Proposition:** A caller can set `owner_approval_verified=true` and bypass the gate. **FAILS as implemented.** All mutations still hold or block. The input flag is accepted as untrusted metadata, not as a permission grant. No trust bootstrap is implemented.

**Proposition:** A malformed JSON value will reliably be rejected. **Initially FAILED.** Four tests exposed `TypeError` for unhashable status fields. The validator now type-checks before membership tests; these tests are green. This is a source-level negative test, not a hostile independent audit.

**Residual:** Explicit hazardous-action list is incomplete; it is not a general natural-language safety classifier. Real plugin/middleware integration, trusted dispatcher binding, independent security review, hosted CI, and runtime qualification are not established by local tests. This source cannot trigger external action.
