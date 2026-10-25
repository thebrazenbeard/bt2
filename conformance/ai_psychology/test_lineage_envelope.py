"""Inert source-only correlation tests; never evaluate real action success."""

from dataclasses import replace
import unittest

from lineage_envelope import (
    CandidateTrace,
    CurrentGoalBinding,
    ForwardTrace,
    InertLineageIndex,
    correlate_candidate,
)


def forward(**changes):
    return replace(
        ForwardTrace(
            meso_source_event_id="meso-1",
            signal_event_id="signal-1",
            goal_id="goal-2",
            choice_id="choice-2",
            target_id="rest",
        ),
        **changes,
    )


def candidate(**changes):
    return replace(
        CandidateTrace(
            candidate_event_id="candidate-1",
            need_id="need-rest-claim",
            goal_id="goal-2",
            action_request_id="request-2",
            claimed_outcome="SUCCESS",
            claimed_need_change=0.8,
            state="CANDIDATE",
            source_kind="observer",
            source_actor_id="source-observer-unverified",
            source_revision="observer-raw-rev",
            evidence_ref="claim://observation-1",
            evidence_sha256="a" * 64,
            observed_at=100,
            expires_at=140,
        ),
        **changes,
    )


def current(**changes):
    return replace(
        CurrentGoalBinding(
            goal_id="goal-2",
            choice_id="choice-2",
            target_id="rest",
            signal_event_id="signal-1",
        ),
        **changes,
    )


class LineageEnvelopeTests(unittest.TestCase):
    def test_structural_match_is_still_untrusted_and_non_effectful(self):
        result = correlate_candidate(forward(), candidate(), current(), now=110)
        self.assertEqual(result.status, "CORRELATED_UNVERIFIED")
        self.assertEqual(result.reason, "CLAIMED_LINEAGE_ONLY")
        self.assertEqual(result.need_id_claim, "need-rest-claim")
        self.assertEqual(result.authorization_effect, "NONE")
        self.assertFalse(result.may_complete_goal)
        self.assertFalse(result.may_update_need)
        self.assertFalse(result.need_id_is_attested)
        self.assertFalse(result.candidate_choice_link_verified)
        self.assertFalse(result.source_receipts_authenticated)
        self.assertFalse(result.evidence_admitted)
        self.assertFalse(result.action_effect_verified)
        self.assertFalse(result.absolute_need_observation_admitted)

    def test_model_self_report_cannot_enter_even_structural_match(self):
        result = correlate_candidate(
            forward(), candidate(source_kind="model_generated"), current(), now=110
        )
        self.assertEqual((result.status, result.reason), ("HOLD", "MODEL_SELF_REPORT"))
        self.assertFalse(result.may_complete_goal)

    def test_same_target_different_goal_is_not_current_goal(self):
        result = correlate_candidate(
            forward(goal_id="goal-1", choice_id="choice-1"),
            candidate(goal_id="goal-1"),
            current(),
            now=110,
        )
        self.assertEqual((result.status, result.reason), ("HOLD", "STALE_GOAL_INSTANCE"))

    def test_inconsistent_forward_choice_or_signal_is_held(self):
        for change in (
            {"choice_id": "forged-choice"},
            {"signal_event_id": "forged-signal"},
            {"target_id": "forged-target"},
        ):
            with self.subTest(change=change):
                result = correlate_candidate(forward(**change), candidate(), current(), now=110)
                self.assertEqual(result.status, "HOLD")

    def test_cross_goal_candidate_and_rejected_candidate_are_held(self):
        for changes in ({"goal_id": "old-goal"}, {"state": "REJECTED"}):
            with self.subTest(changes=changes):
                result = correlate_candidate(forward(), candidate(**changes), current(), now=110)
                self.assertEqual(result.status, "HOLD")

    def test_future_stale_or_expired_candidate_is_held(self):
        for now in (99, 140, 10**1000):
            with self.subTest(now=now):
                if now == 10**1000:
                    with self.assertRaises(ValueError):
                        correlate_candidate(forward(), candidate(), current(), now=now)
                else:
                    self.assertEqual(
                        correlate_candidate(forward(), candidate(), current(), now=now).status,
                        "HOLD",
                    )

    def test_fake_digest_shape_and_bool_clock_rejected(self):
        with self.assertRaises(ValueError):
            candidate(evidence_sha256="not-a-digest")
        with self.assertRaises(ValueError):
            candidate(observed_at=True)
        with self.assertRaises(ValueError):
            candidate(observed_at=float("nan"))
        for invalid in (True, float("nan"), 2, -2):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                candidate(claimed_need_change=invalid)
        with self.assertRaises(ValueError):
            candidate(schema_version=2)
        with self.assertRaises(ValueError):
            candidate(claimed_outcome="UNKNOWN", claimed_need_change=0.8)

    def test_replay_is_inert_and_conflicting_event_is_held(self):
        index = InertLineageIndex()
        result = correlate_candidate(forward(), candidate(), current(), now=110)
        first = index.record(result)
        second = index.record(result)
        self.assertEqual(first.status, "CORRELATED_UNVERIFIED")
        self.assertEqual(second.status, "DUPLICATE_UNVERIFIED")
        other = correlate_candidate(
            forward(), candidate(evidence_sha256="b" * 64), current(), now=110
        )
        conflict = index.record(other)
        self.assertEqual((conflict.status, conflict.reason), ("HOLD", "CONFLICTING_CANDIDATE_ID"))
        self.assertEqual(index.count(), 1)

    def test_exact_v1_claim_mutation_cannot_evict_immutable_event(self):
        initial = correlate_candidate(forward(), candidate(), current(), now=110)
        for changed in (
            {"claimed_need_change": 0.3},
            {"source_actor_id": "other-actor"},
            {"source_revision": "other-revision"},
        ):
            with self.subTest(changed=changed):
                index = InertLineageIndex()
                index.record(initial)
                revised = correlate_candidate(forward(), candidate(**changed), current(), now=110)
                self.assertNotEqual(initial.correlation_sha256, revised.correlation_sha256)
                self.assertEqual(index.record(revised).reason, "CONFLICTING_CANDIDATE_ID")

    def test_hold_event_identity_cannot_be_retried_as_success(self):
        index = InertLineageIndex()
        rejected = correlate_candidate(
            forward(), candidate(source_kind="model_generated"), current(), now=110
        )
        self.assertEqual(index.record(rejected).status, "HOLD")
        altered = correlate_candidate(forward(), candidate(), current(), now=110)
        conflict = index.record(altered)
        self.assertEqual((conflict.status, conflict.reason), ("HOLD", "CONFLICTING_CANDIDATE_ID"))
        self.assertEqual(index.record(rejected), rejected)
        self.assertEqual(index.count(), 1)

    def test_protected_authority_flags_cannot_be_set_by_constructor(self):
        result = correlate_candidate(forward(), candidate(), current(), now=110)
        with self.assertRaises((AttributeError, TypeError)):
            result.may_complete_goal = True
        with self.assertRaises(TypeError):
            replace(result, may_update_need=True)

    def test_index_reset_does_not_claim_crash_safe_replay(self):
        first = InertLineageIndex()
        result = correlate_candidate(forward(), candidate(), current(), now=110)
        first.record(result)
        new_process = InertLineageIndex()
        self.assertEqual(new_process.count(), 0)
        self.assertEqual(new_process.record(result).status, "CORRELATED_UNVERIFIED")
        self.assertFalse(new_process.is_durable)


if __name__ == "__main__":
    unittest.main()
