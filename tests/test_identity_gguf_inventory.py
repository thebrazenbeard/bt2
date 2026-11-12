"""Check internal integrity of the unqualified thirteen-role GGUF inventory."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "coding_models/training/builds/gguf_q8_0_batch_20261028.json"
ONE_RECEIPT = ROOT / "coding_models/training/pilots/one_qwen25coder_cpu_lora_q8_0_20261028.json"
ROLES = {
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "thirteen", "masa", "mune", "hephaestus",
}


class TestIdentityGgufInventory(unittest.TestCase):
    def test_full_role_membership_and_distinct_digests(self):
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        models = inventory["models"]
        self.assertEqual({m["identity"] for m in models}, ROLES)
        self.assertEqual(len(models), len(ROLES))
        self.assertEqual(len({m["gguf_sha256"] for m in models}), len(ROLES))
        self.assertTrue(all(re.fullmatch(r"[a-f0-9]{64}", m["gguf_sha256"]) for m in models))
        self.assertTrue(all(re.fullmatch(r"[a-f0-9]{40}", m["source_commit"]) for m in models))
        self.assertTrue(all(m["gguf_bytes"] > 1_000_000_000 for m in models))
        self.assertTrue(all(m["smoke_exit_code"] == 0 for m in models))
        self.assertEqual(inventory["method"]["optimizer_steps_per_role"], 2)
        self.assertFalse(inventory["method"]["role_identity_qualified"])
        self.assertFalse(inventory["method"]["ollama_tag_installed"])
        self.assertFalse(inventory["storage"]["models_in_git_history"])

    def test_one_is_bound_to_immutable_source_receipt(self):
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        receipt = json.loads(ONE_RECEIPT.read_text(encoding="utf-8"))
        one = next(m for m in inventory["models"] if m["identity"] == "one")
        self.assertEqual(one["gguf_sha256"], receipt["gguf"]["sha256"])
        self.assertEqual(one["gguf_bytes"], receipt["gguf"]["bytes"])
        self.assertEqual(one["gguf_filename"], receipt["gguf"]["filename"])
        self.assertEqual(one["source_commit"], receipt["training"]["bt2_source_commit"])

    def test_remaining_models_bind_to_per_role_receipts(self):
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        for model in inventory["models"]:
            if model["identity"] == "one":
                continue
            with self.subTest(identity=model["identity"]):
                path = INVENTORY.parent / model["source_receipt"]
                receipt = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(receipt["identity_id"], model["identity"])
                self.assertEqual(receipt["gguf_name"], model["gguf_filename"])
                self.assertEqual(receipt["gguf_bytes"], model["gguf_bytes"])
                self.assertEqual(receipt["gguf_sha256"], model["gguf_sha256"])
                self.assertEqual(receipt["source_commit"], model["source_commit"])
                self.assertEqual(receipt["training_steps"], 2)
                self.assertNotEqual(receipt["tensor_sha256_before"], receipt["tensor_sha256_after"])
                self.assertEqual(receipt["smoke_exit_code"], 0)
                self.assertFalse(receipt["installed"])
                self.assertFalse(receipt["qualified"])


if __name__ == "__main__":
    unittest.main()
