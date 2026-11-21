import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from signal_ingest.provider_bridge.semantic_exchange import exchange, SemanticExchangeError

HEAD="a"*40

def frame():
    return {
        "schema":"BT2_SEMANTIC_EVIDENCE_EXCHANGE_INPUT_V1",
        "source":{
            "repository":"thebrazenbeard/semanticatlas",
            "head":HEAD,
            "source_ref":f"https://github.com/thebrazenbeard/semanticatlas/blob/{HEAD}/schemas/semantic_atlas_v0.1.schema.json",
            "surface":"RESEARCH_STAGING",
            "evidence_class":"SOURCE",
            "vsns_repository":"thebrazenbeard/vera",
            "vsns_head":"c"*40,
            "vsns_ref":"https://github.com/thebrazenbeard/vera/blob/"+("c"*40)+"/runtime_cohesion/vsns_reception.py",
            "empathy_repository":"thebrazenbeard/empathy",
            "empathy_head":"d"*40,
            "empathy_ref":"https://github.com/thebrazenbeard/empathy/blob/"+("d"*40)+"/empathy_research/integration_contract.py",
        },
        "vsns":{
            "schema":"VERA_VSNS_RECEPTION_RESULT_V0_1",
            "speech_act":"SHARING",
            "reality_layer":"CONVERSATIONAL_SYMBOLIC",
            "event_class":"PROPOSED_ONLY",
            "interpretation_status":"SINGLE_CANDIDATE_UNVERIFIED",
            "candidates":[{"meaning_id":"salience.test","domain":"RELATIONAL",
                           "claimed_evidence_class":"SYNTHETIC_TEST",
                           "evidence_origin_trust":"UNVERIFIED_CALLER_ASSERTION",
                           "salience":0.98,"uncertainty":0.1,
                           "boundary_tension":0.95,"semantic_relevance":0.99}],
            "interrupt_suggested":True,
            "calibration":"DETERMINISTIC_HEURISTIC_NOT_EMPIRICALLY_VALIDATED",
            "claim_ceiling":"SEMANTIC_SALIENCE_ADVISORY_ONLY",
            "provider_currentness":"UNVERIFIED",
            "behavioral_qualification":"NOT_ESTABLISHED",
            "phenomenology":"UNRESOLVED",
            "consent_effect":"NONE","authority_effect":"NONE",
            "decision_effect":"NONE","action_effect":"NONE",
            "identity_effect":"NONE","memory_admission_effect":"NONE",
        },
        "empathy":{
            "schema":"EMPATHY_RESPONSE_POLICY_HINT_V1",
            "consumer":"RESPONSE_POLICY_ONLY",
            "policy":"PRESERVE_PLAY",
            "reason_code":"CURRENT_MUTUAL_UPTAKE",
            "confidence_band":"HIGH_SCORE",
            "supporting_evidence_ids":["ev_"+"b"*32],
            "superseded_hypothesis_ids":[],
            "focus_needed":False,
            "authority":"NONE","persistence":"EPHEMERAL",
            "volition_want_authority":False,"effect_authority":False,
        },
    }


class SemanticHostile(unittest.TestCase):
    def test_01_high_salience_never_truth_or_consent(self):
        r=exchange(frame())
        self.assertEqual(r["truth"],"NOT_DETERMINED")
        self.assertEqual(r["consent"],"NOT_GRANTED")
        self.assertEqual(r["memory_admission"],"NONE")
        self.assertFalse(r["independently_authenticated"])
        self.assertEqual(r["side_effects"],[])

    def test_02_empathy_preserve_play_is_not_permission(self):
        r=exchange(frame())
        self.assertEqual(r["empathy_policy_hint"],"PRESERVE_PLAY")
        self.assertEqual(r["action_authority"],"NONE")
        self.assertEqual(r["autobiographical_admission"],"NONE")

    def test_03_forged_vsns_effect_rejected(self):
        x=frame()
        x["vsns"]["consent_effect"]="GRANTED"
        with self.assertRaises(SemanticExchangeError):
            exchange(x)

    def test_04_foreign_unpinned_atlas_locator_rejected(self):
        x=frame()
        x["source"]["source_ref"]="https://github.com/thebrazenbeard/semanticatlas/blob/main/schemas/semantic_atlas_v0.1.schema.json"
        with self.assertRaises(SemanticExchangeError):
            exchange(x)

    def test_05_raw_personal_text_not_accepted(self):
        x=frame()
        x["utterance"]="PRIVATE_TRANSCRIPT_SHOULD_NOT_BE_PRESENT"
        with self.assertRaises(SemanticExchangeError):
            exchange(x)

    def test_06_empathy_standing_consent_forbidden(self):
        x=frame()
        x["empathy"]["effect_authority"]=True
        with self.assertRaises(SemanticExchangeError):
            exchange(x)

    def test_07_semantic_ids_are_opaque_not_person_model(self):
        r=exchange(frame())
        self.assertEqual(r["candidate_meaning_ids"],["candidate_1"])
        self.assertEqual(r["vsns_source_head"],"c"*40)
        self.assertEqual(r["empathy_source_head"],"d"*40)
        self.assertNotIn("ev_b",str(r))
        self.assertEqual(r["semantic_currentness"],"UNVERIFIED_SOURCE_SNAPSHOT")

    def test_11_freeform_meaning_id_never_echoed_to_exchange_output(self):
        x=frame()
        secret_id="PRIVATE_MEMBER_NAME_AND_LOCATION"
        x["vsns"]["candidates"][0]["meaning_id"]=secret_id
        result=exchange(x)
        self.assertNotIn(secret_id,str(result))
        self.assertNotIn("PRIVATE_MEMBER",str(result))
        self.assertEqual(len(result["candidate_meaning_ids"]),1)
        self.assertEqual(result["candidate_meaning_ids"],["candidate_1"])

    def test_12_meaning_id_alias_is_ephemeral_and_not_cross_frame_linkable(self):
        first=frame()
        second=frame()
        second["vsns"]["candidates"][0]["meaning_id"]="alternative.label"
        a=exchange(first)
        b=exchange(second)
        self.assertEqual(a["candidate_meaning_ids"],exchange(frame())["candidate_meaning_ids"])
        self.assertEqual(a["candidate_meaning_ids"],b["candidate_meaning_ids"])
        self.assertEqual(a["memory_admission"],"NONE")
        self.assertEqual(b["consent"],"NOT_GRANTED")

    def test_10_cross_repo_semantic_head_locator_mismatch_refused(self):
        x=frame()
        x["source"]["vsns_ref"]="https://github.com/thebrazenbeard/vera/blob/main/runtime_cohesion/vsns_reception.py"
        with self.assertRaises(SemanticExchangeError):
            exchange(x)
    def test_09_extreme_unbounded_integer_is_cleanly_rejected(self):
        x=frame()
        x["vsns"]["candidates"][0]["salience"]=10**1000
        with self.assertRaises(SemanticExchangeError):
            exchange(x)
    def test_08_atlas_source_staging_not_canon(self):
        r=exchange(frame())
        self.assertEqual(r["semantic_authority"],"RESEARCH_ONLY")
        self.assertEqual(r["phenomenology"],"UNRESOLVED")

    def test_13_unhashable_domain_or_evidence_class_rejected_with_bounded_error(self):
        for field in ("domain", "claimed_evidence_class"):
            for payload in (["MODEL_INFERENCE"], {"candidate": "USER_DIRECT"}):
                with self.subTest(field=field, form=type(payload).__name__):
                    x=frame()
                    x["vsns"]["candidates"][0][field]=payload
                    with self.assertRaisesRegex(
                        SemanticExchangeError, "UNTRUSTED_SEMANTIC_CANDIDATE"
                    ):
                        exchange(x)

    def test_14_unhashable_empathy_policy_is_bounded_rejection(self):
        for payload in (["PRESERVE_PLAY"], {"policy": "TASK_DIRECT"}):
            with self.subTest(form=type(payload).__name__):
                x=frame()
                x["empathy"]["policy"]=payload
                with self.assertRaisesRegex(SemanticExchangeError, "EMPATHY_AUTHORITY_FENCE"):
                    exchange(x)


if __name__=="__main__":
    unittest.main()