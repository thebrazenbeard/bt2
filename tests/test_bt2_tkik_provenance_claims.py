"""T'Kal packet replay must not attest a fabricated native reviewer."""

import copy
import json
import os
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_bt2_tkik_proceeding import run  # noqa: E402


class PacketCustodyTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("TKIK_EXACT_REPO"),
                         "exact external T'Kal source required")
    def test_fabricated_reviewer_is_rejected_and_audited_replay_unattested(self):
        packet_path = (ROOT / "coding_models/personality/iterations/tkik/"
                       "BT2-PERSONA-20261029.packet.json")
        original = json.loads(packet_path.read_text(encoding="utf-8"))
        forged = copy.deepcopy(original)
        forged["reviews"][0]["reviewer_id"] = "/root/fabricated-undispatched-agent"
        # The underlying protocol accepts reviewer names as packet data.
        # The bounded BT2 bridge must reject edits to its audited packet.
        with self.assertRaisesRegex(ValueError, "reviewer assignment"):
            run(forged, Path(os.environ["TKIK_EXACT_REPO"]))
        result = run(original, Path(os.environ["TKIK_EXACT_REPO"]))

        self.assertEqual(result["verdict"], "REFINE")
        self.assertIn("protocol_mode", result)
        self.assertEqual(result["protocol_mode"], "PACKET_REPLAY")
        self.assertEqual(result["schema"], "BT2_TKIK_DECLARED_REVIEW_V2")
        self.assertFalse(result["native_dispatch_receipts_verified"])
        self.assertFalse(result["live_cross_examination_attested"])
        self.assertEqual(result["declared_reviewer_ids"][0],
                         "/root/identity_nine")
        self.assertNotIn("native_reviewer_ids", result)


if __name__ == "__main__":
    unittest.main()
