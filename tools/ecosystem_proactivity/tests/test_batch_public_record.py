"""Public projection must not leak raw Batch duplicate identifiers."""
from __future__ import annotations

import json
import unittest
from test_engine import sig, ctx
from governor.engine import Action, evaluate


class PublicBatchProjectionTests(unittest.TestCase):
    def test_private_duplicate_id_is_internal_only(self):
        primary = sig(
            signal_id="private-primary-123",
            fingerprint="private-fingerprint-xyz",
            subject="confidential-repo#1",
            contains_private_data=True,
            evidence_refs=("private://record/identified",),
            concrete_next_step="inspect-secret-token",
        )
        duplicate = sig(
            signal_id="private-secret-duplicate-456",
            fingerprint="private-fingerprint-xyz",
            subject="confidential-repo#1",
            contains_private_data=True,
            evidence_refs=("private://record/backup",),
        )
        batch = evaluate([primary, duplicate], ctx())
        self.assertEqual(batch.dropped_duplicate_signal_ids,
                         ("private-secret-duplicate-456",))
        public = batch.public_record()
        # A masked fingerprint still leaks the presence and priority of a
        # private finding. Omit the private decision from the public view.
        self.assertEqual(public["decisions"], [])
        self.assertEqual(public["external_effects"], False)
        self.assertEqual(public["monitor_is_active"], False)
        serial = json.dumps(public)
        for forbidden in (
            "private-secret-duplicate-456",
            "private-primary-123",
            "private-fingerprint-xyz",
            "confidential-repo#1",
            "private://record/",
            "inspect-secret-token",
            "dropped_duplicate_signal_ids",
        ):
            self.assertNotIn(forbidden, serial)

    def test_public_signal_still_has_public_fingerprint(self):
        batch = evaluate([sig()], ctx())
        public = batch.public_record()
        self.assertEqual(public["decisions"][0]["fingerprint"], "risk-1")
        self.assertEqual(public["decisions"][0]["action"], Action.NOTIFY.value)
        self.assertEqual(public["decisions"][0]["effect_authority"], False)
        self.assertEqual(public["decisions"][0]["emitted"], False)

    def test_cross_batch_private_and_public_do_not_cross_expose(self):
        private = sig(signal_id="private-s2", fingerprint="secret-fp",
                      contains_private_data=False, externally_visible=False,
                      subject="person-only-555")
        public = sig(signal_id="s1", fingerprint="public-fp")
        batch = evaluate([private, public], ctx())
        view = batch.public_record()
        visible = json.dumps(view)
        self.assertEqual(len(view["decisions"]), 1)
        self.assertIn("public-fp", visible)
        self.assertNotIn("secret-fp", visible)
        self.assertNotIn("person-only-555", visible)
        self.assertNotIn("private-s2", visible)
        self.assertTrue(view["currentness_source_only"])


if __name__ == "__main__":
    unittest.main()
