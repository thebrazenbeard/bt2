import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from provider_catalog import evaluate_catalog


def sample():
    return {
        "schema":"BT2_MEMORY_PROVIDER_CATALOG_INPUT_V1",
        "provider_role":"VERA_MEMORY",
        "observation_time":"2026-11-20T20:00:00Z",
        "source_ref":"synthetic://catalog/vera",
        "relations":[
            {"schema":"public","name":name,"kind":"r","rls_enabled":True}
            for name in (
                "vera_memory_epoch_subjects_v1",
                "vera_memory_epoch_events_v1",
                "vera_memory_epoch_provider_receipts_v1",
                "vera_memory_epoch_archive_receipts_v1")
        ] + [
            {"schema":"semantic_atlas","name":name,"kind":"r","rls_enabled":True}
            for name in ("runtime_objects","runtime_snapshots","capture_policy")
        ],
        "routines":[
            {"schema":"public","name":"vera_memory_epoch_get_status_v1"},
            {"schema":"semantic_atlas","name":"search_current_runtime_objects_v11"}
        ],
    }


class ProviderCatalogRed(unittest.TestCase):
    def test_missing_currentness_function_must_not_qualify_catalog(self):
        payload=sample()
        payload["routines"]=payload["routines"][:1]
        result=evaluate_catalog(payload)
        self.assertEqual(result["verdict"],"MISSING_REQUIREMENTS")
        self.assertEqual(result["memory_admission"],"NONE")

if __name__ == "__main__":
    unittest.main()
class ProviderCatalogHostile(unittest.TestCase):
    def test_complete_catalog_is_still_not_authenticated_runtime_or_admitted(self):
        result=evaluate_catalog(sample() | {"independently_authenticated":True})
        self.assertEqual(result["verdict"],"CATALOG_PRESENT_UNQUALIFIED")
        self.assertFalse(result["independently_authenticated"])
        self.assertEqual(result["runtime_currentness"],"UNKNOWN_NOT_PROBED")
        self.assertEqual(result["memory_admission"],"NONE")
        self.assertEqual(result["release_authorization"],"NONE")
        self.assertEqual(result["side_effects"],[])

    def test_one_rls_disabled_table_must_hold(self):
        e=sample()
        e["relations"][0]["rls_enabled"]=False
        r=evaluate_catalog(e)
        self.assertEqual(r["verdict"],"MISSING_REQUIREMENTS")
        self.assertEqual(len(r["rls_disabled_objects"]),1)
        self.assertEqual(r["memory_admission"],"NONE")

    def test_tattler_without_vera_catalog_is_separate_not_missing(self):
        e=sample()
        e["provider_role"]="TATTLER_REVIEW"
        e["relations"]=[{"schema":"public","name":"masamune_webhook_delivery","kind":"r","rls_enabled":True}]
        e["routines"]=[]
        r=evaluate_catalog(e)
        self.assertEqual(r["verdict"],"NOT_APPLICABLE_REVIEW_PROVIDER")
        self.assertFalse(r["catalog_conformance_only"])

    def test_tattler_vera_memory_table_is_scope_conflict(self):
        e=sample()
        e["provider_role"]="TATTLER_REVIEW"
        r=evaluate_catalog(e)
        self.assertEqual(r["verdict"],"CROSS_PROJECT_SCOPE_CONFLICT")
        self.assertFalse(r["catalog_conformance_only"])

    def test_duplicate_catalog_identity_rejected(self):
        from provider_catalog import CatalogError
        e=sample()
        e["relations"].append(dict(e["relations"][0]))
        with self.assertRaises(CatalogError):
            evaluate_catalog(e)

    def test_payload_cannot_launder_private_data(self):
        from provider_catalog import CatalogError
        e=sample()
        e["rows"]=[{"id":"PRIVATE_PERSONAL_CONTENT"}]
        with self.assertRaises(CatalogError):
            evaluate_catalog(e)

    def test_private_source_ref_never_reflected_in_output(self):
        from provider_catalog import canonical
        e=sample()
        e["source_ref"]="private://internal-account-id-sensitive"
        text=canonical(evaluate_catalog(e))
        self.assertNotIn("internal-account-id-sensitive",text)
        self.assertNotIn("private://",text)

    def test_unknown_and_malformed_auth_claims(self):
        from provider_catalog import CatalogError
        e=sample()
        e["independently_authenticated"]="yes"
        with self.assertRaises(CatalogError):
            evaluate_catalog(e)

    def test_invalid_calendar_day_is_rejected(self):
        from provider_catalog import CatalogError
        e=sample()
        e["observation_time"]="2026-02-31T12:00:00Z"
        with self.assertRaises(CatalogError):
            evaluate_catalog(e)

    def test_wrong_shape_catalog_objects_rejected(self):
        from provider_catalog import CatalogError
        e=sample()
        e["relations"][0]["owner_password"]="should-never-be-accepted"
        with self.assertRaises(CatalogError):
            evaluate_catalog(e)

    def test_no_catalog_claims_network_or_memory_write(self):
        result=evaluate_catalog(sample())
        self.assertEqual(result["source_heads_currentness"],"UNKNOWN_NOT_VERIFIED")
        self.assertEqual(result["memory_read"],"NONE")
        self.assertFalse(result["independently_authenticated"])

    def test_bad_expected_object_kind_cannot_satisfy_required_table(self):
        e=sample()
        e["relations"][0]["kind"]="v"
        result=evaluate_catalog(e)
        self.assertEqual(result["verdict"],"MISSING_REQUIREMENTS")


class ProviderFixtureBoundary(unittest.TestCase):
    def test_two_synthetic_fixtures_have_distinct_scopes(self):
        import json
        base=Path(__file__).resolve().parents[1]
        vera=json.loads((base/"fixtures"/"vera_synthetic.json").read_text(encoding="utf-8"))
        tattler=json.loads((base/"fixtures"/"tattler_synthetic.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluate_catalog(vera)["verdict"],"CATALOG_PRESENT_UNQUALIFIED")
        self.assertEqual(evaluate_catalog(tattler)["verdict"],"NOT_APPLICABLE_REVIEW_PROVIDER")
        self.assertNotEqual(vera["provider_role"],tattler["provider_role"])

    def test_json_duplicate_keys_and_nonfinite_values_rejected(self):
        from provider_catalog import strict_json, CatalogError
        for value in ('{"schema":"X","schema":"Y"}','{"a":NaN}','{"a":Infinity}','[]'):
            with self.subTest(value=value),self.assertRaises(CatalogError):
                strict_json(value)

    def test_disjoint_repo_contracts_pinned_as_source_not_live_authority(self):
        import json
        p=Path(__file__).resolve().parents[1]/"SOURCE_BINDINGS_V1.json"
        b=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(b["effect_class"],"SOURCE_INSPECTION_ONLY")
        self.assertEqual(b["currentness"],"UNVERIFIED_AFTER_RETRIEVAL")
        self.assertEqual(set(b["source_snapshot"]),{
            "thebrazenbeard/stm","thebrazenbeard/deepmemorystorage",
            "thebrazenbeard/vera-mono","thebrazenbeard/bt2"})
        self.assertTrue(all(len(x["head"])==40 for x in b["source_snapshot"].values()))

    def test_cli_json_is_reproducible_without_provider_calls(self):
        import json
        import subprocess
        root=Path(__file__).resolve().parents[1]
        args=[sys.executable,str(root/"provider_catalog.py"),
              str(root/"fixtures"/"vera_synthetic.json")]
        first=subprocess.run(args,capture_output=True,text=True,check=True)
        second=subprocess.run(args,capture_output=True,text=True,check=True)
        self.assertEqual(first.stdout,second.stdout)
        out=json.loads(first.stdout)
        self.assertEqual(out["memory_read"],"NONE")
        self.assertEqual(out["public_api_grants"],"UNKNOWN_NOT_INSPECTED")

class BoundSourceRevision(unittest.TestCase):
    def test_bt2_conformance_contract_is_bound_to_actual_pr_head_not_main(self):
        import json
        root=Path(__file__).resolve().parents[1]
        manifest=json.loads((root/"SOURCE_BINDINGS_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_snapshot"]["thebrazenbeard/bt2"]["head"],
                         "a832363060b9cc6fd457ca1c3a9686a6a7da03b0",
                         "PR124-only contract must never be attributed to BT2 main")
