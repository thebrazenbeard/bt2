"""Zero-trust, metadata-only archive intake for recoverable local exports.

Never extracts or executes ZIP members. All records remain local unless an
operator explicitly reviews and separately publishes downstream work.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

SCHEMA = "BT2_EXPORT_READONLY_INVENTORY_V1"
PRIVATE_HINTS = ("CHAT", "PERSONAL", "PRIVATE", "UNSANITIZED", "KEY",
                 "SECRET", "PASSWORD", "TOKEN", "IDENTITY", "MEMORY")

class IntakeError(ValueError):
    """Unsafe input location or exceeded read-only inventory cap."""

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _zip_metadata(path: Path, max_members: int) -> dict:
    result = {"status": "UNREADABLE", "members": 0, "unsafe_paths": 0,
              "encrypted": 0, "symlinks": 0, "suspicious_ratios": 0}
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            result["members"] = len(entries)
            if len(entries) > max_members:
                result["status"] = "MEMBER_LIMIT_EXCEEDED"
                return result
            for member in entries:
                name = member.filename.replace("\\", "/")
                parts = PurePosixPath(name).parts
                unsafe = (name.startswith("/") or bool(re.match(r"^[A-Za-z]:", name))
                          or ".." in parts or "\x00" in name)
                result["unsafe_paths"] += bool(unsafe)
                result["encrypted"] += bool(member.flag_bits & 1)
                result["symlinks"] += stat.S_ISLNK(member.external_attr >> 16)
                result["suspicious_ratios"] += (
                    member.file_size > 10_000_000 and
                    member.file_size / max(1, member.compress_size) > 1000
                )
            result["status"] = "METADATA_READABLE_UNTRUSTED"
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile):
        pass
    return result

def scan_folder(root: Path, *, max_files: int = 20000,
                max_zip_members: int = 60000) -> dict:
    root = Path(root)
    if not root.is_dir() or root.is_symlink() or max_files < 1 or max_zip_members < 1:
        raise IntakeError("input must be a real directory with positive caps")
    root = root.resolve()
    paths = []
    skipped_symlinks = 0
    for path in root.rglob("*"):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            skipped_symlinks += 1
            continue
        if path.is_file():
            paths.append(path)
            if len(paths) > max_files:
                raise IntakeError("file count exceeds hard inventory cap")
    paths.sort(key=lambda p: str(p.relative_to(root)).casefold())
    rows = []
    hashes = defaultdict(list)
    for path in paths:
        relative = str(path.relative_to(root))
        digest = _sha256(path)
        hashes[digest].append(relative)
        row = {"path": relative, "bytes": path.stat().st_size,
               "sha256": digest, "extension": path.suffix.lower(),
               "publication_status": "HOLD_UNREVIEWED",
               "private_review_hold": any(token in relative.upper()
                                          for token in PRIVATE_HINTS)}
        if path.suffix.lower() == ".zip":
            row["zip"] = _zip_metadata(path, max_zip_members)
        rows.append(row)
    archives = [row["zip"] for row in rows if "zip" in row]
    duplicate_groups = [group for group in hashes.values() if len(group) > 1]
    summary = {"schema": SCHEMA, "files": len(rows),
               "total_bytes": sum(row["bytes"] for row in rows),
               "extensions": dict(Counter(row["extension"] for row in rows)),
               "archives": len(archives),
               "archives_readable": sum(a["status"] == "METADATA_READABLE_UNTRUSTED"
                                        for a in archives),
               "archive_members": sum(a["members"] for a in archives),
               "unsafe_zip_paths": sum(a["unsafe_paths"] for a in archives),
               "encrypted_zip_members": sum(a["encrypted"] for a in archives),
               "zip_symlinks": sum(a["symlinks"] for a in archives),
               "suspicious_zip_ratios": sum(a["suspicious_ratios"] for a in archives),
               "unreadable_archives": sum(a["status"] == "UNREADABLE" for a in archives),
               "exact_duplicate_groups": len(duplicate_groups),
               "exact_duplicate_extras": sum(len(group) - 1 for group in duplicate_groups),
               "private_review_hold_files": sum(row["private_review_hold"] for row in rows),
               "skipped_symlinks": skipped_symlinks,
               "content_extracted": False, "files_published": False}
    return {"private_manifest": rows, "private_duplicate_groups": duplicate_groups,
            "summary": summary}

def write_records(out: Path, root: Path, result: dict) -> None:
    source = Path(root).resolve()
    destination = Path(out).resolve()
    if destination == source or source in destination.parents:
        raise IntakeError("output directory must be outside the source tree")
    destination.mkdir(parents=True, exist_ok=False)
    for name, records in (("private_manifest.json", result["private_manifest"]),
                          ("private_duplicate_groups.json", result["private_duplicate_groups"]),
                          ("summary.json", result["summary"])):
        with (destination / name).open("x", encoding="utf-8") as stream:
            json.dump(records, stream, ensure_ascii=False, indent=2, sort_keys=True)

def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only, local export inventory")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    result = scan_folder(opts.root)
    write_records(opts.output, opts.root, result)
    print(json.dumps(result["summary"], sort_keys=True))

if __name__ == "__main__":
    main()
