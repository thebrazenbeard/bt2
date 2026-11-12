"""Validate and render source-only BT2 coding-agent role configurations.

No network, database, agent invocation, mutation, or authorization is performed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = Path("native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json")
MODELS = Path("coding_models/identities")
SCHEMA_VERSION = "BT2_IDENTITY_CODING_MODEL_V1"
MODEL_KIND = "ROLE_CONDITIONED_CODING_AGENT_CONFIGURATION"
STATUS = "SOURCE_ONLY_NOT_ACTIVATED"
FIELDS = {
    "schema_version", "identity_id", "display_name", "role",
    "source_entrypoint", "model_kind", "objective", "coding_capabilities",
    "execution_protocol", "review_focus", "required_evidence",
    "handoff_outputs", "authority_boundaries", "status",
}
LIST_RANGES = {
    "coding_capabilities": (4, 7),
    "execution_protocol": (5, 8),
    "review_focus": (3, 6),
    "required_evidence": (3, 5),
    "handoff_outputs": (3, 5),
    "authority_boundaries": (4, 7),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(type(value) is dict, f"{path}: expected JSON object")
    return value


def expected_worker_entrypoints(root: Path = ROOT) -> dict[str, str]:
    topology = read_object(root / TOPOLOGY)
    require(topology.get("schema_version") == "BT2_EXODUS_WORKER_TOPOLOGY_V2",
            "unexpected worker topology version")
    workers = topology.get("workers")
    require(type(workers) is list and len(workers) == 13,
            "expected exactly 13 mapped workers")
    expected: dict[str, str] = {}
    for worker in workers:
        require(type(worker) is dict, "worker entry must be an object")
        identity = worker.get("id")
        source_path = worker.get("source_path")
        entrypoint = worker.get("entrypoint")
        require(all(type(value) is str and value.strip()
                    for value in (identity, source_path, entrypoint)),
                "worker identity/source binding incomplete")
        require(identity not in expected, f"duplicate worker identity: {identity}")
        path = Path(source_path) / entrypoint
        require(not path.is_absolute() and ".." not in path.parts,
                f"unsafe source path for {identity}")
        require((root / path).is_file(), f"missing source entrypoint: {path}")
        expected[identity] = path.as_posix()
    return expected


def validate_model(model: dict, identity: str, source: str) -> None:
    require(set(model) == FIELDS,
            f"{identity}: field mismatch missing={sorted(FIELDS - set(model))} "
            f"extra={sorted(set(model) - FIELDS)}")
    require(model["schema_version"] == SCHEMA_VERSION, f"{identity}: schema mismatch")
    require(model["identity_id"] == identity, f"{identity}: identity mismatch")
    require(model["model_kind"] == MODEL_KIND, f"{identity}: model kind mismatch")
    require(model["source_entrypoint"] == source, f"{identity}: source entrypoint drift")
    require(model["status"] == STATUS, f"{identity}: activation/status inflation")
    for field in ("display_name", "role", "objective"):
        require(type(model[field]) is str and bool(model[field].strip()),
                f"{identity}: {field} must be nonempty text")
    for field, (minimum, maximum) in LIST_RANGES.items():
        items = model[field]
        require(type(items) is list and minimum <= len(items) <= maximum,
                f"{identity}: {field} requires {minimum}-{maximum} items")
        require(all(type(item) is str and bool(item.strip()) for item in items),
                f"{identity}: {field} items must be nonempty strings")
        require(len({item.strip().casefold() for item in items}) == len(items),
                f"{identity}: repeated {field} item")


def load_models(root: Path = ROOT) -> dict[str, dict]:
    expected = expected_worker_entrypoints(root)
    directory = root / MODELS
    require(directory.is_dir(), f"missing model directory: {directory}")
    actual = {path.stem for path in directory.glob("*.json")}
    require(actual == set(expected),
            f"model coverage mismatch missing={sorted(set(expected) - actual)} "
            f"extra={sorted(actual - set(expected))}")
    result: dict[str, dict] = {}
    for identity, source in sorted(expected.items()):
        model = read_object(directory / f"{identity}.json")
        validate_model(model, identity, source)
        result[identity] = model
    return result


def render_prompt(model: dict, task: str) -> str:
    require(type(task) is str and bool(task.strip()), "a concrete task is required")

    def section(title: str, values: list[str], ordered: bool = False) -> str:
        lines = [f"{index}. {value}" if ordered else f"- {value}"
                 for index, value in enumerate(values, start=1)]
        return f"## {title}\n" + "\n".join(lines)

    return "\n\n".join([
        f"# BT2 coding configuration: {model['display_name']} ({model['identity_id']})",
        "This is a source-only role-conditioned prompt for a temporary coding execution "
        "context, not proof of durable identity, training, qualification, installation, "
        "activation, current assignment, or authority. Live user direction and actually "
        "installed project instructions override this configuration. Refresh exact "
        "repository and work state before effects.",
        f"Role: {model['role']}\nSource: {model['source_entrypoint']}\n"
        f"Objective: {model['objective']}",
        section("Coding capabilities", model["coding_capabilities"]),
        section("Execution protocol", model["execution_protocol"], ordered=True),
        section("Review focus", model["review_focus"]),
        section("Required evidence", model["required_evidence"]),
        section("Handoff outputs", model["handoff_outputs"]),
        section("Authority boundaries", model["authority_boundaries"]),
        "Do not infer that WoWSQL, Supabase, Lantern, or any replacement currentness "
        "backend is active. Follow current repository provider status, and separate "
        "source, tests, review, installation, runtime, and effects.",
        f"## Current task\n{task.strip()}",
    ]) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="check all thirteen role configurations")
    commands.add_parser("list", help="show identity IDs and coding roles")
    render = commands.add_parser("render", help="print a coding prompt for one identity")
    render.add_argument("--identity", required=True)
    render.add_argument("--task", required=True)
    args = parser.parse_args()

    try:
        models = load_models()
        if args.command == "validate":
            print(f"Validated {len(models)} source-only BT2 identity coding models.")
        elif args.command == "list":
            for identity, model in models.items():
                print(f"{identity}: {model['role']}")
        else:
            require(args.identity in models, f"unknown identity: {args.identity}")
            print(render_prompt(models[args.identity], args.task), end="")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"BT2 coding model validation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
