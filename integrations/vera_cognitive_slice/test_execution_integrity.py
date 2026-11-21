"""Execution must consume verified Git blob bytes, not a swapped second read."""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

import cognitive_advisory


def blob_oid(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class ExactExecutionIntegrityTests(unittest.TestCase):
    def test_swapped_module_is_refused_before_execution(self):
        with TemporaryDirectory(prefix="bt2-swap-exec-") as work:
            source = Path(work) / "core.py"
            trusted = b"VALUE = 'trusted'\n"
            source.write_bytes(trusted)
            pinned = blob_oid(trusted)
            source.write_bytes(b"raise RuntimeError('SYNTHETIC_SWAP_EXECUTED')\n")
            with self.assertRaisesRegex(ValueError, "source bytes changed after verification"):
                cognitive_advisory._load_exact_module(source, expected_blob=pinned)

    def test_exact_bytes_execute_and_invalid_pins_fail_closed(self):
        with TemporaryDirectory(prefix="bt2-exact-exec-") as work:
            source = Path(work) / "core.py"
            trusted = b"VALUE = 42\n"
            source.write_bytes(trusted)
            module = cognitive_advisory._load_exact_module(
                source, expected_blob=blob_oid(trusted)
            )
            self.assertEqual(module.VALUE, 42)
            for malformed in (None, "HEAD", "0" * 39, "Z" * 40):
                with self.subTest(malformed=malformed):
                    with self.assertRaises(ValueError):
                        cognitive_advisory._load_exact_module(source, expected_blob=malformed)

    def test_moved_head_cannot_redefine_verified_source(self):
        with TemporaryDirectory(prefix="bt2-head-move-") as work:
            repo = Path(work)
            source = repo / "humility" / "core.py"
            source.parent.mkdir()
            trusted = b"VALUE = 'verified'\n"
            source.write_bytes(trusted)

            def git(*args):
                proc = subprocess.run(
                    ["git", "-C", str(repo), *args],
                    capture_output=True, text=True, check=True, timeout=20,
                )
                return proc.stdout.strip()

            git("init", "-q")
            git("add", "humility/core.py")
            git("-c", "user.name=BT2 Test",
                "-c", "user.email=bt2-test@invalid.local",
                "commit", "-q", "-m", "verified synthetic source")
            verified_commit = git("rev-parse", "HEAD")
            source.write_bytes(b"VALUE = 'UNVERIFIED_HEAD'\n")
            git("add", "humility/core.py")
            git("-c", "user.name=BT2 Test",
                "-c", "user.email=bt2-test@invalid.local",
                "commit", "-q", "-m", "unverified synthetic replacement")
            self.assertNotEqual(git("rev-parse", "HEAD"), verified_commit)
            oid = cognitive_advisory._committed_blob(
                repo, "humility/core.py", commit_sha=verified_commit,
            )
            self.assertEqual(oid, blob_oid(trusted))
            with self.assertRaisesRegex(ValueError, "source bytes changed after verification"):
                cognitive_advisory._load_exact_module(source, expected_blob=oid)

    def test_mutable_or_malformed_commit_reference_is_rejected(self):
        with TemporaryDirectory(prefix="bt2-bad-selector-") as work:
            for selector in ("HEAD", "main", "0" * 39, None, "z" * 40):
                with self.subTest(selector=selector):
                    with self.assertRaisesRegex(ValueError, "pinned commit"):
                        cognitive_advisory._committed_blob(
                            Path(work), "humility/core.py", commit_sha=selector,
                        )


if __name__ == "__main__":
    unittest.main()
