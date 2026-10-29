"""Mune adversarial custody checks against the exact audited T'Kal packet."""

import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from run_bt2_tkik_proceeding import validate_packet  # noqa: E402


PACKET = ROOT / "coding_models/personality/iterations/tkik/BT2-PERSONA-20261029.packet.json"


class MuneTkalAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_three_whitespace_aliases_do_not_forge_independent_reviewers(self):
        forged = copy.deepcopy(self.original)
        forged["reviews"][0]["reviewer_id"] = "/root/identity_nine"
        forged["reviews"][1]["reviewer_id"] = " /root/identity_nine"
        forged["reviews"][2]["reviewer_id"] = "/root/identity_nine "
        with self.assertRaisesRegex(ValueError, "reviewer assignment|audited packet"):
            validate_packet(forged)

    def test_duplicate_challenge_id_is_not_accepted_as_separate_exchange(self):
        forged = copy.deepcopy(self.original)
        forged["challenges"][1]["identifier"] = forged["challenges"][0]["identifier"]
        with self.assertRaisesRegex(ValueError, "challenge lens assignment|audited packet"):
            validate_packet(forged)


if __name__ == "__main__":
    unittest.main()
