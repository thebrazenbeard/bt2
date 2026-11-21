"""Conflicting exact-incident reports must not suppress or elevate by input order."""
from itertools import permutations
import unittest

from test_engine import sig, ctx, HEAD
from governor.engine import Action, evaluate


class ExactIncidentConflictTests(unittest.TestCase):
    def test_unverified_low_and_trusted_high_are_quarantined_both_orders(self):
        high = sig()
        low = sig(signal_id="s2", severity=0, relevance=0, actionability=0,
                  confidence=0, corroborated=False, source_verified_by_evaluator=False)
        one = evaluate([low, high], ctx())
        two = evaluate([high, low], ctx())
        for batch in (one, two):
            self.assertEqual(len(batch.decisions), 1)
            decision = batch.decisions[0]
            self.assertEqual(decision.action, Action.DRAFT)
            self.assertEqual(decision.priority, 0.0)
            self.assertEqual(decision.reasons, ("EXACT_INCIDENT_CONFLICT",))
            self.assertTrue(decision.private_subject)
            self.assertFalse(decision.emitted)
            self.assertFalse(decision.effect_authority)
            self.assertEqual(batch.public_record()["decisions"], [])
            self.assertEqual(batch.dropped_duplicate_signal_ids, ("s2",))
        self.assertEqual(one.decisions, two.decisions)

    def test_trust_membership_difference_alone_is_not_benign_duplicate(self):
        first = sig()
        second = sig(signal_id="s5", evidence_refs=("an independent reporter",))
        # s5 is not present in the context's independently verified IDs.
        for pair in ([first, second], [second, first]):
            batch = evaluate(pair, ctx())
            self.assertEqual(batch.decisions[0].reasons, ("EXACT_INCIDENT_CONFLICT",))
            self.assertEqual(batch.public_record()["decisions"], [])

    def test_privacy_label_conflict_omitted_in_both_projections(self):
        public = sig()
        private = sig(signal_id="s2", externally_visible=False)
        for pair in ([public, private], [private, public]):
            batch = evaluate(pair, ctx())
            self.assertEqual(batch.decisions[0].reasons, ("EXACT_INCIDENT_CONFLICT",))
            self.assertTrue(batch.decisions[0].private_subject)
            self.assertEqual(batch.public_record()["decisions"], [])

    def test_conflicting_public_scores_do_not_publish_untrusted_priorities(self):
        urgent = sig()
        noise = sig(signal_id="s2", severity=1, actionability=0,
                    relevance=0, confidence=0)
        for pair in ([urgent, noise], [noise, urgent]):
            batch = evaluate(pair, ctx())
            self.assertEqual(batch.public_record()["decisions"], [])
            self.assertEqual(batch.decisions[0].priority, 0.0)

    def test_benign_duplicate_ids_with_different_evidence_still_coalesce(self):
        a = sig()
        b = sig(signal_id="s2", evidence_refs=("second observer",))
        for pair in ([a, b], [b, a]):
            batch = evaluate(pair, ctx())
            self.assertEqual(len(batch.decisions), 1)
            self.assertEqual(batch.decisions[0].action, Action.NOTIFY)
            self.assertEqual(batch.dropped_duplicate_signal_ids, ("s2",))
            self.assertEqual(batch.public_record()["decisions"][0]["action"], "notify")

    def test_three_conflicting_reports_have_order_independent_private_hold(self):
        high = sig()
        low = sig(signal_id="s2", severity=0, actionability=0)
        medium = sig(signal_id="s3", severity=2, relevance=2)
        observations = []
        for pair in permutations((high, low, medium)):
            batch = evaluate(pair, ctx())
            self.assertEqual(batch.dropped_duplicate_signal_ids, ("s2", "s3"))
            self.assertEqual(batch.public_record()["decisions"], [])
            self.assertEqual(batch.decisions[0].reasons, ("EXACT_INCIDENT_CONFLICT",))
            observations.append(batch.decisions[0])
        self.assertTrue(all(x == observations[0] for x in observations))

    def test_distinct_incident_with_same_fingerprint_keeps_prior_collision_hold(self):
        a = sig()
        b = sig(signal_id="s2", subject="another-repo")
        batch = evaluate([a, b], ctx())
        self.assertEqual(len(batch.decisions), 2)
        self.assertTrue(all("FINGERPRINT_COLLISION" in d.reasons for d in batch.decisions))
        self.assertTrue(all(d.action != Action.NOTIFY for d in batch.decisions))


if __name__ == "__main__":
    unittest.main()
