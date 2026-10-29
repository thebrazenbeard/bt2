"""Fail closed on mutable CI action references and broad default GITHUB_TOKEN rights.

This is a source-security guard, not evidence of deployed application health.
"""

from pathlib import Path
import re
import subprocess
import sys
import unittest
import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
FULL_SHA_ACTION = re.compile(r"^[^@]+@[0-9a-f]{40}$")


class StrictWorkflowLoader(yaml.SafeLoader):
    """Reject duplicates, YAML merges, anchors, and aliases before policy checks."""

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent) or getattr(self.peek_event(), "anchor", None):
            raise AssertionError("YAML anchors and aliases are forbidden in workflows")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise AssertionError("YAML merge keys are forbidden in workflows")
            key = self.construct_object(key_node, deep=deep)
            try:
                repeated = key in mapping
            except TypeError as exc:
                raise AssertionError("YAML mapping keys must be scalar") from exc
            if repeated:
                raise AssertionError(f"Duplicate YAML mapping key: {key!r}")
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def parse_workflow(source: str) -> dict:
    try:
        workflow = yaml.load(source, Loader=StrictWorkflowLoader)
    except yaml.YAMLError as exc:
        raise AssertionError(f"Invalid workflow YAML: {exc}") from exc
    if not isinstance(workflow, dict):
        raise AssertionError("Workflow must be a YAML mapping")
    return workflow


def workflow_jobs(workflow: dict) -> dict:
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        raise AssertionError("Workflow must contain jobs")
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            raise AssertionError(f"Job {job_id!r} must be a mapping")
    return jobs


def assert_minimum_permissions(source: str) -> None:
    """Require exactly top-level contents:read; forbid all job overrides."""
    workflow = parse_workflow(source)
    if workflow.get("permissions") != {"contents": "read"}:
        raise AssertionError("Workflow permissions must grant only contents: read")
    for job_id, job in workflow_jobs(workflow).items():
        if "permissions" in job:
            raise AssertionError(f"Job {job_id!r} permissions override is forbidden")


def assert_immutable_action_references(source: str) -> None:
    """Inspect all parsed step and reusable-job uses, including flow/explicit keys."""
    for job_id, job in workflow_jobs(parse_workflow(source)).items():
        actions = []
        if "uses" in job:
            actions.append(job["uses"])
        steps = job.get("steps", [])
        if not isinstance(steps, list):
            raise AssertionError(f"Job {job_id!r} steps must be a list")
        for step in steps:
            if not isinstance(step, dict):
                raise AssertionError(f"Job {job_id!r} contains a non-mapping step")
            if "uses" in step:
                actions.append(step["uses"])
        for action in actions:
            if not isinstance(action, str) or (not action.startswith("./") and not FULL_SHA_ACTION.fullmatch(action)):
                raise AssertionError(f"Mutable or invalid action reference in {job_id!r}: {action!r}")


class WorkflowTrustBoundaryTests(unittest.TestCase):
    def test_every_action_uses_immutable_commit(self):
        files = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
        self.assertTrue(files, "No GitHub Actions workflows present")
        for path in files:
            with self.subTest(workflow=path.name):
                assert_immutable_action_references(path.read_text(encoding="utf-8-sig"))

    def test_every_workflow_sets_read_only_token_permissions(self):
        files = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(workflow=path.name):
                source = path.read_text(encoding="utf-8-sig")
                assert_minimum_permissions(source)

    def test_job_level_token_override_is_rejected(self):
        minimal = "permissions:\n  contents: read\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
        assert_minimum_permissions(minimal)
        mutations = (
            "    permissions:\n      contents: write\n",
            "    permissions:\n      issues: write\n",
            "    permissions: write-all\n",
            "    permissions: {}\n",
            "    'permissions': { contents: write }\n",
            '    "permi\\u0073sions": { contents: write }\n',
            '    "permi\\\n      ssions": { contents: write }\n',
        )
        for override in mutations:
            with self.subTest(override=override):
                with self.assertRaises(AssertionError):
                    assert_minimum_permissions(minimal + override)

    def test_duplicate_and_inline_permission_keys_are_rejected(self):
        minimal = "permissions:\n  contents: read\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
        mutations = (
            "permissions:\n  contents: read\n",
            "jobs: { covert: { permissions: write-all } }\n",
            "  covert: { \"permissions\": { actions: write } }\n",
            "  other: &token { permissions: write-all }\n",
            "  other: { <<: *token }\n",
        )
        for override in mutations:
            with self.subTest(override=override):
                with self.assertRaises(AssertionError):
                    assert_minimum_permissions(minimal + override)

    def test_mutable_action_uses_in_flow_and_explicit_yaml_are_rejected(self):
        minimal = "permissions:\n  contents: read\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n"
        assert_immutable_action_references(minimal + "      - uses: ./local-action\n")
        assert_immutable_action_references(minimal + "      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262\n")
        mutations = (
            "      - { uses: actions/checkout@v4 }\n",
            "      - ? uses\n        : actions/checkout@v4\n",
            "      - uses: actions/checkout@v4\n",
            "      - uses: actions/checkout@0\n",
        )
        for step in mutations:
            with self.subTest(step=step):
                with self.assertRaisesRegex(AssertionError, "action"):
                    assert_immutable_action_references(minimal + step)

    def test_duplicate_job_and_alias_are_rejected(self):
        minimal = "permissions:\n  contents: read\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
        mutations = (
            "  build:\n    runs-on: ubuntu-latest\n",
            "  other: &hidden { permissions: write-all }\n",
            "  other: *hidden\n",
        )
        for added in mutations:
            with self.subTest(added=added):
                with self.assertRaises(AssertionError):
                    assert_minimum_permissions(minimal + added)

    def test_optimized_python_cannot_disable_permission_enforcement(self):
        script = (
            "import runpy; "
            f"guard = runpy.run_path({str(Path(__file__).resolve())!r}, run_name='ci_guard'); "
            "guard['assert_minimum_permissions']("
            "'permissions:\\n  contents: read\\n\\njobs:\\n  build:\\n    permissions: write-all\\n')"
        )
        result = subprocess.run([sys.executable, "-O", "-c", script], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Optimized Python stripped the security policy")
        self.assertIn("AssertionError", result.stderr)


if __name__ == "__main__":
    unittest.main()
