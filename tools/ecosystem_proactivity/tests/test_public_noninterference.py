"""Public batch decisions must not depend on private cross-subject signals."""
from __future__ import annotations

import json
import unittest
from test_engine import ctx, sig
from governor.engine import Action, evaluate


class BatchPublicNoninterference(unittest.TestCase):
    def test_private_different_subject_same_fingerprint_does_not_downgrade_public_signal(self):
        public = sig()
        private = sig(
            signal_id="hidden-event-id",
            subject="private-separate-subject#7",
            fingerprint=public.fingerprint,
            contains_private_data=True,
            evidence_refs=("private://do-not-release",),
        )
        reference = evaluate([public], ctx()).public_record()
        mixed = evaluate([private, public], ctx())
        self.assertEqual(mixed.public_record(), reference)
        self.assertEqual(len(mixed.decisions), 2)
        self.assertTrue(all(d.action == Action.DRAFT for d in mixed.decisions))
        self.assertNotIn("hidden-event-id", json.dumps(mixed.public_record()))
        self.assertNotIn("FINGERPRINT_COLLISION", json.dumps(mixed.public_record()))

    def test_privacy_conflict_same_incident_fail_closed_without_declassification(self):
        public = sig()
        private = sig(
            signal_id="privacy-conflict-1",
            contains_private_data=True,
            evidence_refs=("private://same-incident",),
        )
        for signals in ([private, public], [public, private]):
            with self.subTest(order=[x.signal_id for x in signals]):
                batch = evaluate(signals, ctx())
                self.assertEqual(batch.public_record()["decisions"], [])
                self.assertEqual(len(batch.decisions), 1)
                self.assertEqual(len(batch.dropped_duplicate_signal_ids), 1)

    def test_nonexternal_different_subject_is_independent_of_public_evaluation(self):
        public = sig()
        private = sig(
            signal_id="invisible-2",
            subject="hidden-other-domain#9",
            fingerprint=public.fingerprint,
            contains_private_data=False,
            externally_visible=False,
        )
        reference = evaluate([public],ctx()).public_record()
        for signals in ([private, public],[public, private]):
            with self.subTest(order=[x.signal_id for x in signals]):
                self.assertEqual(evaluate(signals, ctx()).public_record(), reference)

    def test_noncolliding_private_does_not_affect_public_projection(self):
        public = sig()
        private = sig(
            signal_id="private-id-2",
            fingerprint="private-other-fp",
            subject="hidden-other#8",
            contains_private_data=True,
        )
        self.assertEqual(evaluate([private, public], ctx()).public_record(),
                         evaluate([public], ctx()).public_record())


if __name__ == "__main__":
    unittest.main()
