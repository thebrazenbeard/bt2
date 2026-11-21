"""No internal private Decision classification in public projection or untrusted bridge."""
from __future__ import annotations

import json
import unittest
from test_engine import sig, ctx
from governor.engine import Action, decide_one, evaluate
from governor.untrusted_b_ingress import review_untrusted
from test_untrusted_b_ingress import sample_signal, NOW


class PrivateDecisionProjectionBoundary(unittest.TestCase):
    def test_private_public_record_is_constant_regardless_of_domain_severity_or_action(self):
        first = decide_one(sig(fingerprint="hidden-a", domain="security",
                               contains_private_data=True, severity=5,
                               actionability=5), ctx())
        second = decide_one(sig(fingerprint="hidden-b", domain="memory",
                                externally_visible=False, contains_private_data=False,
                                severity=0, actionability=0, confidence=0), ctx())
        self.assertEqual(first.action, Action.DRAFT)
        self.assertEqual(second.action, Action.SILENT)
        expected = {"redacted": True, "effect_authority": False, "emitted": False}
        self.assertEqual(first.public_record(), expected)
        self.assertEqual(second.public_record(), expected)
        for secret in ("hidden-a", "hidden-b", "security", "memory",
                       "PRIVATE_LOCAL_ONLY", "priority", "domain", "action"):
            self.assertNotIn(secret, json.dumps(first.public_record()))
            self.assertNotIn(secret, json.dumps(second.public_record()))

    def test_public_decision_retains_safe_existing_summary(self):
        dec = decide_one(sig(), ctx())
        self.assertFalse(dec.private_subject)
        summary = dec.public_record()
        self.assertEqual(summary["fingerprint"], "risk-1")
        self.assertEqual(summary["domain"], "security")
        self.assertEqual(summary["action"], "notify")
        self.assertEqual(summary["effect_authority"], False)
        self.assertEqual(summary["emitted"], False)

    def test_untrusted_private_review_action_survives_without_classification_metadata(self):
        output = review_untrusted(sample_signal(), now=NOW)
        self.assertEqual(output["reviewed_count"], 1)
        self.assertEqual(len(output["decisions"]), 1)
        decision = output["decisions"][0]
        self.assertEqual(decision, {"fingerprint": "", "action": "draft"})
        self.assertNotIn("priority", json.dumps(output))
        self.assertNotIn("reason_codes", json.dumps(output))
        self.assertNotIn("domain", json.dumps(output))
        self.assertFalse(output["notifier_active"])

    def test_untrusted_stale_review_remains_silent_and_metadata_free(self):
        output = review_untrusted(sample_signal(), now="2026-12-01T23:30:00+00:00")
        self.assertEqual(output["decisions"],
                         [{"fingerprint": "", "action": "stay_silent"}])

    def test_batch_public_projection_still_omits_private_decisions(self):
        result = evaluate([sig(fingerprint="private-identifier",
                               contains_private_data=True)], ctx())
        self.assertEqual(result.public_record()["decisions"], [])


if __name__ == "__main__":
    unittest.main()
