"""Source-only tests: blinded comparisons must not invent correctness."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "coding_models/personality/evaluation_v2"))
import runner as evaluation  # noqa: E402


class PersonalityEvalV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.donor = self.root / "donor.gguf"
        self.candidate = self.root / "candidate.gguf"
        self.cli = self.root / "llama-cli.exe"
        for file, content in ((self.donor, b"donor"),
                              (self.candidate, b"candidate"),
                              (self.cli, b"llama-cli")):
            file.write_bytes(content)
        self.report = self.root / "candidate-report.json"
        self.report.write_text(json.dumps({
            "identity_id": "four", "arm": "candidate",
            "qualified": False, "installed": False,
            "frozen_parameters_and_buffers_verified_unchanged": True,
        }), encoding="utf-8")
        self.traits = "Consider several imaginative approaches, then make one falsifiable prototype."
        self.models = [
            {"identity": "four", "variant": "donor",
             "model_path": str(self.donor), "model_sha256": evaluation.file_digest(self.donor),
             "trait_instruction": self.traits},
            {"identity": "four", "variant": "candidate",
             "model_path": str(self.candidate), "model_sha256": evaluation.file_digest(self.candidate),
             "trait_instruction": self.traits,
             "training_report_path": str(self.report),
             "training_report_sha256": evaluation.file_digest(self.report)},
        ]
        self.cases = [
            {"case_id": "opaque-b1", "domain": "behavior", "rubric_id": "independent-b1",
             "prompt": "Propose several ways to make a small art display inclusive."},
            {"case_id": "opaque-c1", "domain": "code", "function": "sample_function",
             "rubric_id": "independent-c1",
             "prompt": "Implement sample_function that returns the input unchanged."},
        ]

    def make_plan(self):
        return evaluation.plan(self.models, self.cases, seed=30)

    def test_paired_plan_exact_prompts_and_reproducible_shuffle(self):
        rows = self.make_plan()
        self.assertEqual(rows, self.make_plan())
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({r["run_id"] for r in rows}), 8)
        evaluation.validate_plan(rows)
        for case in self.cases:
            for mode in evaluation.PROMPT_MODES:
                matching = [r for r in rows if r["case_id"] == case["case_id"]
                            and r["prompt_mode"] == mode]
                self.assertEqual({r["variant"] for r in matching}, {"donor", "candidate"})
                self.assertEqual(len({r["prompt_sha256"] for r in matching}), 1)
        neutral = [r for r in rows if r["prompt_mode"] == "neutral"]
        self.assertTrue(all(self.traits not in r["prompt"] for r in neutral))
        self.assertTrue(all(self.traits in r["prompt"] for r in rows
                            if r["prompt_mode"] == "traits"))

    def test_duplicate_unpinned_or_unmatched_model_control_rejected(self):
        wrong = [dict(m) for m in self.models]
        wrong[1]["trait_instruction"] = "A contradictory and otherwise sufficient instruction."
        with self.assertRaisesRegex(ValueError, "not matched"):
            evaluation.plan(wrong, self.cases, 30)
        wrong = [dict(m) for m in self.models]
        wrong[1].pop("training_report_sha256")
        with self.assertRaisesRegex(ValueError, "training receipt"):
            evaluation.plan(wrong, self.cases, 30)
        with self.assertRaisesRegex(ValueError, "duplicate model variant"):
            evaluation.plan(self.models + [self.models[0]], self.cases, 30)

    def test_generation_uses_direct_argv_zero_temperature_and_no_code_execution(self):
        rows = self.make_plan()
        completed = subprocess.CompletedProcess([], 0,
                                                stdout="def sample_function(x):\n    return x\n",
                                                stderr="model loaded")
        with mock.patch.object(evaluation.subprocess, "run", return_value=completed) as runner:
            answers = evaluation.generate(
                rows, cli=self.cli, expected_cli_sha256=evaluation.file_digest(self.cli),
                max_tokens=128, threads=2, timeout=30, seed=9)
        self.assertEqual(len(answers), len(rows))
        self.assertEqual(runner.call_count, len(rows))
        arguments = runner.call_args.args[0]
        self.assertIsInstance(arguments, list)
        self.assertIn("--temp", arguments)
        self.assertEqual(arguments[arguments.index("--temp") + 1], "0")
        self.assertEqual(arguments[arguments.index("-ngl") + 1], "0")
        self.assertFalse(runner.call_args.kwargs.get("shell", False))
        self.assertEqual(answers[0]["response_sha256"], evaluation.digest(answers[0]["response"]))

    def test_unpinned_model_or_wrong_control_receipt_blocks_inference(self):
        rows = self.make_plan()
        self.candidate.write_bytes(b"tampered")
        with mock.patch.object(evaluation.subprocess, "run") as runner:
            with self.assertRaisesRegex(ValueError, "model digest mismatch"):
                evaluation.generate(rows, cli=self.cli,
                                    expected_cli_sha256=evaluation.file_digest(self.cli),
                                    max_tokens=10, threads=1, timeout=10, seed=0)
            runner.assert_not_called()
        self.candidate.write_bytes(b"candidate")
        self.report.write_text(json.dumps({
            "identity_id": "four", "arm": "sham", "qualified": False,
            "installed": False, "frozen_parameters_and_buffers_verified_unchanged": True,
        }), encoding="utf-8")
        self.models[1]["training_report_sha256"] = evaluation.file_digest(self.report)
        rows = self.make_plan()  # New receipt hash is valid, but arm is false.
        with self.assertRaisesRegex(ValueError, "does not establish"):
            evaluation.verify_inputs(rows, self.cli, evaluation.file_digest(self.cli))

    def test_blinding_and_human_scoring_remain_distinct_from_static_syntax(self):
        rows = self.make_plan()
        completed = subprocess.CompletedProcess([], 0,
                                                stdout="def sample_function(x):\n    return x\n",
                                                stderr="")
        with mock.patch.object(evaluation.subprocess, "run", return_value=completed):
            answers = evaluation.generate(
                rows, cli=self.cli, expected_cli_sha256=evaluation.file_digest(self.cli),
                max_tokens=128, threads=1, timeout=30, seed=4)
        packet, key = evaluation.blind_packet(answers, rows, seed=57)
        self.assertEqual(len(packet), 8)
        self.assertEqual(len(key), 8)
        self.assertTrue(all("variant" not in row and "model_sha256" not in row
                            for row in packet))
        forged = [dict(item) for item in answers]
        forged[0]["variant"] = "donor" if forged[0]["variant"] == "candidate" else "candidate"
        with self.assertRaisesRegex(ValueError, "custody mismatch"):
            evaluation.blind_packet(forged, rows, seed=57)
        self.assertTrue(all(row["syntax_diagnostic_not_correctness"].get("python_parse")
                            is None for row in packet if row["domain"] == "behavior"))
        # Neither a Python parser nor a declared function is a correctness oracle.
        self.assertEqual(evaluation.syntax_diagnostic("def sample_function(x):\n    return 999", "sample_function"),
                         {"python_parse": True, "declares_interface": True})
        scores = [{"review_id": entry["review_id"],
                   "response_sha256": entry["response_sha256"],
                   "correctness": 3 if entry["variant"] == "candidate" else 1,
                   "role_fidelity": 4 if entry["variant"] == "candidate" else 2}
                  for entry in key]
        summary = evaluation.summarize(key, scores)
        self.assertFalse(summary["qualified"])
        self.assertEqual(summary["missing_human_reviews"], 0)
        self.assertEqual(len(summary["comparisons"]), 4)
        self.assertTrue(all(x["identity"] == "four" and
                            x["mean_correctness_delta"] == 2 and
                            x["mean_role_fidelity_delta"] == 2
                            for x in summary["comparisons"]))
        role_only = [dict(item, correctness=None) for item in scores]
        unknown_correctness = evaluation.summarize(key, role_only)
        self.assertTrue(all(x["mean_correctness_delta"] is None and
                            x["paired_correctness_scores"] == 0 and
                            x["mean_role_fidelity_delta"] == 2
                            for x in unknown_correctness["comparisons"]))
        partial = evaluation.summarize(key, scores[:-1])
        self.assertEqual(partial["missing_human_reviews"], 1)
        with self.assertRaisesRegex(ValueError, "response digest"):
            evaluation.summarize(key, [dict(scores[0], response_sha256="0" * 64)])

    def test_forged_unmatched_prompt_and_exclusive_outputs_rejected(self):
        rows = self.make_plan()
        other = [dict(item) for item in rows]
        candidate = next(r for r in other if r["variant"] == "candidate")
        candidate["prompt"] += " attacker-modified prompt"
        candidate["prompt_sha256"] = evaluation.digest(candidate["prompt"])
        with self.assertRaisesRegex(ValueError, "unmatched paired prompt"):
            evaluation.validate_plan(other)
        incomplete = [item for item in rows if item["run_id"] != rows[0]["run_id"]]
        with self.assertRaisesRegex(ValueError, "incomplete paired case coverage"):
            evaluation.validate_plan(incomplete)
        output = self.root / "plan.jsonl"
        evaluation.write_jsonl_new(output, rows)
        with self.assertRaises(FileExistsError):
            evaluation.write_jsonl_new(output, rows)

    def test_generation_refuses_unbounded_batches_before_model_loading(self):
        original = self.make_plan()
        oversized = [dict(original[index % len(original)],
                          run_id=f"oversized-{index}") for index in range(129)]
        with mock.patch.object(evaluation, "verify_inputs") as verify:
            with self.assertRaisesRegex(ValueError, "shard by identity"):
                evaluation.generate(oversized, cli=self.cli,
                                    expected_cli_sha256=evaluation.file_digest(self.cli),
                                    max_tokens=128, threads=2, timeout=30, seed=1)
            verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
