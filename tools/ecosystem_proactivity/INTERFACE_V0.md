# Ecosystem signal proposal interface V0 (coordination candidate)

**Input is an untrusted proposal, not a fact, command, authorization or task.** Engineer B owns adaptation; BT2 owns policy. No renderer, runtime consumer or scheduling process exists. Schema name `ecosystem.signal-proposal/v0` deliberately conveys lack of qualification.

Example structure (synthetic; actual host verifier must re-read sources):

```json
{
  "schema": "ecosystem.signal-proposal/v0",
  "signal_id": "fixture-001",
  "fingerprint": "same-root-cause-family",
  "subject": "example-repo#12",
  "domain": "security",
  "cause": "unexpected-source-change",
  "evidence": [
    {
      "ref": "fixture://example/source-at-known-head",
      "class": "SOURCE_INSPECTION",
      "head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "observed_at": "2026-11-20T19:00:00+00:00"
    }
  ],
  "claimed_owner_lane": "EXAMPLE_OWNER",
  "privacy_class": "PUBLIC_SYNTHETIC",
  "requested_capability": "source-review",
  "source_linkage": "fixture-0001"
}
```

Required host-side mediation (NOT implemented here):

1. Re-read each evidence ref at an exact immutable Git head / CI run ID / signed, authorized provider readback. Verify source and time independently; a 40-character SHA-like string is only a syntactic identifier until fetched.
2. Normalize subjects and root causes; coalesce actual duplicates; if fingerprints conflict across different subjects/heads, quarantine both instead of hiding one.
3. Bind owner assignments through current legitimate writer lanes; actor labels in Bus comments are **not cryptographic identity**.
4. Keep private-source data out of public artifacts. An `evidence_ref` may itself leak data; do not export it without review.
5. Label evidence classes; do not upgrade DOC to TEST, CI to REAL_HOST_PROBE, or source presence to qualified Lantern runtime currentness.
6. Supply separate trusted evaluator context (`verified_signal_ids`, `trusted_owner_ack_fingerprints`, `owner_lanes`) only after real checks, never directly from this proposal.
7. Let BT2 score urgency with measurable impact and feedback. Never permit proposal fields to schedule work or emit notifications.
8. All proposed notification decisions require a separately authorized emitter, currently **absent**.

Owner-specific implementation changes can evolve this contract only through explicit versioning; V0 is not a hard runtime API or an installed plugin.
