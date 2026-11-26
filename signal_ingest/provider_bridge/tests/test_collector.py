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
            "event":"pull_request",
            "pull_requests":[{"number":123,"url":"https://api.github.com/repos/example/app/pulls/123","head":{"sha":HEAD}}],
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
            if payload.get("id")==456:
                payload["head_sha"]="b"*40
                payload["pull_requests"][0]["head"]["sha"]="b"*40
            r.stdout=json.dumps(payload)
            return r
        data=collect_pr("example/app",123,456,NOW,CUT,runner=older)
        result=bridge(data)
        older_reports=[x for x in result["signal"]["observations"] if x["head"]=="b"*40]
        self.assertEqual(len(older_reports),1)
        self.assertFalse(older_reports[0]["candidate_observation"])

    def test_f_other_pr_same_head_cannot_borrow_ci_status(self):
        def wrong_pr(*args,**kwargs):
            r=fake_runner(*args,**kwargs)
            data=json.loads(r.stdout)
            if data.get("id")==456:
                data["pull_requests"][0]["number"]=987
                r.stdout=json.dumps(data)
            return r
        with self.assertRaises(CollectorError):
            collect_pr("example/app",123,456,NOW,CUT,runner=wrong_pr)

    def test_g_branch_push_without_explicit_pr_link_is_not_pr_ci(self):
        def push_only(*args,**kwargs):
            r=fake_runner(*args,**kwargs)
            data=json.loads(r.stdout)
            if data.get("id")==456:
                data["event"]="push"
                data["pull_requests"]=[]
                r.stdout=json.dumps(data)
            return r
        with self.assertRaises(CollectorError):
            collect_pr("example/app",123,456,NOW,CUT,runner=push_only)

    def test_h_same_pr_number_but_conflicting_ci_head_is_rejected(self):
        def forged_link(*args,**kwargs):
            r=fake_runner(*args,**kwargs)
            data=json.loads(r.stdout)
            if data.get("id")==456:
                data["pull_requests"][0]["head"]["sha"]="c"*40
                r.stdout=json.dumps(data)
            return r
        with self.assertRaises(CollectorError):
            collect_pr("example/app",123,456,NOW,CUT,runner=forged_link)


    def test_i_pr_link_url_must_bind_repo_and_number(self):
        def wrong_source(*args,**kwargs):
            r=fake_runner(*args,**kwargs)
            data=json.loads(r.stdout)
            if data.get("id")==456:
                data["pull_requests"][0]["url"]="https://api.github.com/repos/foreign/app/pulls/123"
                r.stdout=json.dumps(data)
            return r
        with self.assertRaises(CollectorError):
            collect_pr("example/app",123,456,NOW,CUT,runner=wrong_source)


    def test_j_provider_pr_number_must_be_strict_integer_even_for_pr_one(self):
        """Python True == 1 and 1.0 == 1 must never bind a provider PR."""
        from types import SimpleNamespace
        for forged_number in (True, 1.0):
            def fake_one(argv, **kw):
                data = {"number": forged_number,
                        "head": {"sha": HEAD, "repo": {"full_name":"example/app"}},
                        "base": {"repo": {"full_name":"example/app"}},
                        "html_url": "https://github.com/example/app/pull/1"}
                return SimpleNamespace(stdout=json.dumps(data))
            with self.subTest(forged=repr(forged_number)):
                with self.assertRaisesRegex(CollectorError, "PROVIDER_PR_BINDING_MISMATCH"):
                    collect_pr("example/app",1,None,NOW,CUT,runner=fake_one)

    def test_k_provider_run_id_must_be_strict_integer_even_for_run_one(self):
        """A boolean or float provider run ID is not the requested run."""
        from types import SimpleNamespace
        for forged_id in (True, 1.0):
            def fake_one(argv, **kw):
                if argv[2].endswith("/pulls/1"):
                    data = {"number":1,"head":{"sha":HEAD,"repo":{"full_name":"example/app"}},
                            "base":{"repo":{"full_name":"example/app"}},
                            "html_url":"https://github.com/example/app/pull/1"}
                else:
                    data = {"id":forged_id,"head_sha":HEAD,"status":"completed",
                            "conclusion":"success","repository":{"full_name":"example/app"},
                            "event":"pull_request","pull_requests":[{
                                "number":1,"url":"https://api.github.com/repos/example/app/pulls/1",
                                "head":{"sha":HEAD}}],
                            "html_url":"https://github.com/example/app/actions/runs/1"}
                return SimpleNamespace(stdout=json.dumps(data))
            with self.subTest(forged=repr(forged_id)):
                with self.assertRaisesRegex(CollectorError, "PROVIDER_RUN_BINDING_MISMATCH"):
                    collect_pr("example/app",1,1,NOW,CUT,runner=fake_one)

    def test_l_nonfinite_provider_json_is_rejected_before_receipt(self):
        """Nonstandard JSON constants cannot be silently hashed as evidence."""
        from signal_ingest.provider_bridge.collect_github import _parse
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaisesRegex(CollectorError, "INVALID_PROVIDER_JSON"):
                    _parse('{"id":' + token + '}')


    def test_m_integer_pr_and_run_one_still_accept_valid_provider_response(self):
        """The strict types must not exclude actual integer identity 1."""
        from types import SimpleNamespace
        def valid_one(argv, **kw):
            if argv[2].endswith("/pulls/1"):
                payload = {"number":1, "head":{"sha":HEAD,"repo":{"full_name":"example/app"}},
                           "base":{"repo":{"full_name":"example/app"}},
                           "html_url":"https://github.com/example/app/pull/1"}
            elif argv[2].endswith("/actions/runs/1"):
                payload = {"id":1,"head_sha":HEAD,"status":"completed",
                           "conclusion":"success","repository":{"full_name":"example/app"},
                           "event":"pull_request","pull_requests":[{
                               "number":1,"url":"https://api.github.com/repos/example/app/pulls/1",
                               "head":{"sha":HEAD}}],
                           "html_url":"https://github.com/example/app/actions/runs/1"}
            else:
                raise AssertionError("unapproved provider read")
            return SimpleNamespace(stdout=json.dumps(payload))
        result=collect_pr("example/app",1,1,NOW,CUT,runner=valid_one)
        self.assertEqual(len(result["receipts"]),2)
        self.assertEqual(result["receipts"][1]["status"],"PASSED")
        normalized=bridge(result)
        self.assertFalse(normalized["independently_authenticated"])
        self.assertFalse(normalized["signal"]["release_permission"])
        self.assertEqual(normalized["memory_admission"],"NONE")


if __name__=="__main__":
    unittest.main()