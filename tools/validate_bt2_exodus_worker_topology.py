import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKERS = ROOT / "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json"
INTERFACES = ROOT / "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json"
COORDINATOR = ROOT / "native/project/BT2_COORDINATOR_RECONSTRUCTION_V1.md"
COMPAT = ROOT / "specs/BT2_COORDINATOR_INTERFACE_V1.json"

EXPECTED_WORKERS = {
    "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "thirteen", "masa", "mune", "hephaestus",
}
EXPECTED_INTERFACES = [
    "Vera",
    "Vera Control Plane Coordinator",
    "BT2 Coordinator",
]

def main():
    workers = json.loads(WORKERS.read_text(encoding="utf-8"))
    interfaces = json.loads(INTERFACES.read_text(encoding="utf-8"))
    compat = json.loads(COMPAT.read_text(encoding="utf-8"))
    coordinator = COORDINATOR.read_text(encoding="utf-8")

    assert workers["persistent_human_interface"] == "BT2 Coordinator"
    assert workers["chat_dependency"] is False
    ids = [w["id"] for w in workers["workers"]]
    assert len(ids) == 13
    assert set(ids) == EXPECTED_WORKERS
    assert len(ids) == len(set(ids))

    for worker in workers["workers"]:
        root = ROOT / worker["source_path"]
        assert root.is_dir(), (worker["id"], root)
        assert (root / worker["entrypoint"]).is_file(), (
            worker["id"], worker["entrypoint"]
        )
        assert worker["source_state"]
        assert worker["qualification_state"]

    seven = next(w for w in workers["workers"] if w["id"] == "seven")
    assert seven["source_path"] == "archive/training-sources/project-achilles/seven/v1.0.0"
    assert seven["compatibility_overlay"] == "docs/exodus/BT2_SEVEN_CHATLESS_RECONSTRUCTION_COMPATIBILITY_20260920.md"
    assert seven["execution_terminal_compatibility"] == "CHATLESS_EPHEMERAL_RUNTIME"
    assert seven["permanent_chat_required"] is False
    assert seven["runtime_instance_mode"] == "EPHEMERAL_EXECUTION_TERMINAL"
    assert seven["qualification_claim_ceiling"] == "PACKAGE_FOUND_QUALIFICATION_UNPROVEN"
    assert seven["current_assignment_resolution"] == "FRESH_DURABLE_STATE_OR_IDLE"
    assert seven["authority_from_role_or_package"] is False
    assert seven["independent_review_exact_subject_binding_required"] is True
    assert seven["peer_review_independence_required_before_first_substantive_judgment"] is True
    seven_overlay = ROOT / seven["compatibility_overlay"]
    assert seven_overlay.is_file()
    assert "archive/training-sources/project-achilles/seven/v1.0.0/" in coordinator

    names = [x["display_name"] for x in interfaces["persistent_chat_interfaces"]]
    assert names == EXPECTED_INTERFACES
    assert len(names) == 3
    assert interfaces["worker_runtime_contract"]["permanent_worker_chat_required"] is False
    assert interfaces["authority_contract"]["protected_effects_require_live_exact_authority"] is True

    assert compat["status"] == "COMPATIBILITY_INTERFACE_ADAPTER"
    assert compat["normative_topology_contract"] == "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json"
    assert compat["normative_worker_reconstruction_contract"] == "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json"

    project = (ROOT / "native/project/PROJECT_INSTRUCTIONS_V3.md").read_text(encoding="utf-8")
    runtime = (ROOT / "native/project/BT2_NATIVE_RUNTIME_V1.md").read_text(encoding="utf-8")
    assert "BT2 Coordinator" in project
    assert "BT2_EXODUS_WORKER_TOPOLOGY_V1.json" in project
    assert "fresh chat" not in runtime.lower()

    print("BT2_EXODUS_RECONCILIATION=PASS workers=13 interfaces=3")

if __name__ == "__main__":
    main()
