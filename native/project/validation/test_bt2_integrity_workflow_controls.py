"""Small negative controls for the unconditional read-only PR gate contract."""

import re
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[3] / ".github/workflows/bt2-integrity-gate.yml"


def check_workflow(source: str) -> None:
    if not re.search(r"(?m)^on:\s*\n  pull_request:\s*(?:\n|$)", source):
        raise ValueError("missing unconditional pull_request trigger")
    if re.search(r"(?m)^\s+(?:paths|paths-ignore|branches|branches-ignore):", source):
        raise ValueError("event path/branch filter could skip checks")
    for literal in (
        "permissions:\n  contents: read",
        "  bt2-integrity-gate:\n    name: bt2-integrity-gate",
        "fetch-depth: 0",
        "persist-credentials: false",
        "verify_bt2_v3_history.py",
        "test_bt2_v3_history_controls.py",
        "test_lantern_postgresql_v4_source_binding.py",
        "test_bt2_native_v5_source_binding.py",
        "test_bt2_native_v5_recovery_pointers.py",
    ):
        if literal not in source:
            raise ValueError(f"missing expected gate element: {literal}")
    uses = re.findall(r"(?m)^\s*uses:\s*(\S+)\s*$", source)
    if not uses or any(not re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", action) for action in uses):
        raise ValueError("actions must use immutable commit pins")
    if re.search(r"(?m)^\s+(?:if|continue-on-error):", source):
        raise ValueError("conditional or tolerated gate failure")


class WorkflowControls(unittest.TestCase):
    def test_unconditional_gate_contract(self):
        check_workflow(WORKFLOW.read_text())

    def test_path_filter_mutation_rejected(self):
        changed = WORKFLOW.read_text().replace("  pull_request:\n", "  pull_request:\n    paths: ['src/**']\n")
        with self.assertRaisesRegex(ValueError, "filter"):
            check_workflow(changed)

    def test_action_pin_mutation_rejected(self):
        changed = re.sub(r"actions/checkout@[0-9a-f]{40}", "actions/checkout@v4", WORKFLOW.read_text())
        with self.assertRaisesRegex(ValueError, "immutable"):
            check_workflow(changed)

    def test_missing_core_verifier_rejected(self):
        changed = WORKFLOW.read_text().replace("test_bt2_native_v5_source_binding.py", "no_v5_source_binding.py")
        with self.assertRaisesRegex(ValueError, "missing expected"):
            check_workflow(changed)


if __name__ == "__main__":
    unittest.main()
