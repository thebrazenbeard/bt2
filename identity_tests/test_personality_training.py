"""Fast, dependency-free checks for persona data and Labyrinth schedule bridge."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_personality_sft import validate_persona_cases  # noqa: E402
from train_personality_lora import (  # noqa: E402
    build_schedule, donor_metadata_digests, encode_case, persona_instruction,
    require_isolated_output, verify_donor_metadata,
)
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

    def test_standalone_and_legacy_templates_override_embedded_and_are_pinned(self):
        with tempfile.TemporaryDirectory() as temp:
            donor = Path(temp)
            (donor / "config.json").write_text("{}", encoding="utf-8")
            (donor / "tokenizer.json").write_text("{}", encoding="utf-8")
            (donor / "tokenizer_config.json").write_text(
                '{"chat_template":"embedded-template"}', encoding="utf-8")
            embedded_only = donor_metadata_digests(donor)
            for name in ("chat_template.jinja", "chat_template.json"):
                with self.subTest(template=name):
                    file = donor / name
                    file.write_text("standalone-overrides-embedded", encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "donor metadata"):
                        verify_donor_metadata(donor, embedded_only)
                    pinned = donor_metadata_digests(donor)
                    self.assertIn(name, pinned)
                    file.write_text("silently-replaced", encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "donor metadata"):
                        verify_donor_metadata(donor, pinned)
                    file.write_text("standalone-overrides-embedded", encoding="utf-8")
                    file.unlink()
                    with self.assertRaisesRegex(ValueError, "donor metadata"):
                        verify_donor_metadata(donor, pinned)

    def test_named_templates_exact_file_set_and_content_are_pinned(self):
        with tempfile.TemporaryDirectory() as temp:
            donor = Path(temp)
            for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
                (donor / name).write_text("{}", encoding="utf-8")
            original = donor_metadata_digests(donor)
            extras = donor / "additional_chat_templates"
            extras.mkdir()
            a = extras / "tools.jinja"
            a.write_text("template-v1", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "donor metadata"):
                verify_donor_metadata(donor, original)
            pinned = donor_metadata_digests(donor)
            self.assertIn("additional_chat_templates/tools.jinja", pinned)
            a.write_text("template-v2", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "donor metadata"):
                verify_donor_metadata(donor, pinned)
            a.write_text("template-v1", encoding="utf-8")
            b = extras / "analysis.jinja"
            b.write_text("template-new", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "donor metadata"):
                verify_donor_metadata(donor, pinned)
            b.unlink()
            a.unlink()
            with self.assertRaisesRegex(ValueError, "donor metadata"):
                verify_donor_metadata(donor, pinned)

    def test_unsafe_template_paths_symlinks_and_nonregular_entries_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            donor = Path(temp)
            for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
                (donor / name).write_text("{}", encoding="utf-8")
            metadata = donor_metadata_digests(donor)
            bad_receipt = dict(metadata, **{"additional_chat_templates/../escape.jinja": "0" * 64})
            with self.assertRaisesRegex(ValueError, "metadata"):
                verify_donor_metadata(donor, bad_receipt)
            (donor / "chat_template.jinja").symlink_to(donor / "tokenizer_config.json")
            with self.assertRaisesRegex(ValueError, "metadata"):
                donor_metadata_digests(donor)
            (donor / "chat_template.jinja").unlink()
            extras = donor / "additional_chat_templates"
            extras.symlink_to(donor, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "metadata"):
                donor_metadata_digests(donor)
            extras.unlink()
            extras.mkdir()
            for unsafe in ("unexpected.txt", ".hidden.jinja", "nested"):
                with self.subTest(entry=unsafe):
                    path = extras / unsafe
                    if unsafe == "nested":
                        path.mkdir()
                    else:
                        path.write_text("untrusted", encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "metadata"):
                        donor_metadata_digests(donor)
                    if unsafe == "nested":
                        path.rmdir()
                    else:
                        path.unlink()
            linked = extras / "linked.jinja"
            linked.symlink_to(donor / "tokenizer_config.json")
            with self.assertRaisesRegex(ValueError, "metadata"):
                donor_metadata_digests(donor)
            linked.unlink()
            if hasattr(os, "mkfifo"):
                pipe = extras / "pipe.jinja"
                os.mkfifo(pipe)
                with self.assertRaisesRegex(ValueError, "metadata"):
                    donor_metadata_digests(donor)

    def test_exact_roster_and_train_dev_separation(self):
        dossiers = validate_persona_cases()
        self.assertEqual(len(dossiers), 13)
        self.assertEqual(sum(len(doc["cases"]) for doc in dossiers.values()), 78)
        self.assertEqual(sum(c["split"] == "train" for d in dossiers.values() for c in d["cases"]), 52)
        self.assertEqual(sum(c["split"] == "dev" for d in dossiers.values() for c in d["cases"]), 26)
        prior = set()
        for filename in (ROOT / "coding_models/training/cases").glob("*.json"):
            previous = json.loads(filename.read_text(encoding="utf-8"))
            prior.update(" ".join(c["task"].split()).casefold() for c in previous["cases"])
        for identity, doc in dossiers.items():
            with self.subTest(identity=identity):
                keys = {" ".join(c["task"].split()).casefold() for c in doc["cases"]}
                self.assertFalse(keys & prior, "persona task duplicates original SFT")
                self.assertEqual(len(keys), 6)

    def test_system_and_user_are_masked_from_supervision(self):
        dossiers = validate_persona_cases()
        profile = load_models()["one"]
        instruction = persona_instruction(profile, dossiers["one"]["traits"])
        self.assertIn("operational response tendencies", instruction)
        self.assertIn("subjective", instruction)
        self.assertIn(dossiers["one"]["traits"][0]["anti_pattern"], instruction)
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


if __name__ == "__main__":
    unittest.main()
