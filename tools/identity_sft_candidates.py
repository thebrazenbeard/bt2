"""Validate and export unqualified BT2 role-specific SFT candidate conversations.

This is an offline source transform: it never calls a model or trains weights.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from identity_coding_models import ROOT, load_models, render_prompt, require


CASES_DIR = Path("coding_models/training/cases")
VERSION = "BT2_IDENTITY_SFT_CANDIDATES_V1"
STATUS = "SYNTHETIC_CANDIDATES_UNQUALIFIED"
FIELDS = {"schema_version", "identity_id", "source_entrypoint", "status", "cases"}
CASE_FIELDS = {"id", "split", "task", "ideal_response", "role_skill", "source_basis"}


def validate_cases(root: Path = ROOT) -> dict[str, dict]:
    models = load_models(root)
    directory = root / CASES_DIR
    require(directory.is_dir(), f"missing training-candidate directory: {directory}")
    files = {path.stem for path in directory.glob("*.json")}
    require(files == set(models),
            f"SFT coverage mismatch missing={sorted(set(models)-files)} "
            f"extra={sorted(files-set(models))}")
    seen_tasks: set[str] = set()
    result = {}
    for identity, model in models.items():
        path = directory / f"{identity}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        require(type(data) is dict and set(data) == FIELDS,
                f"{identity}: invalid candidate file fields")
        require(data["schema_version"] == VERSION, f"{identity}: wrong candidate schema")
        require(data["identity_id"] == identity, f"{identity}: wrong identity")
        require(data["source_entrypoint"] == model["source_entrypoint"],
                f"{identity}: candidate/source binding mismatch")
        require(data["status"] == STATUS, f"{identity}: candidate status inflation")
        cases = data["cases"]
        require(type(cases) is list and len(cases) == 6,
                f"{identity}: expected exactly six candidate cases")
        ids = set()
        for index, case in enumerate(cases):
            require(type(case) is dict and set(case) == CASE_FIELDS,
                    f"{identity}: bad case fields at {index}")
            split = "train" if index < 4 else "dev"
            require(case["split"] == split,
                    f"{identity}: split must be four train then two dev")
            identifier = case["id"]
            require(type(identifier) is str and re.fullmatch(r"[a-z0-9_-]+", identifier)
                    and identity in identifier and identifier not in ids,
                    f"{identity}: invalid/duplicate case ID")
            ids.add(identifier)
            for field in ("task", "ideal_response", "role_skill", "source_basis"):
                require(type(case[field]) is str and bool(case[field].strip()),
                        f"{identity}/{identifier}: empty {field}")
            require(len(case["task"].strip()) >= 30 and len(case["ideal_response"].strip()) >= 70,
                    f"{identity}/{identifier}: insufficiently substantive scenario")
            normalized = " ".join(case["task"].casefold().split())
            require(normalized not in seen_tasks,
                    f"{identity}/{identifier}: duplicate task across identities/splits")
            seen_tasks.add(normalized)
            source = case["source_basis"]
            if source.startswith("https://github.com/"):
                require(source.startswith(("https://github.com/thebrazenbeard/masamune/",
                                           "https://github.com/thebrazenbeard/hephaestus/",
                                           "https://github.com/thebrazenbeard/bt2/")),
                        f"{identity}/{identifier}: unknown source repository")
            else:
                source_path = Path(source)
                require(not source_path.is_absolute() and ".." not in source_path.parts
                        and (root / source_path).is_file(),
                        f"{identity}/{identifier}: source_basis path not in BT2")
        result[identity] = data
    return result


def export_conversations(identity: str, split: str, root: Path = ROOT) -> list[dict]:
    models = load_models(root)
    candidates = validate_cases(root)
    require(identity in models, f"unknown identity {identity}")
    require(split in ("train", "dev"), "split must be train or dev")
    system = render_prompt(models[identity], "Read each concrete task below, act within the role, and state evidence limits.")
    return [
        {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": case["task"]},
                {"role": "assistant", "content": case["ideal_response"]},
            ],
            "metadata": {"identity_id": identity, "case_id": case["id"],
                         "split": split, "source_basis": case["source_basis"],
                         "label_status": STATUS},
        }
        for case in candidates[identity]["cases"] if case["split"] == split
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    export = sub.add_parser("export")
    export.add_argument("--identity", required=True)
    export.add_argument("--split", choices=("train", "dev"), required=True)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            print(f"Validated {len(validate_cases())} identity candidate sets (unqualified).")
        else:
            for case in export_conversations(args.identity, args.split):
                print(json.dumps(case, ensure_ascii=False, separators=(",", ":")))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        parser.exit(1, f"SFT candidate validation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
