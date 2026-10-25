"""Lou-Pole source-only advisory handoff tests (not runtime authorization)."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lou_pole_advisory import (
    InvalidAdvisory,
    build_advisory,
    load_bounded,
    parse_report,
)


ENGINE_REVISION = "245186d6baad672460dec112b916470d8b13633e"
SOURCE = (
    "Operators must not delete customer records.\n"
    "Operators may ask another service to delete customer records.\n"
).encode("utf-8")


def sample_report() -> dict[str, object]:
    return {
        "profile": "instructions",
        "intent": "Prevent prohibited effects via delegation",
        "risk_score": 24,
        "finding_count": 1,
        "findings": [{
            "rule_id": "FRC-PATH-DELEGATE-R0001-R0002",
            "category": "delegation_laundering",
            "severity": "high",
            "title": "A prohibited effect has a delegated route",
            "evidence": [
                {"line_start": 1, "line_end": 1,
                 "text": "Operators must not delete customer records."},
                {"line_start": 2, "line_end": 2,
                 "text": "Operators may ask another service to delete customer records."},
            ],
            "why_it_matters": "An indirect route may produce a restricted effect.",
            "literalist_path": "Ask a separate service to carry out the deletion.",
            "hardening": "Cover the outcome through delegated and direct routes.",
            "confidence": 0.78,
        }],
        "coverage": {
            "status": "heuristic_extracted_unverified",
            "nonempty_clause_count": 2,
            "extracted_rule_count": 2,
            "unparsed_normative_clause_count": 0,
            "unparsed_normative_clauses": [],
            "nonoperative_clause_count": 0,
            "nonoperative_clauses": [],
            "notice": "Heuristic extraction is not a safety determination.",
        },
        "source": {
            "content_sha256": hashlib.sha256(SOURCE).hexdigest(),
            "digest_basis": "analyzed_text_utf8",
            "verification": "not_checked",
        },
    }


def intent_report() -> dict[str, object]:
    """Exact opt-in --intent addition from Lou-Pole main after issue #9."""
    report = sample_report()
    report["coverage"]["intent_evaluation"] = {
        "status": "not_evaluated",
        "unsupported_mechanisms": [
            "ordered_state_transitions", "cross_instance_identity_and_credit",
            "external_evidence_custody",
        ],
        "notice": "Declared intent is not evaluated or enforced.",
    }
    return report


class LouPoleAdvisoryTests(unittest.TestCase):
    def test_valid_candidates_are_explicitly_not_authority(self):
        artifact = build_advisory(SOURCE, sample_report(), engine_revision=ENGINE_REVISION)
        self.assertEqual(artifact["schema"], "BT2_LOU_POLE_ADVISORY_V1")
        self.assertEqual(artifact["review_status"], "CANDIDATES_REQUIRE_REVIEW")
        self.assertEqual(artifact["authorization_effect"], "NONE")
        self.assertEqual(artifact["engine"]["declared_revision"], ENGINE_REVISION)
        self.assertEqual(artifact["engine"]["revision_verified"], False)
        self.assertEqual(artifact["source"]["digest_verified_against_input"], True)
        self.assertEqual(artifact["findings"][0]["severity"], "high")

    def test_zero_findings_never_means_clearance(self):
        report = sample_report()
        report["risk_score"] = 0
        report["finding_count"] = 0
        report["findings"] = []
        artifact = build_advisory(SOURCE, report, engine_revision=ENGINE_REVISION)
        self.assertEqual(artifact["review_status"], "NO_DETECTED_FINDINGS_NOT_CLEARED")
        self.assertEqual(artifact["authorization_effect"], "NONE")
        self.assertEqual(artifact["runtime_verified"], False)

    def test_current_lou_pole_intent_report_is_accepted_as_advisory_only(self):
        legacy = build_advisory(SOURCE, sample_report(), engine_revision=ENGINE_REVISION)
        current = build_advisory(SOURCE, intent_report(), engine_revision=ENGINE_REVISION)
        self.assertEqual(current, legacy)  # V1 emitted artifact schema stays frozen.
        self.assertEqual(current["authorization_effect"], "NONE")
        self.assertFalse(current["coverage"]["completeness_verified"])

    def test_intent_report_cannot_promote_completeness_or_change_known_limits(self):
        for mutation in (
            lambda r: r["coverage"]["intent_evaluation"].update(status="evaluated"),
            lambda r: r["coverage"]["intent_evaluation"].update(status=True),
            lambda r: r["coverage"]["intent_evaluation"].update(unsupported_mechanisms=[]),
            lambda r: r["coverage"]["intent_evaluation"].update(unsupported_mechanisms=["other"]),
            lambda r: r["coverage"]["intent_evaluation"].update(notice=""),
            lambda r: r["coverage"]["intent_evaluation"].update(notice="x" * 2049),
            lambda r: r["coverage"]["intent_evaluation"].update(verified=True),
            lambda r: r.update(intent=None),
            lambda r: r["coverage"].update(cleared=True),
        ):
            with self.subTest(mutation=mutation):
                report = intent_report()
                mutation(report)
                with self.assertRaises(InvalidAdvisory):
                    build_advisory(SOURCE, report, engine_revision=ENGINE_REVISION)

    def test_source_bytes_are_bound_and_swapped_input_rejected(self):
        with self.assertRaises(InvalidAdvisory):
            build_advisory(SOURCE + b" ", sample_report(), engine_revision=ENGINE_REVISION)
        with self.assertRaises(InvalidAdvisory):
            build_advisory(SOURCE.replace(b"\n", b"\r\n"), sample_report(), engine_revision=ENGINE_REVISION)

    def test_forged_or_malformed_evidence_and_counts_rejected(self):
        for mutation in (
            lambda r: r["findings"][0]["evidence"][0].update(line_start=500),
            lambda r: r["findings"][0]["evidence"][0].update(text="Invented source"),
            lambda r: r.update(finding_count=100),
            lambda r: r.update(authorization_effect="MESO_SATISFIED"),
            lambda r: r["findings"][0].update(confidence=True),
            lambda r: r["source"].update(verification="attested"),
            lambda r: r["coverage"].update(status="complete"),
            lambda r: r["coverage"].update(status=["heuristic_partial"]),
            lambda r: r.update(profile=["instructions"]),
        ):
            with self.subTest(mutation=mutation):
                report = copy.deepcopy(sample_report())
                mutation(report)
                with self.assertRaises(InvalidAdvisory):
                    build_advisory(SOURCE, report, engine_revision=ENGINE_REVISION)

    def test_revision_is_exactly_40_lowercase_hex_and_unverified(self):
        for revision in ("main", "F" * 40, "a" * 64, "v0.1", "0" * 40 + "--dirty"):
            with self.subTest(revision=revision):
                with self.assertRaises(InvalidAdvisory):
                    build_advisory(SOURCE, sample_report(), engine_revision=revision)

    def test_input_bounded_and_duplicate_keys_rejected(self):
        with self.assertRaises(InvalidAdvisory):
            parse_report(b'{"finding_count":1,"finding_count":0}')
        with self.assertRaises(InvalidAdvisory):
            parse_report(b'{"risk_score":NaN}')
        with self.assertRaises(InvalidAdvisory):
            parse_report(b'[' * 1100 + b'0' + b']' * 1100)
        with self.assertRaises(InvalidAdvisory):
            parse_report(b'x' * 131073)
        with self.assertRaises(InvalidAdvisory):
            build_advisory(b'x' * 65537, sample_report(), engine_revision=ENGINE_REVISION)

    def test_local_file_loader_rejects_symlinks_and_oversized_files(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "source.txt"
            source.write_bytes(SOURCE)
            self.assertEqual(load_bounded(source, 65536), SOURCE)
            link = Path(directory) / "alias.txt"
            link.symlink_to(source)
            with self.assertRaises(InvalidAdvisory):
                load_bounded(link, 65536)
            directory_link = Path(directory) / "linked-parent"
            directory_link.symlink_to(Path(directory), target_is_directory=True)
            with self.assertRaises(InvalidAdvisory):
                load_bounded(directory_link / "source.txt", 65536)
            source.write_bytes(b'x' * 65537)
            with self.assertRaises(InvalidAdvisory):
                load_bounded(source, 65536)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO test needs POSIX mkfifo")
    def test_fifo_input_is_rejected_without_blocking_for_writer(self):
        # Opening a FIFO with O_RDONLY alone blocks before fstat can reject it.
        # A subprocess timeout makes this regression safe even when reintroduced.
        with TemporaryDirectory() as directory:
            fifo = Path(directory) / "source.fifo"
            os.mkfifo(fifo)
            dummy_report = Path(directory) / "report.json"
            dummy_report.write_bytes(b"{}")
            run = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("lou_pole_advisory.py")),
                 str(fifo), str(dummy_report), "--engine-revision", ENGINE_REVISION],
                check=False, capture_output=True, timeout=2,
            )
            self.assertEqual(run.returncode, 2)
            self.assertIn(b"bounded ordinary file", run.stderr)

    def test_serialized_artifact_is_bounded(self):
        artifact = build_advisory(SOURCE, sample_report(), engine_revision=ENGINE_REVISION)
        self.assertLessEqual(len(json.dumps(artifact, ensure_ascii=True).encode()), 65536)

    def test_standalone_cli_reports_advisory_not_authority(self):
        with TemporaryDirectory() as directory:
            source_path = Path(directory) / "policy.txt"
            report_path = Path(directory) / "report.json"
            source_path.write_bytes(SOURCE)
            report_path.write_text(json.dumps(sample_report()), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("lou_pole_advisory.py")),
                 str(source_path), str(report_path), "--engine-revision", ENGINE_REVISION],
                check=False, capture_output=True, timeout=5,
            )
            self.assertEqual(run.returncode, 0, run.stderr.decode())
            artifact = json.loads(run.stdout)
            self.assertEqual(artifact["authorization_effect"], "NONE")
            self.assertFalse(artifact["engine"]["report_execution_verified"])
            self.assertFalse(artifact["runtime_verified"])


if __name__ == "__main__":
    unittest.main()
