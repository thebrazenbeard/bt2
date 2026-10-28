"""Fail-closed structure/source checks for unqualified BT2 persona SFT candidates.

This validates case custody and train/dev separation, NOT model behavior or
psychological traits. No model execution or external writes occur here.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

from identity_coding_models import ROOT, load_models, require


SCHEMA = "BT2_PERSONALITY_SFT_V1"
STATUS = "SYNTHETIC_SOURCE_GROUNDED_UNQUALIFIED"
CASE_ROOT = ROOT / "coding_models/personality/cases"


def _safe_source(raw: str) -> None:
    require(isinstance(raw, str) and bool(raw.strip()), "empty source basis")
    relative = Path(raw)
    require(not relative.is_absolute() and ".." not in relative.parts, "unsafe source basis")
    target = ROOT / relative
    require(target.is_file() and target.resolve().is_relative_to(ROOT.resolve()),
            f"source basis not a local BT2 file: {raw}")


def _prompt_key(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def validate_persona_cases() -> dict[str, dict]:
    roles = load_models()
    found = set(path.stem for path in CASE_ROOT.glob("*.json"))
    require(found == set(roles), f"persona roster mismatch: missing={sorted(set(roles)-found)} extra={sorted(found-set(roles))}")
    all_prompts: set[str] = set()
    output: dict[str, dict] = {}
    for identity in sorted(roles):
        path = CASE_ROOT / f"{identity}.json"
        require(path.is_file() and not path.is_symlink(), f"unsafe persona file {identity}")
        doc = json.loads(path.read_text(encoding="utf-8"))
        require(doc.get("schema_version") == SCHEMA and doc.get("identity_id") == identity,
                f"persona schema or identity mismatch: {identity}")
        require(doc.get("status") == STATUS, f"persona evidence ceiling mismatch: {identity}")
        traits = doc.get("traits")
        require(isinstance(traits, list) and 3 <= len(traits) <= 12, f"trait count: {identity}")
        labels = set()
        for trait in traits:
            require(isinstance(trait, dict), "trait must be an object")
            label = trait.get("label")
            require(isinstance(label, str) and 3 <= len(label) <= 120, "invalid trait label")
            require(label.casefold() not in labels, "duplicate trait label")
            labels.add(label.casefold())
            require(trait.get("evidence_kind") in ("SOURCE", "INFERENCE"), "trait must classify evidence")
            _safe_source(trait.get("source_basis"))
            for field in ("observable_behavior", "anti_pattern"):
                require(isinstance(trait.get(field), str) and len(trait[field]) >= 25,
                        f"short/empty trait {field}: {identity}")
        cases = doc.get("cases")
        require(isinstance(cases, list) and len(cases) == 6, f"must have 6 persona cases: {identity}")
        ids = set()
        splits = {"train": [], "dev": []}
        for case in cases:
            require(isinstance(case, dict), "persona case must be an object")
            key = case.get("id")
            require(isinstance(key, str) and key.startswith(identity + "-persona-") and key not in ids,
                    f"invalid/duplicate persona case id: {identity}")
            ids.add(key)
            split = case.get("split")
            require(split in splits, f"invalid persona split: {identity}")
            require(case.get("level") in ("grounded", "adversarial"), "invalid persona level")
            for field, minimum in (("task", 35), ("ideal_response", 80)):
                require(isinstance(case.get(field), str) and len(case[field]) >= minimum,
                        f"short/empty {field}: {key}")
            _safe_source(case.get("source_basis"))
            prompt = _prompt_key(case["task"])
            require(prompt not in all_prompts, f"reused persona prompt: {key}")
            all_prompts.add(prompt)
            splits[split].append(case)
        require(len(splits["train"]) == 4 and len(splits["dev"]) == 2,
                f"train/dev count mismatch: {identity}")
        require({c["level"] for c in splits["train"]} == {"grounded", "adversarial"},
                f"missing training level: {identity}")
        require(sum(c["level"] == "grounded" for c in splits["train"]) == 2,
                f"expected exactly two grounded train cases: {identity}")
        output[identity] = doc
    return output


def main() -> int:
    result = validate_persona_cases()
    print(f"VALID: {len(result)} role dossiers, {sum(len(x['cases']) for x in result.values())} source-bound cases; NO model qualification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
