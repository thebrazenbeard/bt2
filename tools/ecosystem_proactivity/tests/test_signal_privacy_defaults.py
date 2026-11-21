"""Public Signal visibility and trust flags fail closed on missing/malformed values."""
from dataclasses import asdict, replace
import unittest

from test_engine import sig, ctx
from governor.engine import Signal, evaluate


class SignalPrivacyValidationTests(unittest.TestCase):
    def test_omitted_external_visibility_remains_private(self):
        # Force the real dataclass default, not the test helper's explicit
        # opt-in for synthetic public examples.
        data = asdict(sig())
        del data["externally_visible"]
        source = Signal(**data)
        self.assertFalse(source.externally_visible)
        self.assertEqual(evaluate([source], ctx()).public_record()["decisions"], [])

    def test_textual_false_is_not_a_true_public_visibility_flag(self):
        with self.assertRaises(ValueError):
            replace(sig(), externally_visible="false")
        with self.assertRaises(ValueError):
            replace(sig(), externally_visible="no")

    def test_integer_truthy_visibility_cannot_publish(self):
        with self.assertRaises(ValueError):
            replace(sig(), externally_visible=1)
        with self.assertRaises(ValueError):
            replace(sig(), externally_visible=0)

    def test_nonboolean_authenticated_flag_cannot_escalate(self):
        with self.assertRaises(ValueError):
            replace(sig(), source_verified_by_evaluator="false")
        with self.assertRaises(ValueError):
            replace(sig(), corroborated="no")

    def test_all_signal_boundary_flags_require_actual_boolean(self):
        fields = (
            "known_to_owner", "needs_user_decision", "protected_effect",
            "contains_private_data", "runtime_claim", "model_subjectivity_claim",
            "outcome_is_release", "corroborated",
            "source_verified_by_evaluator", "externally_visible",
        )
        for field in fields:
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    replace(sig(), **{field: "false"})

    def test_explicit_boolean_public_and_private_remain_distinct(self):
        self.assertEqual(len(evaluate([sig(externally_visible=True)], ctx())
                             .public_record()["decisions"]), 1)
        self.assertEqual(evaluate([sig(externally_visible=False)], ctx())
                         .public_record()["decisions"], [])


if __name__ == "__main__":
    unittest.main()
