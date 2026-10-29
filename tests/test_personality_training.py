"""Fast, dependency-free checks for persona data and Labyrinth schedule bridge."""

import json
import copy
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_personality_sft import validate_persona_cases  # noqa: E402
from train_personality_lora import (  # noqa: E402
    build_schedule, crossrole_label_targets, donor_metadata_digests, encode_case,
    neutral_instruction, persona_instruction, require_isolated_output,
    verify_donor_metadata,
)
import validate_personality_sft as persona_validation  # noqa: E402
from identity_coding_models import load_models  # noqa: E402


class FakeTokenizer:
    eos_token = "!"

    def apply_chat_template(self, messages, tokenize, add_generation_prompt):
        assert not tokenize and add_generation_prompt
        return "[SYSTEM] " + messages[0]["content"] + " [USER] " + messages[1]["content"] + " [ASSISTANT] "

    def __call__(self, text, add_special_tokens):
        assert not add_special_tokens
        return {"input_ids": [ord(char) for char in text]}


class PersonaTrainingTests(unittest.TestCase):
    def test_training_metadata_snapshot_and_reload_guards(self):
        with tempfile.TemporaryDirectory() as temp:
            donor = Path(temp)
            for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
                (donor / name).write_text("{}", encoding="utf-8")
            pinned = donor_metadata_digests(donor)
            self.assertEqual(set(pinned),
                             {"config.json", "tokenizer.json", "tokenizer_config.json"})
            self.assertEqual(verify_donor_metadata(donor, pinned), pinned)
            (donor / "generation_config.json").write_text('{"temperature":0}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "donor metadata"):
                verify_donor_metadata(donor, pinned)
            current = donor_metadata_digests(donor)
            self.assertIn("generation_config.json", current)
            (donor / "tokenizer.json").write_text('{"changed":true}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "donor metadata"):
                verify_donor_metadata(donor, current)

    def test_exact_roster_and_train_dev_separation(self):
        dossiers = validate_persona_cases()
        self.assertEqual(len(dossiers), 13)
        self.assertGreaterEqual(sum(len(doc["cases"]) for doc in dossiers.values()), 78)
        self.assertEqual(sum(c["split"] == "dev" for d in dossiers.values() for c in d["cases"]), 26)
        prior = set()
        for filename in (ROOT / "coding_models/training/cases").glob("*.json"):
            previous = json.loads(filename.read_text(encoding="utf-8"))
            prior.update(" ".join(c["task"].split()).casefold() for c in previous["cases"])
        for identity, doc in dossiers.items():
            with self.subTest(identity=identity):
                keys = {" ".join(c["task"].split()).casefold() for c in doc["cases"]}
                self.assertFalse(keys & prior, "persona task duplicates original SFT")
                self.assertEqual(len(keys), len(doc["cases"]))
                train = [c for c in doc["cases"] if c["split"] == "train"]
                self.assertGreaterEqual(len(train), 4)
                self.assertLessEqual(len(train), 16)
                self.assertEqual(len(train) % 2, 0)

    def test_old_six_case_and_new_ten_case_dossiers_both_validate(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture_root = Path(temp)
            for path in persona_validation.CASE_ROOT.glob("*.json"):
                (fixture_root / path.name).write_bytes(path.read_bytes())
            four_file = fixture_root / "four.json"
            four = json.loads(four_file.read_text(encoding="utf-8"))
            # Start with an older 4-TRAIN/2-DEV-compatible fixture even though
            # the current live corpus already has 8 TRAIN per identity.
            train = [c for level in ("grounded", "adversarial")
                     for c in [case for case in four["cases"]
                               if case["split"] == "train" and case["level"] == level][:2]]
            dev = [c for c in four["cases"] if c["split"] == "dev"]
            four["cases"] = train + dev
            for offset, item in enumerate(train):
                added = copy.deepcopy(item)
                added["id"] = f"four-persona-train-{101 + offset}"
                added["task"] += f" New independent variation {offset + 1}: produce an additional testable example."
                four["cases"].append(added)
            four_file.write_text(json.dumps(four), encoding="utf-8")
            previous = persona_validation.CASE_ROOT
            try:
                persona_validation.CASE_ROOT = fixture_root
                dossiers = persona_validation.validate_persona_cases()
                self.assertEqual(len(dossiers["four"]["cases"]), 10)
                self.assertEqual(len(dossiers["one"]["cases"]), 10)
            finally:
                persona_validation.CASE_ROOT = previous

    def test_system_and_user_are_masked_from_supervision(self):
        dossiers = validate_persona_cases()
        profile = load_models()["one"]
        instruction = persona_instruction(profile, dossiers["one"]["traits"])
        self.assertIn("behavioral tendencies", instruction)
        self.assertNotIn("Role: ", instruction)
        self.assertNotIn("Objective: ", instruction)
        self.assertIn(dossiers["one"]["traits"][0]["anti_pattern"], instruction)
        self.assertEqual(neutral_instruction(), neutral_instruction())
        self.assertNotIn(profile["display_name"], neutral_instruction())
        self.assertNotIn(profile["role"], neutral_instruction())
        task = next(c for c in dossiers["one"]["cases"] if c["split"] == "train")
        tokenizer = FakeTokenizer()
        ids, labels = encode_case(tokenizer, instruction, task, task["ideal_response"], 4000)
        self.assertEqual(len(ids), len(labels))
        self.assertTrue(all(item == -100 for item in labels[:len(ids)-len(task["ideal_response"])-1]))
        self.assertEqual(labels[-1], ord("!"))
        self.assertTrue(any(item != -100 for item in labels))
        with self.assertRaises(ValueError):
            encode_case(tokenizer, instruction, task, task["ideal_response"], 100)

    def test_run_directory_never_overlaps_sources_or_donor(self):
        donor = Path("/experiment/donor")
        bt2 = Path("/experiment/source-bt2")
        labyrinth = Path("/experiment/source-labyrinth")
        require_isolated_output(Path("/experiment/persona-output/one"), donor, bt2, labyrinth)
        for target in (donor, donor / "nested", Path("/experiment"),
                       bt2 / "personality", labyrinth / "cases"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                require_isolated_output(target, donor, bt2, labyrinth)

    def test_crossrole_corruption_requires_identical_train_prompt(self):
        task = "Debug the exact shared incident without inventing deployment state."
        chosen = [{"id": "two-persona-train-101", "split": "train",
                   "task": task, "contrastive_group": "shared-retry-incident",
                   "ideal_response": "Two answers using invariants."}]
        alt = {"id": "four-persona-train-101", "split": "train",
               "task": task, "contrastive_group": "shared-retry-incident",
               "ideal_response": "Four answers through creative alternatives."}
        dossiers = {"two": {"cases": chosen}, "four": {"cases": [alt]}}
        targets, provenance = crossrole_label_targets("two", chosen, dossiers, seed=74413)
        self.assertEqual(targets, [alt["ideal_response"]])
        self.assertEqual(provenance[0]["source_identity"], "four")
        self.assertEqual(targets, crossrole_label_targets("two", chosen, dossiers, seed=74413)[0])
        for broken in (dict(alt, task=task + " changed"),
                       dict(alt, split="dev"),
                       dict(alt, contrastive_group="shared-another-group"),
                       dict(alt, ideal_response=chosen[0]["ideal_response"])):
            with self.subTest(broken=broken), self.assertRaisesRegex(ValueError, "exact same-task"):
                crossrole_label_targets("two", chosen,
                                        {"two": {"cases": chosen}, "four": {"cases": [broken]}},
                                        seed=74413)
        with self.assertRaisesRegex(ValueError, "grouped training"):
            crossrole_label_targets("two", [dict(chosen[0], contrastive_group=None)],
                                    dossiers, seed=74413)

    def test_actual_labyrinth_source_optional_integration(self):
        labyrinth = ROOT.parent / "labyrinth-personality-20261028"
        if not (labyrinth / "labyrinth/curriculum.py").is_file():
            self.skipTest("pinned Labyrinth source checkout not present")
        cases = validate_persona_cases()["mune"]["cases"]
        a = build_schedule(cases, labyrinth_dir=labyrinth, seed=74413, steps=4)
        b = build_schedule(cases, labyrinth_dir=labyrinth, seed=74413, steps=4)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 4)
        self.assertEqual({x["level"] for x in a}, {"grounded", "adversarial"})
        self.assertEqual(len({x["case_id"] for x in a}), 4)
        self.assertFalse(any("dev" in x["case_id"] for x in a))
        with self.assertRaises(ValueError):
            build_schedule(cases, labyrinth_dir=labyrinth, seed=74413, steps=3)
        schedule = build_schedule(cases, labyrinth_dir=labyrinth, seed=74413, steps=8)
        self.assertEqual(len(schedule), 8)
        self.assertEqual(len({c["case_id"] for c in schedule}), 8)
        with self.assertRaisesRegex(ValueError, "not enough unique"):
            build_schedule(cases, labyrinth_dir=labyrinth, seed=74413, steps=10)
        # The corrected full curriculum visits all TRAIN examples and no DEV.
        self.assertEqual({x["case_id"] for x in schedule},
                         {c["id"] for c in cases if c["split"] == "train"})


if __name__ == "__main__":
    unittest.main()
