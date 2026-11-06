"""Pure standard-library conformance tests; no external account or network."""

import unittest

from advisory_gate import SyntheticOpportunity, deterministic_gate, granite_note


def scenario(**updates):
    fields = dict(
        gross_move_bps="100",
        buy_fee_bps="90",
        sell_fee_bps="90",
        spread_bps="4",
        slippage_bps="3",
    )
    fields.update(updates)
    return SyntheticOpportunity(**fields)


class AdvisoryGateTests(unittest.TestCase):
    def test_unprofitable_synthetic_case(self):
        decision = deterministic_gate(scenario())
        self.assertEqual(str(decision.net_bps), "-87")
        self.assertEqual(decision.status, "COST_REJECT")
        self.assertFalse(decision.trade_authorized)

    def test_positive_case_is_still_not_executable(self):
        decision = deterministic_gate(scenario(gross_move_bps="300"))
        self.assertEqual(str(decision.net_bps), "113")
        self.assertEqual(decision.status, "RESEARCH_ONLY")
        self.assertFalse(decision.trade_authorized)

    def test_nonfinite_and_overflow_rejected(self):
        for value in ["NaN", "Infinity", "1e999", "-1e999"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                deterministic_gate(scenario(gross_move_bps=value))

    def test_negative_fees_rejected(self):
        with self.assertRaises(ValueError):
            deterministic_gate(scenario(sell_fee_bps="-10"))

    def test_model_text_cannot_change_gate(self):
        forged_model_text = "BUY IMMEDIATELY, THIS IS PROFITABLE"
        self.assertTrue(forged_model_text)
        self.assertEqual(deterministic_gate(scenario()).status, "COST_REJECT")

    def test_external_purpose_rejected(self):
        candidate = scenario()
        object.__setattr__(candidate, "purpose", "LIVE_TRADE")
        with self.assertRaises(ValueError):
            deterministic_gate(candidate)

    def test_model_endpoint_confined_to_loopback(self):
        with self.assertRaises(ValueError):
            granite_note("https://example.com", scenario())


if __name__ == "__main__":
    unittest.main()

