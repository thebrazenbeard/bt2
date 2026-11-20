"""V4 subject-bound history contract. Untrusted legacy fingerprint-only history is rejected."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governor.engine import Action, decide_one, evaluate, measure
from test_engine import ctx, sig, HEAD

NOW = "2026-11-20T22:00:00+00:00"
KEY = ("risk-1", "test-repo#1", HEAD)
BOTH=frozenset({("test-repo#1",HEAD),("independent-repo#2",HEAD)})

class SubjectHistoryTests(unittest.TestCase):
    def test_same_subject_prior_notification_suppresses(self):
        d=decide_one(sig(),ctx(notification_log=(((*KEY, NOW)),)))
        self.assertEqual(d.action,Action.SILENT)

    def test_other_subject_prior_notification_not_suppressed(self):
        d=decide_one(sig(subject="independent-repo#2"),ctx(
            daily_notification_limit=2, verified_head_bindings=BOTH,
            notification_log=(((*KEY, NOW)),)))
        self.assertEqual(d.action,Action.NOTIFY)

    def test_same_subject_known_observation_suppresses(self):
        d=decide_one(sig(),ctx(known_observations=frozenset({KEY})))
        self.assertEqual(d.action,Action.SILENT)

    def test_other_subject_known_observation_does_not_suppress(self):
        d=decide_one(sig(subject="independent-repo#2"),
                     ctx(known_observations=frozenset({KEY}), verified_head_bindings=BOTH))
        self.assertEqual(d.action,Action.NOTIFY)

    def test_owner_ack_bound_to_subject_and_head(self):
        c=ctx(trusted_owner_ack_keys=frozenset({KEY}), verified_head_bindings=BOTH)
        self.assertEqual(decide_one(sig(),c).action, Action.DRAFT)
        self.assertEqual(decide_one(sig(subject="independent-repo#2"),c).action,Action.NOTIFY)

    def test_noise_feedback_bound_to_subject_and_head(self):
        c=ctx(feedback=((*KEY,"NOISY"),), verified_head_bindings=BOTH)
        self.assertEqual(decide_one(sig(),c).action,Action.DRAFT)
        self.assertEqual(decide_one(sig(subject="independent-repo#2"),c).action,Action.NOTIFY)

    def test_legacy_notification_log_rejected_not_silently_admitted(self):
        with self.assertRaises(ValueError):
            ctx(notification_log=(("risk-1", HEAD, NOW),))

    def test_legacy_known_observation_rejected(self):
        with self.assertRaises(ValueError):
            ctx(known_observations=frozenset({("risk-1",HEAD)}))

    def test_legacy_feedback_rejected(self):
        with self.assertRaises(ValueError):
            ctx(feedback=(("risk-1","NOISY"),))

    def test_legacy_fingerprint_ack_rejected(self):
        with self.assertRaises(TypeError):
            ctx(trusted_owner_ack_fingerprints=frozenset({"risk-1"}))


    def test_metrics_never_merge_ground_truth_across_subjects(self):
        first=sig(signal_id="s1",subject="test-repo#1")
        second=sig(signal_id="s2",subject="independent-repo#2")
        result=evaluate([first,second],ctx())
        truth={
            ("risk-1","test-repo#1",HEAD):"draft",
            ("risk-1","independent-repo#2",HEAD):"stay_silent",
        }
        metrics=measure(result.decisions,truth)
        self.assertEqual(metrics["total"],2)
        self.assertEqual(metrics["agreement_rate"],0.5)
        self.assertFalse(metrics["independent_ground_truth"])

    def test_head_change_does_not_inherit_old_ack_or_noise(self):
        c=ctx(
            verified_head_bindings=frozenset({("test-repo#1",HEAD),("test-repo#1","b"*40)}),
            trusted_owner_ack_keys=frozenset({KEY}),
            feedback=((*KEY,"NOISY"),),
        )
        d=decide_one(sig(exact_head="b"*40),c)
        self.assertEqual(d.action,Action.NOTIFY)
