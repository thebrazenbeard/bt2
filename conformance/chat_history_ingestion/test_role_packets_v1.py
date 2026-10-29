"""Pure source validation; no private archive, credentials or model invocation."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name("role_packets_v1.json")
TOPOLOGY = ROOT / "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json"
SHA = re.compile(r"^[0-9a-f]{40}$")


def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


class RolePacketsV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load(MANIFEST)
        cls.topology = load(TOPOLOGY)
        cls.roles = set(cls.topology["active_organizational_topology"]["numbered_specialists"])
        cls.roles.update(cls.topology["active_organizational_topology"]["debugger_reliability_pair"])
        cls.roles.update(cls.topology["active_organizational_topology"]["independent_specialist"])
        cls.roles.add("one")
        assert cls.topology["active_organizational_topology"]["one"] == "PRIMARY_ORCHESTRATOR"

    def test_exact_thirteen_topology(self):
        self.assertEqual(len(self.roles), 13)
        packet_ids = [p["identity"] for p in self.manifest["packets"]]
        self.assertEqual(len(packet_ids), len(set(packet_ids)))
        self.assertEqual(set(packet_ids), self.roles)

    def test_concurrency_and_nonoverlap(self):
        waves = self.manifest["waves"]
        self.assertEqual([w["wave"] for w in waves], [1, 2])
        child_roles = [r for wave in waves for r in wave["child_roles"]]
        self.assertEqual(len(child_roles), 12)
        self.assertEqual(len(child_roles), len(set(child_roles)))
        self.assertEqual(set(child_roles), self.roles - {"one"})
        self.assertTrue(all(len(w["child_roles"]) == 6 for w in waves))
        self.assertTrue(all(w["status"].startswith("PROPOSED") for w in waves))

    def test_every_role_has_falsifiable_work_packet(self):
        for packet in self.manifest["packets"]:
            self.assertGreaterEqual(len(packet["responsibility"]), 35)
            self.assertGreaterEqual(len(packet["deliverable"]), 35)
            self.assertGreaterEqual(len(packet["proof_required"]), 3)
            self.assertTrue(all(isinstance(x, str) and len(x) > 12 for x in packet["proof_required"]))

    def test_exact_commit_source_subjects_and_event(self):
        m = self.manifest
        self.assertEqual(m["event_id"], "chat_history_ingestion_live_coordination")
        self.assertEqual(m["status"], "SOURCE_ONLY_PROPOSED_ASSIGNMENTS_NOT_INSTALLED")
        for key in ("bt2_main", "masamune_main", "hephaestus_main", "stm_pr3_source_candidate"):
            self.assertRegex(m["source_subjects"][key], SHA)
        self.assertRegex(m["source_subjects"]["bt2_identity_profile_candidate"], r"^draft-pr-89@[0-9a-f]{40}$")
        self.assertEqual(m["source_subjects"]["bt2_topology_path"], str(TOPOLOGY.relative_to(ROOT)))

    def test_no_role_prompt_grants_runtime_identity_or_effect(self):
        boundary = self.manifest["execution_boundary"]
        self.assertTrue(boundary["one_role_is_coordinator"])
        self.assertTrue(boundary["role_profiles_source_only"])
        for key in (
            "role_adoption_is_runtime_identity", "git_read_is_runtime_proof",
            "actual_role_activation_proven", "actual_model_identity_proven",
            "merge_or_deploy_automatically_authorized",
        ):
            self.assertIs(boundary[key], False)
        for key in (
            "no_private_data_in_git", "no_historical_source_as_current_autobiography",
            "no_historical_source_as_model_weight_update", "no_retired_currentness_provider",
        ):
            self.assertIs(boundary[key], True)

    def test_open_gates_preserve_critical_separation(self):
        gates = " ".join(self.manifest["open_runtime_gates"]).lower()
        for required in ("recount", "consent", "android v2", "selected vera model", "neural weight"):
            self.assertIn(required, gates)


if __name__ == "__main__":
    unittest.main()
