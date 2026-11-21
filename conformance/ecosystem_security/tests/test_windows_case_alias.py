"""Case-folded Windows security paths must not evade Linux scanner CI.

All files are synthetic, inert; neither editor commands nor package scripts run.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scanner

HEAD = "c" * 40


class WindowsCaseAliasTests(unittest.TestCase):
    def findings(self, root):
        return scanner.scan_workspace(root, "example/synthetic", HEAD)

    def test_nested_mixed_case_vscode_folder_open_cannot_scan_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "packages" / "module" / ".VSCODE"
            folder.mkdir(parents=True)
            (folder / "TASKS.JSON").write_text(json.dumps({
                "tasks": [{"label": "open", "command": "echo synthetic",
                           "runOptions": {"runOn": "folderOpen"}}]}),
                encoding="utf-8")
            out = self.findings(root)
            self.assertTrue(any(f.rule_id == "SECURITY_PATH_CASE_ALIAS"
                                and f.severity == "HIGH"
                                and ".VSCODE" in f.path for f in out), out)

    def test_mixed_case_package_and_disguised_font_sources_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = root / "packages" / "module"
            module.mkdir(parents=True)
            (module / "PACKAGE.JSON").write_text(json.dumps({
                "scripts": {"postinstall": "echo synthetic"}}), encoding="utf-8")
            fonts = module / "PUBLIC" / "FONTS"
            fonts.mkdir(parents=True)
            (fonts / "look.TTF").write_bytes(b"inert non-font sample")
            out = self.findings(root)
            paths = {f.path for f in out
                     if f.rule_id == "SECURITY_PATH_CASE_ALIAS" and f.severity == "HIGH"}
            self.assertIn("packages/module/PACKAGE.JSON", paths, out)
            self.assertTrue(any("PUBLIC" in p or "FONTS" in p for p in paths), out)

    def test_case_alias_high_fails_cli_source_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "tools"
            folder.mkdir()
            (folder / "PACKAGE.JSON").write_text('{"scripts":{"postinstall":"echo synthetic"}}')
            result = subprocess.run(
                [sys.executable, "-B", str(Path(scanner.__file__)),
                 "--root", str(root), "--repo", "example/synthetic",
                 "--head", HEAD, "--fail-on-high", "--format", "json"],
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertIn("SECURITY_PATH_CASE_ALIAS", result.stdout)

    def test_code_workspace_extension_alias_is_high(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "office.CODE-WORKSPACE").write_text('{"settings":{},"tasks":{}}')
            out = self.findings(root)
            self.assertTrue(any(f.rule_id == "SECURITY_PATH_CASE_ALIAS"
                                and f.severity == "HIGH"
                                and f.path == "office.CODE-WORKSPACE" for f in out), out)

    def test_canonical_and_unrelated_uppercase_names_do_not_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.MD").write_text("synthetic")
            (root / "package.json").write_text('{"scripts": {}}')
            folder = root / "public" / "fonts"
            folder.mkdir(parents=True)
            (folder / "font.ttf").write_bytes(b"\x00\x01\x00\x00" + b"x" * 12)
            out = self.findings(root)
            self.assertFalse(any(f.rule_id == "SECURITY_PATH_CASE_ALIAS" for f in out), out)


if __name__ == "__main__":
    unittest.main()
