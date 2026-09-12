#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SUPPORT_ROOT = Path(__file__).resolve().parents[1]
VERIFY = SUPPORT_ROOT / "scripts" / "verify_package.py"
CHECKPOINT = SUPPORT_ROOT / "scripts" / "training_checkpoint.py"
PACKAGE_ROOT = Path(__file__).resolve().parents[3] / "v1.0.0"


def run(*args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run([sys.executable, *args], text=True, capture_output=True)
    if ok and cp.returncode != 0:
        raise AssertionError(f"command failed: {cp.args}\nstdout={cp.stdout}\nstderr={cp.stderr}")
    if not ok and cp.returncode == 0:
        raise AssertionError(f"command unexpectedly passed: {cp.args}")
    return cp


class CheckpointSupportTests(unittest.TestCase):
    def test_target_v1_package_verifier(self) -> None:
        if PACKAGE_ROOT.is_dir():
            cp = run(str(VERIFY), str(PACKAGE_ROOT))
            self.assertEqual(json.loads(cp.stdout)["status"], "PASS")

    def test_checkpoint_order_failure_and_base_ready_gate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ck = Path(td) / "checkpoint.json"
            run(
                str(CHECKPOINT), "init", "--output", str(ck),
                "--package-version", "1.0.0",
                "--repository", "thebrazenbeard/build-team-2.0",
                "--source-ref", "training/hephaestus-v1.0.0",
                "--source-commit-or-tag", "0" * 40,
                "--manifest-sha256", "1" * 64,
                "--checksums-sha256", "2" * 64,
            )
            run(str(CHECKPOINT), "record", "--file", str(ck), "--module", "01", "--verdict", "FAIL")
            data = json.loads(ck.read_text())
            self.assertEqual(data["next_module"], "01")
            self.assertEqual(len(data["failed_attempts"]), 1)
            run(str(CHECKPOINT), "record", "--file", str(ck), "--module", "01", "--verdict", "PASS")
            run(str(CHECKPOINT), "record", "--file", str(ck), "--module", "03", "--verdict", "PASS", ok=False)
            for i in range(2, 11):
                run(str(CHECKPOINT), "record", "--file", str(ck), "--module", f"{i:02d}", "--verdict", "PASS")
            run(
                str(CHECKPOINT), "finalize", "--file", str(ck),
                "--verdict", "QUALIFIED_FOR_BASE_FREEZE",
                "--score", "17", "--critical-passed", "18", ok=False,
            )
            run(
                str(CHECKPOINT), "finalize", "--file", str(ck),
                "--verdict", "QUALIFIED_FOR_BASE_FREEZE",
                "--score", "18", "--critical-passed", "18",
            )
            out = json.loads(run(str(CHECKPOINT), "verify", "--file", str(ck)).stdout)
            self.assertEqual(out["status"], "PASS")
            self.assertEqual(out["checkpoint_state"], "BASE_READY")


if __name__ == "__main__":
    unittest.main()
