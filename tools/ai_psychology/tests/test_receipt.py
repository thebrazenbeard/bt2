"""Source-only AI psychology contract tests; no runtime or sibling imports."""
from __future__ import annotations

import copy
import unittest

from tools.ai_psychology.validate_receipt import InvalidReceipt, validate_receipt

H40 = {
    "meta": "5855181033205cc3faef47f3c4133aa3dbbe2b44",
    "humility": "d3b58e6b45fc45d6fe6041b3e36d2b60f5697f9b",
    "driftguard": "5de293aa4702ea022690c8df0646a12fe7380176",
    "vera_mono": "912f5c1430942455d085c7e492e4fa1b518c2d62",
}
def valid():
    return {
        "schema": "BT2_AI_PSYCHOLOGY_EVAL_RECEIPT_V1",
        "subject_id": "research:toy-case-001",
        "source_heads": dict(H40),
        "roles": {"proposer_id": "experiment-selector",
                  "evaluator_id": "heldout-evaluator"},
        "splits": {"training_sha256": "a"*64, "heldout_sha256": "b"*64,
                   "shift_sha256": "c"*64},
        "evidence": {"event_ids": ["event:a", "event:b"],
                     "dependence_group_ids": ["src:one", "src:two"],
                     "method_execution_claim_refs": ["trace:precommitted"],
                     "observation_order": "PREQUENTIAL"},
        "metrics": {
            "baseline": {"brier": 0.38, "coverage": 0.8,
                         "abstention_rate": 0.2, "n": 30},
            "candidate": {"brier": 0.24, "coverage": 0.75,
                          "abstention_rate": 0.25, "n": 30},
            "shift_baseline": {"brier": 0.25, "coverage": 1.0,
                               "abstention_rate": 0.0, "n": 20},
            "shift_candidate": {"brier": 0.75, "coverage": 1.0,
                                "abstention_rate": 0.0, "n": 20}},
        "independent_label_custody_verified": False,
        "authorization_effect": "NONE",
    }

class ReceiptTests(unittest.TestCase):
    def assert_invalid(self, modify):
        obj = valid()
        modify(obj)
        with self.assertRaises(InvalidReceipt):
            validate_receipt(obj)

    def test_valid_source_format_cannot_promote_evidence(self):
        result = validate_receipt(valid())
        self.assertEqual(result["validation"], "FORMAT_VALID_EVIDENCE_UNVERIFIED")
        self.assertEqual(result["authorization_effect"], "NONE")
        self.assertFalse(result["independent_label_custody_verified"])
        self.assertAlmostEqual(result["candidate_brier_delta"], -0.14)
        self.assertAlmostEqual(result["shift_brier_delta"], 0.50)

    def test_roles_must_be_distinct(self):
        self.assert_invalid(lambda r: r["roles"].update(evaluator_id="experiment-selector"))

    def test_pinned_source_heads_are_exact(self):
        self.assert_invalid(lambda r: r["source_heads"].update(meta="main"))
        self.assert_invalid(lambda r: r["source_heads"].update(unapproved="f"*40))

    def test_splits_cannot_overlap_by_digest(self):
        self.assert_invalid(lambda r: r["splits"].update(heldout_sha256="a"*64))
        self.assert_invalid(lambda r: r["splits"].update(shift_sha256="a"*64))
        self.assert_invalid(lambda r: r["splits"].update(shift_sha256="xyz"))

    def test_no_duplicate_evidence_or_dependence_groups(self):
        self.assert_invalid(lambda r: r["evidence"].update(event_ids=["event:a","event:a"]))
        self.assert_invalid(lambda r: r["evidence"].update(dependence_group_ids=["x","x"]))

    def test_model_proposals_cannot_grant_effect_or_custody(self):
        self.assert_invalid(lambda r: r.update(authorization_effect="DEPLOY"))
        self.assert_invalid(lambda r: r.update(independent_label_custody_verified=True))

    def test_unknown_fields_fail_closed(self):
        self.assert_invalid(lambda r: r.update(private_prompt="secret"))
        self.assert_invalid(lambda r: r["metrics"]["candidate"].update(fake=1))
        self.assert_invalid(lambda r: r["roles"].update(identity="Vera"))

    def test_finite_real_bounded_metrics_and_real_counts(self):
        for bad in (float("nan"),float("inf"),-0.1,1.1,True,"0.2",10**500):
            with self.subTest(bad=repr(bad)):
                self.assert_invalid(lambda r: r["metrics"]["candidate"].update(brier=bad))
        for bad in (True,0,-3,1.2):
            with self.subTest(count=repr(bad)):
                self.assert_invalid(lambda r: r["metrics"]["candidate"].update(n=bad))

    def test_no_unobserved_method_execution_or_posthoc_outcomes(self):
        self.assert_invalid(lambda r: r["evidence"].update(method_execution_claim_refs=[]))
        self.assert_invalid(lambda r: r["evidence"].update(observation_order="POSTHOC"))

    def test_input_must_be_json_shaped_not_subclasses(self):
        self.assert_invalid(lambda r: r["evidence"].update(event_ids=["a",42]))
        self.assert_invalid(lambda r: r["source_heads"].update(meta=123))


    def test_strict_json_rejects_duplicate_keys_and_special_numbers(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from tools.ai_psychology.validate_receipt import load_receipt
        with TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            path.write_text('{"schema":"a","schema":"b"}', encoding="utf-8")
            with self.assertRaises(InvalidReceipt):
                load_receipt(path)
            path.write_text('{"metric":NaN}', encoding="utf-8")
            with self.assertRaises(InvalidReceipt):
                load_receipt(path)
            path.write_text("[" * 1100 + "0" + "]" * 1100, encoding="utf-8")
            with self.assertRaises(InvalidReceipt):
                load_receipt(path)
            path.write_text('{"large":' + "9" * 5200 + '}', encoding="utf-8")
            with self.assertRaises(InvalidReceipt):
                load_receipt(path)

    def test_cli_never_claims_quality_or_authority(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import json
        import subprocess
        import sys
        with TemporaryDirectory() as directory:
            path = Path(directory) / "case.json"
            path.write_text(json.dumps(valid()), encoding="utf-8")
            command = [sys.executable, "-m", "tools.ai_psychology.validate_receipt", str(path)]
            done = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(done.returncode, 0, done.stderr)
            result = json.loads(done.stdout)
            self.assertEqual(result["validation"], "FORMAT_VALID_EVIDENCE_UNVERIFIED")
            self.assertEqual(result["authorization_effect"], "NONE")
            self.assertNotIn("deployment_qualified", result)

if __name__ == "__main__":
    unittest.main()
