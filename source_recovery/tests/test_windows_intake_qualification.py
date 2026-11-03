"""Fail-closed Windows source-intake contract (synthetic; no host inspection)."""
from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

from source_recovery import export_intake


def _simulated_windows_os():
    # Patch only this module's OS reference: never mutate global os.name,
    # which would make pathlib choose WindowsPath on a POSIX test runner.
    return types.SimpleNamespace(**{**vars(os), "name": "nt"})


def _simulated_wsl_os(*, env: bool = False):
    return types.SimpleNamespace(**{
        **vars(os), "name": "posix",
        "uname": lambda: types.SimpleNamespace(release="5.15.153-microsoft-standard-WSL2"),
        "environ": {"WSL_DISTRO_NAME": "Ubuntu"} if env else {},
    })


def _simulated_unmarked_linux_os():
    return types.SimpleNamespace(**{
        **vars(os), "name": "posix",
        "uname": lambda: types.SimpleNamespace(release="6.8.7-custom"),
        "environ": {},
    })


class WindowsIntakeQualificationTests(unittest.TestCase):
    def test_proc_version_wsl_marker_rejects_custom_kernel_release(self):
        linux_os = _simulated_unmarked_linux_os()
        with patch.object(export_intake, "os", linux_os), \
                patch("builtins.open", return_value=io.StringIO("Linux version 6.8.7 (Microsoft WSL)")), \
                patch.object(Path, "lstat", side_effect=AssertionError("lstat called")):
            with self.assertRaisesRegex(export_intake.IntakeError, "WSL.*unqualified"):
                export_intake.scan_folder(Path("unused"))

    def test_drvfs_mount_marker_rejects_stripped_wsl_release(self):
        linux_os = _simulated_unmarked_linux_os()

        def proc_open(path, *args, **kwargs):
            if path == "/proc/version":
                return io.StringIO("Linux version 6.8.7-custom\n")
            if path == "/proc/self/mountinfo":
                return io.StringIO("18 11 0:32 / /mnt/c rw - drvfs C: rw\n")
            raise AssertionError(f"unexpected proc probe {path}")

        with patch.object(export_intake, "os", linux_os), \
                patch("builtins.open", side_effect=proc_open), \
                patch.object(Path, "lstat", side_effect=AssertionError("lstat called")):
            with self.assertRaisesRegex(export_intake.IntakeError, "WSL.*unqualified"):
                export_intake.scan_folder(Path("unused"))

    def test_unreadable_proc_host_evidence_fails_closed(self):
        linux_os = _simulated_unmarked_linux_os()
        with patch.object(export_intake, "os", linux_os), \
                patch("builtins.open", side_effect=OSError("proc unavailable")):
            with self.assertRaisesRegex(export_intake.IntakeError, "host qualification unavailable"):
                export_intake._require_qualified_host()

    def test_oversized_proc_host_evidence_fails_closed(self):
        linux_os = _simulated_unmarked_linux_os()
        with patch.object(export_intake, "os", linux_os), \
                patch.object(export_intake, "_PROC_HOST_EVIDENCE_LIMIT", 8), \
                patch("builtins.open", return_value=io.StringIO("longer than eight bytes")):
            with self.assertRaisesRegex(export_intake.IntakeError, "host qualification unavailable"):
                export_intake._require_qualified_host()

    def test_unmarked_proc_evidence_keeps_existing_posix_behavior(self):
        linux_os = _simulated_unmarked_linux_os()

        def ordinary_linux_proc(path, *args, **kwargs):
            if path == "/proc/version":
                return io.StringIO("Linux version 6.8.7-custom\n")
            if path == "/proc/self/mountinfo":
                return io.StringIO("18 11 0:32 / / rw - ext4 /dev/sda rw\n")
            raise AssertionError(f"unexpected proc probe {path}")

        with patch.object(export_intake, "os", linux_os), \
                patch("builtins.open", side_effect=ordinary_linux_proc):
            export_intake._require_qualified_host()

    def test_wsl_host_refuses_before_metadata_enumeration(self):
        wsl_os = _simulated_wsl_os()
        wsl_os.scandir = Mock(side_effect=AssertionError("scandir called"))
        with patch.object(export_intake, "os", wsl_os), \
                patch.object(Path, "lstat", side_effect=AssertionError("lstat called")):
            with self.assertRaisesRegex(export_intake.IntakeError, "WSL.*unqualified"):
                export_intake.scan_folder(Path("unused"))
        wsl_os.scandir.assert_not_called()

    def test_wsl_host_refuses_private_write_before_resolve(self):
        with patch.object(export_intake, "os", _simulated_wsl_os()), \
                patch.object(Path, "resolve", side_effect=AssertionError("resolve called")):
            with self.assertRaisesRegex(export_intake.IntakeError, "WSL.*unqualified"):
                export_intake.write_records(Path("unused-out"), Path("unused-root"), {})

    def test_wsl_environment_marker_refuses_before_byte_open(self):
        wsl_os = _simulated_wsl_os(env=True)
        wsl_os.uname = lambda: types.SimpleNamespace(release="ordinary-linux")
        wsl_os.open = Mock(side_effect=AssertionError("opened"))
        with patch.object(export_intake, "os", wsl_os):
            with self.assertRaisesRegex(export_intake.IntakeError, "WSL.*unqualified"):
                export_intake._open_local(Path("unused"), 0, 10)
        wsl_os.open.assert_not_called()

    @unittest.skipUnless(os.name == "nt", "native Windows gate requires a Windows runner")
    def test_real_windows_host_refuses_unqualified_scan(self):
        # The guard must run before considering the existence of the input.
        with self.assertRaisesRegex(export_intake.IntakeError, "Windows.*unqualified"):
            export_intake.scan_folder(Path("intentionally-nonexistent"))

    def test_scan_rejects_before_root_lstat_or_scandir(self):
        windows_os = _simulated_windows_os()
        windows_os.scandir = Mock(side_effect=AssertionError("scandir called"))
        with patch.object(export_intake, "os", windows_os), \
                patch.object(Path, "lstat", side_effect=AssertionError("lstat called")):
            with self.assertRaisesRegex(export_intake.IntakeError, "Windows.*unqualified"):
                export_intake.scan_folder(Path("unused"))
        windows_os.scandir.assert_not_called()

    def test_private_write_rejects_before_resolve_or_mkdir(self):
        with patch.object(export_intake, "os", _simulated_windows_os()), \
                patch.object(Path, "resolve", side_effect=AssertionError("resolve called")), \
                patch.object(Path, "mkdir", side_effect=AssertionError("mkdir called")):
            with self.assertRaisesRegex(export_intake.IntakeError, "Windows.*unqualified"):
                export_intake.write_records(Path("unused-out"), Path("unused-root"),
                                            {"private_manifest": [],
                                             "private_duplicate_groups": [], "summary": {}})

    def test_direct_byte_open_rejects_before_os_open(self):
        windows_os = _simulated_windows_os()
        windows_os.open = Mock(side_effect=AssertionError("opened"))
        with patch.object(export_intake, "os", windows_os):
            with self.assertRaisesRegex(export_intake.IntakeError, "Windows.*unqualified"):
                export_intake._open_local(Path("unused"), 0, 10)
        windows_os.open.assert_not_called()

    def test_cli_refuses_simulated_windows_without_stdout_or_persistence(self):
        stderr, stdout = io.StringIO(), io.StringIO()
        with patch.object(export_intake, "os", _simulated_windows_os()), \
                patch.object(sys, "argv", ["export_intake", "--root", "unused"]), \
                contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as trapped:
                export_intake.main()
        self.assertEqual(trapped.exception.code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("inventory rejected unsafe", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
