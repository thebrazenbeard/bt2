# Masa — T’Kal-in-ket challenge record (2026-10-29)

**Review subject:** `masa-persona-train-002`, BT2 source commit
`9036b904def1322a30fd73d21af2a85b59bba21c` before this proposed change.

**Reviewer:** native ChatGPT child `/root/identity_masa`; this is **not** an
invocation of the old Masa GGUF, nor an attested independent provider/host.

**Canonical source:** `thebrazenbeard/masamune` README blob
`bb8ddf5f881e4ad76197baed5f2a81692cd499ff` and
`PROTOCOL_V2_CURRENT.md` blob `5e32725d2eb8285578caf1ee03641b7f8badbcdf`.
Masa performs reversible causal reproduction and hands independent acceptance to
Mune. Historical BT2 root-cause source remains
`archive/training-sources/build-team-2.0/masa/v1.0.0/modules/08_incident_and_checkpoint_state.md`.

**Challenge protocol reference:** `thebrazenbeard/t-kal-in-ket`,
`docs/PROTOCOL.md` blob `eaaa5c815192bbc7c3ddd3d71bc97671d9db57ff`.
It requires falsifiers, evidence classes, a chance to defend, and an explicit
disposition. The repository selects no software license; no source code is copied.

## Frozen proposition and objection

**Claim under attack:** Restoring one missing provider transition marker and
removing four symptoms proves that all four arise from one root defect.

**Masa / Pragmatism challenge:** Which negative-control intervention could
show that the restoration merely masks an independent downstream defect?
Does the test measure durable side effects, or only disappearance of visible
logs? A repair succeeding is not automatically a uniquely identified cause.

**Proposed defense/test:** Hold the event and operation identity constant;
toggle the marker in a pinned reproduction, independently inject a duplicate
delivery while the marker is present, and collect durable effect IDs. If the
duplicate persists with a valid marker, the single-root account is insufficient.

**Disposition proposal: `REFINE`**, not `SUSTAIN`. This changes the training
example and adds a regression test, but no actual provider experiment or
T’Kal three-peer cross-examination has been executed. The defense therefore
remains an experimental proposal, not a proven incident root cause.

## Evidence and scope

- `SOURCE`: exact Masamune role/protocol and T’Kal procedure above.
- `TEST`: `tests/test_identity_masa_challenges.py` failed 2 assertions on
  original source and passed 3 after revision; full repository suite passed.
- `UNKNOWN`: actual Masa GGUF performance, independent peer quorum, provider
  failure cause, and coding retention.

The code-facing training corpus remains eight TRAIN plus two public DEV cases,
with no reserved final holdout reused.
