"""Regression tests for exact BT2 identity coding-model coverage and rendering."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "identity_coding_models", ROOT / "tools/identity_coding_models.py"
)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class IdentityCodingModelsTest(unittest.TestCase):
    def test_exact_thirteen_roles(self):
        models = module.load_models()
        self.assertEqual(set(models), {
            "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "thirteen", "masa", "mune", "hephaestus",
        })
        self.assertTrue(all(model["status"] == module.STATUS for model in models.values()))

    def test_source_bindings_remain_exact(self):
        models = module.load_models()
        sources = module.expected_worker_entrypoints()
        for identity, model in models.items():
            self.assertEqual(model["source_entrypoint"], sources[identity])

    def test_prompt_is_useful_but_non_activating(self):
        model = module.load_models()["three"]
        prompt = module.render_prompt(model, "Implement reproducible acceptance tests")
        self.assertIn("Implement reproducible acceptance tests", prompt)
        self.assertIn("temporary coding execution context", prompt)
        self.assertIn("## Execution protocol", prompt)
        self.assertIn("## Authority boundaries", prompt)
        self.assertIn("not proof of durable identity", prompt)

    def test_rejects_unknown_activation_or_source_drift(self):
        model = module.load_models()["one"].copy()
        model["status"] = "ACTIVE"
        with self.assertRaisesRegex(ValueError, "activation/status inflation"):
            module.validate_model(model, "one", model["source_entrypoint"])
        model["status"] = module.STATUS
        with self.assertRaisesRegex(ValueError, "source entrypoint drift"):
            module.validate_model(model, "one", "invented/role.md")

    def test_rejects_missing_or_extra_model(self):
        with tempfile.TemporaryDirectory(prefix="bt2-models-test-") as temp:
            root = Path(temp)
            (root / "native/project").mkdir(parents=True)
            (root / "coding_models/identities").mkdir(parents=True)
            topology = json.loads((ROOT / module.TOPOLOGY).read_text(encoding="utf-8"))
            (root / module.TOPOLOGY).write_text(json.dumps(topology), encoding="utf-8")
            for worker in topology["workers"]:
                source = root / worker["source_path"] / worker["entrypoint"]
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("stub", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "coverage mismatch"):
                module.load_models(root)


if __name__ == "__main__":
    unittest.main()
