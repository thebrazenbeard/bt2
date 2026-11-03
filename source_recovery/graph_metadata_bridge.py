"""Pure bridge: normalized children listing + exact-ID metadata-only lookup.

This module does *not* call Graph/OneDrive/SharePoint, open files, hydrate
cloud placeholders, or serialize source metadata. A list item lacking eTag is
only a selector for a separately performed, exactly addressed get-item call;
the latter is a new observation, NOT proof of the listing item's revision.
All results remain PRIVATE_HOLD_UNVERIFIED through the base adapter.
"""

from __future__ import annotations

from .cloud_metadata_inventory import (
    CloudInventoryError,
    HeldCloudInventory,
    build_held_cloud_inventory,
)


_CHILD_BASE = frozenset({"id", "name", "size", "parent_reference"})
_LOOKUP_BASE = _CHILD_BASE | {"e_tag"}
_REQUEST_FIELDS = frozenset({"drive_id", "item_id"})
_LOOKUP_FIELDS = frozenset({"request", "status", "item"})


def _exact_fields(value: object, required: frozenset[str]) -> bool:
    return (type(value) is dict
            and all(type(key) is str for key in value)
            and value.keys() == required)


def _parse_item(item: object, *, exact_get: bool) -> dict:
    """Return ephemeral normalized source row (never persisted or exposed)."""
    if type(item) is not dict or not all(type(key) is str for key in item):
        raise CloudInventoryError("INVALID_GRAPH_ITEM")
    facets = [facet for facet in ("file", "folder") if facet in item]
    if len(facets) != 1:
        raise CloudInventoryError("UNSUPPORTED_GRAPH_KIND")
    facet = facets[0]
    expected = (_LOOKUP_BASE if exact_get else _CHILD_BASE) | {facet}
    if item.keys() != expected or type(item[facet]) is not dict or item[facet]:
        # An exact empty file/folder facet is required. The caller must strip
        # all irrelevant Graph fields *before* crossing this source-only API.
        # RemoteItem, links, hashes, permissions and downloadUrl are forbidden.
        raise CloudInventoryError("UNEXPECTED_GRAPH_METADATA")
    parent = item["parent_reference"]
    if not _exact_fields(parent, frozenset({"drive_id"})):
        raise CloudInventoryError("INVALID_GRAPH_PARENT")
    if (type(item["id"]) is not str
            or type(parent["drive_id"]) is not str
            or type(item["name"]) is not str
            or type(item["size"]) is not int):
        raise CloudInventoryError("INVALID_GRAPH_ITEM_TYPE")
    normalized = {
        "drive_id": parent["drive_id"],
        "item_id": item["id"],
        "name": item["name"],
        "kind": facet,
        "size": item["size"],
    }
    if exact_get:
        if type(item["e_tag"]) is not str or not item["e_tag"]:
            raise CloudInventoryError("MISSING_EXACT_VERSION")
        normalized["e_tag"] = item["e_tag"]
    return normalized


def _paired_gets(selected: dict, lookups: object) -> list[dict]:
    if type(lookups) not in (list, tuple) or len(lookups) != len(selected):
        raise CloudInventoryError("MISSING_EXACT_GET")
    seen = {}
    for response in lookups:
        if not _exact_fields(response, _LOOKUP_FIELDS):
            raise CloudInventoryError("INVALID_EXACT_GET_ENVELOPE")
        request = response["request"]
        if (not _exact_fields(request, _REQUEST_FIELDS)
                or type(request["drive_id"]) is not str
                or type(request["item_id"]) is not str
                or type(response["status"]) is not int
                or response["status"] != 200):
            raise CloudInventoryError("EXACT_GET_NOT_CONFIRMED")
        identity = (request["drive_id"], request["item_id"])
        if identity in seen or identity not in selected:
            raise CloudInventoryError("DUPLICATE_OR_UNREQUESTED_GET")
        item = _parse_item(response["item"], exact_get=True)
        if (item["drive_id"], item["item_id"]) != identity:
            raise CloudInventoryError("EXACT_GET_IDENTITY_MISMATCH")
        # No eTag existed in children metadata; compare every shared field.
        # This still cannot prove that the listing selected the same revision.
        if any(item[field] != selected[identity][field]
               for field in ("drive_id", "item_id", "name", "kind", "size")):
            raise CloudInventoryError("LIST_EXACT_GET_METADATA_CHANGED")
        seen[identity] = item
    if len(seen) != len(selected):
        raise CloudInventoryError("MISSING_EXACT_GET")
    return list(seen.values())


def _selected_children(children: object) -> dict:
    if type(children) not in (tuple, list):
        raise CloudInventoryError("INVALID_GRAPH_CHILDREN")
    selected = {}
    for raw in children:
        row = _parse_item(raw, exact_get=False)
        identity = (row["drive_id"], row["item_id"])
        if identity in selected:
            raise CloudInventoryError("DUPLICATE_GRAPH_CHILD")
        selected[identity] = row
    return selected


def build_held_inventory_from_graph_metadata(
    children: object,
    exact_lookups: object,
    *,
    custody_key: object,
    page_sizes: object,
    expected_count: object,
    exhausted: object,
    capped: object = False,
    failed_pages: object = 0,
    verification_children: object = None,
    verification_lookups: object = None,
) -> HeldCloudInventory:
    """Bridge caller-supplied exact-ID metadata receipts into held records.

    ``children`` is a flattened collection from externally governed recursive
    listing; pagination/folder completeness remains a caller assertion.
    ``exact_lookups`` contains one 200-status, exact-(drive_id,item_id) get
    envelope per child. ``verification_children`` optionally compares a
    complete second listing's identity/name/kind/size set; separately,
    ``verification_lookups`` can compare exact second-get version tags. These
    are not atomic snapshots or authenticated connector receipts.
    """
    selected = _selected_children(children)
    if verification_children is not None:
        second = _selected_children(verification_children)
        if second != selected:
            raise CloudInventoryError("GRAPH_LISTING_CHANGED")
    exact = _paired_gets(selected, exact_lookups)
    verified = (_paired_gets(selected, verification_lookups)
                if verification_lookups is not None else None)
    # The underlying pure adapter validates safe names, source IDs, version
    # tags, pagination count/cap, and held output. No raw rows are returned.
    return build_held_cloud_inventory(
        exact,
        custody_key=custody_key,
        page_sizes=page_sizes,
        expected_count=expected_count,
        exhausted=exhausted,
        capped=capped,
        failed_pages=failed_pages,
        previous_items=verified,
    )
