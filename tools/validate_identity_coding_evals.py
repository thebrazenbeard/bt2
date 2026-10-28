"""Validate source-grounded BT2 coding evaluation *drafts*, not model quality."""

from __future__ import annotations

import json
from pathlib import Path

from identity_coding_models import ROOT, load_models, require


DIR = ROOT / "coding_models/evaluation/cases"
VERSION = "BT2_IDENTITY_CODING_EVAL_V1"
STATUS = "AUTHOR_DRAFT_NOT_BLIND"
CASE_FIELDS = {"case_id", "prompt", "expected_properties", "failure_signals", "rationale"}


def validate_evaluation_file(path: Path, identity: str, repo_root: Path = ROOT) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    require(set(doc) == {"schema_version", "identity_id", "status", "source_refs", "cases"},
            f"{identity}: unexpected evaluation document keys")
    require(doc["schema_version"] == VERSION and doc["identity_id"] == identity,
            f"{identity}: schema or identity mismatch")
    require(doc["status"] == STATUS, f"{identity}: case set must remain author draft")
    refs = doc["source_refs"]
    require(isinstance(refs, list) and refs, f"{identity}: no source refs")
    for ref in refs:
        require(isinstance(ref, str) and ref and "\\" not in ref,
                f"{identity}: source path must be repository-relative")
        relative = Path(ref)
        require(not relative.is_absolute() and ".." not in relative.parts,
                f"{identity}: unsafe source path")
        require((repo_root / relative).is_file(), f"{identity}: source missing: {ref}")
    cases = doc["cases"]
    require(isinstance(cases, list) and len(cases) == 3,
            f"{identity}: expected exactly three author-draft evaluations")
    seen = set()
    for case in cases:
        require(isinstance(case, dict) and set(case) == CASE_FIELDS,
                f"{identity}: missing/extra case fields")
        cid = case["case_id"]
        require(isinstance(cid, str) and cid.startswith(identity + "-eval-") and
                cid not in seen, f"{identity}: duplicate/invalid case ID")
        seen.add(cid)
        require(isinstance(case["prompt"], str) and len(case["prompt"].strip()) >= 80,
                f"{cid}: prompt not specific enough")
        require(isinstance(case["rationale"], str) and
                len(case["rationale"].strip()) >= 25, f"{cid}: rationale missing")
        for field in ("expected_properties", "failure_signals"):
            values = case[field]
            require(isinstance(values, list) and len(values) >= 2 and
                    all(isinstance(v, str) and len(v.strip()) >= 15 for v in values),
                    f"{cid}: {field} needs distinct observable criteria")
    return doc


def validate_all() -> dict[str, dict]:
    profiles = load_models()
    actual = {p.stem for p in DIR.glob("*.json")}
    require(actual == set(profiles),
            f"evaluation file identity mismatch: missing={sorted(set(profiles)-actual)}, "
            f"extra={sorted(actual-set(profiles))}")
    return {identity: validate_evaluation_file(DIR / f"{identity}.json", identity)
            for identity in sorted(profiles)}


if __name__ == "__main__":
    cases = validate_all()
    print(f"Validated {len(cases)} BT2 identity evaluation drafts; "
          f"{sum(len(item['cases']) for item in cases.values())} author-drafted cases; "
          "no blind or model-competence claim")
