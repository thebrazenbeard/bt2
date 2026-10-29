"""Fail-closed tests for the explicitly superseding PostgreSQL build manifest.

These source-only tests do not qualify an installed database or Lantern runtime.
"""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_DIR = ROOT / "tools" / "qualification"
sys.path.insert(0, str(QUALIFICATION_DIR))
MODULE_PATH = QUALIFICATION_DIR / "bt2_build_manifest.py"
spec = importlib.util.spec_from_file_location("bt2_build_manifest_v4_scope", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ScopedQualificationIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = ROOT / "database" / "BUILD_MANIFEST_V4.json"
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))

    def test_manifest_is_explicit_supersession_and_source_only(self):
        self.assertEqual(
            self.manifest["supersedes_manifest"],
            "database/BUILD_MANIFEST_V3.json",
        )
        self.assertEqual(
            self.manifest["manifest_version"],
            "BT2_DATABASE_BUILD_MANIFEST_V4",
        )
        self.assertEqual(
            self.manifest["qualification"]["lantern_v4_runtime_currentness"],
            "UNKNOWN",
        )
        self.assertTrue(self.manifest["authority"]["merge_deploy_not_granted_by_manifest"])

    def test_v3_remains_present_and_unchanged_in_history(self):
        old = ROOT / "database" / "BUILD_MANIFEST_V3.json"
        self.assertTrue(old.is_file())
        self.assertEqual(
            json.loads(old.read_text(encoding="utf-8"))["manifest_version"],
            "BT2_DATABASE_BUILD_MANIFEST_V3",
        )

    def test_scoped_identity_exactly_matches_head_qualification_tests(self):
        path, manifest, digest = module.load_and_verify_manifest(postgres_major=16)
        self.assertEqual(path, self.manifest_path)
        self.assertEqual(
            digest, manifest["package_identity"]["package_digest_sha256"]
        )
        self.assertNotIn("qualification_tests_tree", manifest["package_identity"])
        self.assertEqual(
            sorted(manifest["package_identity"]["qualification_tests_files"]),
            module._qualification_paths_at_head(),
        )

    def test_both_postgresql_majors_accepted_by_source_manifest(self):
        for major in (16, 17):
            with self.subTest(major=major):
                module.load_and_verify_manifest(postgres_major=major)
        with self.assertRaisesRegex(SystemExit, "does not admit PostgreSQL 15"):
            module.load_and_verify_manifest(postgres_major=15)

    def test_unlisted_new_postgresql_test_fails_closed(self):
        identity = copy.deepcopy(self.manifest["package_identity"])
        added = "tests/test_postgres_unlisted_qualification.py"
        with patch.object(
            module, "_qualification_paths_at_head",
            return_value=sorted([*identity["qualification_tests_files"], added]),
        ):
            with self.assertRaisesRegex(SystemExit, "membership mismatch"):
                module._verify_scoped_qualification_tests(identity)

    def test_missing_postgresql_test_fails_closed(self):
        identity = copy.deepcopy(self.manifest["package_identity"])
        paths = sorted(identity["qualification_tests_files"])
        with patch.object(module, "_qualification_paths_at_head", return_value=paths[:-1]):
            with self.assertRaisesRegex(SystemExit, "membership mismatch"):
                module._verify_scoped_qualification_tests(identity)

    def test_changed_qualification_blob_fails_closed(self):
        identity = copy.deepcopy(self.manifest["package_identity"])
        path = sorted(identity["qualification_tests_files"])[0]
        identity["qualification_tests_files"][path] = "0" * 40
        identity[module.SCOPED_QUALIFICATION_FIELD] = module.scoped_qualification_digest(
            identity["qualification_tests_files"]
        )
        with self.assertRaisesRegex(SystemExit, "blob mismatch"):
            module._verify_scoped_qualification_tests(identity)

    def test_tampered_test_set_digest_fails_closed(self):
        identity = copy.deepcopy(self.manifest["package_identity"])
        identity[module.SCOPED_QUALIFICATION_FIELD] = "f" * 64
        with self.assertRaisesRegex(SystemExit, "set digest mismatch"):
            module._verify_scoped_qualification_tests(identity)

    def test_unrelated_persona_test_does_not_change_v4_identity(self):
        expected = module.canonical_digest_input(self.manifest)
        fake = copy.deepcopy(self.manifest)
        fake["package_identity"]["qualification_tests_tree"] = "f" * 40
        self.assertEqual(module.canonical_digest_input(fake), expected)
        self.assertNotIn("qualification-tests:ffffffff", expected)
        self.assertIn("qualification-tests-scoped:", expected)
        self.assertNotIn("tests/", expected)

    def test_scoped_digest_is_order_independent_and_sensitive_to_blobs(self):
        original = {"tests/test_postgres_z.py": "1" * 40, "tests/test_postgres_a.py": "2" * 40}
        reversed_entries = dict(reversed(list(original.items())))
        self.assertEqual(
            module.scoped_qualification_digest(original),
            module.scoped_qualification_digest(reversed_entries),
        )
        changed = dict(original)
        changed["tests/test_postgres_a.py"] = "3" * 40
        self.assertNotEqual(
            module.scoped_qualification_digest(original),
            module.scoped_qualification_digest(changed),
        )

    def test_persona_trainer_is_outside_database_bound_tools_tree(self):
        # All current database qualification tools are under tools/qualification.
        # A LoRA trainer edit in tools/ must not invalidate a database package.
        self.assertEqual(
            module.TREE_BINDINGS["qualification_tools_tree"],
            "tools/qualification",
        )
        self.assertNotIn("tools", module.TREE_BINDINGS.values())
        self.assertNotIn("tools/train_personality_lora.py", module.TREE_BINDINGS.values())

    def test_changed_database_qualification_tools_tree_fails_closed(self):
        actual_tree = module._git_tree

        def changed_tree(path):
            if path == "tools/qualification":
                return "f" * 40
            return actual_tree(path)

        with patch.object(module, "_git_tree", side_effect=changed_tree):
            with self.assertRaisesRegex(
                SystemExit, "package tree mismatch for tools/qualification"
            ):
                module.load_and_verify_manifest(postgres_major=16)


if __name__ == "__main__":
    unittest.main()
