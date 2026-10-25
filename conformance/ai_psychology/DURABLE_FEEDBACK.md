# Durable feedback: deliberately local qualification fixture

Coordination: `bt2_coordination_ai_psychology` / [BT2 #61](https://github.com/thebrazenbeard/bt2/issues/61).

`durable_feedback.py` is a **source-only SQLite qualification fixture** for a
possible future MESO need-state / Volition goal-state feedback adapter. It is
not a deployed service, an authenticated witness, an AI emotion, a permission
system, or a runtime integration with MESO, Volition, Pre-Active, or VeraOS.

The test owns and supplies the synthetic `verifier` callback and the allowed
observer names. A value such as `observer_id="independent:fixture"` is **not** a
cryptographic identity or independent physical evidence; a caller can fabricate
it. The callback runs outside SQLite's transaction. Do not invoke a real tool,
credential holder, or remote effect in that callback. The database contains
only fixture state, not the canonical MESO or Volition databases.

## What the tests actually establish

Run from the repository root:

```bash
python -m unittest discover -s conformance/ai_psychology -p 'test_*.py' -v
```

- A separately injected test-witness measurement can advance the local need
  revision and mark the local goal complete in **one SQLite transaction**.
  `synchronous=FULL`, a single atomic transaction and durable receipt rows
  model the crash-consistency shape; no distributed atomic commit is tested.
- An injected abort on the goal-write step rolls back the preceding need write
  and event receipt. A new fixture instance can then retry once successfully.
- Process-reopen same-event replay cannot double-credit. Reminting event,
  attempt, and evidence identifiers with a reused synthetic physical-effect
  identity is denied, even after simulated goal replacement.
- A goal `g1` replaced by `g2` for the same target cannot be completed by a
  late `g1` claim. Revision and choice identifiers are checked. This small
  fixture admits exactly **one** need axis: `goal.target_id` must equal the
  canonical `need.need_id`, including on simulated goal replacement. It cannot
  safely project improvements across distinct target/need identifiers.
- A local protection veto blocks satisfaction even if the test callback
  returns a supposedly beneficial observation. No protected effect API exists.
- Missing or throwing verifiers, self-reports with plausible labels/hashes,
  untrusted observer names, non-improving measurements, stale/invalid fields,
  and conflicting event identities cannot create positive need feedback.

A rejected (`HOLD`) claim permanently reserves **only its event ID**. It does
not globally reserve attacker-asserted attempt/evidence identifiers: doing so
would let unauthenticated claims deny service to later legitimate measurements.
A new event with the same claimed attempt/evidence can therefore be reconsidered
only under the currently bound goal/revisions and an injected test verifier.
**Applied** attempt IDs, evidence refs, and synthetic physical-effect IDs do
have durable uniqueness constraints, so a reminted already-applied effect
cannot be counted again. In production, real observer custody would determine
which attempt/evidence identities are genuine in the first place.

The explicit result code `INJECTED_TEST_WITNESS_ACCEPTED` is scoped to this
fixture. `DurableFeedbackReceipt.effect_authority` is always `False` and
cannot be assigned through its constructor. `replace_goal()` is an **untrusted
test setup transition**, not a callable Volition goal-adoption authority.

## What remains unproven

1. A real independent sensor or actor with cryptographically/governance-
   qualified identity, calibration, provenance, and evidence custody.
2. Durable cross-repository atomicity, exactly-once effect reconciliation,
   key rotation/consent revocation, and crash recovery of **real** MESO and
   Volition state. This fixture's single SQLite file is not a distributed
   transaction coordinator.
3. The Pre-Active V1 candidate lacks immutable MESO source and Volition choice
   bindings, so structural correlation does not prove causal outcome custody.
4. The SQLite connection is opened per operation; a caller-controlled `now`,
   test-selected verifier, and test-generated `physical_effect_id` are not
   trusted production evidence. No installed DRIVE feedback loop exists.
5. No subjective liking, wanting, satiation, attachment, or sentience is
   established by a green test. Pleasure is not proof of actual need recovery.

Source-of-truth owners should remain MESO (need state), Volition (goal state),
Pre-Active (untrusted candidate ingress), and a separately governed qualified
observer/adjudicator. F.U.C.K.U.P. is a potential durable outbox/reconciliation
donor, not an outcome witness. LGCM may learn only from subsequently admitted
feedback. This fixture neither changes those repos nor grants their rights.

**Status: `UNWIRED_LOCAL_SQLITE_QUALIFICATION_ONLY`.**
