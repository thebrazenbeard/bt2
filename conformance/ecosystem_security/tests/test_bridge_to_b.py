"""Source-only PR125 -> PR123 pinned normalization tests; no external effects."""
from __future__ import annotations
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import scanner
from bridge_to_signal import adapt

B_DIR=os.environ.get("B_SIGNAL_INGEST_DIR")
if B_DIR:
    sys.path.insert(0,B_DIR)
    from signal_ingest.v1 import normalize
else:
    normalize=None

REPO="example/app"
HEAD="b"*40
OLD="a"*40
TS="2026-11-20T20:00:00Z"
CUTOFF="2099-01-01T00:00:00Z"

def finding(path=".vscode/tasks.json",severity="CRITICAL",raw=b"root-A"):
    return scanner._make(REPO,HEAD,path,"EDITOR_OPEN_EXECUTION",severity,
                         "synthetic source finding",raw,("test-fixture",))

def convert(items,seen=HEAD,current=HEAD):
    return adapt(items,repository=REPO,observed_head=seen,current_head=current,
                 subject="repo:main",observed_at=TS,host_access_cutoff=CUTOFF)

class BridgeSourceSafety(unittest.TestCase):
    def test_01_duplicate_critical_review_queue_does_not_repeat(self):
        f=finding()
        x=convert([f,f,f])
        self.assertEqual(len(x["severe_review_queue"]),1)
        self.assertEqual(len(x["ingest_input"]["observations"]),3)
        self.assertEqual(x["authorization"],"NONE")
        self.assertEqual(x["external_effects"],[])
        self.assertFalse(x["source_binding_verified"])

    def test_02_distinct_roots_remain_distinct(self):
        a=finding(raw=b"A");b=finding(path=".vscode/settings.json",raw=b"B")
        x=convert([a,b])
        self.assertEqual(len(x["severe_review_queue"]),2)
        self.assertEqual(len(set(v["incident_key"] for v in x["ingest_input"]["observations"])),2)

    def test_03_forged_permission_not_promoted(self):
        bad=finding()
        from dataclasses import replace
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_EFFECT_CLAIM"):
            convert([replace(bad,authority="APPROVED")])
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_EFFECT_CLAIM"):
            convert([replace(bad,independent_revalidation="PASS")])

    def test_04_wrong_head_or_provider_path_fails_closed(self):
        f=finding()
        with self.assertRaisesRegex(ValueError,"FINDING_SOURCE_HEAD_BINDING_MISMATCH"):
            convert([f],seen=OLD)
        p=scanner._make(REPO,HEAD,"supabase/advisors","SUPABASE_POLICY","INFO",
                        "synthetic",b"provider",("fixture",))
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_SOURCE_PATH"):
            convert([p])

    def test_05_overflow_does_not_truncate_critical(self):
        with self.assertRaisesRegex(ValueError,"TOO_MANY_FINDINGS"):
            convert([finding()]*257)

    def test_06_b_pinned_source_present_when_integration_required(self):
        if os.environ.get("B_SIGNAL_INGEST_REQUIRED")=="1":
            self.assertIsNotNone(normalize,"Pinned B module is required, no silent skip")

    @unittest.skipUnless(normalize is not None,"Requires exact pinned B module")
    def test_07_real_b_keeps_critical_reports_but_no_authority(self):
        f=finding()
        source=convert([f,f,f])
        x=normalize(source["ingest_input"])
        self.assertEqual(len(x["observations"]),1)
        self.assertEqual(len(x["observations"][0]["reports"]),3)
        self.assertFalse(x["observations"][0]["independently_authenticated"])
        self.assertFalse(x["release_permission"])
        self.assertEqual(x["external_effects"],[])
        self.assertEqual(x["host_task_proposals"],[])

    @unittest.skipUnless(normalize is not None,"Requires exact pinned B module")
    def test_08_blinded_50_case_scanner_to_ingest_corpus(self):
        completed=0
        for case in range(50):
            with self.subTest(case=case):
                if case<40:
                    f=finding(severity="INFO",raw=("noise:"+str(case)).encode())
                    source=convert([f]);x=normalize(source["ingest_input"])
                    self.assertFalse(x["observations"][0]["candidate_observation"])
                    self.assertEqual(source["severe_review_queue"],[])
                elif case in (40,41,42):
                    f=finding()
                    source=convert([f,f,f]);x=normalize(source["ingest_input"])
                    self.assertEqual(len(source["severe_review_queue"]),1)
                    self.assertEqual(len(x["observations"]),1)
                    self.assertEqual(len(x["observations"][0]["reports"]),3)
                elif case==43:
                    x=normalize(convert([finding(),finding(path=".vscode/settings.json")])["ingest_input"])
                    self.assertEqual(len(x["observations"]),2)
                elif case==44:
                    old=scanner._make(REPO,OLD,".vscode/tasks.json","EDITOR_OPEN_EXECUTION",
                                      "CRITICAL","old head",b"old",("fixture",))
                    x=normalize(convert([old],seen=OLD,current=HEAD)["ingest_input"])
                    self.assertFalse(x["observations"][0]["candidate_observation"])
                elif case==45:
                    from dataclasses import replace
                    with self.assertRaises(ValueError):convert([replace(finding(),authority="ALLOWED")])
                elif case==46:
                    with self.assertRaises(ValueError):convert([finding()],seen=OLD)
                elif case==47:
                    p=scanner._make(REPO,HEAD,"supabase/advisors","SUPABASE_POLICY",
                                    "INFO","x",b"x",("fixture",))
                    with self.assertRaises(ValueError):convert([p])
                elif case==48:
                    source=convert([finding()]);x=normalize(source["ingest_input"])
                    self.assertEqual(source["external_effects"],[])
                    self.assertEqual(x["external_effects"],[])
                    self.assertFalse(x["release_permission"])
                else:
                    with self.assertRaises(ValueError):convert([finding()]*257)
                completed+=1
        self.assertEqual(completed,50)

if __name__=="__main__":unittest.main()
