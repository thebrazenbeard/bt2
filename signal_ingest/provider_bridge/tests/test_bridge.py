import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from signal_ingest.provider_bridge.v1 import bridge, BridgeError


HEAD_A="a"*40
HEAD_B="b"*40
NOW="2026-11-20T21:30:00Z"
CUTOFF="2026-11-20T18:00:00Z"


def packet():
    return {
        "schema":"BT2_GITHUB_PROVIDER_BRIDGE_INPUT_V1",
        "snapshot":{
            "observed_at":NOW,
            "host_access_cutoff":CUTOFF,
            "subjects":[
                {"repository":"example/app","subject":"pr:12","head":HEAD_B,
                 "runtime_required":False,"reported_runtime_status":"UNKNOWN"}
            ],
        },
        "receipts":[
            {"event_id":"ci-first","repository":"example/app","subject":"pr:12",
             "kind":"CI_RESULT","status":"FAILED","head":HEAD_B,
             "incident_key":"test-failure-300","observed_at":"2026-11-20T21:29:00Z",
             "source_ref":"https://github.com/example/app/actions/runs/300",
             "provider_response_sha256":"1"*64,
             "claimed_owner":"author-reported","claimed_reviewer":None,
             "claims_authenticated":True,"transport":"GITHUB_API_SESSION_READONLY"}
        ],
        "seen_receipt_digests":[],
    }


class ProviderBridgeHostile(unittest.TestCase):
    def test_01_normalize_real_provider_shape_to_exact_signal_contract(self):
        r=bridge(packet())
        self.assertEqual(r["schema"],"BT2_GITHUB_PROVIDER_BRIDGE_OUTPUT_V1")
        self.assertEqual(r["signal"]["schema"],"BT2_ECOSYSTEM_SIGNAL_OUTPUT_V1")
        self.assertEqual(r["signal"]["observations"][0]["head_currentness"],"EXACT_HEAD")
        self.assertEqual(r["signal"]["observations"][0]["categories"],["CI_RESULT"])
        self.assertFalse(r["signal"]["release_permission"])
        self.assertFalse(r["signal"]["observations"][0]["independently_authenticated"])

    def test_02_duplicate_ci_reports_one_underlying_incident(self):
        x=packet()
        second=copy.deepcopy(x["receipts"][0])
        second["event_id"]="ci-secondary"
        x["receipts"].append(second)
        r=bridge(x)
        self.assertEqual(len(r["signal"]["observations"]),1)
        self.assertEqual(len(r["signal"]["observations"][0]["reports"]),2)

    def test_03_duplicate_exact_report_suppressed_by_seen_digest(self):
        first=bridge(packet())
        key=first["accepted_receipt_digests"][0]
        x=packet()
        x["seen_receipt_digests"]=[key]
        second=bridge(x)
        self.assertEqual(second["accepted_receipt_digests"],[])
        self.assertEqual(second["replay_suppressed"],[key])
        self.assertEqual(second["signal"]["observations"],[])
        self.assertEqual(second["replay_scope"],"CALLER_PROVIDED_CACHE_NOT_INDEPENDENT")

    def test_04_conflicting_same_event_id_refused(self):
        x=packet()
        bad=copy.deepcopy(x["receipts"][0])
        bad["status"]="PASSED"
        x["receipts"].append(bad)
        with self.assertRaises(BridgeError):
            bridge(x)

    def test_05_new_head_makes_old_ci_stale_not_qualified(self):
        x=packet()
        x["receipts"][0]["head"]=HEAD_A
        r=bridge(x)
        self.assertEqual(r["signal"]["observations"][0]["head_currentness"],"STALE_HEAD")
        self.assertFalse(r["signal"]["observations"][0]["candidate_observation"])

    def test_06_green_ci_cannot_grant_release(self):
        x=packet()
        x["receipts"][0]["status"]="PASSED"
        r=bridge(x)
        self.assertFalse(r["signal"]["release_permission"])
        self.assertFalse(r["signal"]["observations"][0]["release_permission"])

    def test_07_credential_claim_does_not_verify_reporter(self):
        r=bridge(packet())
        self.assertEqual(r["source_authentication"],"UNVERIFIED_NO_SIGNED_RECEIPT")
        self.assertFalse(r["independently_authenticated"])
        self.assertFalse(r["signal"]["observations"][0]["reports"][0]["owner_verified"])

    def test_08_wrong_repo_source_url_is_rejected(self):
        x=packet()
        x["receipts"][0]["source_ref"]="https://github.com/foreign/app/actions/runs/300"
        with self.assertRaises(BridgeError):
            bridge(x)

    def test_09_untrusted_bus_provider_does_not_masquerade_as_api(self):
        x=packet()
        x["receipts"][0]["transport"]="BUS_COMMENT"
        with self.assertRaises(BridgeError):
            bridge(x)

    def test_10_host_cutoff_suppresses_effects(self):
        r=bridge(packet())
        self.assertEqual(r["signal"]["host_task_start_permitted"],"NO_EXPIRED_CUTOFF")
        self.assertEqual(r["signal"]["host_task_proposals"],[])
        self.assertEqual(r["signal"]["external_effects"],[])
        self.assertEqual(r["side_effects"],[])

    def test_11_missing_runtime_remains_unknown(self):
        x=packet()
        x["snapshot"]["subjects"].append({
            "repository":"example/app","subject":"lantern","head":None,
            "runtime_required":True,"reported_runtime_status":"REPORTED_QUALIFIED"})
        r=bridge(x)
        self.assertEqual(r["signal"]["runtime"][0]["currentness"],"UNKNOWN")
        self.assertEqual(r["signal"]["runtime"][0]["availability"],"UNKNOWN")

    def test_13_replay_cache_cannot_overgrow_bound(self):
        x=packet()
        x["seen_receipt_digests"]=[f"{i:064x}" for i in range(512)]
        with self.assertRaisesRegex(BridgeError,"REPLAY_CACHE_CAPACITY_REQUIRES_EXTERNAL_CHECKPOINT"):
            bridge(x)
    def test_12_source_hash_must_be_exact_digest(self):
        x=packet()
        x["receipts"][0]["provider_response_sha256"]="not-a-hash"
        with self.assertRaises(BridgeError):
            bridge(x)

    def test_14_bounded_adjacent_batch_equivocation_rejected(self):
        from signal_ingest.provider_bridge.v1 import bridge_with_predecessor
        first = packet()
        previous = bridge(first)
        changed = packet()
        changed["receipts"][0]["status"] = "PASSED"
        changed["seen_receipt_digests"] = previous["next_seen_receipt_digests"]
        # Existing V1 has no event-ID history across separate calls.
        self.assertEqual(len(bridge(changed)["accepted_receipt_digests"]), 1)
        with self.assertRaisesRegex(BridgeError, "CROSS_BATCH_EVENT_ID_CONFLICT"):
            bridge_with_predecessor(first, changed)

    def test_15_bounded_adjacent_batch_replay_reset_rejected(self):
        from signal_ingest.provider_bridge.v1 import bridge_with_predecessor
        first = packet()
        omitted = packet()
        self.assertEqual(len(bridge(omitted)["accepted_receipt_digests"]), 1)
        with self.assertRaisesRegex(BridgeError, "CROSS_BATCH_REPLAY_HISTORY_DROPPED"):
            bridge_with_predecessor(first, omitted)

    def test_16_bounded_adjacent_batch_valid_replay_and_new_event(self):
        from signal_ingest.provider_bridge.v1 import bridge_with_predecessor
        first = packet()
        old = bridge(first)
        second = packet()
        second["seen_receipt_digests"] = old["next_seen_receipt_digests"]
        new = copy.deepcopy(second["receipts"][0])
        new["event_id"] = "ci-second"
        new["status"] = "PASSED"
        new["incident_key"] = "second-incident-301"
        new["source_ref"] = "https://github.com/example/app/actions/runs/301"
        second["receipts"].append(new)
        result = bridge_with_predecessor(first, second)
        self.assertEqual(len(result["accepted_receipt_digests"]), 1)
        self.assertEqual(len(result["replay_suppressed"]), 1)
        self.assertEqual(len(result["next_seen_receipt_digests"]), 2)
        self.assertEqual(result["memory_admission"], "NONE")
        self.assertFalse(result["independently_authenticated"])
        self.assertFalse(result["signal"]["release_permission"])
        self.assertEqual(result["replay_scope"], "CALLER_PROVIDED_CACHE_NOT_INDEPENDENT")

    def test_17_bounded_adjacent_batch_rejects_bad_predecessor(self):
        from signal_ingest.provider_bridge.v1 import bridge_with_predecessor
        first = packet()
        first["receipts"][0]["head"] = "not-sha"
        with self.assertRaises((BridgeError, ValueError)):
            bridge_with_predecessor(first, packet())


    def test_18_predecessor_helper_preserves_unmodified_v1_contract(self):
        from signal_ingest.provider_bridge.v1 import bridge_with_predecessor
        first = packet()
        next_doc = packet()
        next_doc["seen_receipt_digests"] = bridge(first)["next_seen_receipt_digests"]
        direct = bridge(next_doc)
        reconciled = bridge_with_predecessor(first, next_doc)
        self.assertEqual(reconciled, direct)
        self.assertEqual(reconciled["replay_scope"], "CALLER_PROVIDED_CACHE_NOT_INDEPENDENT")
        self.assertEqual(reconciled["source_authentication"], "UNVERIFIED_NO_SIGNED_RECEIPT")
        self.assertEqual(reconciled["memory_admission"], "NONE")
        self.assertEqual(reconciled["side_effects"], [])


    def test_19_consistent_caller_forgery_still_has_no_trust(self):
        """Passing two self-consistent caller documents is not attestation."""
        from signal_ingest.provider_bridge.v1 import bridge_with_predecessor
        original = packet()
        forged_predecessor = copy.deepcopy(original)
        forged_predecessor["receipts"][0]["status"] = "PASSED"
        self.assertNotEqual(bridge(original)["accepted_receipt_digests"],
                            bridge(forged_predecessor)["accepted_receipt_digests"])
        forged_followup = copy.deepcopy(forged_predecessor)
        forged_followup["seen_receipt_digests"] = (
            bridge(forged_predecessor)["next_seen_receipt_digests"]
        )
        r = bridge_with_predecessor(forged_predecessor, forged_followup)
        self.assertEqual(r["accepted_receipt_digests"], [])
        self.assertFalse(r["independently_authenticated"])
        self.assertEqual(r["memory_admission"], "NONE")
        self.assertFalse(r["signal"]["release_permission"])


if __name__=="__main__":
    unittest.main()