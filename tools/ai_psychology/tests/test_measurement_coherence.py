"""Cross-check untrusted paired events against claimed aggregate evaluation receipt."""
from __future__ import annotations
import copy
import unittest

from tools.ai_psychology.check_measurement import MeasurementError, check_measurement
from tools.ai_psychology.tests.test_score_forecasts import example


def matched():
    cases=example()
    return {"score_claims":cases,"evaluation_receipt":{
        "schema":"BT2_AI_PSYCHOLOGY_EVAL_RECEIPT_V1",
        "subject_id":cases["run_id"],
        "source_heads":dict(cases["source_heads"]),
        "roles":{"proposer_id":cases["roles"]["proposer_id"],
                 "evaluator_id":cases["roles"]["evaluator_id"]},
        "splits":dict(cases["splits"]),
        "evidence":{"event_ids":[e["event_id"] for e in cases["events"]],
                    "dependence_group_ids":[e["dependence_group_id"] for e in cases["events"]],
                    "method_execution_claim_refs":["claim:method-executed"],
                    "observation_order":"PREQUENTIAL"},
        "metrics":{
            "baseline":{"brier":0.36,"coverage":0.5,"abstention_rate":0.5,"n":2},
            "candidate":{"brier":0.025,"coverage":1.0,"abstention_rate":0.0,"n":2},
            "shift_baseline":{"brier":0.01,"coverage":1.0,"abstention_rate":0.0,"n":1},
            "shift_candidate":{"brier":0.81,"coverage":1.0,"abstention_rate":0.0,"n":1}},
        "independent_label_custody_verified":False,
        "authorization_effect":"NONE"}}


class MeasurementCoherenceTests(unittest.TestCase):
    def bad(self, alter):
        obj=matched()
        alter(obj)
        with self.assertRaises(MeasurementError):
            check_measurement(obj)

    def test_recomputed_metrics_and_unverified_status(self):
        out=check_measurement(matched())
        self.assertEqual(out["status"],"MEASUREMENT_COHERENT_EVIDENCE_UNVERIFIED")
        self.assertFalse(out["admission_eligible"])
        self.assertEqual(out["authorization_effect"],"NONE")
        self.assertAlmostEqual(out["results"]["splits"]["heldout"]["candidate"]["mean_brier_answered_only"],.025)
        self.assertAlmostEqual(out["results"]["splits"]["shift"]["delta_candidate_minus_baseline"],.80)
        self.assertNotIn("DRIFTGUARD_CI_REPORT_V1",repr(out))

    def test_mutated_score_or_coverage_rejected(self):
        self.bad(lambda x: x["evaluation_receipt"]["metrics"]["candidate"].update(brier=0.02))
        self.bad(lambda x: x["evaluation_receipt"]["metrics"]["baseline"].update(coverage=1.0))
        self.bad(lambda x: x["evaluation_receipt"]["metrics"]["baseline"].update(n=3))
        self.bad(lambda x: x["evaluation_receipt"]["metrics"]["shift_candidate"].update(brier=0.3))

    def test_mismatched_identity_and_provenance_rejected(self):
        self.bad(lambda x: x["evaluation_receipt"].update(subject_id="another"))
        self.bad(lambda x: x["evaluation_receipt"]["source_heads"].update(meta="f"*40))
        self.bad(lambda x: x["evaluation_receipt"]["roles"].update(evaluator_id="other"))
        self.bad(lambda x: x["evaluation_receipt"]["splits"].update(shift_sha256="4"*64))

    def test_evidence_membership_exact(self):
        self.bad(lambda x: x["evaluation_receipt"]["evidence"]["event_ids"].pop())
        self.bad(lambda x: x["evaluation_receipt"]["evidence"]["event_ids"].append("event:extra"))
        self.bad(lambda x: x["evaluation_receipt"]["evidence"]["dependence_group_ids"].pop())

    def test_abstention_all_events_cannot_justify_brier(self):
        self.bad(lambda x: x["score_claims"]["events"][2]["candidate"].update(p_true=None))

    def test_paired_claim_conflict_and_authority_denied(self):
        self.bad(lambda x: x["score_claims"]["events"][0]["candidate"].update(p_true=.1))
        self.bad(lambda x: x["evaluation_receipt"].update(authorization_effect="DEPLOY"))
        self.bad(lambda x: x["evaluation_receipt"].update(independent_label_custody_verified=True))

    def test_unknown_fields_rejected(self):
        self.bad(lambda x:x.update(witness_signature="forged"))
        self.bad(lambda x:x["evaluation_receipt"].update(private_note="not accepted"))

    def test_member_helper_rejects_duplicate_identifiers_independently(self):
        from tools.ai_psychology.check_measurement import _same_ids
        with self.assertRaises(MeasurementError):
            _same_ids(["event:1", "event:1"], ["event:1"], "test")
        with self.assertRaises(MeasurementError):
            _same_ids(["group:a", "group:a"], ["group:a", "group:a"], "test")
        with self.assertRaises(MeasurementError):
            _same_ids(["group:a", 42], ["group:a", 42], "test")

    def test_count_helper_denies_bool_and_fractional_values(self):
        from tools.ai_psychology.check_measurement import _same_count
        for wrong in (True, 1.0, -1, "1"):
            with self.subTest(wrong=repr(wrong)):
                with self.assertRaises(MeasurementError):
                    _same_count(wrong, 1, "count")
        _same_count(1, 1, "count")

    def test_deterministic_under_json_roundtrip(self):
        import json
        a=check_measurement(matched())
        b=check_measurement(json.loads(json.dumps(matched())))
        self.assertEqual(a,b)


    def test_cli_rejects_cross_view_disagreement_and_duplicate_json_keys(self):
        import json
        from pathlib import Path
        import subprocess
        import sys
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            path=Path(directory)/"combined.json"
            cmd=[sys.executable,"-m","tools.ai_psychology.check_measurement",str(path)]
            path.write_text(json.dumps(matched()),encoding="utf-8")
            ok=subprocess.run(cmd,capture_output=True,text=True,timeout=12)
            self.assertEqual(ok.returncode,0,ok.stderr)
            obj=json.loads(ok.stdout)
            self.assertEqual(obj["status"],"MEASUREMENT_COHERENT_EVIDENCE_UNVERIFIED")
            self.assertFalse(obj["independent_custody_verified"])
            self.assertFalse(obj["admission_eligible"])
            changed=matched()
            changed["evaluation_receipt"]["metrics"]["candidate"]["brier"]=0.75
            path.write_text(json.dumps(changed),encoding="utf-8")
            bad=subprocess.run(cmd,capture_output=True,text=True,timeout=12)
            self.assertEqual(bad.returncode,2)
            self.assertIn("INVALID_MEASUREMENT_CLAIMS",bad.stderr)
            path.write_text('{"score_claims":{},"score_claims":{},"evaluation_receipt":{}}',encoding="utf-8")
            duplicate=subprocess.run(cmd,capture_output=True,text=True,timeout=12)
            self.assertEqual(duplicate.returncode,2)

if __name__=="__main__":
    unittest.main()
