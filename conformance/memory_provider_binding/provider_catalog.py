"""Offline, read-only Vera memory provider metadata conformance.

The input snapshot is always untrusted even if it originated from a connected
provider: JSON serialization is not an independently rooted provider receipt.
No credentials, SQL, network, host actions or private record contents.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

INPUT_SCHEMA = "BT2_MEMORY_PROVIDER_CATALOG_INPUT_V1"
OUTPUT_SCHEMA = "BT2_MEMORY_PROVIDER_CATALOG_OUTPUT_V1"

REQUIRED_RELATIONS = frozenset({
    ("public", "vera_memory_epoch_subjects_v1", "r"),
    ("public", "vera_memory_epoch_events_v1", "r"),
    ("public", "vera_memory_epoch_provider_receipts_v1", "r"),
    ("public", "vera_memory_epoch_archive_receipts_v1", "r"),
    ("semantic_atlas", "runtime_objects", "r"),
    ("semantic_atlas", "runtime_snapshots", "r"),
    ("semantic_atlas", "capture_policy", "r"),
})
REQUIRED_ROUTINES = frozenset({
    ("public", "vera_memory_epoch_get_status_v1"),
    ("semantic_atlas", "search_current_runtime_objects_v11"),
})
RECORD_NAME = re.compile(r"^[a-z][a-z0-9_]{0,96}$")
UTC_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class CatalogError(ValueError):
    """Invalid untrusted catalog envelope."""


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      allow_nan=False, separators=(",", ":"))


def strict_json(data: str) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        out: dict[str, object] = {}
        for key, value in pairs:
            if key in out:
                raise CatalogError("duplicate JSON key")
            out[key] = value
        return out

    def nonfinite(_: str) -> None:
        raise CatalogError("nonfinite JSON disallowed")

    try:
        result = json.loads(data, object_pairs_hook=unique,
                            parse_constant=nonfinite)
    except json.JSONDecodeError as exc:
        raise CatalogError("invalid JSON") from exc
    if type(result) is not dict:
        raise CatalogError("catalog input must be object")
    return result


def _name(value: object) -> str:
    if type(value) is not str or RECORD_NAME.fullmatch(value) is None:
        raise CatalogError("invalid catalog identifier")
    return value


def _require(item: dict, key: str, kind: type) -> Any:
    v = item.get(key)
    if type(v) is not kind:
        raise CatalogError("invalid catalog field " + key)
    return v


def _inventory(items: object, keys: tuple[str, ...], *,
               max_items: int, with_rls: bool = False) -> dict[tuple[str, ...], bool]:
    if type(items) is not list or len(items) > max_items:
        raise CatalogError("inventory size/type invalid")
    found: dict[tuple[str, ...], bool] = {}
    for item in items:
        if type(item) is not dict or set(item) != set(keys) | ({"rls_enabled"} if with_rls else set()):
            raise CatalogError("catalog inventory fields invalid")
        name = tuple(_name(item[k]) for k in keys)
        if name in found:
            raise CatalogError("duplicate catalog object identity")
        has_rls = _require(item, "rls_enabled", bool) if with_rls else False
        found[name] = has_rls
    return found


def evaluate_catalog(payload: dict[str, Any]) -> dict[str, Any]:
    if type(payload) is not dict or payload.get("schema") != INPUT_SCHEMA:
        raise CatalogError("unsupported input schema")
    role = _require(payload, "provider_role", str)
    if role not in ("VERA_MEMORY", "TATTLER_REVIEW"):
        raise CatalogError("unsupported provider role")
    observed = _require(payload, "observation_time", str)
    if UTC_TIME.fullmatch(observed) is None:
        raise CatalogError("uncanonical observation time")
    try:
        datetime.fromisoformat(observed.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CatalogError("invalid observation calendar time") from exc
    # The following field has no power to authenticate a source. Output only
    # its fingerprint to avoid disclosing private provider locators.
    source_ref = _require(payload, "source_ref", str)
    if not source_ref or len(source_ref.encode("utf-8")) > 512:
        raise CatalogError("invalid provenance reference")
    if set(payload) - {"schema","provider_role","observation_time","source_ref",
                       "relations","routines","independently_authenticated"}:
        raise CatalogError("unexpected payload fields (private rows not accepted)")
    if "independently_authenticated" in payload and type(payload["independently_authenticated"]) is not bool:
        raise CatalogError("authentication claim must be boolean")
    relations = _inventory(payload.get("relations"), ("schema","name","kind"),
                           max_items=256,with_rls=True)
    routines = _inventory(payload.get("routines"), ("schema","name"),max_items=128)
    memory_objects = set(relations).intersection(REQUIRED_RELATIONS)
    if role == "TATTLER_REVIEW":
        verdict = ("CROSS_PROJECT_SCOPE_CONFLICT" if memory_objects else
                   "NOT_APPLICABLE_REVIEW_PROVIDER")
        missing = []
        no_rls = []
    else:
        missing = sorted(".".join(v) for v in REQUIRED_RELATIONS if v not in relations)
        missing += sorted(".".join(v) for v in REQUIRED_ROUTINES if v not in routines)
        no_rls = sorted(".".join(v) for v in REQUIRED_RELATIONS
                        if v in relations and not relations[v])
        verdict = "MISSING_REQUIREMENTS" if missing or no_rls else "CATALOG_PRESENT_UNQUALIFIED"
    return {
        "schema": OUTPUT_SCHEMA,
        "provider_role": role,
        "observation_time": observed,
        "source_ref_sha256": sha256(source_ref.encode("utf-8")).hexdigest(),
        "verdict": verdict,
        "missing_catalog_objects": sorted(missing),
        "rls_disabled_objects": sorted(no_rls),
        "catalog_conformance_only": verdict == "CATALOG_PRESENT_UNQUALIFIED",
        "public_api_grants": "UNKNOWN_NOT_INSPECTED",
        "provider_authentication": "UNKNOWN_NOT_INDEPENDENTLY_VERIFIED",
        "source_heads_currentness": "UNKNOWN_NOT_VERIFIED",
        "runtime_currentness": "UNKNOWN_NOT_PROBED",
        "independently_authenticated": False,
        "memory_admission": "NONE",
        "memory_read": "NONE",
        "release_authorization": "NONE",
        "side_effects": [],
        "result_semantics": "UNTRUSTED_METADATA_ONLY_NO_RUNTIME_OR_AUTHORITY"
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BT2 memory provider metadata conformance V1")
    parser.add_argument("snapshot",type=Path)
    args = parser.parse_args(argv)
    try:
        data = args.snapshot.read_bytes()
        if len(data) > 131072:
            raise CatalogError("snapshot too large")
        output = evaluate_catalog(strict_json(data.decode("utf-8")))
    except (OSError, UnicodeError, CatalogError) as exc:
        print("MEMORY_PROVIDER_CATALOG_ERROR:" + str(exc),file=sys.stderr)
        return 2
    print(canonical(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())