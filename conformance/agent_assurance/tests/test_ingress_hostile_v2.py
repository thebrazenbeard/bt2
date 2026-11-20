"""Independent hostile input regression cases for source-only BT2 assurance."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import gate_v1 as gate


def clean_case():
    return {
        "schema": "BT2_AGENT_ASSURANCE_INPUT_V1",
        "operation": "inspect",
        "proposed_action_id": "codex.inspect_metadata",
        "model_label": "ALLOW",
        "world_model": {"status": "AGREEMENT_UNQUALIFIED", "grants_effect": False},
        "recovery": {
            "status": "PARTIAL_FAILED_TURN",
            "complete_conversations": 0,
            "source_rows_verified": True,
        },
        "skillopt": {
            "status": "REJECT_CRITICAL_BLOCK_MISS",
            "critical_block_miss_count": 2,
        },
        "authority": {"owner_approval_verified": False, "runtime_bound": False},
    }


class IngressHostileTests(unittest.TestCase):
    def test_deep_json_nesting_rejected_as_value_error(self):
        deeply_nested = b"[" * 1500 + b"0" + b"]" * 1500
        with self.assertRaises(ValueError):
            gate.parse_evidence(deeply_nested)

    def test_complete_recovery_missing_verified_rows_is_rejected(self):
        d = clean_case()
        d["recovery"] = {"status":"COMPLETE_VERIFIED","complete_conversations":1,"source_rows_verified":False}
        with self.assertRaises(ValueError):
            gate.decide(d)

    def test_complete_recovery_zero_conversations_is_rejected(self):
        d = clean_case()
        d["recovery"] = {"status":"COMPLETE_VERIFIED","complete_conversations":0,"source_rows_verified":True}
        with self.assertRaises(ValueError):
            gate.decide(d)

    def test_none_recovery_cannot_claim_complete_conversations(self):
        d = clean_case()
        d["recovery"] = {"status":"NONE","complete_conversations":2,"source_rows_verified":True}
        with self.assertRaises(ValueError):
            gate.decide(d)

    def test_critical_miss_status_requires_positive_miss_count(self):
        d = clean_case()
        d["skillopt"] = {"status":"REJECT_CRITICAL_BLOCK_MISS","critical_block_miss_count":0}
        with self.assertRaises(ValueError):
            gate.decide(d)

    def test_bounded_reader_returns_identical_valid_bytes_without_path_read_bytes(self):
        content = json.dumps(clean_case()).encode("utf-8")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"input.json"
            p.write_bytes(content)
            with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("Path.read_bytes() is forbidden")):
                observed = gate.read_bounded_file(p)
            self.assertEqual(observed, content)
            self.assertFalse(gate.decide(gate.parse_evidence(observed))["action_authorized"])

    def test_reader_rejects_oversized_regular_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"oversized.json"
            p.write_bytes(b" "*(gate.MAX_INPUT_BYTES+1))
            with self.assertRaises(ValueError):
                gate.read_bounded_file(p)

    def test_reader_rejects_symlinked_input(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            target = folder/"real.json"
            target.write_bytes(json.dumps(clean_case()).encode())
            link = folder/"alias.json"
            try:
                link.symlink_to(target)
            except (PermissionError, OSError, NotImplementedError):
                self.skipTest("Host does not allow test symlinks")
            with self.assertRaises(ValueError):
                gate.read_bounded_file(link)

    @unittest.skipUnless(hasattr(os,"mkfifo"), "FIFO only available on POSIX")
    def test_reader_rejects_fifo_without_blocking(self):
        with tempfile.TemporaryDirectory() as d:
            fifo = Path(d)/"evidence.pipe"
            os.mkfifo(fifo)
            with self.assertRaises(ValueError):
                gate.read_bounded_file(fifo)


if __name__ == "__main__":
    unittest.main()
