"""Execution must consume verified Git blob bytes, not a swapped second read."""
from __future__ import annotations

import hashlib
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
