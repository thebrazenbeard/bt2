"""Malformed Context membership types must not impersonate trusted policy sets."""
from __future__ import annotations

import unittest
from test_engine import sig, ctx, HEAD
from governor.engine import Action, Context, decide_one


class ContextTrustTypes(unittest.TestCase):
    def test_string_trust_claims_cannot_promote_notification(self):
        # On the vulnerable source, Python uses substring membership; both
        # strings satisfy the trusted-ID and owner-lane checks.
        with self.assertRaises(ValueError):
            ctx(verified_signal_ids="s1", owner_lanes="SECURITY")

    def test_each_trusted_membership_field_rejects_text_and_mutable_collections(self):
        data = {
            "verified_signal_ids": ("s1",),
            "owner_lanes": ("SECURITY",),
            "qualified_capabilities": ("release-qualified",),
            "verified_head_bindings": (("test-repo#1", HEAD),),
            "known_observations": (("risk-1", "test-repo#1", HEAD),),
            "trusted_owner_ack_keys": (("risk-1", "test-repo#1", HEAD),),
            "muted_domains": ("security",),
        }
        for field, values in data.items():
            with self.subTest(field=field, kind="tuple"):
                with self.assertRaises(ValueError):
                    ctx(**{field: values})
            with self.subTest(field=field, kind="string"):
                with self.assertRaises(ValueError):
                    ctx(**{field: values[0] if field in ("verified_signal_ids", "owner_lanes",
                                                        "qualified_capabilities", "muted_domains")
                           else "trusted-string"})

    def test_mixed_type_member_rejected_before_any_decision(self):
        for field, good in (
            ("verified_signal_ids", "s1"), ("owner_lanes", "SECURITY"),
            ("qualified_capabilities", "release-qualified"),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    ctx(**{field: frozenset((good, 1))})

    def test_history_and_feedback_require_exact_outer_tuple(self):
        for field, entries in (
            ("notification_log", (("risk-1", "test-repo#1", HEAD,
                                   "2026-11-20T22:00:00+00:00"),)),
            ("feedback", (("risk-1", "test-repo#1", HEAD, "NOISY"),)),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    ctx(**{field: list(entries)})

    def test_numeric_policy_limits_reject_booleans(self):
        with self.assertRaises(ValueError):
            ctx(daily_notification_limit=True)
        with self.assertRaises(ValueError):
            ctx(same_subject_cooldown_hours=True)

    def test_explicit_frozenset_trust_still_proposes_only(self):
        decision = decide_one(sig(), ctx())
        self.assertEqual(decision.action, Action.NOTIFY)
        self.assertFalse(decision.effect_authority)
        self.assertFalse(decision.emitted)
        self.assertFalse(decision.source_authenticity_verified)


if __name__ == "__main__":
    unittest.main()
