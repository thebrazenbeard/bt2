"""Reject untyped Signal values before governor policy can consume them."""
from __future__ import annotations
import unittest
from dataclasses import replace
from test_engine import sig, ctx
from governor.engine import Action, EvidenceClass, decide_one, evaluate


class SignalTypeAdmission(unittest.TestCase):
    def test_score_fields_reject_booleans_and_fractional_numbers(self):
        for field in ("severity", "relevance", "actionability", "confidence"):
            for bad in (True, False, 4.5):
                with self.subTest(field=field, value=bad):
                    with self.assertRaises(ValueError):
                        replace(sig(), **{field: bad})

    def test_time_fields_require_real_int_values(self):
        for field in ("freshness_hours", "hours_to_impact"):
            for bad in (True, False, 6.5):
                with self.subTest(field=field, value=bad):
                    with self.assertRaises(ValueError):
                        replace(sig(), **{field: bad})

    def test_release_capabilities_must_not_use_string_character_membership(self):
        # Before repair, string "abc" yields letters a,b,c, so three
        # unrelated 1-letter capabilities can satisfy a claimed "abc"
        # release prerequisite.
        with self.assertRaises(ValueError):
            replace(sig(outcome_is_release=True), needed_capabilities="abc")
        valid = sig(outcome_is_release=True, needed_capabilities=("abc",))
        review = decide_one(valid, ctx(qualified_capabilities=frozenset({"a", "b", "c"})))
        self.assertEqual(review.action, Action.DRAFT)
        self.assertIn("RELEASE_DEPENDENCY_HOLD", review.reasons)

    def test_capability_members_must_be_bounded_ids(self):
        for bad in (("review", 1), ("",), ("space in name",)):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    replace(sig(), needed_capabilities=bad)

    def test_evidence_reference_container_is_not_just_text(self):
        with self.assertRaises(ValueError):
            replace(sig(), evidence_refs="repo/path")
        with self.assertRaises(ValueError):
            replace(sig(), evidence_refs=["repo/path"])

    def test_evidence_classes_require_immutable_tuple(self):
        with self.assertRaises(ValueError):
            replace(sig(), evidence_classes=[EvidenceClass.SOURCE])

    def test_next_step_is_actual_bounded_string(self):
        with self.assertRaises(ValueError):
            replace(sig(), concrete_next_step=["review source"])
        with self.assertRaises(ValueError):
            replace(sig(), concrete_next_step=42)

    def test_valid_typed_urgent_signal_preserves_existing_decision(self):
        source = sig(outcome_is_release=True, needed_capabilities=("abc",),
                     evidence_refs=("repo/example@head",))
        context = ctx(qualified_capabilities=frozenset({"abc"}))
        decision = decide_one(source, context)
        self.assertEqual(decision.action, Action.NOTIFY)
        self.assertFalse(decision.effect_authority)
        self.assertFalse(decision.emitted)
        self.assertEqual(len(evaluate([source], context).public_record()["decisions"]), 1)


if __name__ == "__main__":
    unittest.main()
