"""Negative controls for the non-mutating V3 historical source gate."""

import json
import unittest

from verify_bt2_v3_history import ROOT, MANIFEST, verify


class V3HistoryControls(unittest.TestCase):
    def test_real_witness(self):
        verify()

    def test_modified_payload_rejected(self):
        with self.assertRaisesRegex(ValueError, "source witness mismatch"):
            verify(overrides={"native/project/BT2_NATIVE_RUNTIME_V1.md": b"tampered payload"})

    def test_manifest_blob_tampering_rejected(self):
        manifest = json.loads((ROOT / MANIFEST).read_text())
        manifest["required_project_files"][0]["git_blob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "manifest bytes modified"):
            verify(manifest_bytes=json.dumps(manifest).encode())

    def test_manifest_set_tampering_rejected(self):
        manifest = json.loads((ROOT / MANIFEST).read_text())
        manifest["required_project_files"] = manifest["required_project_files"][1:]
        with self.assertRaisesRegex(ValueError, "manifest bytes modified"):
            verify(manifest_bytes=json.dumps(manifest).encode())

    def test_manifest_semantic_only_tampering_rejected(self):
        manifest = json.loads((ROOT / MANIFEST).read_text())
        manifest["installation_rule"] = "changed despite unchanged payload digest"
        with self.assertRaisesRegex(ValueError, "manifest bytes modified"):
            verify(manifest_bytes=json.dumps(manifest).encode())


if __name__ == "__main__":
    unittest.main()
