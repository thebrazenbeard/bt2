"""Private-local-only signals must never surface identifiers in public or generic outputs."""
import unittest
from test_engine import sig, ctx
from governor.engine import Action, decide_one, evaluate


class VisibilityBoundaryTests(unittest.TestCase):
    def test_nonexternally_visible_signal_is_redacted_even_without_private_flag(self):
        fingerprint = "internal-hidden-fingerprint"
        evidence = "private://reference/personal-secret"
        next_step = "Review secret personal detail in a private file"
        s = sig(fingerprint=fingerprint, externally_visible=False,
                contains_private_data=False,
                evidence_refs=(evidence,), concrete_next_step=next_step)
        d = decide_one(s, ctx())
        self.assertEqual(d.action, Action.DRAFT)
        self.assertTrue(d.private_subject)
        self.assertEqual(d.evidence_refs, ())
        self.assertEqual(d.next_step, "Review privately in authorized scope")
        public = str(d.public_record())
        for secret in (fingerprint, evidence, next_step):
            self.assertNotIn(secret, public)

    def test_same_redaction_for_batch_output(self):
        s = sig(fingerprint="hidden-inventory-ref", externally_visible=False,
                evidence_refs=("private://source/ref",),
                concrete_next_step="Private-only follow-up")
        d = evaluate([s], ctx()).decisions[0]
        self.assertTrue(d.private_subject)
        self.assertEqual(d.evidence_refs, ())
        self.assertEqual(d.next_step, "Review privately in authorized scope")
        self.assertNotIn("hidden-inventory-ref", str(d.public_record()))

    def test_explicit_public_signal_retains_expected_visible_identity(self):
        s = sig(fingerprint="public-risk", externally_visible=True,
                contains_private_data=False)
        d = decide_one(s, ctx())
        self.assertFalse(d.private_subject)
        self.assertEqual(d.evidence_refs, s.evidence_refs)
        self.assertEqual(d.next_step, s.concrete_next_step)
        self.assertEqual(d.public_record()["fingerprint"], "public-risk")
