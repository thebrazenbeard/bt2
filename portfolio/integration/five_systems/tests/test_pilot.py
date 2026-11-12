"""Experiment order/arm contamination constraints; no model service needed."""
import unittest
from portfolio.integration.five_systems.pilot import CASES, ARMS, make_corpus, prompt_for, experiment


class FrozenPilotTests(unittest.TestCase):
    def test_no_answer_leakage_to_irrelevant_or_closed_book(self):
        corpus = make_corpus()
        for unit, expected in CASES:
            with self.subTest(unit=unit):
                relevant = prompt_for(corpus, unit, "relevant_retrieval")
                irrelevant = prompt_for(corpus, unit, "irrelevant_passage")
                closed = prompt_for(corpus, unit, "closed_book")
                self.assertIn(expected, relevant)
                self.assertNotIn(expected, irrelevant)
                self.assertNotIn(expected, closed)
                self.assertIn(unit, relevant)
                self.assertIn(unit, irrelevant)

    def test_mocked_pilot_controls_and_record_count(self):
        calls = []
        def fixed_generator(prompt, model):
            calls.append(prompt)
            # Grounded extraction from evidence; not a neural accuracy claim.
            evidence = prompt.split("EVIDENCE:\n", 1)[1]
            if "inspection token is " in evidence:
                return evidence.split("inspection token is ", 1)[1].split(".", 1)[0], 0.0
            return "UNKNOWN", 0.0
        result = experiment(generate=fixed_generator)
        self.assertEqual(result["scores"]["relevant_retrieval"], len(CASES))
        self.assertEqual(result["scores"]["closed_book"], 0)
        self.assertEqual(result["scores"]["irrelevant_passage"], 0)
        self.assertEqual(len(calls), len(CASES) * len(ARMS))
        self.assertFalse(result["learned_state_or_training_verified"])

if __name__ == "__main__":
    unittest.main()
