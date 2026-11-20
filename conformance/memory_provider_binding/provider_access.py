"""Read-only privilege-surface conformance over supplied untrusted metadata.

Data API grants, RLS presence and security-definer search-path indicators are
observations, not proof of a correct policy, safe function body, current role,
API exposure, provider authentication or permission to admit memory.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import sys
from typing import Any

from provider_catalog import canonical, strict_json, CatalogError, _name

INPUT_SCHEMA = "BT2_MEMORY_PROVIDER_ACCESS_INPUT_V1"
OUTPUT_SCHEMA = "BT2_MEMORY_PROVIDER_ACCESS_OUTPUT_V1"
EXPECTED_TABLES = frozenset({
    ("public", "vera_memory_epoch_subjects_v1"),
    ("public", "vera_memory_epoch_events_v1"),
    ("public", "vera_memory_epoch_provider_receipts_v1"),
    ("public", "vera_memory_epoch_archive_receipts_v1"),
    ("semantic_atlas", "runtime_objects"),
    ("semantic_atlas", "runtime_snapshots"),
    ("semantic_atlas", "capture_policy"),
})
EXPECTED_FUNCTIONS = frozenset({
    ("public", "vera_memory_epoch_get_status_v1"),
    ("semantic_atlas", "search_current_runtime_objects_v11"),
})
TABLE_PRIVILEGES = frozenset({"select", "insert", "update", "delete"})
ROLE_NAMES = ("anon", "authenticated")
UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _strict_object(value: object, keys: set[str]) -> dict:
    if type(value) is not dict or set(value) != keys:
        raise CatalogError("access snapshot object shape invalid")
    return value


def _flag(value: object) -> bool:
    if type(value) is not bool:
        raise CatalogError("access snapshot boolean field invalid")
    return value


def _key(obj: dict) -> tuple[str, str]:
    return (_name(obj["schema"]), _name(obj["name"]))


def evaluate_access(snapshot: dict[str, Any]) -> dict[str, Any]:
    if type(snapshot) is not dict or snapshot.get("schema") != INPUT_SCHEMA:
        raise CatalogError("unsupported access snapshot schema")
    required = {"schema","observed_at","source_ref","tables","functions"}
    optionals = {"independently_authenticated", "schema_rights"}
    if not required.issubset(snapshot) or set(snapshot)-required-optionals:
        raise CatalogError("access envelope fields invalid")
    observed = snapshot["observed_at"]
    if type(observed) is not str or UTC.fullmatch(observed) is None:
        raise CatalogError("access observation time invalid")
    try:
        datetime.fromisoformat(observed.replace("Z","+00:00"))
    except ValueError as exc:
        raise CatalogError("invalid observation calendar time") from exc
    source = snapshot["source_ref"]
    if type(source) is not str or not source or len(source.encode("utf-8")) > 512:
        raise CatalogError("invalid opaque access source reference")
    if "independently_authenticated" in snapshot:
        _flag(snapshot["independently_authenticated"])
    tables, functions = snapshot["tables"], snapshot["functions"]
    if type(tables) is not list or len(tables) > 32 or type(functions) is not list or len(functions) > 32:
        raise CatalogError("access snapshot size exceeded")
    table_map: dict[tuple[str,str],dict] = {}
    function_map: dict[tuple[str,str],dict] = {}
    table_shape = {"schema","name","rls_enabled","force_rls","anon","authenticated"}
    function_shape = {"schema","name","security_definer","anon_execute",
                      "authenticated_execute","search_path_limited"}
    for t in tables:
        t = _strict_object(t,table_shape)
        key = _key(t)
        if key in table_map:
            raise CatalogError("duplicate access table identity")
        _flag(t["rls_enabled"])
        _flag(t["force_rls"])
        for role in ROLE_NAMES:
            grants = _strict_object(t[role],set(TABLE_PRIVILEGES))
            for value in grants.values():
                _flag(value)
        table_map[key]=t
    for f in functions:
        f = _strict_object(f,function_shape)
        key = _key(f)
        if key in function_map:
            raise CatalogError("duplicate access function identity")
        for field in function_shape-{"schema","name"}:
            _flag(f[field])
        function_map[key]=f

    # SECURITY DEFINER search paths also require negative CREATE grants on
    # their constituent namespaces. Absence of this metadata is UNKNOWN.
    schema_map: dict[str, dict] = {}
    rights = snapshot.get("schema_rights")
    if rights is not None:
        if type(rights) is not list or len(rights) > 8:
            raise CatalogError("schema rights inventory invalid")
        for entry in rights:
            entry = _strict_object(entry,{"schema","anon_create","authenticated_create","anon_usage","authenticated_usage"})
            schema = _name(entry["schema"])
            if schema in schema_map:
                raise CatalogError("duplicate schema rights identity")
            _flag(entry["anon_create"])
            _flag(entry["authenticated_create"])
            _flag(entry["anon_usage"])
            _flag(entry["authenticated_usage"])
            schema_map[schema]=entry
    missing_schemas = {"public","semantic_atlas"}-set(schema_map)
    missing = EXPECTED_TABLES-set(table_map)
    missing_functions = EXPECTED_FUNCTIONS-set(function_map)
    codes: set[str] = set()
    review_codes: set[str] = set()
    for key in EXPECTED_TABLES.intersection(table_map):
        table = table_map[key]
        if not table["rls_enabled"]:
            codes.add("RLS_DISABLED")
        for role in ROLE_NAMES:
            if any(table[role].values()):
                codes.add("ANON_TABLE_PRIVILEGE" if role=="anon" else "AUTHENTICATED_TABLE_PRIVILEGE")
    for key in EXPECTED_FUNCTIONS.intersection(function_map):
        fn = function_map[key]
        if fn["anon_execute"]:
            codes.add("ANON_SECURITY_DEFINER_EXECUTE" if fn["security_definer"] else "ANON_FUNCTION_EXECUTE")
        if fn["authenticated_execute"]:
            codes.add("AUTHENTICATED_SECURITY_DEFINER_EXECUTE" if fn["security_definer"] else "AUTHENTICATED_FUNCTION_EXECUTE")
        if fn["security_definer"] and not fn["search_path_limited"]:
            codes.add("SECURITY_DEFINER_SEARCH_PATH_NOT_PINNED")
        if not fn["security_definer"]:
            codes.add("FUNCTION_EXECUTION_MODE_CHANGED")
    # Unknown memory-bearing objects are considered, but a grant to EXECUTE
    # without USAGE on that schema does not prove a callable Data API surface.
    # Keep that latent grant visible as review evidence; NEVER call it safe.
    for (schema, name), table in table_map.items():
        if (schema, name) in EXPECTED_TABLES:
            continue
        related = (schema == "public" and name.startswith("vera_memory_")) or (
            schema == "semantic_atlas" and name.startswith(("runtime_", "capture_", "memory_")))
        if not related:
            continue
        any_grant = any(table[role][privilege] for role in ROLE_NAMES
                        for privilege in TABLE_PRIVILEGES)
        any_effective_grant = any(
            table[role][privilege] and
            schema_map.get(schema, {}).get(role+"_usage", True)
            for role in ROLE_NAMES for privilege in TABLE_PRIVILEGES)
        if any_effective_grant:
            codes.add("UNLISTED_MEMORY_TABLE_GRANT")
        elif any_grant:
            review_codes.add("UNLISTED_MEMORY_TABLE_GRANT_NO_SCHEMA_USAGE")
        else:
            review_codes.add("UNLISTED_MEMORY_TABLE_REVIEW")
    for (schema, name), fn in function_map.items():
        if (schema, name) in EXPECTED_FUNCTIONS:
            continue
        related = (schema == "public" and name.startswith("vera_memory_")) or (
            schema == "semantic_atlas" and name.startswith(("search_current_", "runtime_", "memory_")))
        if not related:
            continue
        any_grant = fn["anon_execute"] or fn["authenticated_execute"]
        any_effective_grant = (
            (fn["anon_execute"] and schema_map.get(schema, {}).get("anon_usage", True))
            or (fn["authenticated_execute"] and schema_map.get(schema, {}).get("authenticated_usage", True)))
        if any_effective_grant:
            codes.add("UNLISTED_MEMORY_FUNCTION_EXECUTE")
        elif any_grant:
            review_codes.add("UNLISTED_EXECUTE_GRANT_NO_SCHEMA_USAGE")
        else:
            review_codes.add("UNLISTED_MEMORY_FUNCTION_REVIEW")
    for schema, flags in schema_map.items():
        if schema not in {"public","semantic_atlas"}:
            continue
        if flags["anon_create"]:
            codes.add("ANON_CREATE_ON_MEMORY_SCHEMA")
        if flags["authenticated_create"]:
            codes.add("AUTHENTICATED_CREATE_ON_MEMORY_SCHEMA")
    if codes:
        verdict = "HOLD_PRIVILEGE_EXPOSURE"
    elif missing or missing_functions or missing_schemas:
        verdict = "UNKNOWN_INCOMPLETE_CATALOG"
    elif review_codes:
        verdict = "REVIEW_UNLISTED_SURFACES"
    else:
        verdict = "ACCESS_SURFACE_RESTRICTED_UNQUALIFIED"
    return {
        "schema": OUTPUT_SCHEMA,
        "verdict": verdict,
        "observed_at": observed,
        "source_ref_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "reason_codes": sorted(codes | review_codes),
        "missing_required_tables": len(missing),
        "missing_required_functions": len(missing_functions),
        "missing_required_schemas": len(missing_schemas),
        "requested_role_privileges": "OBSERVED_IN_SUPPLIED_SNAPSHOT_ONLY",
        "rls_policy_correctness": "UNKNOWN_NOT_PROBED",
        "provider_authentication": "UNKNOWN_NOT_INDEPENDENTLY_VERIFIED",
        "runtime_currentness": "UNKNOWN_NOT_PROBED",
        "independently_authenticated": False,
        "memory_read": "NONE",
        "memory_admission": "NONE",
        "release_authorization": "NONE",
        "side_effects": [],
        "result_semantics": "ACCESS_SURFACE_CLAIMS_NOT_PROVIDER_AUTHORITY",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only memory provider privilege source conformance")
    ap.add_argument("input", type=Path)
    args = ap.parse_args(argv)
    try:
        data = args.input.read_bytes()
        if len(data) > 65536:
            raise CatalogError("access snapshot exceeds byte budget")
        result = evaluate_access(strict_json(data.decode("utf-8")))
    except (OSError, UnicodeError, CatalogError) as exc:
        print("PROVIDER_ACCESS_ERROR:"+str(exc),file=sys.stderr)
        return 2
    print(canonical(result))
    return 0


if __name__=="__main__":
    raise SystemExit(main())