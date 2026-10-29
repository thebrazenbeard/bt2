"""Falsification tests for the native-agent T'Kal-in-ket REFINE bridge."""

import copy
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_bt2_tkik_proceeding import run, validate_packet, TKIK_COMMIT  # noqa: E402


PACKET = ROOT / "coding_models/personality/iterations/tkik/BT2-PERSONA-20261029.packet.json"


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

    @unittest.skipUnless(os.environ.get("TKIK_EXACT_REPO"),
                         "external pinned T'Kal checkout required for real protocol integration")
    def test_real_pinned_tkal_core_runs_refine_not_sustain(self):
        repo = Path(os.environ["TKIK_EXACT_REPO"])
        result = run(self.original, repo)
        self.assertEqual(result["tkik_commit"], TKIK_COMMIT)
        self.assertEqual(result["verdict"], "REFINE")
        self.assertFalse(result["independent_model_or_host_attestation"])
        self.assertEqual(len(result["challenge_statuses"]), 3)


if __name__ == "__main__":
    unittest.main()
