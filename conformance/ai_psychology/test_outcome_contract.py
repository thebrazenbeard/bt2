"""Conformance vectors for a proposed drive-feedback contract, not an E2E test."""

from dataclasses import replace
from threading import Event, Thread
import unittest

from outcome_contract import (
    InMemoryContractOracle,
    NeedSnapshot,
    OutcomeClaim,
    RUNTIME_INTEGRATION_STATUS,
    WitnessedMeasurement,
)


def claim(**changes):
    return replace(
        OutcomeClaim(
            event_id="event-1",
            attempt_id="attempt-1",
            need_id="resource-1",
            goal_id="goal-1",
            expected_revision=4,
            asserted_status="SUCCESS",
            evidence_ref="witness-record-1",
            observed_at=100,
            expires_at=150,
        ),
        **changes,
    )


def witness(**changes):
    return replace(
        WitnessedMeasurement(
            event_id="event-1",
            attempt_id="attempt-1",
            need_id="resource-1",
            goal_id="goal-1",
            evidence_ref="witness-record-1",
            measured_level=0.7,
            observer_id="external-fixture",
            measured_at=105,
        ),
        **changes,
    )


def oracle(verifier=None, *, trusted_observers=frozenset({"external-fixture"})):
    return InMemoryContractOracle(
        NeedSnapshot("resource-1", "goal-1", 4, 0.2, 0.8),
        verifier=verifier,
        trusted_observers=trusted_observers,
    )


class OutcomeContractAdversarialTests(unittest.TestCase):
    def test_unverified_model_success_is_held(self):
        contract = oracle()
        self.assertEqual(contract.admit(claim(), now=110).reason, "NO_INDEPENDENT_VERIFIER")
        self.assertEqual(contract.admit(claim(), now=111).status, "HOLD")
        self.assertEqual(contract.snapshot.revision, 4)

    def test_external_witness_applies_exactly_one_delta(self):
        contract = oracle(verifier=lambda event: witness())
        result = contract.admit(claim(), now=110)
        self.assertEqual((result.status, result.snapshot.revision), ("APPLIED", 5))
        self.assertAlmostEqual(result.measured_improvement, 0.5)
        self.assertEqual(contract.admit(claim(), now=111).status, "REPLAY")
        self.assertEqual(contract.snapshot.revision, 5)

    def test_same_event_id_conflicting_payload_cannot_reapply(self):
        contract = oracle(verifier=lambda event: witness())
        contract.admit(claim(), now=110)
        result = contract.admit(claim(attempt_id="attempt-forged"), now=110)
        self.assertEqual(result.reason, "CONFLICTING_EVENT_ID")
        self.assertEqual(contract.snapshot.revision, 5)

    def test_stale_revision_is_held(self):
        contract = oracle(verifier=lambda event: witness())
        result = contract.admit(claim(expected_revision=3), now=110)
        self.assertEqual(result.reason, "STALE_NEED_REVISION")
        self.assertEqual(contract.snapshot.revision, 4)

    def test_cross_goal_or_need_is_held(self):
        for change in (dict(goal_id="other-goal"), dict(need_id="other-need")):
            with self.subTest(change=change):
                contract = oracle(verifier=lambda event: witness())
                result = contract.admit(claim(**change), now=110)
                self.assertEqual(result.reason, "CROSS_NEED_OR_GOAL")
                self.assertEqual(contract.snapshot.revision, 4)

    def test_failed_noop_unknown_do_not_satiate(self):
        for status in ("FAILED", "NO_OP", "UNKNOWN"):
            with self.subTest(status=status):
                contract = oracle(verifier=lambda event: witness())
                result = contract.admit(claim(asserted_status=status), now=110)
                self.assertEqual(result.reason, "NO_VERIFIED_EFFECT")
                self.assertEqual(contract.snapshot.revision, 4)

    def test_stale_future_and_expired_measurement_are_held(self):
        for stamp in (99, 151):
            with self.subTest(stamp=stamp):
                contract = oracle(verifier=lambda event: witness())
                self.assertEqual(
                    contract.admit(claim(), now=stamp).reason,
                    "OUTSIDE_OBSERVATION_WINDOW",
                )
        contract = oracle(verifier=lambda event: witness(measured_at=120))
        self.assertEqual(contract.admit(claim(), now=110).reason, "WITNESS_TIME_MISMATCH")

    def test_forged_or_mismatched_witness_is_held(self):
        for change in (
            dict(event_id="forged-event"),
            dict(attempt_id="forged-attempt"),
            dict(need_id="forged-need"),
            dict(goal_id="forged-goal"),
            dict(evidence_ref="forged-evidence"),
        ):
            with self.subTest(change=change):
                contract = oracle(verifier=lambda event: witness(**change))
                self.assertEqual(contract.admit(claim(), now=110).reason, "WITNESS_BINDING_MISMATCH")
                self.assertEqual(contract.snapshot.revision, 4)

    def test_no_observed_improvement_does_not_complete(self):
        for level in (0.2, 0.0):
            with self.subTest(level=level):
                contract = oracle(verifier=lambda event: witness(measured_level=level))
                self.assertEqual(contract.admit(claim(), now=110).reason, "NO_MEASURED_NEED_IMPROVEMENT")
                self.assertEqual(contract.snapshot.revision, 4)

    def test_false_or_nonfinite_level_rejected(self):
        for bad in (False, float("nan"), float("inf"), -0.1, 1.1, 10**1000):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    replace(witness(), measured_level=bad)

    def test_unbounded_claim_timestamps_fail_with_validation_error(self):
        for field in ("observed_at", "expires_at"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    claim(**{field: 10**1000})
        with self.assertRaises(ValueError):
            oracle().admit(claim(), now=10**1000)

    def test_new_event_at_old_revision_cannot_double_apply(self):
        contract = oracle(verifier=lambda event: replace(witness(), event_id=event.event_id, evidence_ref=event.evidence_ref))
        self.assertEqual(contract.admit(claim(), now=110).status, "APPLIED")
        stale_new_event = claim(event_id="event-2", attempt_id="attempt-2", evidence_ref="witness-record-2")
        self.assertEqual(contract.admit(stale_new_event, now=111).reason, "STALE_NEED_REVISION")
        self.assertEqual(contract.snapshot.revision, 5)

    def test_two_event_ids_for_one_attempt_or_evidence_are_held(self):
        for alteration in (
            dict(event_id="event-2", expected_revision=5, evidence_ref="different-evidence"),
            dict(event_id="event-2", expected_revision=5, attempt_id="different-attempt"),
        ):
            with self.subTest(alteration=alteration):
                contract = oracle(verifier=lambda event: witness(
                    event_id=event.event_id,
                    attempt_id=event.attempt_id,
                    evidence_ref=event.evidence_ref,
                    measured_level=0.8,
                ))
                self.assertEqual(contract.admit(claim(), now=110).status, "APPLIED")
                second = contract.admit(claim(**alteration), now=111)
                self.assertEqual(second.reason, "DUPLICATE_ATTEMPT_OR_EVIDENCE")
                self.assertEqual(contract.snapshot.revision, 5)

    def test_new_goal_with_same_need_is_not_the_old_goal(self):
        contract = oracle(verifier=lambda event: witness())
        self.assertEqual(contract.admit(claim(goal_id="replacement-goal"), now=110).reason, "CROSS_NEED_OR_GOAL")
        self.assertEqual(contract.snapshot.revision, 4)

    def test_observer_not_on_separately_configured_allowlist_is_held(self):
        contract = oracle(verifier=lambda event: witness(observer_id="self-described-model"))
        self.assertEqual(contract.admit(claim(), now=110).reason, "UNTRUSTED_OBSERVER")
        self.assertEqual(contract.snapshot.revision, 4)

    def test_need_revision_cannot_aba_after_observed_change(self):
        contract = oracle(verifier=lambda event: witness(
            event_id=event.event_id,
            attempt_id=event.attempt_id,
            evidence_ref=event.evidence_ref,
        ))
        self.assertEqual(contract.admit(claim(), now=110).status, "APPLIED")
        # Even if a later reading happens to equal an earlier level, a stale
        # claim bound to revision 4 may not alias the new revision 5.
        stale = claim(event_id="event-3", attempt_id="attempt-3", evidence_ref="evidence-3")
        self.assertEqual(contract.admit(stale, now=111).reason, "STALE_NEED_REVISION")

    def test_concurrent_revision_competitors_cannot_both_apply(self):
        first_entered_verifier = Event()
        second_attempt_started = Event()
        second_entered_verifier = Event()
        release_first = Event()
        results = []

        def verified(event):
            if event.event_id == "event-1":
                first_entered_verifier.set()
                if not release_first.wait(timeout=2):
                    raise AssertionError("concurrency fixture timed out")
            else:
                second_entered_verifier.set()
            return witness(
                event_id=event.event_id,
                attempt_id=event.attempt_id,
                evidence_ref=event.evidence_ref,
            )

        contract = oracle(verifier=verified)
        competing = claim(
            event_id="event-2",
            attempt_id="attempt-2",
            evidence_ref="witness-record-2",
        )

        def apply(event):
            if event.event_id == "event-2":
                second_attempt_started.set()
            results.append(contract.admit(event, now=110))

        first = Thread(target=apply, args=(claim(),))
        second = Thread(target=apply, args=(competing,))
        first.start()
        self.assertTrue(first_entered_verifier.wait(timeout=2))
        second.start()
        self.assertTrue(second_attempt_started.wait(timeout=2))
        # A second verifier must NOT begin while the first revision's
        # commitment is unresolved. Without the admission lock this event is
        # set before release_first and the test fails (real race falsifier).
        try:
            self.assertFalse(second_entered_verifier.wait(timeout=0.2))
            self.assertTrue(second.is_alive())
        finally:
            release_first.set()
        first.join(timeout=2)
        second.join(timeout=2)
        self.assertFalse(first.is_alive() or second.is_alive())
        self.assertEqual(sorted(result.status for result in results), ["APPLIED", "HOLD"])
        self.assertEqual(contract.snapshot.revision, 5)

    def test_reentrant_verifier_cannot_apply_competing_revision(self):
        competing = claim(
            event_id="event-2", attempt_id="attempt-2", evidence_ref="witness-record-2"
        )
        nested = []

        def verified(event):
            if event.event_id == "event-1":
                nested.append(contract.admit(competing, now=110))
            return witness(
                event_id=event.event_id,
                attempt_id=event.attempt_id,
                evidence_ref=event.evidence_ref,
                measured_level=0.7 if event.event_id == "event-1" else 0.4,
            )

        contract = oracle(verifier=verified)
        outer = contract.admit(claim(), now=110)
        self.assertEqual((outer.status, outer.snapshot.revision), ("APPLIED", 5))
        self.assertEqual(len(nested), 1)
        self.assertEqual((nested[0].status, nested[0].reason), ("HOLD", "REENTRANT_ADMISSION"))
        self.assertEqual(contract.snapshot.revision, 5)

    def test_reentrant_verifier_cannot_admit_same_event_twice(self):
        nested = []

        def verified(event):
            if not nested:
                # One guarded recursion avoids an unbounded recursion in the
                # prior implementation while still exposing double-apply.
                nested.append("entered")
                nested[0] = contract.admit(event, now=110)
            return witness()

        contract = oracle(verifier=verified)
        outer = contract.admit(claim(), now=110)
        self.assertEqual((outer.status, outer.snapshot.revision), ("APPLIED", 5))
        self.assertEqual((nested[0].status, nested[0].reason), ("HOLD", "REENTRANT_ADMISSION"))
        self.assertEqual(contract.snapshot.revision, 5)

    def test_verifier_exception_does_not_poison_future_admission(self):
        calls = []

        def verified(event):
            calls.append(event.event_id)
            if len(calls) == 1:
                raise RuntimeError("temporary verifier fault")
            return witness(
                event_id=event.event_id,
                attempt_id=event.attempt_id,
                evidence_ref=event.evidence_ref,
            )

        contract = oracle(verifier=verified)
        with self.assertRaisesRegex(RuntimeError, "temporary verifier fault"):
            contract.admit(claim(), now=110)
        # Recover the local admission guard on a distinct test claim; this
        # does not authorize retrying an ambiguous real-world effect.
        fresh = claim(event_id="event-2", attempt_id="attempt-2", evidence_ref="witness-record-2")
        self.assertEqual(contract.admit(fresh, now=111).status, "APPLIED")
        self.assertEqual(contract.snapshot.revision, 5)

    @unittest.expectedFailure
    def test_process_restart_preserves_replay_receipt(self):
        # Expected RED: volatile in-memory oracle cannot restore an outcome
        # journal or give deterministic replay receipts after restart.
        first = oracle(verifier=lambda event: witness())
        self.assertEqual(first.admit(claim(), now=110).status, "APPLIED")
        restarted = InMemoryContractOracle(first.snapshot, verifier=lambda event: witness(), trusted_observers=frozenset({"external-fixture"}))
        self.assertEqual(restarted.admit(claim(), now=111).status, "REPLAY")

    @unittest.skip("no durable MESO/Volition transaction exists in this source-only fixture")
    def test_meso_and_volition_transition_commit_atomically_after_crash(self):
        # Expected RED: this fixture has no MESO or Volition runtime journal,
        # so an interrupted two-module update cannot be qualified.
        self.assertEqual(RUNTIME_INTEGRATION_STATUS, "ATOMIC_CROSS_MODULE_TRANSITION_VERIFIED")

    @unittest.skip("no installed MESO/Volition/Pre-Active feedback adapter exists")
    def test_real_cross_repo_verified_outcome_transition_remains_unwired(self):
        # Expected RED: the local contract oracle is not a MESO/Volition/
        # Pre-Active runtime adapter and does not close the real feedback loop.
        self.assertEqual(RUNTIME_INTEGRATION_STATUS, "WIRED_AND_RUNTIME_VERIFIED")


if __name__ == "__main__":
    unittest.main()
