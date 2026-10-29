"""Strict semantic controls for the unconditional, read-only BT2 PR gate.

The whole accepted YAML document is allowlisted, including every ordered step
and command. Substring checks are insufficient for workflow security.
"""

import unittest
from pathlib import Path

import yaml


WORKFLOW = Path(__file__).resolve().parents[3] / ".github/workflows/bt2-integrity-gate.yml"
CHECKOUT = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
V3 = (
    "python native/project/validation/verify_bt2_v3_history.py\n"
    "python -m unittest discover -s native/project/validation -p 'test_bt2_v3_history_controls.py' -v\n"
    "python -m unittest discover -s native/project/validation -p 'test_bt2_integrity_workflow_controls.py' -v\n"
)
V4_V5 = (
    "python tools/qualification/test_lantern_postgresql_v4_source_binding.py\n"
    "python native/project/validation/test_bt2_native_v5_source_binding.py\n"
)
EXPECTED = {
    "name": "BT2 Integrity Gate",
    "on": {"pull_request": ""},
    "permissions": {"contents": "read"},
    "jobs": {
        "bt2-integrity-gate": {
            "name": "bt2-integrity-gate",
            "runs-on": "ubuntu-latest",
            "steps": [
                {
                    "name": "Check out proposed merge",
                    "uses": CHECKOUT,
                    "with": {"fetch-depth": "0", "persist-credentials": "false"},
                },
                {
                    "name": "Install pinned YAML parser",
                    "run": "python -m pip install --disable-pip-version-check PyYAML==6.0.3",
                },
                {"name": "Check V3 historical payload and mutation controls", "run": V3},
                {"name": "Check V4 and V5 source bindings", "run": V4_V5},
                {
                    "name": "Check V5 recovery pointers",
                    "run": "python -m unittest discover -s native/project/tests -p 'test_bt2_native_v5_recovery_pointers.py' -v",
                },
            ],
        },
    },
}


class NoDuplicateKeysLoader(yaml.BaseLoader):
    """Load strings literally (`on` is not a YAML 1.1 boolean)."""

    def construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise ValueError("expected mapping")
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError(f"duplicate or invalid YAML key: {key!r}")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def check_workflow(source: str) -> None:
    for event in yaml.parse(source):
        if isinstance(event, yaml.AliasEvent) or getattr(event, "anchor", None):
            raise ValueError("YAML aliases/anchors are not permitted")
        if getattr(event, "tag", None) is not None:
            raise ValueError("explicit YAML tags are not permitted")
    try:
        parsed = yaml.load(source, Loader=NoDuplicateKeysLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"malformed workflow YAML: {exc}") from exc
    if parsed != EXPECTED:
        raise ValueError("workflow AST differs from unconditional read-only allowlist")


class WorkflowControls(unittest.TestCase):
    def setUp(self):
        self.source = WORKFLOW.read_text(encoding="utf-8")

    def rejected(self, altered: str):
        self.assertNotEqual(altered, self.source, "negative-control mutation must change input")
        with self.assertRaises(ValueError):
            check_workflow(altered)

    def test_unconditional_gate_contract(self):
        check_workflow(self.source)

    def test_path_filter_mutation_rejected(self):
        self.rejected(self.source.replace("  pull_request:\n", "  pull_request:\n    paths: ['src/**']\n"))

    def test_unicode_escaped_filter_rejected(self):
        self.rejected(self.source.replace("  pull_request:\n", '  pull_request:\n    "pa\\u0074hs": ["src/**"]\n'))

    def test_duplicate_trigger_rejected(self):
        self.rejected(self.source.replace("on:\n", "on:\n  pull_request: {paths: ['src/**']}\n", 1))

    def test_job_write_all_rejected(self):
        self.rejected(self.source.replace("    runs-on: ubuntu-latest\n", "    permissions: write-all\n    runs-on: ubuntu-latest\n"))

    def test_unicode_escaped_permissions_rejected(self):
        self.rejected(self.source.replace("    runs-on: ubuntu-latest\n", '    "permissio\\u006es": write-all\n    runs-on: ubuntu-latest\n'))

    def test_continue_on_error_rejected(self):
        self.rejected(self.source.replace("    runs-on: ubuntu-latest\n", '    "continue-on-\\u0065rror": true\n    runs-on: ubuntu-latest\n'))

    def test_action_pin_mutation_rejected(self):
        self.rejected(self.source.replace(CHECKOUT, "actions/checkout@v4"))

    def test_missing_core_verifier_rejected(self):
        self.rejected(self.source.replace("test_bt2_native_v5_source_binding.py", "no_v5_source_binding.py"))

    def test_fake_echo_verifier_rejected(self):
        self.rejected(self.source.replace("python native/project/validation/verify_bt2_v3_history.py", "echo python native/project/validation/verify_bt2_v3_history.py"))

    def test_base_checkout_injection_rejected(self):
        injected = "      - name: Discard PR source\n        run: git checkout --detach ${{ github.event.pull_request.base.sha }}\n"
        self.rejected(self.source.replace("      - name: Check V3 historical", injected + "      - name: Check V3 historical"))

    def test_alias_rejected(self):
        self.rejected(self.source.replace("  contents: read", "  contents: &level read\n  issues: *level"))


if __name__ == "__main__":
    unittest.main()
