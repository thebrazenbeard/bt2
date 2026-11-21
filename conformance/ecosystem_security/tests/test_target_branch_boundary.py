"""Keep pull_request_target from executing a writable branch's scanner policy."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[3] / ".github/workflows/ecosystem-security-trusted.yml"

class TargetBranchBoundary(unittest.TestCase):
    def test_only_main_target_triggers_policy(self):
        s = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("  pull_request_target:\n    branches: [main]\n", s,
            "PRs targeting arbitrary branches must not execute base-supplied Python")

    def test_preflight_base_origin_precedes_checkout(self):
        s = WORKFLOW.read_text(encoding="utf-8")
        guard = s.index("      - name: Validate default-branch policy origin")
        checkout = s.index("      - name: Checkout trusted base policy")
        self.assertLess(guard, checkout)
        for token in (
            "BASE_REF: ${{ github.event.pull_request.base.ref }}",
            "BASE_REPO: ${{ github.event.pull_request.base.repo.full_name }}",
            "TARGET_REPO: ${{ github.repository }}",
            'test "$BASE_REF" = "main"',
            'test "$BASE_REPO" = "$TARGET_REPO"',
        ):
            self.assertIn(token, s)

if __name__ == "__main__":
    unittest.main()
