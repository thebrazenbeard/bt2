"""Paired binary forecast scoring: research-only, no governance decisions."""
from __future__ import annotations

import copy
import math
import unittest

from tools.ai_psychology.score_forecasts import ScoreError, score_events

HEADS = {"meta": "a"*40, "humility": "b"*40,
         "driftguard": "c"*40, "vera_mono": "d"*40}


def case(event, split, group, outcome, base, cand):
    return {
        "event_id": event, "split": split, "dependence_group_id": group,
        "outcome": outcome, "label_release_epoch_ms": 1300,
        "baseline": {"forecast_id": event + ":base", "issued_epoch_ms": 1100,
                     "p_true": base},
        "candidate": {"forecast_id": event + ":candidate", "issued_epoch_ms": 1200,
                      "p_true": cand},
    }


def example():
    return {
        "schema": "BT2_PAIRED_FORECAST_SCORE_V1",
        "run_id": "research:paired-001",
        "source_heads": dict(HEADS),
        "roles": {"proposer_id": "selector", "evaluator_id": "grader",
                  "outcome_releaser_id": "labels"},
        "splits": {"training_sha256": "1"*64,
                   "heldout_sha256": "2"*64,
                   "shift_sha256": "3"*64},
        "training_cutoff_epoch_ms": 1000,
        "train_group_ids": ["train:a"],
        "events": [
            case("event:1", "heldout", "grp:a", 1, .4, .8),
            case("event:2", "heldout", "grp:b", 0, None, .1),
            case("event:3", "shift", "grp:c", 1, .9, .1),
        ],
        "authorization_effect": "NONE",
    }


class PairedScoreTests(unittest.TestCase):
    def assert_bad(self, change):
        receipt = example()
        change(receipt)
        with self.assertRaises(ScoreError):
            score_events(receipt)

    def test_recomputes_paired_losses_with_fixed_abstention_penalty(self):
        result = score_events(example())
        self.assertEqual(result["status"], "RECOMPUTED_FROM_UNVERIFIED_CLAIMS")
        self.assertEqual(result["authorization_effect"], "NONE")
        self.assertTrue(result["preview_only"])
        held = result["splits"]["heldout"]
        shift = result["splits"]["shift"]
        self.assertEqual(held["n"], 2)
        self.assertAlmostEqual(held["baseline"]["mean_fixed_loss"], .305)
        self.assertAlmostEqual(held["candidate"]["mean_fixed_loss"], .025)
        self.assertAlmostEqual(held["baseline"]["coverage"], .5)
        self.assertAlmostEqual(held["candidate"]["coverage"], 1.0)
        self.assertAlmostEqual(shift["delta_candidate_minus_baseline"], .8)
        self.assertEqual(result["driftguard_preview"]["schema"],
                         "BT2_DRIFTGUARD_UNTRUSTED_PREVIEW_V1")
        self.assertNotIn("DRIFTGUARD_CI_REPORT_V1", repr(result))

    def test_duplicate_event_and_forecast_ids_refused(self):
        self.assert_bad(lambda x: x["events"].append(copy.deepcopy(x["events"][0])))
        self.assert_bad(lambda x: x["events"][1]["candidate"].update(
            forecast_id="event:1:base"))

    def test_no_training_or_group_overlap_across_splits(self):
        self.assert_bad(lambda x: x["events"][0].update(split="training"))
        self.assert_bad(lambda x: x["events"][2].update(dependence_group_id="grp:a"))
        self.assert_bad(lambda x: x["train_group_ids"].append("grp:a"))
        self.assert_bad(lambda x: x["splits"].update(shift_sha256="2"*64))

    def test_requires_prequential_claimed_time_order(self):
        self.assert_bad(lambda x: x["events"][0]["candidate"].update(
            issued_epoch_ms=1400))
        self.assert_bad(lambda x: x["events"][0].update(
            label_release_epoch_ms=1100))
        self.assert_bad(lambda x: x.update(training_cutoff_epoch_ms=1200))

    def test_rejects_nonbinary_outcomes_and_bad_probs(self):
        for value in (True, "1", 2, None):
            with self.subTest(outcome=value):
                self.assert_bad(lambda x: x["events"][0].update(outcome=value))
        for value in (True, -0.1, 1.01, float("nan"), float("inf"), "0.2"):
            with self.subTest(probability=repr(value)):
                self.assert_bad(lambda x: x["events"][0]["baseline"].update(p_true=value))

    def test_rejects_unknown_fields_and_authority_claims(self):
        self.assert_bad(lambda x: x.update(private_prompt="not for this schema"))
        self.assert_bad(lambda x: x["events"][0].update(witness_signature="invented"))
        self.assert_bad(lambda x: x.update(authorization_effect="DEPLOY"))
        self.assert_bad(lambda x: x["roles"].update(evaluator_id="selector"))

    def test_rejects_duplicate_source_and_identity_malformed(self):
        self.assert_bad(lambda x: x["source_heads"].update(meta="main"))
        self.assert_bad(lambda x: x["roles"].update(outcome_releaser_id="grader"))
        self.assert_bad(lambda x: x["events"][0]["baseline"].update(
            forecast_id=""))

    def test_requires_both_split_sets_and_bounded_count(self):
        self.assert_bad(lambda x: x["events"].pop())
        self.assert_bad(lambda x: x["events"].clear())
        self.assert_bad(lambda x: x["events"].extend(
            [copy.deepcopy(x["events"][0])] * 1001))

    def test_output_is_deterministic_and_has_no_runtime_actions(self):
        a, b = score_events(example()), score_events(copy.deepcopy(example()))
        self.assertEqual(a, b)
        self.assertEqual(a["independent_custody_verified"], False)
        self.assertEqual(a["driftguard_preview"]["admission_eligible"], False)
        self.assertNotIn("PASS", str(a))
        self.assertNotIn("deployment_qualified", a)


if __name__ == "__main__":
    unittest.main()
