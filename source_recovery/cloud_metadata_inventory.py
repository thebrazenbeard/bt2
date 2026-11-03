"""Pure, private, *non-admitting* normalized cloud metadata intake.

No connector, Graph client, filesystem access, network call, byte reader,
archive extraction, public export, classification, or repository routing.
Caller-supplied, independently obtained metadata and pagination attestations
remain *untrusted*. All rows must pass validation before any held records are
returned. A caller-held HMAC custody key protects the raw identities against
straightforward reversal (assuming key secrecy), but deterministic identical
IDs remain linkable by equality even without the key. Neither the key nor
names/raw cloud IDs are retained in results.
The ID represents one version-tagged metadata *observation*, NOT an item that
stays stable across revisions and emphatically NOT a byte/content digest.

This source-only adapter is not a currentness, license, or custody authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import re


_FIELDS = frozenset({"drive_id", "item_id", "name", "kind", "size", "e_tag"})
_ID = re.compile(r"^[A-Za-z0-9_.:@!-]{1,192}$")
_HELD_ID = re.compile(r"^CLD_[A-F0-9]{32}$")
_INVALID_NAME = re.compile(r"[\\/\x00-\x1f\x7f]|[<>:\"|?*]")
_RESERVED_NAME = re.compile(r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", re.I)
_SECRET_NAME = re.compile(
    r"(?:PASSWORD|PASSWD|TOKEN|SECRET|CREDENTIAL|PRIVATE|PERSONAL|IDENTITY|"
    r"(?:^|[._-])(?:KEY|SSH|ENV|PEM|P12|PFX|KDBX)(?:[._-]|$))", re.I
)
_SHORTCUT_SUFFIXES = (".lnk", ".url", ".webloc", ".website")
_SCHEMA = "BT2_HISTORICAL_EXPORT_ADJUDICATION_V1"
_REASONS = ("SOURCE_PROVENANCE_UNVERIFIED", "RIGHTS_UNVERIFIED",
            "PRIVATE_CONTENT_UNREVIEWED", "CURRENT_GIT_COMPARISON_PENDING")
_MAX_ENTRIES = 5_000
_MAX_FILE_BYTES = 2**63 - 1


class CloudInventoryError(ValueError):
    """Generic error code only; never includes untrusted private metadata."""


@dataclass(frozen=True, slots=True)
class HeldCloudArtifact:
    """Opaque index entry; absolutely no source name or source identifier."""

    artifact_id: str
    evidence_class: str = "INVENTORY"
    privacy: str = "PRIVATE_HOLD"
    source_state: str = "HISTORICAL_NOT_INSTALLED"
    rights: str = "UNVERIFIED"
    public_admission: str = "HOLD"
    raw_material_git_eligible: bool = False

    def __post_init__(self) -> None:
        if (type(self.artifact_id) is not str or not _HELD_ID.fullmatch(self.artifact_id)
                or any(type(value) is not str for value in (
                    self.evidence_class, self.privacy, self.source_state,
                    self.rights, self.public_admission))
                or self.evidence_class != "INVENTORY"
                or self.privacy != "PRIVATE_HOLD"
                or self.source_state != "HISTORICAL_NOT_INSTALLED"
                or self.rights != "UNVERIFIED" or self.public_admission != "HOLD"
                or self.raw_material_git_eligible is not False):
            raise CloudInventoryError("INVALID_HELD_RECORD")


@dataclass(frozen=True, slots=True)
class HeldCloudInventory:
    """Only safe structural projections; keep in privately governed custody."""

    records: tuple[HeldCloudArtifact, ...]
    total_entries: int
    files: int
    folders: int
    total_bytes: int
    status: str = "PRIVATE_HOLD_UNVERIFIED"

    def __post_init__(self) -> None:
        if (type(self.status) is not str
                or self.status != "PRIVATE_HOLD_UNVERIFIED"
                or type(self.records) is not tuple
                or any(type(record) is not HeldCloudArtifact for record in self.records)
                or any(type(value) is not int for value in (
                    self.total_entries, self.files, self.folders, self.total_bytes))
                or not 0 <= self.total_entries <= _MAX_ENTRIES
                or not 0 <= self.total_bytes <= _MAX_FILE_BYTES
                or self.files < 0 or self.folders < 0
                or self.files + self.folders != self.total_entries
                or len(self.records) != self.total_entries
                or (self.files == 0 and self.total_bytes != 0)
                or len({record.artifact_id for record in self.records}) != self.total_entries):
            raise CloudInventoryError("INVALID_HELD_INVENTORY")

    def to_private_adjudication_records(self) -> tuple[dict, ...]:
        """Produce schema-shaped held records, never a public export grant."""
        return tuple({
            "schema": _SCHEMA,
            "artifact_id": item.artifact_id,
            "private_locator": "REDACTED",
            "source_state": item.source_state,
            "evidence_class": item.evidence_class,
            "duplicate_group": None,
            "privacy": item.privacy,
            "rights": item.rights,
            "target_repo_candidate": None,
            "current_git_comparison": "NOT_PERFORMED",
            "source_test": "NOT_RUN",
            "independent_review": "NOT_PERFORMED",
            "public_admission": item.public_admission,
            "reason_codes": list(_REASONS),
        } for item in self.records)

    def to_public_json(self) -> None:
        """Reject even held-record publication; use a separate authorized review."""
        raise CloudInventoryError("PUBLIC_SERIALIZATION_FORBIDDEN")


def _validate_rows(rows: object) -> dict[tuple[str, str], tuple[str, int, str, str]]:
    if type(rows) not in (tuple, list) or len(rows) > _MAX_ENTRIES:
        raise CloudInventoryError("INVALID_ROWS")
    seen: dict[tuple[str, str], tuple[str, int, str, str]] = {}
    for row in rows:
        # Exact built-in types prevent user-supplied object hooks and avoid
        # accidentally admitting Graph's remoteItem/shortcut/content surfaces.
        if (type(row) is not dict
                or not all(type(field) is str for field in row)
                or row.keys() != _FIELDS):
            raise CloudInventoryError("UNEXPECTED_METADATA_FIELD")
        drive, item_id = row["drive_id"], row["item_id"]
        if (type(drive) is not str or type(item_id) is not str
                or not _ID.fullmatch(drive) or not _ID.fullmatch(item_id)
                or drive in (".", "..") or item_id in (".", "..")):
            raise CloudInventoryError("INVALID_OPAQUE_SOURCE_ID")
        identity = (drive, item_id)
        if identity in seen:
            raise CloudInventoryError("DUPLICATE_SOURCE_ID")
        name = row["name"]
        if (type(name) is not str or not 1 <= len(name) <= 240
                or name in (".", "..") or name != name.strip(" .")
                or any(0xD800 <= ord(char) <= 0xDFFF for char in name)
                or _INVALID_NAME.search(name) or _RESERVED_NAME.search(name)
                or _SECRET_NAME.search(name)
                or name.casefold().endswith(_SHORTCUT_SUFFIXES)):
            raise CloudInventoryError("SUSPICIOUS_SOURCE_NAME")
        kind, size, tag = row["kind"], row["size"], row["e_tag"]
        if type(kind) is not str or kind not in ("file", "folder"):
            raise CloudInventoryError("UNSUPPORTED_SOURCE_KIND")
        if (type(size) is not int or size < 0 or size > _MAX_FILE_BYTES
                or (kind == "folder" and size != 0)):
            raise CloudInventoryError("INVALID_SOURCE_SIZE")
        if (type(tag) is not str or not 1 <= len(tag) <= 192
                or any(ord(char) < 32 or ord(char) > 126 for char in tag)):
            raise CloudInventoryError("INVALID_VERSION_TAG")
        seen[identity] = (kind, size, tag, name)
    return seen


def _validate_pagination(rows: object, page_sizes: object, expected_count: object,
                         exhausted: object, capped: object, failed_pages: object) -> None:
    if (type(exhausted) is not bool or exhausted is not True
            or type(capped) is not bool or capped
            or type(failed_pages) is not int or failed_pages != 0):
        raise CloudInventoryError("INCOMPLETE_LISTING")
    if (type(expected_count) is not int or not 0 <= expected_count <= _MAX_ENTRIES
            or type(page_sizes) not in (tuple, list) or not page_sizes
            or any(type(n) is not int or n < 0 or n > 200 for n in page_sizes)
            or sum(page_sizes) != expected_count or len(rows) != expected_count):
        raise CloudInventoryError("AMBIGUOUS_LISTING_COUNT")
    # A sole full 200-item page is indistinguishable from a capped response
    # in a normalized metadata-only result. Refuse even a caller's assertion
    # of exhaustion until an uncapped paginated result is supplied.
    if len(page_sizes) == 1 and page_sizes[0] == 200:
        raise CloudInventoryError("SINGLE_PAGE_CAP_AMBIGUITY")


def build_held_cloud_inventory(
    items: object,
    *,
    custody_key: object,
    page_sizes: object,
    expected_count: object,
    exhausted: object,
    capped: object = False,
    failed_pages: object = 0,
    previous_items: object = None,
) -> HeldCloudInventory:
    """Fail-closed projection of two-pass normalized metadata into held IDs.

    ``previous_items`` is optional caller-supplied metadata for detecting
    version-tag, identity, kind, and size changes. Without it, this only
    constructs an unverified one-pass candidate and does not claim stability.

    ``page_sizes`` must include all pages (each at most 200); a lone page of
    exactly 200 is ambiguous and rejected. ``exhausted`` is a *claim*, not an
    authenticated Graph page-end proof. No file data is ever read.
    """
    if (type(custody_key) is not bytes or len(custody_key) < 16
            or len(custody_key) > 512):
        raise CloudInventoryError("INVALID_CUSTODY_KEY")
    if type(items) not in (tuple, list):
        raise CloudInventoryError("INVALID_ROWS")
    _validate_pagination(items, page_sizes, expected_count, exhausted, capped, failed_pages)
    validated = _validate_rows(items)
    if previous_items is not None:
        previous = _validate_rows(previous_items)
        if previous != validated:
            raise CloudInventoryError("SOURCE_IDENTITY_OR_VERSION_CHANGED")

    records = []
    files = folders = total_bytes = 0
    for (drive_id, item_id), (kind, size, tag, name) in sorted(validated.items()):
        # Version-tagged observation identity, not content identity. Bind every
        # relevant metadata field so a changed eTag, name, size, or kind cannot
        # silently reuse an adjudication artifact ID in independent runs.
        # Domain separation and length-framing prevent concatenation aliasing.
        parts = (drive_id.encode("ascii"), item_id.encode("ascii"),
                 kind.encode("ascii"), str(size).encode("ascii"),
                 tag.encode("ascii"), name.encode("utf-8"))
        framed = b"BT2_CLOUD_HELD_OBSERVATION_V1\x00" + b"".join(
            len(part).to_bytes(4, "big") + part for part in parts
        )
        opaque = "CLD_" + hmac.new(custody_key, framed, hashlib.sha256).hexdigest()[:32].upper()
        records.append(HeldCloudArtifact(opaque))
        files += kind == "file"
        folders += kind == "folder"
        total_bytes += size
        if total_bytes > _MAX_FILE_BYTES:
            raise CloudInventoryError("INVALID_TOTAL_SIZE")
    return HeldCloudInventory(tuple(records), len(records), files, folders, total_bytes)
