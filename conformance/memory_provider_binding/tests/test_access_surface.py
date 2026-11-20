import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from provider_access import evaluate_access


TABLES=[("public",x) for x in (
    "vera_memory_epoch_subjects_v1","vera_memory_epoch_events_v1",
    "vera_memory_epoch_provider_receipts_v1","vera_memory_epoch_archive_receipts_v1"
)] + [("semantic_atlas",x) for x in (
    "runtime_objects","runtime_snapshots","capture_policy")]
FUNCTIONS=[
    ("public","vera_memory_epoch_get_status_v1"),
    ("semantic_atlas","search_current_runtime_objects_v11")
]


def snapshot():
    return {
        "schema":"BT2_MEMORY_PROVIDER_ACCESS_INPUT_V1",
        "observed_at":"2026-11-20T21:00:00Z",
        "source_ref":"synthetic://secure-access-test",
        "independently_authenticated":True,
        "schema_rights":[
            {"schema":"public","anon_create":False,"authenticated_create":False,
             "anon_usage":True,"authenticated_usage":True},
            {"schema":"semantic_atlas","anon_create":False,"authenticated_create":False,
             "anon_usage":False,"authenticated_usage":False}
        ],
        "tables":[{"schema":s,"name":n,"rls_enabled":True,
                   "force_rls":s=="public",
                   "anon":{"select":False,"insert":False,"update":False,"delete":False},
                   "authenticated":{"select":False,"insert":False,"update":False,"delete":False}}
                  for s,n in TABLES],
        "functions":[{"schema":s,"name":n,"security_definer":True,
                      "anon_execute":False,"authenticated_execute":False,
                      "search_path_limited":True} for s,n in FUNCTIONS],
    }


class ProviderAccessHostile(unittest.TestCase):
    def test_existing_protected_catalog_is_still_unqualified_authority(self):
        r=evaluate_access(snapshot())
        self.assertEqual(r["verdict"],"ACCESS_SURFACE_RESTRICTED_UNQUALIFIED")
        self.assertFalse(r["independently_authenticated"])
        self.assertEqual(r["memory_admission"],"NONE")
        self.assertEqual(r["side_effects"],[])

    def test_missing_schema_write_permissions_must_be_unknown(self):
        data=snapshot()
        del data["schema_rights"]
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"UNKNOWN_INCOMPLETE_CATALOG",
                         "security-definer search paths require schema CREATE checks")
    def test_anon_schema_create_with_security_definer_is_hold(self):
        data=snapshot()
        data["schema_rights"][1]["anon_create"]=True
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("ANON_CREATE_ON_MEMORY_SCHEMA",result["reason_codes"])

    def test_authenticated_schema_create_with_security_definer_is_hold(self):
        data=snapshot()
        data["schema_rights"][0]["authenticated_create"]=True
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("AUTHENTICATED_CREATE_ON_MEMORY_SCHEMA",result["reason_codes"])

    def test_definer_search_path_without_pinning_is_hold(self):
        data=snapshot()
        data["functions"][1]["search_path_limited"]=False
        self.assertIn("SECURITY_DEFINER_SEARCH_PATH_NOT_PINNED",
                      evaluate_access(data)["reason_codes"])
    def test_anon_select_privilege_cannot_be_described_as_restricted(self):
        data=snapshot()
        data["tables"][0]["anon"]["select"]=True
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("ANON_TABLE_PRIVILEGE",result["reason_codes"])

    def test_security_definer_function_publicly_executable_is_hold(self):
        data=snapshot()
        data["functions"][0]["anon_execute"]=True
        r=evaluate_access(data)
        self.assertEqual(r["verdict"],"HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("ANON_SECURITY_DEFINER_EXECUTE",r["reason_codes"])

    def test_unlisted_memory_relation_with_anon_select_must_hold(self):
        data=snapshot()
        other=copy.deepcopy(data["tables"][0])
        other["name"]="vera_memory_epoch_debug_v2"
        other["anon"]["select"]=True
        data["tables"].append(other)
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("UNLISTED_MEMORY_TABLE_GRANT",result["reason_codes"])

    def test_unlisted_memory_function_with_anon_execute_must_hold(self):
        data=snapshot()
        other=copy.deepcopy(data["functions"][0])
        other["name"]="vera_memory_epoch_dump_debug"
        other["anon_execute"]=True
        data["functions"].append(other)
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("UNLISTED_MEMORY_FUNCTION_EXECUTE",result["reason_codes"])
    def test_unlisted_invoker_with_execute_but_no_schema_usage_is_review_not_proven_leak(self):
        data=snapshot()
        extra=copy.deepcopy(data["functions"][1])
        extra["name"]="runtime_manifest_stream_v4"
        extra["security_definer"]=False
        extra["anon_execute"]=True
        extra["authenticated_execute"]=True
        data["functions"].append(extra)
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"REVIEW_UNLISTED_SURFACES")
        self.assertIn("UNLISTED_EXECUTE_GRANT_NO_SCHEMA_USAGE",result["reason_codes"])
    def test_new_schema_usage_grant_changes_invoker_review_to_hold(self):
        data=snapshot()
        extra=copy.deepcopy(data["functions"][1])
        extra["name"]="runtime_manifest_stream_v4"
        extra["security_definer"]=False
        extra["anon_execute"]=True
        data["functions"].append(extra)
        data["schema_rights"][1]["anon_usage"]=True
        result=evaluate_access(data)
        self.assertEqual(result["verdict"],"HOLD_PRIVILEGE_EXPOSURE")
        self.assertIn("UNLISTED_MEMORY_FUNCTION_EXECUTE",result["reason_codes"])

    def test_one_missing_function_keeps_privileges_unknown(self):
        data=snapshot()
        data["functions"]=data["functions"][:1]
        self.assertEqual(evaluate_access(data)["verdict"],"UNKNOWN_INCOMPLETE_CATALOG")


if __name__=="__main__":
    unittest.main()
class ProviderAccessMetadataAdversaries(unittest.TestCase):
    def test_spoofed_authenticated_flag_still_source_only(self):
        report=evaluate_access(snapshot())
        self.assertFalse(report["independently_authenticated"])
        self.assertEqual(report["provider_authentication"],
                         "UNKNOWN_NOT_INDEPENDENTLY_VERIFIED")
        self.assertEqual(report["memory_admission"],"NONE")

    def test_denied_direct_role_grants_do_not_imply_policy_correctness(self):
        report=evaluate_access(snapshot())
        self.assertEqual(report["rls_policy_correctness"],"UNKNOWN_NOT_PROBED")
        self.assertEqual(report["runtime_currentness"],"UNKNOWN_NOT_PROBED")

    def test_duplicate_and_bad_schema_rights_rejected(self):
        from provider_catalog import CatalogError
        data=snapshot()
        data["schema_rights"].append(dict(data["schema_rights"][0]))
        with self.assertRaises(CatalogError):
            evaluate_access(data)
        data=snapshot()
        data["schema_rights"][0]["anon_usage"]="false"
        with self.assertRaises(CatalogError):
            evaluate_access(data)

    def test_extra_private_payload_not_accepted_or_rendered(self):
        from provider_catalog import CatalogError
        data=snapshot()
        data["private_rows"]=[{"secret":"MUST_NOT_APPEAR"}]
        with self.assertRaises(CatalogError):
            evaluate_access(data)

    def test_source_ref_is_hashed_not_returned(self):
        from provider_catalog import canonical
        data=snapshot()
        data["source_ref"]="private://SECRET_ACCOUNT_IDENTIFIER"
        report=canonical(evaluate_access(data))
        self.assertNotIn("SECRET_ACCOUNT_IDENTIFIER",report)
        self.assertNotIn("private://",report)

    def test_access_cli_fixture_deterministic_and_read_only(self):
        import json
        import subprocess
        root=Path(__file__).resolve().parents[1]
        fixture=root/"fixtures"/"vera_access_synthetic_v1.json"
        args=[sys.executable,str(root/"provider_access.py"),str(fixture)]
        one=subprocess.run(args,check=True,capture_output=True,text=True)
        two=subprocess.run(args,check=True,capture_output=True,text=True)
        self.assertEqual(one.stdout,two.stdout)
        report=json.loads(one.stdout)
        self.assertEqual(report["verdict"],"ACCESS_SURFACE_RESTRICTED_UNQUALIFIED")
        self.assertEqual(report["side_effects"],[])
        self.assertEqual(report["release_authorization"],"NONE")

    def test_incomplete_schema_usage_is_not_unknown_pass(self):
        data=snapshot()
        data["schema_rights"][1].pop("anon_usage")
        from provider_catalog import CatalogError
        with self.assertRaises(CatalogError):
            evaluate_access(data)
