# Exact-ID cloud metadata bridge — source-only candidate

`graph_metadata_bridge.py` is a pure bridge from two **caller-supplied,
normalized** Microsoft Graph-like metadata shapes to the held-only adapter
in `cloud_metadata_inventory.py`. No connector call, endpoint request, file
read, folder traversal, local hydration, or output write occurs in this code.

The relevant connector behavior observed separately is that a
`list_drive_item_children` item may omit `e_tag`; a separately addressed
`get_drive_item(drive_id, item_id)` metadata response can supply that marker.
The bridge **never invents a tag** from name, size, timestamp, path, or a
file hash. Every listed item requires a distinct exact-ID get envelope.

## Strict normalized inputs

The caller must project externally obtained objects to these exact shapes,
discarding all unrelated Graph properties **only after** independently
checking they are not shortcuts/remote objects:

```python
children = [{
    "id": "synthetic-item",
    "name": "example.txt",
    "size": 12,
    "parent_reference": {"drive_id": "synthetic!drive"},
    "file": {},  # OR "folder": {}, never both
}]

lookups = [{
    "request": {"drive_id": "synthetic!drive", "item_id": "synthetic-item"},
    "status": 200,
    "item": {**children[0], "e_tag": "synthetic-version"},
}]
```

All IDs and names above are invented examples. No real identifier, secret,
path, or filename belongs in GitHub examples or tests.

`children` requires exactly `id`, `name`, `size`, `parent_reference`, and one
empty `file`/`folder` facet. In particular it omits `e_tag`. A lookup requires
the same keys **plus** nonempty `e_tag`, inside an envelope containing exactly
`request`, `status=200`, and `item`. The requested drive/item IDs must be
identical to both the listed and returned IDs; missing/duplicate/unrequested
lookups, changed name/kind/size, 304/null responses, unexpected fields,
shortcuts/`remoteItem`, download URLs, content, and malformed values are
rejected with generic errors (no raw names or URLs in error strings).

Graph may provide extra benign metadata such as MIME types, folder child
counts, or web URLs. Those are **not accepted by this narrow contract**.
Dropping a `remoteItem`/shortcut flag before checking it externally can hide
dangerous aliasing. A trusted normalizer must document how it identifies
and rejects remote items before constructing these exact dictionaries.
This module does not attest that such stripping was performed safely.

`verification_children` optionally supplies a second complete normalized
listing; changed identities, names, kinds, and sizes fail closed.
`verification_lookups` optionally supplies a second complete round of
exact-ID get envelopes; changed eTag, name, kind, size, or identity fails
closed. Without a second get pass, there is **no version-stability evidence**.
Even with both repeated listings and gets, time-of-check/time-of-use races
remain. Neither second pass authenticates a connector receipt.

## Critical provenance ceiling

The children listing is only a collection of **untrusted selectors**. Since
its items omit eTag, matching `id`, `name`, `size`, and kind against a later
exact get **cannot prove the two calls observed the same revision**. The get
is a new metadata observation. Pagination `page_sizes`, `exhausted`, and
recursive folder coverage remain caller attestations; an exactly full
200-item page without further proof is ambiguous and rejected by the base
adapter. Even `exhausted=True` is not a signed Graph pagination witness.

Outputs are only `HeldCloudInventory` / `HeldCloudArtifact` with pseudonymous
revision-tagged metadata observation IDs and schema-shaped private records:
`PRIVATE_HOLD_UNVERIFIED`, rights `UNVERIFIED`, `public_admission=HOLD`.
They are neither content hashes nor verified file revisions. No public
serialization, training, repository routing, installation, or rights
admission follows.

A two-item canary is **two selected observations**, not a complete Downloads
inventory even if both parents were listed. Its `expected_count=2` and
`exhausted=True` describe only the selected input to this pure function;
they must not be reinterpreted as proof that every source folder was visited
or every sibling item was admitted. The separately observed 355-item
aggregate remains a distinct, unqualified evidence class.

Run the synthetic contract tests:

```sh
python -m unittest source_recovery.tests.test_graph_metadata_bridge -v
python -m unittest discover -s source_recovery/tests -p 'test_*.py' -q
```
