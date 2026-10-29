"""Fail closed on mutable CI action references and broad default GITHUB_TOKEN rights.

This is a source-security guard, not evidence of deployed application health.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
USES = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", flags=re.MULTILINE)
FULL_SHA_ACTION = re.compile(r"^[^@]+@[0-9a-f]{40}$")


class WorkflowTrustBoundaryTests(unittest.TestCase):
    def test_every_action_uses_immutable_commit(self):
        files = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
        self.assertTrue(files, "No GitHub Actions workflows present")
        for path in files:
            source = path.read_text(encoding="utf-8-sig")
            for action in USES.findall(source):
                with self.subTest(workflow=path.name, action=action):
                    if action.startswith("./"):
                        continue  # Local action source is bound to this checkout.
                    self.assertRegex(action, FULL_SHA_ACTION)

    def test_every_workflow_sets_read_only_token_permissions(self):
        files = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(workflow=path.name):
                source = path.read_text(encoding="utf-8-sig")
                self.assertRegex(
                    source,
                    r"(?m)^permissions:\n  contents: read\n(?=\n|jobs:)",
                    "Only the minimum top-level contents read permission is permitted",
                )


if __name__ == "__main__":
    unittest.main()
