import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


validator = load_module(ROOT / "tools" / "validate_package.py", "validate_package")
checkpoint = load_module(ROOT / "tools" / "training_checkpoint.py", "training_checkpoint")


class TrainingToolsTests(unittest.TestCase):
    def make_package(self, root: Path):
        pkg = root / "pkg"
        (pkg / "modules").mkdir(parents=True)
        (pkg / "BOOTSTRAP.md").write_text("loader\n", encoding="utf-8")
        (pkg / "modules" / "01.md").write_text("exercise\n", encoding="utf-8")
        (pkg / "modules" / "02.md").write_text("qualification\n", encoding="utf-8")
        manifest = {
            "schema": "BT2_ROLE_TRAINING_MANIFEST_V1",
            "package_id": "bt2-role-three-training",
            "training_version": "test",
            "role": {"identity": "Three"},
            "non_goals": ["Restore current assignments", "Authorize any external mutation"],
            "modules": [
                {"order": 1, "id": "M1", "path": "modules/01.md", "pass_criteria": ["reason"]},
                {"order": 2, "id": "Q", "path": "modules/02.md", "qualification_module": True, "pass_criteria": ["integrate"]}
            ],
            "qualification": {"result_values": ["BASE_READY", "NOT_QUALIFIED"]}
        }
        (pkg / "TRAINING_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
        return pkg

    def test_package_validation_and_checkpoint_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = self.make_package(root)
            self.assertTrue(validator.validate_package(pkg)["valid"])
            cp = root / "checkpoint.json"
            checkpoint.init_checkpoint(pkg, cp)
            checkpoint.record_module(pkg, cp, "M1", "PASS", ["eval:1"])
            checkpoint.record_module(pkg, cp, "Q", "PASS", ["eval:2"])
            receipt = checkpoint.qualify(pkg, cp)
            self.assertEqual(receipt["result"], "BASE_READY")
            self.assertTrue(checkpoint.verify_checkpoint(pkg, cp)["valid"])

    def test_checkpoint_cannot_live_inside_training_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = self.make_package(root)
            with self.assertRaisesRegex(ValueError, "CHECKPOINT_MUST_BE_OUTSIDE"):
                checkpoint.init_checkpoint(pkg, pkg / "progress.json")

    def test_manifest_tamper_invalidates_checkpoint_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = self.make_package(root)
            cp = root / "checkpoint.json"
            checkpoint.init_checkpoint(pkg, cp)
            manifest_path = pkg / "TRAINING_MANIFEST.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["training_version"] = "tampered"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = checkpoint.verify_checkpoint(pkg, cp)
            self.assertFalse(result["valid"])
            self.assertIn("TRAINING_VERSION_MISMATCH", result["errors"])
            self.assertIn("MANIFEST_SHA256_MISMATCH", result["errors"])

    def test_unresolved_prevents_base_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pkg = self.make_package(root)
            cp = root / "checkpoint.json"
            checkpoint.init_checkpoint(pkg, cp)
            checkpoint.record_module(pkg, cp, "M1", "PASS", [])
            checkpoint.record_module(pkg, cp, "Q", "UNRESOLVED", [])
            self.assertEqual(checkpoint.qualify(pkg, cp)["result"], "TRAINING_UNRESOLVED")


if __name__ == "__main__":
    unittest.main()
