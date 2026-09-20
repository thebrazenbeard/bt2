import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKERS_REL = Path("native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json")
INTERFACES_REL = Path("native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json")
COORDINATOR_REL = Path("native/project/BT2_COORDINATOR_RECONSTRUCTION_V1.md")
COMPAT_REL = Path("specs/BT2_COORDINATOR_INTERFACE_V1.json")

EXPECTED_ORGANIZATIONAL_TOPOLOGY = {
    "one": "PRIMARY_ORCHESTRATOR",
    "numbered_specialists": [
        "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "thirteen",
    ],
    "debugger_reliability_pair": ["masa", "mune"],
    "independent_specialist": ["hephaestus"],
}
EXPECTED_WORKER_BINDINGS = {
    "one": (
        "BT2_PRIMARY_ORCHESTRATOR",
        "archive/training-sources/build-team-2.0/one/v1.0.0",
        "BOOTSTRAP_LOADER.md",
        "PACKAGE_SOURCE_BOUND",
        "QUALIFICATION_IMPORT_PENDING",
    ),
    "two": (
        "BT2_NUMBERED_SPECIALIST_SYSTEMS_ARCHITECT",
        "archive/training-sources/build-team-2.0/two/v1.0.0",
        "TRAINING_MANIFEST.yaml",
        "PACKAGE_FOUND",
        "QUALIFICATION_UNPROVEN",
    ),
    "three": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/build-team-2.0/three/v1.0.0",
        "BOOTSTRAP.md",
        "PACKAGE_FOUND",
        "QUALIFICATION_UNPROVEN",
    ),
    "four": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/build-team-2.0/four/v1.0.1",
        "BOOTSTRAP.md",
        "PACKAGE_SOURCE_BOUND",
        "QUALIFICATION_IMPORT_PENDING",
    ),
    "five": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/build-team-2.0/five/v1.0.0",
        "ROLE_CHARTER.md",
        "PACKAGE_SOURCE_BOUND",
        "QUALIFICATION_IMPORT_PENDING",
    ),
    "six": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/build-team-2.0/six/v1.0.0",
        "BOOTSTRAP.md",
        "PACKAGE_SOURCE_BOUND",
        "QUALIFICATION_IMPORT_PENDING",
    ),
    "seven": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/project-achilles/seven/v1.0.0",
        "BOOTSTRAP.md",
        "PACKAGE_FOUND",
        "QUALIFICATION_UNPROVEN",
    ),
    "eight": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/build-team-2.0/eight/v1.0.0",
        "BOOTSTRAP_LOADER.md",
        "PACKAGE_FOUND",
        "QUALIFICATION_UNPROVEN",
    ),
    "nine": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/build-team-2.0/nine/v1.0.0",
        "ROLE_CONTRACT.md",
        "PACKAGE_SOURCE_BOUND",
        "QUALIFICATION_IMPORT_PENDING",
    ),
    "thirteen": (
        "BT2_NUMBERED_SPECIALIST",
        "archive/training-sources/build-team-2.0/thirteen/corrections/v1.0.0",
        "BOOTSTRAP.md",
        "PACKAGE_SOURCE_BOUND",
        "QUALIFICATION_IMPORT_PENDING",
    ),
    "masa": (
        "DEBUGGER_RELIABILITY_PAIR_MEMBER",
        "archive/training-sources/build-team-2.0/masa/v1.0.0",
        "OPERATIONAL_REORIENTATION.md",
        "PACKAGE_FOUND",
        "QUALIFICATION_UNPROVEN",
    ),
    "mune": (
        "DEBUGGER_RELIABILITY_PAIR_MEMBER",
        "archive/training-sources/build-team-2.0/mune/v1.0.1",
        "BOOTSTRAP.md",
        "PACKAGE_FOUND_RECOMMENDED_VERSION",
        "QUALIFICATION_UNPROVEN",
    ),
    "hephaestus": (
        "INDEPENDENT_IMPLEMENTATION_REPAIR_SPECIALIST",
        "archive/training-sources/build-team-2.0/hephaestus/v1.0.0",
        "ROLE_CONTRACT.md",
        "QUALIFICATION_EVIDENCE_FOUND",
        "CANONICAL_QUALIFICATION_IMPORT_HELD",
    ),
}
EXPECTED_INTERFACES = [
    ("VERA", "Vera"),
    ("VERA_CONTROL_PLANE_COORDINATOR", "Vera Control Plane Coordinator"),
    ("BT2_COORDINATOR", "BT2 Coordinator"),
]
EXPECTED_PROTECTED_EFFECTS = {
    "MERGE",
    "DEPLOYMENT",
    "PROVIDER_MUTATION",
    "CREDENTIAL_OR_PERMISSION_CHANGE",
    "PRODUCTION_MACHINE_WRITE_OR_CONNECTION",
    "MODEL_TRAINING_OR_WEIGHT_CHANGE",
    "CANONICAL_PROMOTION",
    "DESTRUCTIVE_CLEANUP",
}

EXPECTED_WORKER_BASE_KEYS = {
    "id", "class", "source_path", "entrypoint", "source_state", "qualification_state",
}
EXPECTED_SEVEN_EXTRA_KEYS = {
    "compatibility_overlay",
    "execution_terminal_compatibility",
    "permanent_chat_required",
    "runtime_instance_mode",
    "qualification_claim_ceiling",
    "current_assignment_resolution",
    "authority_from_role_or_package",
    "independent_review_exact_subject_binding_required",
    "peer_review_independence_required_before_first_substantive_judgment",
}
EXPECTED_INTERFACE_ENTRY_KEYS = {
    "interface_id", "display_name", "domain", "durable_state_owner",
}
EXPECTED_RUNTIME_KEYS = {
    "permanent_worker_chat_required",
    "execution_context_is_terminal_not_identity",
    "worker_reconstruction_sources",
    "chat_title_is_authority",
    "conversation_id_is_authority",
    "archived_chat_required_for_reconstruction",
    "hidden_chat_state_required_for_reconstruction",
}
EXPECTED_RECONSTRUCTION_SOURCES = [
    "current live user instruction and Project Instructions",
    "thebrazenbeard/bt2 current canonical source",
    "target repository exact current source/PR/review state",
    "thebrazenbeard/chat-communication-bus current protocol, worker lane, and recovery checkpoint",
    "authorized live provider readback when the task depends on provider currentness",
]
EXPECTED_COMMUNICATION_KEYS = {
    "non_pr_coordination_hub",
    "external_prs_mirrored_to_bus_when_material",
    "recovery_checkpoint_namespace",
    "source_prs_remain_canonical_in_source_repository",
}
EXPECTED_AUTHORITY_KEYS = {
    "worker_identity_does_not_imply_write_authority",
    "tool_access_does_not_imply_write_authority",
    "protected_effects_require_live_exact_authority",
    "protected_effect_examples",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _read_json(root: Path, rel: Path) -> dict:
    value = json.loads((root / rel).read_text(encoding="utf-8"))
    _require(type(value) is dict, f"{rel} must contain one JSON object")
    return value


def validate_worker_topology(workers: dict, root: Path = ROOT) -> None:
    _require(
        workers.get("schema_version") == "BT2_EXODUS_WORKER_TOPOLOGY_V1",
        "worker topology schema mismatch",
    )
    _require(workers.get("source_repo") == "thebrazenbeard/bt2", "source repo drift")
    _require(
        workers.get("persistent_human_interface") == "BT2 Coordinator",
        "persistent human interface drift",
    )
    _require(workers.get("chat_dependency") is False, "chat dependency must remain false")
    _require(
        workers.get("active_organizational_topology") == EXPECTED_ORGANIZATIONAL_TOPOLOGY,
        "organizational topology drift",
    )

    entries = workers.get("workers")
    _require(type(entries) is list and len(entries) == 13, "expected exactly 13 workers")
    ids = [entry.get("id") for entry in entries if type(entry) is dict]
    _require(len(ids) == 13, "every worker entry must be an object with an id")
    _require(len(ids) == len(set(ids)), "worker ids must be unique")
    _require(set(ids) == set(EXPECTED_WORKER_BINDINGS), "worker id set drift")

    for worker in entries:
        worker_id = worker["id"]
        expected_keys = (
            EXPECTED_WORKER_BASE_KEYS | EXPECTED_SEVEN_EXTRA_KEYS
            if worker_id == "seven"
            else EXPECTED_WORKER_BASE_KEYS
        )
        _require(
            set(worker) == expected_keys,
            f"{worker_id} worker field set drift",
        )
        expected = EXPECTED_WORKER_BINDINGS[worker_id]
        actual = (
            worker.get("class"),
            worker.get("source_path"),
            worker.get("entrypoint"),
            worker.get("source_state"),
            worker.get("qualification_state"),
        )
        _require(actual == expected, f"{worker_id} durable source binding drift")
        package_root = root / worker["source_path"]
        _require(package_root.is_dir(), f"{worker_id} source package missing")
        _require(
            (package_root / worker["entrypoint"]).is_file(),
            f"{worker_id} source entrypoint missing",
        )

    seven = next(worker for worker in entries if worker["id"] == "seven")
    expected_seven = {
        "compatibility_overlay":
            "docs/exodus/BT2_SEVEN_CHATLESS_RECONSTRUCTION_COMPATIBILITY_20260920.md",
        "execution_terminal_compatibility": "CHATLESS_EPHEMERAL_RUNTIME",
        "permanent_chat_required": False,
        "runtime_instance_mode": "EPHEMERAL_EXECUTION_TERMINAL",
        "qualification_claim_ceiling": "PACKAGE_FOUND_QUALIFICATION_UNPROVEN",
        "current_assignment_resolution": "FRESH_DURABLE_STATE_OR_IDLE",
        "authority_from_role_or_package": False,
        "independent_review_exact_subject_binding_required": True,
        "peer_review_independence_required_before_first_substantive_judgment": True,
    }
    for key, expected in expected_seven.items():
        _require(seven.get(key) == expected, f"seven {key} drift")
    _require(
        (root / seven["compatibility_overlay"]).is_file(),
        "seven compatibility overlay missing",
    )


def validate_interfaces(interfaces: dict) -> None:
    _require(
        interfaces.get("schema_version") == "BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1",
        "interface topology schema mismatch",
    )
    entries = interfaces.get("persistent_chat_interfaces")
    _require(type(entries) is list and len(entries) == 3, "expected exactly 3 interfaces")
    _require(
        all(type(entry) is dict and set(entry) == EXPECTED_INTERFACE_ENTRY_KEYS for entry in entries),
        "persistent interface field set drift",
    )
    pairs = [(entry.get("interface_id"), entry.get("display_name")) for entry in entries]
    _require(pairs == EXPECTED_INTERFACES, "persistent interface identity/order drift")
    _require(
        all(entry.get("durable_state_owner") is False for entry in entries),
        "persistent interfaces must not own durable state",
    )

    runtime = interfaces.get("worker_runtime_contract")
    _require(type(runtime) is dict, "worker runtime contract missing")
    _require(set(runtime) == EXPECTED_RUNTIME_KEYS, "worker runtime field set drift")
    for field in (
        "permanent_worker_chat_required",
        "chat_title_is_authority",
        "conversation_id_is_authority",
        "archived_chat_required_for_reconstruction",
        "hidden_chat_state_required_for_reconstruction",
    ):
        _require(runtime.get(field) is False, f"worker runtime authority drift: {field}")
    _require(
        runtime.get("execution_context_is_terminal_not_identity") is True,
        "execution context identity boundary drift",
    )
    sources = runtime.get("worker_reconstruction_sources")
    _require(
        sources == EXPECTED_RECONSTRUCTION_SOURCES,
        "worker reconstruction sources drift",
    )

    communication = interfaces.get("communication_contract")
    _require(type(communication) is dict, "communication contract missing")
    _require(set(communication) == EXPECTED_COMMUNICATION_KEYS, "communication field set drift")
    _require(
        communication.get("non_pr_coordination_hub")
        == "thebrazenbeard/chat-communication-bus",
        "coordination hub drift",
    )
    _require(
        communication.get("external_prs_mirrored_to_bus_when_material") is True,
        "external PR mirroring contract drift",
    )
    _require(
        communication.get("recovery_checkpoint_namespace") == "checkpoints/<identity>/",
        "recovery checkpoint namespace drift",
    )
    _require(
        communication.get("source_prs_remain_canonical_in_source_repository") is True,
        "source PR canonicality drift",
    )

    authority = interfaces.get("authority_contract")
    _require(type(authority) is dict, "authority contract missing")
    _require(set(authority) == EXPECTED_AUTHORITY_KEYS, "authority field set drift")
    _require(
        authority.get("worker_identity_does_not_imply_write_authority") is True,
        "worker identity authority boundary drift",
    )
    _require(
        authority.get("tool_access_does_not_imply_write_authority") is True,
        "tool access authority boundary drift",
    )
    _require(
        authority.get("protected_effects_require_live_exact_authority") is True,
        "protected-effect authority boundary drift",
    )
    _require(
        set(authority.get("protected_effect_examples", [])) == EXPECTED_PROTECTED_EFFECTS,
        "protected-effect vocabulary drift",
    )


def validate_compat(compat: dict) -> None:
    _require(compat.get("status") == "COMPATIBILITY_INTERFACE_ADAPTER", "compat status drift")
    _require(compat.get("project") == "Build Team Two", "compat project drift")
    _require(compat.get("persistent_chat_name") == "BT2 Coordinator", "compat interface drift")
    _require(compat.get("interface_not_worker_identity") is True, "compat identity boundary drift")
    _require(
        compat.get("normative_topology_contract")
        == "native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json",
        "compat topology binding drift",
    )
    _require(
        compat.get("normative_worker_reconstruction_contract")
        == "native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json",
        "compat worker binding drift",
    )
    worker_model = compat.get("worker_model", {})
    for field in (
        "permanent_worker_chats_required",
        "retired_chat_url_dependency_forbidden",
    ):
        expected = field == "retired_chat_url_dependency_forbidden"
        _require(worker_model.get(field) is expected, f"compat worker-model drift: {field}")
    _require(
        worker_model.get("workers_are_reconstructed_from_durable_state") is True,
        "compat reconstruction boundary drift",
    )
    _require(
        worker_model.get("ephemeral_execution_terminals_allowed") is True,
        "compat ephemeral execution drift",
    )
    authority = compat.get("authority", {})
    _require(
        authority.get("interface_role_does_not_grant_merge_deploy_or_provider_authority")
        is True,
        "compat authority ceiling drift",
    )
    _require(
        authority.get("patrick_exact_authority_required_for_protected_effects") is True,
        "compat protected-effect authority drift",
    )
    persistence = compat.get("persistence", {})
    _require(
        persistence.get("project_outputs_canonical_in_owning_repositories") is True,
        "compat project-output canonicality drift",
    )
    _require(persistence.get("non_pr_coordination_via_bus") is True, "compat Bus routing drift")
    _require(
        persistence.get("continuation_must_not_depend_on_chat_history") is True,
        "compat chat-dependency drift",
    )


def validate(root: Path = ROOT) -> None:
    workers = _read_json(root, WORKERS_REL)
    interfaces = _read_json(root, INTERFACES_REL)
    compat = _read_json(root, COMPAT_REL)
    coordinator = (root / COORDINATOR_REL).read_text(encoding="utf-8")

    validate_worker_topology(workers, root)
    validate_interfaces(interfaces)
    validate_compat(compat)

    _require(
        "archive/training-sources/project-achilles/seven/v1.0.0/" in coordinator,
        "coordinator Seven source binding missing",
    )
    project = (root / "native/project/PROJECT_INSTRUCTIONS_V3.md").read_text(
        encoding="utf-8"
    )
    runtime = (root / "native/project/BT2_NATIVE_RUNTIME_V1.md").read_text(
        encoding="utf-8"
    )
    _require("BT2 Coordinator" in project, "Project Instructions coordinator marker missing")
    _require(
        "BT2_EXODUS_WORKER_TOPOLOGY_V1.json" in project,
        "Project Instructions worker-map marker missing",
    )
    _require("fresh chat" not in runtime.lower(), "native runtime retains fresh-chat dependency")


def main() -> None:
    validate(ROOT)
    print("BT2_EXODUS_RECONCILIATION=PASS workers=13 interfaces=3")


if __name__ == "__main__":
    main()
