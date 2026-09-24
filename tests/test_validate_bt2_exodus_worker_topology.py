import copy
import json
import unittest
from pathlib import Path

from tools import validate_bt2_exodus_worker_topology as validator


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class ExodusTopologyValidationTests(unittest.TestCase):
    def test_current_subject_passes(self):
        validator.validate(ROOT)

    def test_worker_package_rebinding_is_rejected(self):
        workers = load_json(
            "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(workers)
        one = next(item for item in mutated["workers"] if item["id"] == "one")
        one["source_path"] = "archive/training-sources/build-team-2.0/two/v1.0.0"
        one["entrypoint"] = "TRAINING_MANIFEST.yaml"
        with self.assertRaisesRegex(ValueError, "one durable source binding drift"):
            validator.validate_worker_topology(mutated, ROOT)

    def test_worker_class_rebinding_is_rejected(self):
        workers = load_json(
            "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(workers)
        one = next(item for item in mutated["workers"] if item["id"] == "one")
        one["class"] = "BT2_NUMBERED_SPECIALIST"
        with self.assertRaisesRegex(ValueError, "one durable source binding drift"):
            validator.validate_worker_topology(mutated, ROOT)

    def test_organizational_topology_drift_is_rejected(self):
        workers = load_json(
            "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(workers)
        mutated["active_organizational_topology"]["numbered_specialists"].remove(
            "thirteen"
        )
        with self.assertRaisesRegex(ValueError, "organizational topology drift"):
            validator.validate_worker_topology(mutated, ROOT)

    def test_interface_cannot_become_durable_state_owner(self):
        interfaces = load_json(
            "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(interfaces)
        mutated["persistent_chat_interfaces"][0]["durable_state_owner"] = True
        with self.assertRaisesRegex(
            ValueError,
            "persistent interfaces must not own durable state",
        ):
            validator.validate_interfaces(mutated)

    def test_chat_title_cannot_become_authority(self):
        interfaces = load_json(
            "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(interfaces)
        mutated["worker_runtime_contract"]["chat_title_is_authority"] = True
        with self.assertRaisesRegex(
            ValueError,
            "worker runtime authority drift: chat_title_is_authority",
        ):
            validator.validate_interfaces(mutated)

    def test_tool_access_cannot_become_authority(self):
        interfaces = load_json(
            "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(interfaces)
        mutated["authority_contract"]["tool_access_does_not_imply_write_authority"] = False
        with self.assertRaisesRegex(
            ValueError,
            "tool access authority boundary drift",
        ):
            validator.validate_interfaces(mutated)

    def test_worker_cannot_add_undeclared_authority_field(self):
        workers = load_json(
            "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(workers)
        one = next(item for item in mutated["workers"] if item["id"] == "one")
        one["merge_authority"] = True
        with self.assertRaisesRegex(ValueError, "one worker field set drift"):
            validator.validate_worker_topology(mutated, ROOT)

    def test_authority_contract_rejects_unknown_authority_field(self):
        interfaces = load_json(
            "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(interfaces)
        mutated["authority_contract"]["interface_role_grants_merge_authority"] = True
        with self.assertRaisesRegex(ValueError, "authority field set drift"):
            validator.validate_interfaces(mutated)

    def test_worker_reconstruction_sources_are_exactly_bound(self):
        interfaces = load_json(
            "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json"
        )
        mutated = copy.deepcopy(interfaces)
        mutated["worker_runtime_contract"]["worker_reconstruction_sources"] = [
            "arbitrary-1",
            "arbitrary-2",
            "arbitrary-3",
            "arbitrary-4",
            "arbitrary-5",
        ]
        with self.assertRaisesRegex(ValueError, "worker reconstruction sources drift"):
            validator.validate_interfaces(mutated)

    def test_compat_authority_rejects_undeclared_merge_authority(self):
        compat = load_json("specs/BT2_COORDINATOR_INTERFACE_V1.json")
        mutated = copy.deepcopy(compat)
        mutated["authority"]["merge_authority"] = True
        with self.assertRaisesRegex(ValueError, "compat authority field set drift"):
            validator.validate_compat(mutated)

    def test_compat_adapter_cannot_grant_protected_effect_authority(self):
        compat = load_json("specs/BT2_COORDINATOR_INTERFACE_V1.json")
        mutated = copy.deepcopy(compat)
        mutated["authority"][
            "interface_role_does_not_grant_merge_deploy_or_provider_authority"
        ] = False
        with self.assertRaisesRegex(ValueError, "compat authority ceiling drift"):
            validator.validate_compat(mutated)


if __name__ == "__main__":
    unittest.main()
