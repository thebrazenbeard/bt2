"""Windows Cloud Files metadata diagnostic; does not directly read payloads.

This diagnostic only helps route files for later authorized review. A successful
state classification is NOT proof of complete on-disk byte ranges or permission
to read, copy, hydrate, train, publish, or ingest an export.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
from pathlib import Path

_REPARSE = 0x400
_OFFLINE_OR_RECALL = 0x1000 | 0x40000 | 0x400000
_CF_PLACEHOLDER = 0x01
_CF_IN_SYNC = 0x08
_CF_PARTIAL = 0x10
_CF_PARTIALLY_ON_DISK = 0x20
_CF_INVALID = 0xFFFFFFFF
_CF_KNOWN_STATE_MASK = 0x3F  # All currently documented CF_PLACEHOLDER_STATE bits
_DOS_DEVICE_NAMES = frozenset(
    ("CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$")
) | frozenset(
    f"{prefix}{number}" for prefix in ("COM", "LPT")
    for number in "123456789¹²³"
)


def classify_placeholder(attributes: int, state: int) -> dict[str, object]:
    """Classify CFAPI state without ever admitting a file to byte reading."""
    if type(attributes) is not int or type(state) is not int:
        raise TypeError("attributes and state must be exact integers")
    if not (0 <= attributes <= 0xFFFFFFFF and 0 <= state <= 0xFFFFFFFF):
        raise ValueError("invalid Windows metadata range")
    if state == _CF_INVALID:
        status = "INVALID_STATE_HOLD"
    elif state & ~_CF_KNOWN_STATE_MASK:
        status = "UNKNOWN_STATE_BITS_HOLD"
    elif attributes & _OFFLINE_OR_RECALL:
        status = "OFFLINE_OR_RECALL_HOLD"
    elif state & (_CF_PARTIAL | _CF_PARTIALLY_ON_DISK):
        status = "PARTIAL_PLACEHOLDER_HOLD"
    elif attributes & _REPARSE:
        if not state & _CF_PLACEHOLDER:
            status = "UNKNOWN_REPARSE_HOLD"
        elif state & _CF_IN_SYNC:
            status = "CLOUD_PLACEHOLDER_METADATA_ONLY"
        else:
            status = "UNSYNCED_PLACEHOLDER_HOLD"
    elif state:
        status = "INCONSISTENT_METADATA_HOLD"
    else:
        status = "REGULAR_FILE_METADATA_ONLY"
    return {"status": status, "byte_read_authorized": False}


class _FindDataW(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", wintypes.FILETIME),
        ("ftLastAccessTime", wintypes.FILETIME),
        ("ftLastWriteTime", wintypes.FILETIME),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("dwReserved0", wintypes.DWORD),
        ("dwReserved1", wintypes.DWORD),
        ("cFileName", wintypes.WCHAR * 260),
        ("cAlternateFileName", wintypes.WCHAR * 14),
        ("dwFileType", wintypes.DWORD),
        ("dwCreatorType", wintypes.DWORD),
        ("wFinderFlags", wintypes.WORD),
    ]


def _literal_query_path(path: str | Path) -> str:
    """Reject Win32 search patterns before FindFirstFileW can enumerate them."""
    try:
        # PathLike.__fspath__ is caller-controlled. Only normalize exceptions
        # at this untrusted boundary; do not mask bugs in native-query logic.
        literal = os.fspath(path)
    except Exception as exc:
        raise TypeError("Windows metadata path coercion failed") from exc
    # A str subclass may override __contains__ to conceal a Win32 wildcard.
    # Accept only built-in strings returned by os.fspath before inspecting it.
    if type(literal) is not str:
        raise TypeError("Windows metadata path must be text")
    if not literal or any(char in literal for char in ("*", "?", "\x00")):
        raise ValueError("Windows metadata path must be a nonempty literal")
    normalized = literal.replace("/", "\\")
    # UNC and device paths can trigger network, pipe or device I/O even when
    # the caller only intended a local metadata query.
    if normalized.startswith("\\\\"):
        raise ValueError("Windows metadata path must not be UNC or device")
    if (len(normalized) < 3 or normalized[0] not in
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            or normalized[1:3] != ":\\"):
        raise ValueError("Windows metadata path requires absolute drive root")
    segments = normalized[3:].split("\\")
    if ":" in normalized[3:] or any(part in (".", "..") for part in segments):
        raise ValueError("Windows metadata path contains ambiguous segments")
    if any(not part or part.endswith((".", " ")) for part in segments):
        raise ValueError("Windows metadata path has ambiguous components")
    if any(part.partition(".")[0].upper() in _DOS_DEVICE_NAMES for part in segments):
        raise ValueError("Windows metadata path contains reserved DOS device")
    return literal


def _drive_type(root: str) -> int:
    """Ask Windows for root-drive type before querying a file path."""
    if os.name != "nt":
        raise OSError("Windows-only drive type probe")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    query = kernel.GetDriveTypeW
    query.argtypes = [wintypes.LPCWSTR]
    query.restype = wintypes.UINT
    return int(query(root))


def _attributes_and_tag(path: str | Path) -> tuple[int, int]:
    literal = _literal_query_path(path)
    if os.name != "nt":
        raise OSError("Windows-only metadata probe")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    first = kernel.FindFirstFileW
    first.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(_FindDataW)]
    first.restype = ctypes.c_void_p
    close = kernel.FindClose
    close.argtypes = [ctypes.c_void_p]
    close.restype = wintypes.BOOL
    data = _FindDataW()
    handle = first(literal, ctypes.byref(data))
    if handle is None or handle == ctypes.c_void_p(-1).value:
        raise OSError("Windows attribute/tag query failed")
    try:
        attributes = int(data.dwFileAttributes)
        tag = int(data.dwReserved0) if attributes & _REPARSE else 0
        return attributes, tag
    finally:
        close(handle)


def _state_from_attributes_tag(attributes: int, reparse_tag: int) -> int:
    if os.name != "nt":
        raise OSError("Windows-only CFAPI probe")
    cloud = ctypes.WinDLL("CldApi.dll", use_last_error=True)
    state = cloud.CfGetPlaceholderStateFromAttributeTag
    state.argtypes = [wintypes.DWORD, wintypes.DWORD]
    state.restype = wintypes.DWORD
    return int(state(attributes, reparse_tag))


def _is_cloud_sync_root(path: str | Path) -> bool | None:
    """CFAPI checks sync-root membership even when normal Win32 hides reparse tags.

    Failure is *unknown*, never proof of an ordinary file. No file handle or
    payload read is performed.
    """
    if os.name != "nt":
        raise OSError("Windows-only CFAPI sync-root probe")
    cloud = ctypes.WinDLL("CldApi.dll", use_last_error=True)
    call = cloud.CfGetSyncRootInfoByPath
    call.argtypes = [
        wintypes.LPCWSTR, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    call.restype = wintypes.LONG
    buffer = ctypes.create_string_buffer(1024)
    returned = wintypes.DWORD()
    status = call(os.fspath(Path(path).absolute()), 0, buffer, len(buffer),
                  ctypes.byref(returned))
    return True if status == 0 else None


def probe_placeholder(path: str | Path) -> dict[str, object]:
    """Metadata-only and path-redacted; all read/publish authority stays HOLD."""
    try:
        literal = _literal_query_path(path)
        root = literal[:3].replace("/", "\\")
        if _drive_type(root) != 3:
            return {"status": "REMOTE_OR_NONFIXED_VOLUME_HOLD",
                    "byte_read_authorized": False}
        attributes, tag = _attributes_and_tag(literal)
        state = _state_from_attributes_tag(attributes, tag)
        result = classify_placeholder(attributes, state)
        if result["status"] == "OFFLINE_OR_RECALL_HOLD":
            return result
        root_state = _is_cloud_sync_root(literal)
        if root_state is True:
            return {"status": "CLOUD_SYNC_ROOT_HOLD", "byte_read_authorized": False}
        if root_state is None and result["status"] in (
                "REGULAR_FILE_METADATA_ONLY", "CLOUD_PLACEHOLDER_METADATA_ONLY"):
            return {"status": "SYNC_ROOT_UNVERIFIED_HOLD", "byte_read_authorized": False}
        return result
    except (OSError, AttributeError, ValueError, TypeError,
            OverflowError, ctypes.ArgumentError):
        return {"status": "METADATA_QUERY_FAILED_HOLD", "byte_read_authorized": False}
