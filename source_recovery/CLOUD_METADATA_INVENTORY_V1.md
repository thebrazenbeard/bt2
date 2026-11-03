# Cloud metadata inventory adapter — source-only candidate

`cloud_metadata_inventory.py` is a **pure, private, fail-closed transformation**
for normalized Graph-like metadata supplied by a separately authenticated
enumerator. It does not call Graph, the OneDrive connector, a local filesystem,
an archive reader, GitHub, or any service. It does not authorize a read or
write on Lappy, VN1, VN2, NAS, or cloud storage.

## Input contract

Every item is a plain Python dictionary with **exactly** these fields:

| Field | Input | Treatment |
| --- | --- | --- |
| `drive_id` | Nonempty bounded ASCII opaque identity | HMAC input only; discarded |
| `item_id` | Nonempty bounded ASCII opaque identity | HMAC input only; discarded |
| `name` | Bounded plain basename | Validate for unsafe paths, reserved names, secret hints, shortcuts; discard |
| `kind` | `file` or `folder` | Aggregate only |
| `size` | Nonnegative integer (folders must be zero) | Aggregate only |
| `e_tag` | Bounded ASCII version marker | Optional two-pass stability check; discarded |

Opaque identities permit a conservative subset of ASCII (`A-Z`, `a-z`, digits,
`_.:@!-`) including the `!` used in some Graph drive IDs. **Never truncate,
strip, case-fold, or replace** an upstream identifier to fit this grammar.
An otherwise valid item whose ID cannot be represented losslessly is held;
any future alias mapping requires authenticated, collision-resistant,
stable provenance and a separate review.

Graph keys such as `remoteItem`, share links, child contents, download URLs,
`parentReference`, permissions, and content **must not** be passed through. The
caller must normalize only allowed fields; unknown fields fail closed. A
shortcut/remote item is *not* a normal file and is rejected.

The caller must supply a secret custody HMAC key (16–512 bytes) held outside
the output. The adapter returns IDs such as `CLD_<32_HEX>` without emitting
raw drive IDs, item IDs, names, paths, eTags, or the key. IDs are tied to
**one metadata observation**: `(drive_id, item_id, name, kind, size, e_tag)`.
Changing an observation field changes the opaque ID, even across separately
submitted snapshots. This is **not** a content hash, attested version, durable
item locator, duplicate detector, or proof of byte identity. Do not persist the
key in Git or logs. Rotating the key intentionally changes all pseudonyms.
Unchanged observations remain linkable across outputs by equality of their
HMAC IDs, even to someone without the key; this is pseudonymization, not
anonymization or unlinkability.

`page_sizes`, `expected_count`, `exhausted=True`, `capped=False`, and
`failed_pages=0` express a **caller declaration**, not authenticated evidence.
Each page must contain at most 200 rows; summed counts must equal the input.
One uncontinued page of exactly 200 is rejected as cap-ambiguous, including
when the caller asserts completion. A separately authenticated enumerator must
prove that all folders and pagination cursors were exhausted; this module
cannot prove it. For an external 355-entry inventory, e.g. two pages of 200
and 155, accepting count consistency does **not** establish Graph custody,
correct folder traversal, or source currentness.

An optional `previous_items` second-pass list must have identical identities,
names, kinds, sizes, and eTags. Any change or disappearance raises a generic error.
Passing it does not make a race-free or cryptographically signed snapshot;
independent host-owned custody is still required.

## Output and boundaries

`HeldCloudInventory.records` contains only frozen `HeldCloudArtifact` objects
with opaque HMAC IDs and constant HOLD / UNVERIFIED states. The optional
`to_private_adjudication_records()` returns **private**, schema-shaped records
compatible with `historical_adjudication_v1.schema.json`; every record has
`private_locator=REDACTED`, `public_admission=HOLD`,
`rights=UNVERIFIED`, `target_repo_candidate=null`, and
`current_git_comparison=NOT_PERFORMED`.

`to_public_json()` always raises `PUBLIC_SERIALIZATION_FORBIDDEN`. These
objects do not implement JSON serialization. An operator with Python source
control could still manually serialize `to_private_adjudication_records()`:
this is a **code/API guardrail**, not a security boundary against a malicious
caller. The generated private records themselves are not approved for Git.
Both held dataclasses validate their status and structural invariants even if
constructed directly; callers cannot mark their `status` verified or insert
raw identifiers by passing ordinary constructor arguments. These structural
checks do not authenticate the HMAC's origin or the caller's authority.

This adapter performs **no classification or candidate repository routing**:
names and ZIP titles are never allowed to pick a repo. Rights, privacy,
independent review, exact Git comparison, and the admission decision remain
separate gates. A passing unit test is source-code evidence only, not a
cloud inventory readback, runtime binding, verified historical source, or
permission grant.

Run synthetic focused tests:

```sh
python -m unittest source_recovery.tests.test_cloud_metadata_inventory -v
```
