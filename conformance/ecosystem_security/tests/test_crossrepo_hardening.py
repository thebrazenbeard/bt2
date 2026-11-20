"""Independent hostile cases against the exact A scanner source.
Synthetic only: no editor, hook, disguised executable or remote provider is run.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scanner as s
HEAD = "a" * 40


class CrossRepoSecurityTests(unittest.TestCase):
    def test_nested_workspace_hidden_startup_is_not_missed(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            folder = root / "packages" / "crew" / ".vscode"
            folder.mkdir(parents=True)
            (folder / "tasks.json").write_text(json.dumps({"tasks": [{
                "label": "startup", "command": "${workspaceFolder}/startup.cmd",
                "hide": True, "runOptions": {"runOn": "folderOpen"}}]}))
            (folder / "settings.json").write_text(json.dumps({"task.allowAutomaticTasks": True}))
            out = s.scan_workspace(root, "example/repo", HEAD)
            self.assertTrue(any(f.rule_id == "EDITOR_OPEN_EXECUTION" and
                                f.path == "packages/crew/.vscode/tasks.json"
                                for f in out), [f.rule_id for f in out])

    def test_code_workspace_hidden_startup_is_not_missed(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "crew.code-workspace").write_text(json.dumps({
                "settings": {"task.allowAutomaticTasks": True},
                "tasks": {"version": "2.0.0", "tasks": [{
                    "label": "startup", "command": "node hidden.dat", "hide": True,
                    "runOptions": {"runOn": "folderOpen"}}]}}))
            out = s.scan_workspace(root, "example/repo", HEAD)
            self.assertTrue(any(f.rule_id == "WORKSPACE_FILE_AUTOEXEC" and
                                f.path == "crew.code-workspace" for f in out),
                            [f.rule_id for f in out])

    def test_nested_package_install_hook_executes_disguised_asset(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            folder = root / "packages" / "crew"
            folder.mkdir(parents=True)
            (folder / "package.json").write_text(json.dumps({
                "name": "crew", "scripts": {"postinstall": "node public/fonts/looks.ttf"}}))
            out = s.scan_workspace(root, "example/repo", HEAD)
            self.assertTrue(any(f.rule_id == "PACKAGE_LIFECYCLE_EXECUTION" and
                                f.path == "packages/crew/package.json" and
                                f.severity in ("HIGH", "CRITICAL") for f in out),
                            [f.rule_id for f in out])

    def test_nested_manifest_malformed_json_cannot_be_clean(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            folder = root / "packages" / "crew"
            folder.mkdir(parents=True)
            (folder / "package.json").write_text('{"scripts": {"preinstall":')
            out = s.scan_workspace(root, "example/repo", HEAD)
            self.assertTrue(any(f.rule_id == "CONFIG_UNREADABLE" and
                                f.path == "packages/crew/package.json" for f in out),
                            [f.rule_id for f in out])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink unavailable")
    def test_nested_symlink_cannot_hide_unknown_security_source(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            outsite = Path(t) / "source-target"
            outsite.mkdir()
            (root / "packages").mkdir()
            (root / "packages" / "crew").symlink_to(outsite, target_is_directory=True)
            found = s.scan_workspace(root, "example/repo", HEAD)
            self.assertTrue(any(f.rule_id == "CONFIG_UNREADABLE" and
                                f.path == "packages/crew" for f in found),
                            [f.rule_id for f in found])

    def test_duplicate_task_labels_are_unqualified(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            folder = root / ".vscode"
            folder.mkdir()
            (folder / "tasks.json").write_text(json.dumps({"tasks": [
                {"label": "same", "command": "node normal.js"},
                {"label": "same", "command": "node suspicious.ttf"},
                {"label": "startup", "dependsOn": "same",
                 "runOptions": {"runOn": "folderOpen"}}]}))
            out = s.scan_workspace(root, "example/repo", HEAD)
            self.assertTrue(any(f.rule_id == "CONFIG_SCHEMA_INVALID" and
                                f.path == ".vscode/tasks.json" for f in out),
                            [f.rule_id for f in out])

    def test_dirty_scanned_source_must_not_pass_provenance_gate(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            folder = root / ".vscode"
            folder.mkdir()
            task = folder / "tasks.json"
            task.write_text('{"tasks": []}')
            subprocess.run(["git", "-C", str(root), "add", ".vscode/tasks.json"], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=T", "-c", "user.email=t@invalid", "commit", "-qm", "init"], check=True)
            head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            task.write_text('{"tasks": [{"label":"x","command":"node malicious.ttf"}]}')
            result = subprocess.run([sys.executable, str(Path(s.__file__)), "--root", str(root),
                "--repo", "example/repo", "--head", head,
                "--require-git-head", "--require-clean-source", "--fail-on-high"],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, "dirty source was treated as pinned HEAD")
            self.assertIn("SOURCE_TREE_DIRTY", result.stderr + result.stdout)


class TraversalTrustTests(unittest.TestCase):
    def test_disguised_font_inside_package_directory_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            folder=root/'packages'/'crew'/'public'/'fonts'
            folder.mkdir(parents=True)
            (folder/'spoof.TTF').write_bytes(b'not a font')
            findings=s.scan_workspace(root,'example/repo',HEAD)
            self.assertTrue(any(f.rule_id=='FONT_MAGIC_MISMATCH' and
                f.path=='packages/crew/public/fonts/spoof.TTF' for f in findings),
                [f.rule_id for f in findings])

    def test_walker_oserror_cannot_be_reported_as_clean(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def walk_stub(*args, **kwargs):
                onerror=kwargs.get('onerror')
                if onerror:
                    onerror(PermissionError('synthetic inaccessible directory'))
                return iter([(str(root), [], [])])
            with patch.object(s.os,'walk',side_effect=walk_stub):
                out=s.scan_workspace(root,'example/repo',HEAD)
            self.assertTrue(any(f.rule_id=='CONFIG_UNREADABLE' for f in out),
                'os.walk access error cannot be a clean scan')

    def test_unbounded_directory_traversal_is_a_hold(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def many_dirs(*args, **kwargs):
                for i in range(8193):
                    yield str(root), [], []
            with patch.object(s.os,'walk',side_effect=many_dirs):
                out=s.scan_workspace(root,'example/repo',HEAD)
            self.assertTrue(any(f.rule_id=='SCAN_LIMIT_EXCEEDED' for f in out),
                'synthetic huge traversal must fail closed')
