"""Adversarial scientific-method checks for Seven's supervised examples."""

import json
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "coding_models/personality/cases/seven.json"


class SevenScientificChallengeTests(unittest.TestCase):
    def test_extreme_finite_range_is_part_of_training_fixture(self):
        dossier = json.loads(DATA.read_text(encoding="utf-8"))
        case = next(c for c in dossier["cases"] if c["id"] == "seven-persona-train-007")
        self.assertEqual(case["split"], "train")
        self.assertIn("1e308", case["task"])
        self.assertIn("1e308", case["ideal_response"])
        self.assertIn("isfinite", case["ideal_response"])
        self.assertIn("(1.0 / h) / (1.0 + x / h)", case["ideal_response"])

    def test_large_finite_float_discriminates_overflow_from_subnormal(self):
        x = 1e308
        naive_rationalization = 1.0 / (math.hypot(x, 1.0) + x)
        self.assertEqual(naive_rationalization, 0.0)

        h = math.hypot(x, 1.0)
        scaled_rationalization = (1.0 / h) / (1.0 + x / h)
        self.assertGreater(scaled_rationalization, 0.0)
        self.assertTrue(math.isclose(scaled_rationalization, 0.5 / x,
                                     rel_tol=1e-14, abs_tol=0.0))
        self.assertGreater((1.0 / math.hypot(math.nextafter(math.inf, 0.0), 1.0)) /
                           (1.0 + math.nextafter(math.inf, 0.0) /
                            math.hypot(math.nextafter(math.inf, 0.0), 1.0)), 0.0)


if __name__ == "__main__":
    unittest.main()
