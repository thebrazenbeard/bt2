"""Two hostile source adapter regressions (no live effects)."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scanner
from bridge_to_signal import adapt

REPO="example/app"
HEAD="b"*40
TIME="2026-11-20T20:00:00Z"

def make(severity="CRITICAL",raw=b"same-raw"):
    return scanner._make(REPO,HEAD,".vscode/tasks.json",
                         "EDITOR_OPEN_EXECUTION",severity,
                         "synthetic fixture",raw,("test",))

def convert(items):
    return adapt(items,repository=REPO,observed_head=HEAD,
                 current_head=HEAD,subject="repo:main",
                 observed_at=TIME,
                 host_access_cutoff="2099-01-01T00:00:00Z")

class HostileReviewSafety(unittest.TestCase):
    def test_high_then_critical_same_incident_cannot_downgrade_critical(self):
        x=convert([make("HIGH"),make("CRITICAL")])
        self.assertEqual(len(x["severe_review_queue"]),1)
        self.assertEqual(x["severe_review_queue"][0]["severity"],"CRITICAL")
        self.assertEqual(len(x["ingest_input"]["observations"]),2)
        self.assertEqual(x["external_effects"],[])

    def test_unbounded_iterator_rejected_after_bounded_read(self):
        seen=[0]
        def infinite():
            while True:
                seen[0]+=1
                if seen[0]>258: raise RuntimeError("UNBOUNDED_ITERATOR")
                yield make(raw=str(seen[0]).encode())
        with self.assertRaisesRegex(ValueError,"TOO_MANY_FINDINGS"):
            convert(infinite())
        self.assertLessEqual(seen[0],257)

if __name__=="__main__":unittest.main()
