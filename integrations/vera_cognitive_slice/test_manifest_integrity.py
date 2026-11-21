"""Synthetic adversarial tests for the source-pin manifest trust boundary."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import qualify
import cognitive_advisory
from cognitive_advisory import AdvisoryRequest, EvidenceSignal


class PinManifestIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(prefix="bt2-manifest-")
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.directory = self.repo / "integrations" / "vera_cognitive_slice"
        self.directory.mkdir(parents=True)
        shutil.copyfile(Path(qualify.__file__), self.directory / "qualify.py")
        shutil.copyfile(Path(qualify.__file__).with_name("source_pins.json"),
                        self.directory / "source_pins.json")
        attrs = Path(qualify.__file__).with_name(".gitattributes")
        if attrs.is_file():
            shutil.copyfile(attrs, self.directory / ".gitattributes")
        self.git("init", "-q")
        self.git("add", "integrations/vera_cognitive_slice/qualify.py",
                 "integrations/vera_cognitive_slice/source_pins.json")
        if attrs.is_file():
            self.git("add", "integrations/vera_cognitive_slice/.gitattributes")
        self.git("-c", "user.name=BT2 Synthetic",
                 "-c", "user.email=synthetic@invalid.local",
                 "commit", "-q", "-m", "frozen trusted manifest")
        self.pinned = self.git("rev-parse", "HEAD")
        self.fake_sources = self.repo / "absent-donors"

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            capture_output=True, text=True, timeout=20, check=True,
        )
        return result.stdout.strip()

    def malicious_manifest(self):
        path = self.directory / "source_pins.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["humility"] = "b" * 40
        path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    def test_uncommitted_manifest_override_rejected_before_donor_access(self):
        self.malicious_manifest()
        with patch.object(qualify, "__file__", str(self.directory / "qualify.py")):
            with self.assertRaisesRegex(ValueError, "source pin manifest"):
                qualify._verify_sources(self.fake_sources)
    def test_autocrlf_checkout_keeps_exact_manifest_bytes(self):
        with TemporaryDirectory(prefix="bt2-win-checkout-") as work:
            clone = Path(work) / "checkout"
            subprocess.run(
                ["git", "-c", "core.autocrlf=true", "clone", "-q",
                 str(self.repo), str(clone)],
                capture_output=True, text=True, timeout=30, check=True,
            )
            checked = (clone / "integrations" / "vera_cognitive_slice"
                       / "source_pins.json").read_bytes()
            canonical = (self.directory / "source_pins.json").read_bytes()
            self.assertEqual(
                checked, canonical,
                "autocrlf transformed a hash-bound manifest during checkout",
            )

    def test_clean_manifest_reaches_normal_missing_donor_rejection(self):
        with patch.object(qualify, "__file__", str(self.directory / "qualify.py")):
            with self.assertRaisesRegex(ValueError, "missing source checkout"):
                qualify._verify_sources(self.fake_sources)

    def test_moved_head_does_not_redefine_expected_manifest(self):
        self.malicious_manifest()
        self.git("add", "integrations/vera_cognitive_slice/source_pins.json")
        self.git("-c", "user.name=BT2 Synthetic",
                 "-c", "user.email=synthetic@invalid.local",
                 "commit", "-q", "-m", "untrusted alternate manifest")
        self.assertNotEqual(self.git("rev-parse", "HEAD"), self.pinned)
        with patch.object(qualify, "__file__", str(self.directory / "qualify.py")):
            with self.assertRaisesRegex(ValueError, "source pin manifest"):
                qualify._verify_sources(
                    self.fake_sources, manifest_commit=self.pinned,
                )

    def test_actual_advisory_fails_on_tampered_manifest_read(self):
        from os import environ
        root = environ.get("BT2_VERA_COGNITIVE_REPOS")
        self.assertTrue(root, "explicit pinned source checkouts required")
        original_read = Path.read_bytes
        def override(path):
            if path.name == "source_pins.json" and path.parent.name == "vera_cognitive_slice":
                return b'{"humility":"bypassed","fake":"unverified"}'
            return original_read(path)

        request = AdvisoryRequest(
            "synthetic fixture", 0.5,
            (EvidenceSignal("fixture1", "group1", 0.9, 0.1),),
        )
        with patch.object(Path, "read_bytes", autospec=True, side_effect=override):
            with self.assertRaisesRegex(ValueError, "source pin manifest"):
                cognitive_advisory.propose(Path(root), request)


if __name__ == "__main__":
    unittest.main()
