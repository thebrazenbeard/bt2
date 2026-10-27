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
            self.assertTrue(output["tool_free_model_turn"])
            self.assertTrue(output["model_text_not_completion"])
            self.assertTrue(output["stale_completion_rejected"])
            self.assertTrue(output["host_verified_fixture_completion"])
            self.assertFalse(output["independently_admitted_completion"])
            self.assertTrue(output["idempotent_replay"])
            self.assertFalse(output["effect_authority_granted"])
            self.assertTrue(output["semantic_atlas_committed_bundle_verified"])
            self.assertTrue(output["personification_active_source_bounded"])
            self.assertTrue(output["committed_bundle_tamper_rejected"])
            self.assertTrue(output["unchanged_fixture_completion_rejected"])
            self.assertTrue(output["model_false_success_did_not_complete"])

    @unittest.skipUnless(ROOT, "set BT2_VERA_COGNITIVE_REPOS to explicit pinned checkouts")
    def test_optimized_assertions_cannot_publish_a_false_pass(self):
        with tempfile.TemporaryDirectory(prefix="bt2-cognitive-optimized-") as tmp:
            result = subprocess.run(
                [sys.executable, "-O", str(QUALIFY), "--repos", ROOT, "--state", tmp],
                capture_output=True, text=True, timeout=90,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("optimization", result.stderr.lower())


    @unittest.skipUnless(ROOT, "set BT2_VERA_COGNITIVE_REPOS to explicit pinned checkouts")
    def test_preloaded_import_substitution_rejected_before_module_import(self):
        script = """
import importlib.util, pathlib, sys, types
fake = types.ModuleType('meta')
fake.__file__ = str(pathlib.Path.cwd() / 'unreviewed' / 'meta.py')
sys.modules['meta'] = fake
spec = importlib.util.spec_from_file_location('bt2_fixture_qualify', sys.argv[1])
qualify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualify)
qualify.run_slice(pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]))
"""
        with tempfile.TemporaryDirectory(prefix="bt2-cognitive-import-") as tmp:
            result = subprocess.run(
                [sys.executable, "-c", script, str(QUALIFY), ROOT, tmp],
                capture_output=True, text=True, timeout=90,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("untrusted preloaded module", result.stderr)

if __name__ == "__main__":
    unittest.main()
