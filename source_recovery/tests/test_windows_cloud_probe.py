"""Hostile contract tests: CFAPI classification never authorizes content reads."""
import ctypes
import unittest
from unittest.mock import patch
from source_recovery import windows_cloud_probe as w

class WindowsCloudMetadataTests(unittest.TestCase):
    def test_in_sync_complete_cloud_placeholder_is_still_metadata_only(self):
        result = w.classify_placeholder(0x400, 0x01 | 0x08)
        self.assertEqual(result["status"], "CLOUD_PLACEHOLDER_METADATA_ONLY")
        self.assertFalse(result["byte_read_authorized"])

    def test_partial_and_partially_on_disk_are_hard_holds(self):
        for state in (0x01 | 0x10, 0x01 | 0x20, 0x01 | 0x10 | 0x20):
            with self.subTest(state=state):
                result = w.classify_placeholder(0x400, state)
                self.assertEqual(result["status"], "PARTIAL_PLACEHOLDER_HOLD")
                self.assertFalse(result["byte_read_authorized"])

    def test_other_reparse_and_invalid_cf_state_fail_closed(self):
        self.assertEqual(w.classify_placeholder(0x400, 0)["status"], "UNKNOWN_REPARSE_HOLD")
        self.assertEqual(w.classify_placeholder(0x400, 0xffffffff)["status"], "INVALID_STATE_HOLD")

    def test_unknown_cfapi_state_bits_fail_closed(self):
        # Windows can extend CF_PLACEHOLDER_STATE in newer versions.
        # Future bits must never be misreported as a known synchronized state.
        for attributes, state in ((0x400, 0x01 | 0x08 | 0x40),
                                  (0x20, 0x08 | 0x80)):
            with self.subTest(attributes=attributes, state=state):
                report = w.classify_placeholder(attributes, state)
                self.assertEqual(report["status"], "UNKNOWN_STATE_BITS_HOLD")
                self.assertFalse(report["byte_read_authorized"])

    def test_plain_local_file_is_not_permission_to_read(self):
        result = w.classify_placeholder(0x20, 0)
        self.assertEqual(result["status"], "REGULAR_FILE_METADATA_ONLY")
        self.assertFalse(result["byte_read_authorized"])

    def test_cloud_offline_attributes_override_sync_flag(self):
        for flag in (0x1000, 0x40000, 0x400000):
            with self.subTest(flag=flag):
                result = w.classify_placeholder(0x400 | flag, 0x01 | 0x08)
                self.assertEqual(result["status"], "OFFLINE_OR_RECALL_HOLD")

    def test_cloud_sync_root_does_not_hide_behind_regular_file_attributes(self):
        with patch.object(w, "_attributes_and_tag", return_value=(0x20, 0)), \
             patch.object(w, "_state_from_attributes_tag", return_value=0), \
             patch.object(w, "_is_cloud_sync_root", return_value=True):
            actual = w.probe_placeholder(r"C:\cloud-root\export.zip")
        self.assertEqual(actual["status"], "CLOUD_SYNC_ROOT_HOLD")
        self.assertFalse(actual["byte_read_authorized"])

    def test_native_query_uses_only_metadata_and_never_exposes_source_path(self):
        with patch.object(w, "_attributes_and_tag", return_value=(0x400, 0x9000001A)), \
             patch.object(w, "_state_from_attributes_tag", return_value=0x09), \
             patch.object(w, "_is_cloud_sync_root", return_value=False), \
             patch("builtins.open", side_effect=AssertionError("payload open forbidden")):
            result = w.probe_placeholder(r"C:\synthetic-private\secret.zip")
        self.assertEqual(result["status"], "CLOUD_PLACEHOLDER_METADATA_ONLY")
        self.assertNotIn("secret.zip", str(result))
        self.assertFalse(result["byte_read_authorized"])

    def test_ctypes_marshalling_failure_is_a_metadata_hold(self):
        with patch.object(w, "_attributes_and_tag", return_value=(0x400, 0x9000001A)), \
             patch.object(w, "_state_from_attributes_tag",
                          side_effect=ctypes.ArgumentError("synthetic marshalling failure")):
            result = w.probe_placeholder(r"C:\synthetic-private\export.zip")
        self.assertEqual(result, {"status": "METADATA_QUERY_FAILED_HOLD",
                                  "byte_read_authorized": False})

    def test_wildcard_paths_are_rejected_before_native_query(self):
        for path in (r"C:\synthetic-private\*.zip", r"C:\synthetic-private\exp?rt.zip"):
            with self.subTest(path=path), \
                 patch.object(w, "_attributes_and_tag") as query:
                result = w.probe_placeholder(path)
                self.assertEqual(result, {"status": "METADATA_QUERY_FAILED_HOLD",
                                          "byte_read_authorized": False})
                query.assert_not_called()

    def test_direct_findfirstfile_wrapper_rejects_wildcards(self):
        # Reject before native boundary, including on a non-Windows test runner.
        for path in ("*.zip", "exp?rt.zip"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    w._attributes_and_tag(path)

    def test_empty_nul_and_binary_paths_fail_without_native_call(self):
        for path in ("", "bad\x00name.zip", b"bytes.zip"):
            with self.subTest(path=repr(path)), \
                 patch.object(w, "_attributes_and_tag") as query:
                self.assertEqual(w.probe_placeholder(path),
                                 {"status": "METADATA_QUERY_FAILED_HOLD",
                                  "byte_read_authorized": False})
                query.assert_not_called()

if __name__ == "__main__":
    unittest.main()
