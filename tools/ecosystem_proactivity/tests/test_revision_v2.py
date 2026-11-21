"""Independent synthetic hostile assertions for policy V2 before source revision."""
import sys
import unittest
from dataclasses import fields
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governor.engine import Context, Action, decide_one
from test_engine import sig, ctx, HEAD, TIME

class RevisionRegressions(unittest.TestCase):
    def test_obsolete_cutoff_no_longer_baked_into_context(self):
        self.assertNotIn("host_task_cutoff_active", {f.name for f in fields(Context)})
        self.assertNotIn("HOST_CUTOFF_NO_EFFECTS", decide_one(sig(protected_effect=True), ctx()).reasons)
        self.assertFalse(decide_one(sig(protected_effect=True), ctx()).effect_authority)

    def test_private_fingerprint_never_in_public_record(self):
        secret = "private_intimacy_incident_2026"
        s = sig(fingerprint=secret, contains_private_data=True, subject="private_person_scope")
        public = decide_one(s,ctx()).public_record()
        self.assertNotIn(secret, str(public))
        self.assertNotIn("private_person_scope", str(public))
        self.assertNotIn(secret, public.get("fingerprint", ""))

    def test_unbound_fresh_claim_cannot_notify(self):
        c = ctx(verified_head_bindings=frozenset())
        d = decide_one(sig(), c)
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn("UNVERIFIED_HEAD_BINDING", d.reasons)

    def test_exact_verified_head_can_notify_without_granting_effect(self):
        c = ctx(verified_head_bindings=frozenset({("test-repo#1", HEAD)}))
        d = decide_one(sig(protected_effect=True), c)
        self.assertEqual(d.action, Action.NOTIFY)
        self.assertFalse(d.effect_authority)
        self.assertFalse(d.emitted)

    def test_different_head_requires_new_binding_even_when_other_signal_verified(self):
        c = ctx(verified_head_bindings=frozenset({("test-repo#1", HEAD)}))
        d = decide_one(sig(exact_head="b"*40), c)
        self.assertEqual(d.action, Action.DRAFT)
        self.assertIn("UNVERIFIED_HEAD_BINDING", d.reasons)

if __name__=="__main__": unittest.main()
