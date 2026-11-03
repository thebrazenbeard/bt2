"""Offline hostile tests for metadata-only archival recovery intake."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
import os
from unittest.mock import patch
from source_recovery import export_intake
from source_recovery.export_intake import scan_folder, write_records, IntakeError

@unittest.skipIf(os.name == "nt", "Windows intake is held until native traversal/DACL qualification")
class ExportIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "incoming"
        self.root.mkdir()
        self.out = Path(self.tmp.name) / "private-output"

    def test_dedup_uses_content_not_similar_filenames(self):
        (self.root / "a.md").write_bytes(b"same")
        (self.root / "a - Copy.md").write_bytes(b"same")
        (self.root / "other.md").write_bytes(b"different")
        result = scan_folder(self.root, hash_local=True)
        self.assertEqual(result["summary"]["files"], 3)
        self.assertEqual(result["summary"]["exact_duplicate_groups"], 1)
        self.assertEqual(result["summary"]["exact_duplicate_extras"], 1)
        self.assertTrue(all(x["publication_status"] == "HOLD_UNREVIEWED"
                            for x in result["private_manifest"]))

    def test_archive_traversal_and_encryption_are_not_trusted(self):
        archive = self.root / "hostile.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("../outside.txt", "do not extract")
            z.writestr("/absolute.txt", "do not extract")
            z.writestr("safe.txt", "ok")
        result = scan_folder(self.root, inspect_zip_local=True)
        self.assertEqual(result["summary"]["unsafe_zip_paths"], 2)
        self.assertEqual(result["summary"]["archive_members"], 3)
        self.assertFalse((self.root.parent / "outside.txt").exists())
        self.assertEqual(result["summary"]["archives_readable"], 0)
        self.assertEqual(result["private_manifest"][0]["zip"]["status"], "REJECTED_METADATA")

    def test_sensitive_member_inside_generic_zip_is_held(self):
        archive = self.root / "release.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("configs/private_token.json", '{"value":"DO_NOT_EXPORT"}')
        result = scan_folder(self.root, inspect_zip_local=True)
        row = result["private_manifest"][0]
        self.assertTrue(row["private_review_hold"])
        self.assertEqual(row["zip"]["sensitive_member_names"], 1)
        self.assertNotIn("private_token.json", json.dumps(result))
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(result))

    def test_invalid_archive_fails_closed(self):
        (self.root / "bad.zip").write_bytes(b"not actually a ZIP")
        result = scan_folder(self.root, inspect_zip_local=True)
        self.assertEqual(result["summary"]["archives_readable"], 0)
        self.assertEqual(result["summary"]["unreadable_archives"], 1)

    def test_archive_entry_cap_holds_without_inspecting_payloads(self):
        with zipfile.ZipFile(self.root / "bounded.zip", "w") as z:
            z.writestr("a.py", "print('not executed')")
            z.writestr("b.py", "print('not executed')")
        result = scan_folder(self.root, max_zip_members=1, inspect_zip_local=True)
        self.assertEqual(result["summary"]["archives_readable"], 0)
        self.assertEqual(result["summary"]["archive_members"], 2)
        archive = result["private_manifest"][0]["zip"]
        self.assertEqual(archive["status"], "MEMBER_LIMIT_EXCEEDED")
        self.assertFalse((self.root / "a.py").exists())

    def test_raw_sensitive_contents_never_appear_in_summary(self):
        secret = "PRIVATE_CONTENT_DO_NOT_PUBLISH"
        (self.root / "private_chat.txt").write_text(secret)
        result = scan_folder(self.root, hash_local=True)
        self.assertNotIn(secret, json.dumps(result["summary"]))
        self.assertNotIn(secret, json.dumps(result["private_manifest"]))
        self.assertEqual(result["private_manifest"][0]["sha256"],
                         hashlib.sha256(secret.encode()).hexdigest())
        self.assertTrue(result["private_manifest"][0]["private_review_hold"])

    def test_file_count_cap(self):
        (self.root / "1").write_text("1")
        (self.root / "2").write_text("2")
        with self.assertRaises(IntakeError):
            scan_folder(self.root, max_files=1)

    def test_default_metadata_only_never_opens_file_bytes(self):
        from unittest.mock import patch
        (self.root / "asset.bin").write_bytes(b"private bytes")
        # Secure traversal opens directory handles; file payloads still go
        # exclusively through _open_local and must remain unopened by default.
        with patch("source_recovery.export_intake._open_local", side_effect=AssertionError("read payload")):
            result = scan_folder(self.root)
        self.assertIsNone(result["private_manifest"][0]["sha256"])
        self.assertFalse(result["summary"]["byte_reads_opted_in"])

    def test_global_entry_limit_includes_empty_directory_fanout(self):
        for index in range(40):
            (self.root / f"empty_{index}").mkdir()
        with self.assertRaisesRegex(IntakeError, "entry count"):
            scan_folder(self.root, max_files=1)

    @unittest.skipUnless(os.name == "posix", "POSIX descriptor traversal fixture")
    def test_directory_swap_during_enumeration_cannot_escape_root(self):
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "local.bin").write_bytes(b"L")
        outside = self.root.parent / "outside"
        outside.mkdir()
        (outside / "secret.bin").write_bytes(b"PRIVATE")
        original_scandir = os.scandir
        visits = 0

        def racing_scandir(target):
            nonlocal visits
            visits += 1
            if visits == 2:
                nested.rename(self.root / "nested_moved")
                nested.symlink_to(outside, target_is_directory=True)
            return original_scandir(target)

        with patch("source_recovery.export_intake.os.scandir", side_effect=racing_scandir):
            try:
                result = scan_folder(self.root)
            except IntakeError:
                return  # Fail-closed refusal also satisfies confinement.
        names = [r["path"] for r in result["private_manifest"]]
        self.assertNotIn("nested/secret.bin", names)

    @unittest.skipUnless(os.name == "posix", "POSIX descriptor traversal fixture")
    def test_symlinked_root_ancestor_is_rejected(self):
        outside = self.root.parent / "outside"
        (outside / "inner").mkdir(parents=True)
        (outside / "inner" / "secret.bin").write_bytes(b"PRIVATE")
        alias = self.root.parent / "alias"
        alias.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(IntakeError):
            scan_folder(alias / "inner")

    @unittest.skipUnless(os.name == "posix", "POSIX descriptor traversal fixture")
    def test_parent_swap_before_hash_never_hashes_outside_bytes(self):
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "private.bin").write_bytes(b"IN")
        outside = self.root.parent / "outside"
        outside.mkdir()
        (outside / "private.bin").write_bytes(b"NO")
        original_sha = export_intake._sha256
        swapped = False

        def racing_hash(*args, **kwargs):
            nonlocal swapped
            if not swapped:
                swapped = True
                nested.rename(self.root / "nested_moved")
                nested.symlink_to(outside, target_is_directory=True)
            return original_sha(*args, **kwargs)

        with patch("source_recovery.export_intake._sha256", side_effect=racing_hash):
            result = scan_folder(self.root, hash_local=True)
        row = result["private_manifest"][0]
        self.assertNotEqual(row["sha256"], hashlib.sha256(b"NO").hexdigest())
        self.assertIn(row["read_status"], ("BOUNDED_LOCAL_BYTES", "SKIPPED_CHANGED_OR_UNSAFE_FILE"))

    def test_directory_iterator_stops_at_limit_before_full_materialization(self):
        from unittest.mock import patch
        class Listing:
            consumed = 0
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def __iter__(self):
                for index in range(10000):
                    self.consumed += 1
                    yield type("Entry", (), {"name": str(index)})()
        listing = Listing()
        with patch("source_recovery.export_intake.os.scandir", return_value=listing):
            with self.assertRaisesRegex(IntakeError, "entry count"):
                scan_folder(self.root, max_files=5)
        self.assertEqual(listing.consumed, 6)

    def test_large_file_is_skipped_without_hashing(self):
        from unittest.mock import patch
        (self.root / "large.bin").write_bytes(b"0" * (2 * 1024 * 1024))
        with patch("source_recovery.export_intake._open_local", side_effect=AssertionError("read payload")):
            result = scan_folder(self.root, hash_local=True, max_read_bytes=1024)
        self.assertEqual(result["private_manifest"][0]["read_status"], "SKIPPED_READ_SIZE_LIMIT")
        self.assertIsNone(result["private_manifest"][0]["sha256"])

    def test_cloud_and_reparse_flags_are_detected(self):
        from source_recovery.export_intake import _cloud_or_reparse
        for flag in (0x1000, 0x400, 0x00040000, 0x00400000):
            metadata = type("Metadata", (), {"st_file_attributes": flag})()
            self.assertTrue(_cloud_or_reparse(metadata))

    def test_large_zip_is_skipped_before_open(self):
        from unittest.mock import patch
        (self.root / "large.zip").write_bytes(b"0" * (2 * 1024 * 1024 + 1))
        with patch("source_recovery.export_intake._open_local", side_effect=AssertionError("read payload")):
            result = scan_folder(self.root, inspect_zip_local=True, max_read_bytes=3 * 1024 * 1024)
        self.assertEqual(result["private_manifest"][0]["read_status"], "SKIPPED_READ_SIZE_LIMIT")

    def test_total_budget_counts_both_hash_and_zip_reads(self):
        with zipfile.ZipFile(self.root / "small.zip", "w") as archive:
            archive.writestr("member.txt", "hello")
        size = (self.root / "small.zip").stat().st_size
        result = scan_folder(self.root, hash_local=True, inspect_zip_local=True,
                             max_read_bytes=size, max_total_read_bytes=size)
        self.assertEqual(result["private_manifest"][0]["read_status"], "SKIPPED_READ_SIZE_LIMIT")
        self.assertEqual(result["summary"]["read_bytes_budgeted"], 0)

    def test_cli_defaults_to_aggregate_only(self):
        import subprocess
        import sys
        script = Path(__file__).resolve().parents[1] / "export_intake.py"
        (self.root / "private_notes.md").write_text("PRIVATE_NOT_IN_STDOUT")
        bare = subprocess.run([sys.executable, str(script), "--root", str(self.root)],
                              capture_output=True, text=True, check=False)
        self.assertEqual(bare.returncode, 0, bare.stderr)
        self.assertEqual(json.loads(bare.stdout)["files"], 1)
        self.assertNotIn("private_notes.md", bare.stdout)
        self.assertNotIn("PRIVATE_NOT_IN_STDOUT", bare.stdout)
        self.assertFalse(self.out.exists())
        denied = subprocess.run([sys.executable, str(script), "--root", str(self.root),
                                 "--output", str(self.out)],
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(denied.returncode, 0)
        self.assertFalse(self.out.exists())
        allowed = subprocess.run([sys.executable, str(script), "--root", str(self.root),
                                  "--output", str(self.out),
                                  "--write-private-manifest"],
                                 capture_output=True, text=True, check=False)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertTrue((self.out / "private_manifest.json").is_file())

    def test_write_is_separate_and_never_overwrites(self):
        (self.root / "a").write_text("only data")
        result = scan_folder(self.root)
        with self.assertRaises(IntakeError):
            write_records(self.root / "nested", self.root, result)
        write_records(self.out, self.root, result)
        self.assertTrue((self.out / "private_manifest.json").is_file())
        self.assertTrue((self.out / "summary.json").is_file())
        with self.assertRaises(FileExistsError):
            write_records(self.out, self.root, result)
        self.assertEqual((self.root / "a").read_text(), "only data")

if __name__ == "__main__":
    unittest.main()
