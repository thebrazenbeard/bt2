"""Independent Lappy-only qualification against explicit source checkouts."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

QUALIFY = Path(__file__).with_name("qualify.py")
ROOT = os.environ.get("BT2_VERA_COGNITIVE_REPOS")

class CognitiveVerticalSliceTests(unittest.TestCase):
    @unittest.skipUnless(ROOT, "set BT2_VERA_COGNITIVE_REPOS to explicit pinned checkouts")
    def test_evidence_to_want_to_tool_free_turn_and_verified_completion(self):
        with tempfile.TemporaryDirectory(prefix="bt2-cognitive-slice-") as tmp:
            result = subprocess.run(
                [sys.executable, str(QUALIFY), "--repos", ROOT, "--state", tmp],
                capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = json.loads(result.stdout)
            self.assertTrue(output["source_heads_verified"])
            self.assertTrue(output["observed_want_survived_restart"])
            self.assertTrue(output["meso_local_sequence_persisted"])
            self.assertTrue(output["tool_free_model_turn"])
            self.assertTrue(output["model_text_not_completion"])
            self.assertTrue(output["stale_completion_rejected"])
            self.assertTrue(output["independently_admitted_completion"])
            self.assertTrue(output["idempotent_replay"])
            self.assertFalse(output["effect_authority_granted"])

if __name__ == "__main__":
    unittest.main()
