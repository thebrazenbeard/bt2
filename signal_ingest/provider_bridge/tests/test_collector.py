import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from signal_ingest.provider_bridge.collect_github import collect_pr, CollectorError
from signal_ingest.provider_bridge.v1 import bridge


NOW="2026-11-20T22:00:00Z"
CUT="2026-11-20T18:00:00Z"
HEAD="a"*40

def pull():
    return {"number":123,"head":{"sha":HEAD,"repo":{"full_name":"example/app"}},
            "base":{"repo":{"full_name":"example/app"}},
            "html_url":"https://github.com/example/app/pull/123",
            "state":"open"}

def fake_runner(*args,**kwargs):
    class Done: pass
    done=Done()
    if args[0][-1].endswith("/pulls/123"):
        done.stdout=json.dumps(pull())
    elif args[0][-1].endswith("/actions/runs/456"):
        done.stdout=json.dumps({
            "id":456,"head_sha":HEAD,"status":"completed","conclusion":"failure",
            "repository":{"full_name":"example/app"},
            "html_url":"https://github.com/example/app/actions/runs/456"})
    else:
        raise AssertionError("collector made unexpected API request")
    return done


class GitHubCollectorTest(unittest.TestCase):
    def test_a_collects_pr_and_ci_against_exact_provider_fields(self):
        data=collect_pr("example/app",123,456,NOW,CUT,runner=fake_runner)
        self.assertEqual(data["schema"],"BT2_GITHUB_PROVIDER_BRIDGE_INPUT_V1")
        self.assertEqual(data["receipts"][0]["head"],HEAD)
        self.assertEqual(data["receipts"][1]["status"],"FAILED")
        self.assertFalse(data["receipts"][0]["claims_authenticated"])
        normalized=bridge(data)
        self.assertEqual(len(normalized["signal"]["observations"]),2)
        self.assertFalse(normalized["signal"]["release_permission"])

    def test_b_rejects_forged_pr_repo(self):
        def forged(*args,**kwargs):
            r=fake_runner(*args,**kwargs)
            payload=json.loads(r.stdout)
            if payload.get("number")==123: payload["head"]["repo"]["full_name"]="foreign/app"
            r.stdout=json.dumps(payload)
            return r
        with self.assertRaises(CollectorError):
            collect_pr("example/app",123,None,NOW,CUT,runner=forged)

    def test_c_run_attached_to_other_repo_rejected(self):
        def forged(*args,**kwargs):
            r=fake_runner(*args,**kwargs)
            payload=json.loads(r.stdout)
            if payload.get("id")==456: payload["repository"]["full_name"]="foreign/app"
            r.stdout=json.dumps(payload)
            return r
        with self.assertRaises(CollectorError):
            collect_pr("example/app",123,456,NOW,CUT,runner=forged)

    def test_d_no_shell_or_write_operation(self):
        calls=[]
        def logged(*args,**kwargs):
            calls.append((args,kwargs))
            return fake_runner(*args,**kwargs)
        collect_pr("example/app",123,456,NOW,CUT,runner=logged)
        self.assertEqual(len(calls),2)
        for args,kw in calls:
            self.assertEqual(args[0][0:2],["gh","api"])
            self.assertFalse(kw.get("shell",False))
            self.assertLessEqual(kw["timeout"],20)

    def test_e_run_head_changed_remains_stale(self):
        def older(*args,**kwargs):
            r=fake_runner(*args,**kwargs)
            payload=json.loads(r.stdout)
            if payload.get("id")==456:payload["head_sha"]="b"*40
            r.stdout=json.dumps(payload)
            return r
        data=collect_pr("example/app",123,456,NOW,CUT,runner=older)
        result=bridge(data)
        older_reports=[x for x in result["signal"]["observations"] if x["head"]=="b"*40]
        self.assertEqual(len(older_reports),1)
        self.assertFalse(older_reports[0]["candidate_observation"])

if __name__=="__main__":
    unittest.main()