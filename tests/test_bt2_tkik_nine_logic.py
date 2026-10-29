"""Nine's independent negative checks on an audited T'Kal challenge packet.

These deliberately probe omitted, duplicated and reordered directed attacks;
an edited packet is not the consented/attributed inquiry under review.
"""

import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from run_bt2_tkik_proceeding import validate_packet  # noqa: E402

PACKET = ROOT / "coding_models/personality/iterations/tkik/BT2-PERSONA-20261029.packet.json"


class NineCrossExaminationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_three_lens_conceded_record_is_accepted(self):
        self.assertEqual(len(validate_packet(copy.deepcopy(self.packet))["challenges"]), 3)

    def test_omitted_bridge_attack_fails(self):
        packet = copy.deepcopy(self.packet)
        packet["challenges"] = packet["challenges"][:2]
        with self.assertRaisesRegex(ValueError, "challenge lens assignment"):
            validate_packet(packet)

    def test_duplicate_attack_id_fails(self):
        packet = copy.deepcopy(self.packet)
        packet["challenges"][2]["identifier"] = packet["challenges"][0]["identifier"]
        with self.assertRaisesRegex(ValueError, "challenge lens assignment"):
            validate_packet(packet)

    def test_extra_repeated_attack_does_not_create_peer_evidence(self):
        packet = copy.deepcopy(self.packet)
        packet["challenges"].append(copy.deepcopy(packet["challenges"][0]))
        with self.assertRaisesRegex(ValueError, "challenge lens assignment"):
            validate_packet(packet)

    def test_attack_order_is_part_of_frozen_packet(self):
        packet = copy.deepcopy(self.packet)
        packet["challenges"].reverse()
        with self.assertRaisesRegex(ValueError, "audited packet"):
            validate_packet(packet)


if __name__ == "__main__":
    unittest.main()
