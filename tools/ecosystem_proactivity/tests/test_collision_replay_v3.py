"""Adversarial regression: duplicate incident keys must not hide independent subjects."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governor.engine import Action, evaluate
from test_engine import sig, ctx, HEAD

class CollisionAfterHistory(unittest.TestCase):
    def test_prior_notification_same_fingerprint_head_quarantines_both_subjects(self):
        first = sig(signal_id="s1", subject="test-repo#1")
        second = sig(signal_id="s2", subject="independent-repo#2")
        context = ctx(notification_log=(("risk-1", "test-repo#1", HEAD, "2026-11-20T22:00:00+00:00"),))
        result = evaluate([first, second], context)
        self.assertEqual(len(result.decisions), 2)
        self.assertTrue(all(d.action == Action.DRAFT for d in result.decisions))
        self.assertTrue(all("FINGERPRINT_COLLISION" in d.reasons for d in result.decisions))
        self.assertTrue(all(not d.emitted for d in result.decisions))

    def test_known_observation_of_one_fingerprint_does_not_hide_distinct_subject(self):
        first = sig(signal_id="s1", subject="test-repo#1")
        second = sig(signal_id="s2", subject="independent-repo#2")
        result = evaluate([first, second], ctx(known_observations=frozenset({("risk-1", "test-repo#1", HEAD)})))
        self.assertEqual(len(result.decisions), 2)
        self.assertTrue(all(d.action == Action.DRAFT for d in result.decisions))
        self.assertTrue(all("FINGERPRINT_COLLISION" in d.reasons for d in result.decisions))

    def test_stale_collision_remains_silent(self):
        first = sig(signal_id="s1", observed_at="2026-11-15T22:00:00+00:00")
        second = sig(signal_id="s2", subject="independent-repo#2",
                     observed_at="2026-11-15T22:00:00+00:00")
        result = evaluate([first, second], ctx())
        self.assertTrue(all(d.action == Action.SILENT for d in result.decisions))
        self.assertTrue(all("STALE_SUBJECT" in d.reasons for d in result.decisions))
