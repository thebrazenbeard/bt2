"""Falsification tests for the native-agent T'Kal-in-ket REFINE bridge."""

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_bt2_tkik_proceeding import run, validate_packet, TKIK_COMMIT  # noqa: E402


PACKET = ROOT / "coding_models/personality/iterations/tkik/BT2-PERSONA-20261029.packet.json"
RESULT = ROOT / "coding_models/personality/iterations/tkik/BT2-PERSONA-20261029.declared.result.json"


class Bt2TkalProceedingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_real_attributed_packet_is_valid_for_refine(self):
        packet = validate_packet(copy.deepcopy(self.original))
        self.assertEqual({r["lens"] for r in packet["reviews"]},
                         {"purist_logic", "pragmatism", "bridge"})
        self.assertEqual(len({r["reviewer_id"] for r in packet["reviews"]}), 3)
        self.assertTrue(all(c["status"] == "CONCEDED" for c in packet["challenges"]))

    def test_rejects_pretended_model_execution_ref(self):
        packet = copy.deepcopy(self.original)
        packet["reviews"][0]["execution_ref"] = "fake-model-invocation"
        with self.assertRaisesRegex(ValueError, "masquerade"):
            validate_packet(packet)

    def test_rejects_missing_peer_or_duplicate_identity(self):
        packet = copy.deepcopy(self.original)
        packet["reviews"][2]["reviewer_id"] = packet["reviews"][1]["reviewer_id"]
        with self.assertRaisesRegex(ValueError, "distinct native"):
            validate_packet(packet)
        packet = copy.deepcopy(self.original)
        packet["reviews"][0]["lens"] = "pragmatism"
        with self.assertRaisesRegex(ValueError, "missing or duplicate"):
            validate_packet(packet)

    def test_rejects_unresolved_or_waived_attack_as_concession(self):
        for status in ("OPEN", "PARTLY_ANSWERED", "UNRESOLVED", "WAIVED", "ANSWERED"):
            packet = copy.deepcopy(self.original)
            packet["challenges"][0]["status"] = status
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "conceded REFINE"):
                validate_packet(packet)

    def test_rejects_empty_claim_and_unbounded_evidence(self):
        packet = copy.deepcopy(self.original)
        packet["hypothesis"] = ""
        with self.assertRaisesRegex(ValueError, "missing hypothesis"):
            validate_packet(packet)
        packet = copy.deepcopy(self.original)
        packet["evidence"] *= 20
        with self.assertRaisesRegex(ValueError, "bounded evidence"):
            validate_packet(packet)

    def test_rejects_unverified_derived_claim_and_custody_overclaims(self):
        for field, text in (
            ("refined_claim", "All thirteen neural identities independently verified and ready"),
            ("review_custody_limitations", "Cryptographically independent model quorum verified"),
            ("rationale", "SUSTAIN proven by the reviewers"),
        ):
            packet = copy.deepcopy(self.original)
            packet[field] = text
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "audited packet"):
                validate_packet(packet)

    def test_rejects_forged_identity_and_misbound_challenge_lens(self):
        packet = copy.deepcopy(self.original)
        packet["reviews"][0]["reviewer_id"] = "fabricated-reviewer"
        with self.assertRaisesRegex(ValueError, "reviewer assignment"):
            validate_packet(packet)
        packet = copy.deepcopy(self.original)
        packet["challenges"][1]["lens"] = "purist_logic"
        with self.assertRaisesRegex(ValueError, "challenge lens assignment"):
            validate_packet(packet)

    def test_rejects_changed_review_assertion_even_if_id_is_reused(self):
        packet = copy.deepcopy(self.original)
        packet["reviews"][0]["finding"] = "We independently tested all thirteen weights"
        with self.assertRaisesRegex(ValueError, "audited packet"):
            validate_packet(packet)

    def test_checked_in_v2_result_is_packet_bound_and_does_not_overstate_native_custody(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        packet_bytes = json.dumps(self.original, sort_keys=True,
                                  separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.assertEqual(result["packet_sha256"], hashlib.sha256(packet_bytes).hexdigest())
        self.assertEqual(result["tkik_commit"], TKIK_COMMIT)
        self.assertEqual(result["schema"], "BT2_TKIK_DECLARED_REVIEW_V2")
        self.assertEqual(result["declared_reviewer_ids"], [
            next(r["reviewer_id"] for r in self.original["reviews"] if r["lens"] == lens)
            for lens in ("purist_logic", "pragmatism", "bridge")
        ])
        self.assertNotIn("native_reviewer_ids", result)
        self.assertFalse(result["native_dispatch_receipts_verified"])
        self.assertEqual(result["protocol_mode"], "PACKET_REPLAY")
        self.assertFalse(result["live_cross_examination_attested"])
        self.assertTrue(result["packet_authored_custody_text_unverified"])

    @unittest.skipUnless(os.environ.get("TKIK_EXACT_REPO"),
                         "external pinned T'Kal checkout required for real protocol integration")
    def test_real_pinned_tkal_core_runs_refine_not_sustain(self):
        repo = Path(os.environ["TKIK_EXACT_REPO"])
        result = run(self.original, repo)
        self.assertEqual(result["tkik_commit"], TKIK_COMMIT)
        self.assertEqual(result["verdict"], "REFINE")
        self.assertFalse(result["independent_model_or_host_attestation"])
        self.assertEqual(len(result["challenge_statuses"]), 3)
        self.assertNotIn("native_reviewer_ids", result)
        self.assertFalse(result["native_dispatch_receipts_verified"])
        self.assertEqual(result["protocol_mode"], "PACKET_REPLAY")
        self.assertFalse(result["live_cross_examination_attested"])
        self.assertTrue(result["packet_authored_custody_text_unverified"])
        self.assertEqual(result, json.loads(RESULT.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
