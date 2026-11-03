"""Bounded, metadata-only-by-default local export inventory.

Never extracts or executes ZIP members. All records remain local unless an
operator explicitly reviews and separately publishes downstream work.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

SCHEMA = "BT2_EXPORT_READONLY_INVENTORY_V1"
PRIVATE_HINTS = ("CHAT", "PERSONAL", "PRIVATE", "UNSANITIZED", "KEY",
                 "SECRET", "PASSWORD", "TOKEN", "IDENTITY", "MEMORY")
_CLOUD_FLAGS = (0x1000 | 0x400 | 0x00040000 | 0x00400000)
_ZIP_INPUT_CAP = 2 * 1024 * 1024
_ZIP_UNCOMPRESSED_CAP = 128 * 1024 * 1024
_ZIP_RATIO_CAP = 100

class IntakeError(ValueError):
    """Unsafe input location or exceeded read-only inventory cap."""

def _require_qualified_host() -> None:
    # Python path-based enumeration/open cannot pin every ancestor against a
    # Windows reparse-point swap, and creation modes do not attest the actual
    # host DACL. A native, independently qualified Windows implementation is
    # required before even metadata-only traversal or private output writes.
    if os.name == "nt":
        raise IntakeError("Windows intake unqualified: refuse traversal and private writes")
    # WSL is POSIX at Python's os.name boundary but can expose OneDrive paths
    # through DrvFs (/mnt/c, /mnt/d), where cloud/recall attributes are not
    # represented by POSIX st_file_attributes. Refuse the whole WSL runtime
    # rather than guessing which mounted paths are safely local.
    if os.environ.get("WSL_INTEROP") or os.environ.get("WSL_DISTRO_NAME"):
        raise IntakeError("WSL intake unqualified: refuse traversal and private writes")
    uname = getattr(os, "uname", None)
    if callable(uname):
        try:
            release = uname().release.casefold()
        except OSError as exc:
            raise IntakeError("host qualification unavailable") from exc
        if "microsoft" in release or "wsl" in release:
            raise IntakeError("WSL intake unqualified: refuse traversal and private writes")

def _cloud_or_reparse(metadata: os.stat_result) -> bool:
    attributes = getattr(metadata, "st_file_attributes", None)
    # Windows attribute absence is not evidence that a Files On-Demand path
    # is hydrated. Refuse byte reads in that uncertain state.
    return ((attributes is None and os.name == "nt")
            or bool((attributes or 0) & _CLOUD_FLAGS))

def _open_directory_beneath(root_fd: int, components: tuple[str, ...]) -> int:
    """Reopen only directories beneath a held POSIX root without link following.

    A path-based lstat/resolve check followed by scandir(path) is racy: its
    intermediate directory can become a symlink after inspection. The return
    value is an owned file descriptor and must be closed by the caller.
    """
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.dup(root_fd)
    try:
        for component in components:
            if not component or component in (".", "..") or "/" in component:
                raise IntakeError("unsafe relative directory component")
            next_fd = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def _open_posix_root_without_links(path: Path) -> int:
    """Anchor every root-path component without following ancestor symlinks.

    Opening ``alias/child`` with O_NOFOLLOW only protects ``child``. Walk from
    the filesystem anchor through held directory fds to reject ``alias`` too.
    """
    if ".." in path.parts:
        raise IntakeError("parent-relative source root is ambiguous")
    absolute = Path(os.path.abspath(path))
    anchor_fd = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return _open_directory_beneath(anchor_fd, absolute.parts[1:])
    finally:
        os.close(anchor_fd)


def _open_local(path: Path, expected_size: int, limit: int, *,
                root_fd: int | None = None,
                relative_parts: tuple[str, ...] | None = None,
                expected_identity: tuple[int, int] | None = None):
    _require_qualified_host()
    if expected_size > limit:
        raise IntakeError("bounded local read limit exceeded")
    if not getattr(os, "O_NOFOLLOW", 0):
        raise IntakeError("no safe final-component no-follow open available")
    # If a regular file is replaced with a FIFO after stat, the open must
    # return without blocking before the subsequent fstat can reject it.
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) | os.O_NOFOLLOW
             | getattr(os, "O_NONBLOCK", 0))
    if root_fd is not None:
        if not relative_parts:
            raise IntakeError("relative file components required")
        parent_fd = _open_directory_beneath(root_fd, relative_parts[:-1])
        try:
            fd = os.open(relative_parts[-1], flags, dir_fd=parent_fd)
        finally:
            os.close(parent_fd)
    else:
        fd = os.open(path, flags)
    try:
        metadata = os.fstat(fd)
        if (not stat.S_ISREG(metadata.st_mode) or _cloud_or_reparse(metadata)
                or metadata.st_size != expected_size or metadata.st_size > limit
                or (expected_identity is not None
                    and (metadata.st_dev, metadata.st_ino) != expected_identity)):
            raise IntakeError("local file changed or is not safely readable")
        return os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise

def _sha256(path: Path, *, expected_size: int, max_bytes: int,
            root_fd: int | None = None,
            relative_parts: tuple[str, ...] | None = None,
            expected_identity: tuple[int, int] | None = None) -> str:
    digest = hashlib.sha256()
    counted = 0
    with _open_local(path, expected_size, max_bytes, root_fd=root_fd,
                     relative_parts=relative_parts,
                     expected_identity=expected_identity) as stream:
        for chunk in iter(lambda: stream.read(min(64 * 1024, max_bytes + 1 - counted)), b""):
            counted += len(chunk)
            if counted > max_bytes:
                raise IntakeError("local hash byte limit exceeded")
            digest.update(chunk)
        if counted != expected_size or os.fstat(stream.fileno()).st_size != expected_size:
            raise IntakeError("local file changed during hash")
    return digest.hexdigest()

def _zip_metadata(path: Path, max_members: int, expected_size: int, *,
                  root_fd: int | None = None,
                  relative_parts: tuple[str, ...] | None = None,
                  expected_identity: tuple[int, int] | None = None) -> dict:
    result = {"status": "UNREADABLE", "members": 0, "unsafe_paths": 0,
              "encrypted": 0, "symlinks": 0, "suspicious_ratios": 0,
              "sensitive_member_names": 0}
    try:
        if expected_size > _ZIP_INPUT_CAP:
            result["status"] = "ZIP_INPUT_LIMIT_EXCEEDED"
            return result
        with _open_local(path, expected_size, _ZIP_INPUT_CAP, root_fd=root_fd,
                         relative_parts=relative_parts,
                         expected_identity=expected_identity) as stream:
            with zipfile.ZipFile(stream) as archive:
                entries = archive.infolist()
                result["members"] = len(entries)
                if len(entries) > max_members:
                    result["status"] = "MEMBER_LIMIT_EXCEEDED"
                    return result
                uncompressed = 0
                for member in entries:
                    name = member.filename.replace("\\", "/")
                    parts = PurePosixPath(name).parts
                    unsafe = (name.startswith("/") or bool(re.match(r"^[A-Za-z]:", name))
                              or ".." in parts or "\x00" in name)
                    result["unsafe_paths"] += bool(unsafe)
                    result["sensitive_member_names"] += int(any(
                        hint in name.upper() for hint in PRIVATE_HINTS))
                    result["encrypted"] += bool(member.flag_bits & 1)
                    result["symlinks"] += stat.S_ISLNK(member.external_attr >> 16)
                    uncompressed += member.file_size
                    result["suspicious_ratios"] += bool(
                        member.file_size > _ZIP_RATIO_CAP * max(1, member.compress_size)
                    )
                result["status"] = ("REJECTED_METADATA" if uncompressed > _ZIP_UNCOMPRESSED_CAP
                                   or result["unsafe_paths"] or result["encrypted"]
                                   or result["symlinks"] or result["suspicious_ratios"]
                                   else "METADATA_READABLE_UNTRUSTED")
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, IntakeError):
        pass
    return result

def scan_folder(root: Path, *, max_files: int = 500,
                max_zip_members: int = 2048, max_read_bytes: int = 1024 * 1024,
                max_total_read_bytes: int = 16 * 1024 * 1024,
                hash_local: bool = False, inspect_zip_local: bool = False) -> dict:
    """Enumerate local metadata; bytes require explicit bounded opt-in.

    ``max_files`` is a global entry cap (files AND directories). Results are
    private Python data; only aggregate summary is printed by the CLI.
    """
    _require_qualified_host()
    root = Path(root)
    if (max_files < 1 or max_zip_members < 1 or max_read_bytes < 1
            or max_total_read_bytes < 1):
        raise IntakeError("positive inventory caps required")
    secure_posix = os.name == "posix"
    if secure_posix and not (getattr(os, "O_DIRECTORY", 0)
                             and getattr(os, "O_NOFOLLOW", 0)
                             and os.open in os.supports_dir_fd):
        raise IntakeError("descriptor-relative no-follow traversal unavailable")
    root_fd = None
    try:
        if secure_posix:
            root_fd = _open_posix_root_without_links(root)
            root_meta = os.fstat(root_fd)
        else:
            root_meta = root.lstat()
        if not stat.S_ISDIR(root_meta.st_mode) or _cloud_or_reparse(root_meta):
            raise IntakeError("input must be a real non-cloud directory")
    except OSError as exc:
        if root_fd is not None:
            os.close(root_fd)
        raise IntakeError("input location unavailable") from exc
    except BaseException:
        if root_fd is not None:
            os.close(root_fd)
        raise
    # The POSIX root fd, not this presentation path, is the trust anchor.
    root = root.absolute() if secure_posix else root.resolve()
    queue = [(((), (root_meta.st_dev, root_meta.st_ino)) if secure_posix else root)]
    paths = []  # (relative, display_path, size, relative_parts, (device, inode))
    skipped_symlinks = 0
    skipped_cloud = 0
    scanned_entries = 0
    try:
        while queue:
            folder = queue.pop(0)
            folder_fd = None
            if secure_posix:
                components, identity = folder
                try:
                    folder_fd = _open_directory_beneath(root_fd, components)
                    folder_meta = os.fstat(folder_fd)
                    if ((folder_meta.st_dev, folder_meta.st_ino) != identity
                            or _cloud_or_reparse(folder_meta)):
                        os.close(folder_fd)
                        folder_fd = None
                        raise IntakeError("queued directory changed during inspection")
                except OSError as exc:
                    if folder_fd is not None:
                        os.close(folder_fd)
                    raise IntakeError("queued directory is no longer safely reachable") from exc
            try:
                with os.scandir(folder_fd if secure_posix else folder) as listing:
                    entries = []
                    for entry in listing:
                        entries.append(entry)
                        if scanned_entries + len(entries) > max_files:
                            raise IntakeError("entry count exceeds hard inventory cap")
                    entries.sort(key=lambda e: (e.name.casefold(), e.name))
                scanned_entries += len(entries)
                for entry in entries:
                    try:
                        meta = (os.stat(entry.name, dir_fd=folder_fd, follow_symlinks=False)
                                if secure_posix else entry.stat(follow_symlinks=False))
                    except OSError as exc:
                        raise IntakeError("unreadable entry metadata") from exc
                    if secure_posix:
                        relative_parts = components + (entry.name,)
                        path = root.joinpath(*relative_parts)
                    else:
                        path = Path(entry.path)
                        relative_parts = None
                    if _cloud_or_reparse(meta):
                        skipped_cloud += 1
                    elif stat.S_ISDIR(meta.st_mode):
                        queue.append((relative_parts, (meta.st_dev, meta.st_ino))
                                     if secure_posix else path)
                    elif stat.S_ISREG(meta.st_mode):
                        paths.append((str(path.relative_to(root)), path, meta.st_size,
                                      relative_parts, (meta.st_dev, meta.st_ino)))
                    else:
                        skipped_symlinks += 1
            except OSError as exc:
                raise IntakeError("unsafe directory inspection") from exc
            finally:
                if folder_fd is not None:
                    os.close(folder_fd)
        paths.sort(key=lambda pair: pair[0].casefold())
        rows = []
        hashes = defaultdict(list)
        byte_budget_used = 0
        for relative, path, expected_size, relative_parts, identity in paths:
            row = {"path": relative, "bytes": expected_size,
                   "sha256": None, "extension": path.suffix.lower(),
                   "publication_status": "HOLD_UNREVIEWED",
                   "read_status": "METADATA_ONLY",
                   "private_review_hold": any(token in relative.upper()
                                              for token in PRIVATE_HINTS)}
            if hash_local or (inspect_zip_local and row["extension"] == ".zip"):
                # Cumulative budget includes every separately requested byte read.
                cap = min(max_read_bytes, _ZIP_INPUT_CAP if row["extension"] == ".zip"
                          and inspect_zip_local else max_read_bytes)
                read_count = int(hash_local) + int(inspect_zip_local and row["extension"] == ".zip")
                planned_bytes = expected_size * read_count
                if expected_size > cap or byte_budget_used + planned_bytes > max_total_read_bytes:
                    row["read_status"] = "SKIPPED_READ_SIZE_LIMIT"
                else:
                    byte_budget_used += planned_bytes
                    try:
                        if hash_local:
                            digest = _sha256(path, expected_size=expected_size, max_bytes=cap,
                                             root_fd=root_fd, relative_parts=relative_parts,
                                             expected_identity=identity if secure_posix else None)
                            row["sha256"] = digest
                            hashes[digest].append(relative)
                        if inspect_zip_local and row["extension"] == ".zip":
                            row["zip"] = _zip_metadata(
                                path, max_zip_members, expected_size, root_fd=root_fd,
                                relative_parts=relative_parts,
                                expected_identity=identity if secure_posix else None)
                            row["private_review_hold"] = bool(
                                row["private_review_hold"] or
                                row["zip"]["sensitive_member_names"] or
                                row["zip"]["status"] != "METADATA_READABLE_UNTRUSTED")
                        row["read_status"] = "BOUNDED_LOCAL_BYTES"
                    except (OSError, IntakeError):
                        row["read_status"] = "SKIPPED_CHANGED_OR_UNSAFE_FILE"
            rows.append(row)
    finally:
        if root_fd is not None:
            os.close(root_fd)
    archives = [row["zip"] for row in rows if "zip" in row]
    duplicate_groups = [group for group in hashes.values() if len(group) > 1]
    summary = {"schema": SCHEMA, "files": len(rows),
               "total_bytes": sum(row["bytes"] for row in rows),
               "extensions": dict(Counter(row["extension"] for row in rows)),
               "archives": sum(row["extension"] == ".zip" for row in rows),
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
               "skipped_cloud_or_reparse": skipped_cloud,
               "scanned_entries": scanned_entries,
               "read_bytes_budgeted": byte_budget_used,
               "byte_reads_opted_in": bool(hash_local or inspect_zip_local),
               "content_extracted": False, "files_published": False}
    return {"private_manifest": rows, "private_duplicate_groups": duplicate_groups,
            "summary": summary}

def write_records(out: Path, root: Path, result: dict) -> None:
    _require_qualified_host()
    source = Path(root).resolve()
    destination = Path(out).resolve()
    if destination == source or source in destination.parents:
        raise IntakeError("output directory must be outside the source tree")
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    for name, records in (("private_manifest.json", result["private_manifest"]),
                          ("private_duplicate_groups.json", result["private_duplicate_groups"]),
                          ("summary.json", result["summary"])):
        descriptor = os.open(destination / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(records, stream, ensure_ascii=False, indent=2, sort_keys=True)

def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only, local export inventory")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        help="new private output directory outside the source")
    parser.add_argument("--write-private-manifest", action="store_true",
                        help="explicitly persist filename-level private metadata")
    parser.add_argument("--hash-local", action="store_true",
                        help="opt in to capped hashing of already-local files")
    parser.add_argument("--inspect-zip-local", action="store_true",
                        help="opt in to capped ZIP central-directory reads")
    parser.add_argument("--max-files", type=int, default=500,
                        help="hard cap on total traversed entries (files and dirs)")
    parser.add_argument("--max-read-bytes", type=int, default=1024 * 1024)
    parser.add_argument("--max-total-read-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--max-zip-members", type=int, default=2048)
    opts = parser.parse_args()
    if opts.output is not None and not opts.write_private_manifest:
        parser.error("--output requires --write-private-manifest; review output ACLs first")
    if opts.write_private_manifest and opts.output is None:
        parser.error("--write-private-manifest requires --output")
    try:
        result = scan_folder(opts.root, max_files=opts.max_files,
                             max_zip_members=opts.max_zip_members,
                             max_read_bytes=opts.max_read_bytes,
                             max_total_read_bytes=opts.max_total_read_bytes,
                             hash_local=opts.hash_local,
                             inspect_zip_local=opts.inspect_zip_local)
    except IntakeError:
        parser.error("inventory rejected unsafe or over-limit source")
    if opts.output is not None:
        write_records(opts.output, opts.root, result)
    print(json.dumps(result["summary"], sort_keys=True))

if __name__ == "__main__":
    main()
