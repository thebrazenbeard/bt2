"""Adversarial static checks for the bounded V5 recovery routing package."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from native.project.validation.test_bt2_native_v5_source_binding import verify_recovery_pointers


ROOT = Path(__file__).resolve().parents[3]


class V5RecoveryPointersTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instructions = (ROOT / "native/project/PROJECT_INSTRUCTIONS_V5.md").read_text()
        self.reconstruction = (ROOT / "native/project/BT2_COORDINATOR_RECONSTRUCTION_V2.md").read_text()
        self.topology = json.loads((ROOT / "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json").read_text())

    def test_current_package_routes_to_v2_and_v4_runtime(self):
        verify_recovery_pointers(self.instructions, self.reconstruction, self.topology)

    def test_stale_coordinator_pointer_cannot_pass(self):
        stale = self.reconstruction.replace("BT2_RECOVERY_AND_STATE_V2.md", "BT2_RECOVERY_AND_STATE_V1.md")
        with self.assertRaisesRegex(ValueError, "contradictory historical entrypoint"):
            verify_recovery_pointers(self.instructions, stale, self.topology)

    def test_appended_legacy_coordinator_instruction_cannot_hide_behind_v2(self):
        malicious = self.reconstruction + "\nUse native/project/BT2_RECOVERY_AND_STATE_V1.md.\n"
        with self.assertRaisesRegex(ValueError, "contradictory historical entrypoint"):
            verify_recovery_pointers(self.instructions, malicious, self.topology)

    def test_appended_v3_project_instruction_cannot_hide_behind_v5(self):
        malicious = self.instructions + "\nUse PROJECT_INSTRUCTIONS_V3.md for worker recovery.\n"
        with self.assertRaisesRegex(ValueError, "contradictory historical entrypoint"):
            verify_recovery_pointers(malicious, self.reconstruction, self.topology)

    def test_bare_casefold_v3_worker_instruction_cannot_hide_behind_v5(self):
        malicious = json.loads(json.dumps(self.topology))
        malicious["common_recovery"][0] += (
            " ALSO read current pRoJeCt_InStRuCtIoNs_V3 for active instructions."
        )
        with self.assertRaisesRegex(ValueError, "active stale pointer"):
            verify_recovery_pointers(self.instructions, self.reconstruction, malicious)

    def test_bare_lowercase_v1_coordinator_pointer_fails(self):
        malicious = self.reconstruction + "\nUse bt2_recovery_and_state_v1 for recovery.\n"
        with self.assertRaisesRegex(ValueError, "contradictory historical entrypoint"):
            verify_recovery_pointers(self.instructions, malicious, self.topology)

    def test_stale_worker_instructions_cannot_pass(self):
        bad = json.loads(json.dumps(self.topology))
        bad["common_recovery"][0] = "Read current PROJECT_INSTRUCTIONS_V3 and this map."
        with self.assertRaisesRegex(ValueError, "stale Project Instructions"):
            verify_recovery_pointers(self.instructions, self.reconstruction, bad)

    def test_stale_project_binding_cannot_pass(self):
        bad = self.instructions.replace("BT2_EXODUS_WORKER_TOPOLOGY_V2.json",
                                        "BT2_EXODUS_WORKER_TOPOLOGY_V1.json")
        with self.assertRaisesRegex(ValueError, "contradictory historical entrypoint"):
            verify_recovery_pointers(bad, self.reconstruction, self.topology)

    def test_chat_continuity_is_never_a_recovery_dependency(self):
        bad = json.loads(json.dumps(self.topology))
        bad["chat_dependency"] = True
        with self.assertRaisesRegex(ValueError, "chat continuity"):
            verify_recovery_pointers(self.instructions, self.reconstruction, bad)

    def test_v2_keeps_worker_roles_and_authority_from_v1(self):
        frozen = json.loads((ROOT / "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json").read_text())
        self.assertEqual(self.topology["workers"], frozen["workers"])
        self.assertEqual(self.topology["active_organizational_topology"],
                         frozen["active_organizational_topology"])
        self.assertEqual(self.topology["authority_rule"], frozen["authority_rule"])
        self.assertEqual(self.topology["execution_terminal_rule"], frozen["execution_terminal_rule"])


if __name__ == "__main__":
    unittest.main()
