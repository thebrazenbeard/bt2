"""Source-bound, read-only Humility proposal tests; no model or private data."""
from dataclasses import asdict
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import cognitive_advisory
from cognitive_advisory import EvidenceSignal, AdvisoryRequest, propose

ROOT = os.environ.get("BT2_VERA_COGNITIVE_REPOS")


@unittest.skipUnless(ROOT, "set explicit pinned source checkouts")
class ReadOnlyAdvisoryTests(unittest.TestCase):
    def test_real_humility_source_produces_unverified_math_only(self):
        request = AdvisoryRequest("synthetic fixture exists", 0.5, (
            EvidenceSignal("fixture-a", "fixture-source-a", 0.9, 0.1),
        ))
        result = propose(Path(ROOT), request)
        self.assertAlmostEqual(result.posterior, 0.9)
        self.assertEqual(result.evidence_ids, ("fixture-a",))
        self.assertEqual(result.status, "UNVERIFIED_CALLER_LIKELIHOODS")
        self.assertFalse(result.effect_authority)
        self.assertFalse(result.memory_admission)
        self.assertIn("humility", dict(result.source_pins))
        self.assertEqual(asdict(result)["status"], result.status)
    def test_replayed_or_dependent_source_is_rejected(self):
        request = AdvisoryRequest("synthetic fixture exists", 0.5, (
            EvidenceSignal("a", "same", 0.8, 0.2),
            EvidenceSignal("b", "same", 0.9, 0.1),
        ))
        with self.assertRaisesRegex(ValueError, "dependent evidence"):
            propose(Path(ROOT), request)

    def test_historical_replay_rejected_when_history_provided(self):
        request = AdvisoryRequest(
            "synthetic fixture exists", 0.5,
            (EvidenceSignal("a", "source-a", 0.8, 0.2),),
            seen_evidence_ids=("a",),
        )
        with self.assertRaisesRegex(ValueError, "historical evidence"):
            propose(Path(ROOT), request)

    def test_invalid_boolean_likelihood_rejected(self):
        request = AdvisoryRequest("synthetic fixture exists", 0.5, (
            EvidenceSignal("a", "source-a", True, 0.2),
        ))
        with self.assertRaises(ValueError):
            propose(Path(ROOT), request)

    def test_nontrivial_source_revision_is_not_a_fixed_fixture_answer(self):
        request = AdvisoryRequest("independent synthetic claim", 0.25, (
            EvidenceSignal("b", "source-b", 0.7, 0.3),
        ))
        outcome = propose(Path(ROOT), request)
        self.assertAlmostEqual(outcome.posterior, 0.4375)
        self.assertNotAlmostEqual(outcome.posterior, 0.9)

    def test_actual_pinned_humility_revision_is_invoked(self):
        actual_loader = cognitive_advisory._load_exact_module
        observed = []

        def instrument(path):
            module = actual_loader(path)
            if path.name == "core.py" and path.parent.name == "humility":
                original = module.revise_distinct

                def counted(*args, **kwargs):
                    observed.append(True)
                    return original(*args, **kwargs)

                module.revise_distinct = counted
            return module

        request = AdvisoryRequest("synthetic claim", 0.5, (
            EvidenceSignal("witness", "independent-group", 0.6, 0.4),
        ))
        with patch.object(cognitive_advisory, "_load_exact_module", side_effect=instrument):
            outcome = propose(Path(ROOT), request)
        self.assertEqual(observed, [True])
        self.assertAlmostEqual(outcome.posterior, 0.6)

    def test_missing_pinned_source_fails_closed_before_advisory(self):
        request = AdvisoryRequest("synthetic claim", 0.5, (
            EvidenceSignal("a", "source-a", 0.9, 0.1),
        ))
        with self.assertRaisesRegex(ValueError, "missing source checkout"):
            propose(Path(ROOT) / "nonexistent-root", request)


if __name__ == "__main__":
    unittest.main()
