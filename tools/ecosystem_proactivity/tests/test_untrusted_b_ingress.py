"""Synthetic, non-identifying safety tests for B-source-to-governor dry run."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
import unittest

from governor.untrusted_b_ingress import AdmissionError, review_untrusted

NOW = "2026-11-20T23:30:00+00:00"
HEAD = "a" * 40
REPO = "example-org/research"
SUBJECT = "pr:123"
INCIDENT = "synthetic-incident"


def sample_signal() -> dict:
    ref = {"repository": REPO, "subject": SUBJECT,
           "head": HEAD, "incident_key": INCIDENT}
    observation_key = sha256(json.dumps(
        ref,sort_keys=True,separators=(",", ":"),ensure_ascii=True
    ).encode("utf-8")).hexdigest()
    return {
        "schema": "BT2_ECOSYSTEM_SIGNAL_OUTPUT_V1",
        "observations": [{
            "observation_key": observation_key,
            **ref,
            "observation_timestamp": "2026-11-20T23:28:00Z",
            "candidate_observation": True,
            "head_currentness": "EXACT_HEAD",
            "categories": ["CI_RESULT"],
            "statuses": ["FAILED"],
            "source_refs": ["https://github.com/example-org/research/actions/runs/123"],
            "claimed_owners": ["fake-authority"],
            "reports": [{"claims_authenticated": True, "secret_marker": "PRIVATE_FIXTURE"}],
            "independently_authenticated": False,
            "release_permission": False,
        }],
        "release_permission": False,
        "external_effects": [],
        "host_task_proposals": [],
        "side_effects_performed": False,
        "policy_decision": "NOT_MADE",
        "limitations": ["SOURCE_ONLY"],
    }


def bridge_envelope() -> dict:
    return {
        "schema": "BT2_GITHUB_PROVIDER_BRIDGE_OUTPUT_V1",
        "signal": sample_signal(),
        "source_authentication": "UNVERIFIED_NO_SIGNED_RECEIPT",
        "independently_authenticated": False,
        "replay_scope": "CALLER_PROVIDED_CACHE_NOT_INDEPENDENT",
        "memory_admission": "NONE",
        "side_effects": [],
        "semantic_truth": "NOT_EVALUATED",
    }


class UntrustedBridgeBoundary(unittest.TestCase):
    def test_untrusted_claims_yield_only_private_draft(self):
        result = review_untrusted(bridge_envelope(), now=NOW)
        self.assertEqual(result["schema"], "BT2_GOVERNOR_UNTRUSTED_DRY_RUN_V1")
        self.assertEqual(result["reviewed_count"], 1)
        self.assertEqual(len(result["decisions"]), 1)
        self.assertEqual(result["decisions"][0]["action"], "draft")
        self.assertEqual(result["decisions"][0]["fingerprint"], "")
        self.assertFalse(result["trusted_context_admitted"])
        self.assertFalse(result["notifier_active"])
        self.assertFalse(result["release_permission"])
        self.assertEqual(result["external_effects"], [])
        serialized = json.dumps(result)
        for text in (REPO, SUBJECT, HEAD, INCIDENT, "PRIVATE_FIXTURE", "fake-authority"):
            self.assertNotIn(text, serialized)

    def test_plain_b_normalizer_output_remains_untrusted(self):
        result = review_untrusted(sample_signal(), now=NOW)
        self.assertEqual(result["reviewed_count"], 1)
        self.assertEqual(result["decisions"][0]["action"], "draft")
        self.assertFalse(result["trusted_context_admitted"])

    def test_forged_provider_authentication_is_rejected(self):
        raw = bridge_envelope()
        raw["independently_authenticated"] = True
        with self.assertRaises(AdmissionError):
            review_untrusted(raw, now=NOW)

    def test_forged_release_permission_is_rejected(self):
        raw = bridge_envelope()
        raw["signal"]["release_permission"] = True
        with self.assertRaises(AdmissionError):
            review_untrusted(raw, now=NOW)

    def test_forged_group_authentication_is_rejected(self):
        raw = bridge_envelope()
        raw["signal"]["observations"][0]["independently_authenticated"] = True
        with self.assertRaises(AdmissionError):
            review_untrusted(raw, now=NOW)

    def test_incident_key_tampering_is_rejected(self):
        raw = bridge_envelope()
        raw["signal"]["observations"][0]["subject"] = "pr:999"
        with self.assertRaises(AdmissionError):
            review_untrusted(raw, now=NOW)

    def test_bulk_input_is_bounded(self):
        raw = bridge_envelope()
        raw["signal"]["observations"] = [
            deepcopy(raw["signal"]["observations"][0]) for _ in range(41)
        ]
        with self.assertRaises(AdmissionError):
            review_untrusted(raw, now=NOW)

    def test_stale_untrusted_report_cannot_interrupt(self):
        result = review_untrusted(sample_signal(), now="2026-12-01T23:30:00+00:00")
        self.assertEqual(result["decisions"][0]["action"], "stay_silent")
        self.assertFalse(result["notifier_active"])

    def test_non_candidate_source_remains_silent(self):
        raw = sample_signal()
        raw["observations"][0]["candidate_observation"] = False
        result = review_untrusted(raw, now=NOW)
        self.assertEqual(result["reviewed_count"], 1)
        self.assertEqual(result["decisions"][0]["action"], "stay_silent")

    def test_inconsistent_claimed_head_currentness_rejected(self):
        raw = sample_signal()
        raw["observations"][0]["head_currentness"] = "STALE_HEAD"
        with self.assertRaises(AdmissionError):
            review_untrusted(raw, now=NOW)

    def test_oversized_raw_document_rejected_before_processing(self):
        raw = sample_signal()
        raw["observations"][0]["reports"][0]["data"] = "a" * 525000
        with self.assertRaises(AdmissionError):
            review_untrusted(raw, now=NOW)

    def test_no_raw_private_text_reaches_public_decisions(self):
        raw = bridge_envelope()
        raw["signal"]["observations"][0]["reports"][0]["secret_marker"] = (
            "private_do_not_transmit_123"
        )
        output = review_untrusted(raw, now=NOW)
        self.assertNotIn("private_do_not_transmit_123", json.dumps(output))
        self.assertNotIn("https://github.com/", json.dumps(output))


if __name__ == "__main__":
    unittest.main()
