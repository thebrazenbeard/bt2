"""Trusted-base scan contract: PR source never supplies the executable policy."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "ecosystem-security-trusted.yml"


class TrustedBaseGateContract(unittest.TestCase):
    def source(self):
        self.assertTrue(WORKFLOW.is_file(), "missing default-branch trusted-base workflow")
        return WORKFLOW.read_text(encoding="utf-8")

    def test_target_event_without_path_skip(self):
        s = self.source()
        self.assertRegex(s, r"(?m)^on:\s*$")
        self.assertRegex(s, r"(?m)^  pull_request_target:\s*$")
        self.assertNotRegex(s, r"(?m)^\s+(?:paths|paths-ignore):")
        self.assertIn("synchronize", s)

    def test_caller_cannot_supply_executable_scanner(self):
        s = self.source()
        self.assertIn("path: .trusted", s)
        self.assertIn("path: .candidate", s)
        self.assertIn("python3 .trusted/conformance/ecosystem_security/scanner.py", s)
        self.assertNotIn("python3 .candidate/", s)
        self.assertNotIn("bash .candidate/", s)
        self.assertNotIn("source .candidate/", s)
        self.assertNotIn("pip install", s)
        self.assertNotIn("npm ", s)

    def test_candidate_exact_commit_and_clean_source_checked(self):
        s = self.source()
        self.assertIn("github.event.pull_request.base.sha", s)
        self.assertIn("github.event.pull_request.head.sha", s)
        self.assertIn("github.event.pull_request.head.repo.full_name", s)
        for flag in ("--require-git-head", "--require-clean-source", "--fail-on-high"):
            self.assertIn(flag, s)
        self.assertIn('test "$(git -C .candidate rev-parse HEAD)" = "$HEAD_SHA"', s)

    def test_mutated_trusted_policy_requires_separate_release(self):
        s = self.source()
        # Do not allow a PR to remove/change the trusted workflow,
        # executable policy, or tests and then bless its own modifications.
        self.assertIn("Protect trusted executable policy from PR replacement", s)
        self.assertIn('git -C .trusted rev-parse "HEAD:$path"', s)
        self.assertIn('git -C .candidate rev-parse "HEAD:$path"', s)
        self.assertIn('exit 2', s)
        self.assertIn(".github/workflows", s)
        self.assertIn("conformance/ecosystem_security", s)

    def test_runner_has_readonly_token_and_no_secrets(self):
        s = self.source()
        self.assertRegex(s, r"(?m)^permissions:\s*\n  contents: read\s*$")
        self.assertNotIn("secrets.", s)
        self.assertNotIn("id-token:", s)
        self.assertNotIn("contents: write", s)
        self.assertNotIn("pull-requests: write", s)
        self.assertIn("persist-credentials: false", s)
        self.assertIn("submodules: false", s)
        self.assertIn("lfs: false", s)


if __name__ == "__main__":
    unittest.main()
