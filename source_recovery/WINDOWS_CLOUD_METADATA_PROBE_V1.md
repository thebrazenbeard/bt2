# Windows Cloud Files metadata-only recovery probe

**Status:** source candidate; read-only diagnostic, not archive admission or
proof that a cloud-backed file is fully available offline.

The local export intake remains fail-closed on cloud/reparse folders. A
Windows-host investigation showed why a naïve exception for Cloud Files would
be unsafe: Windows PowerShell reported a cloud export as a reparse point, while
a Python application using `FindFirstFileW` saw ordinary-looking attributes.
Windows Cloud Files can hide their reparse information from applications.

`source_recovery.windows_cloud_probe.probe_placeholder(path)` requests
Windows metadata, using `FindFirstFileW`,
`CfGetPlaceholderStateFromAttributeTag`, and, importantly,
`CfGetSyncRootInfoByPath`. The last query detects cloud sync-root membership
even if normal file-attribute reporting suppresses the reparse point.
Query failure remains UNKNOWN/HOLD, never an ordinary-file assertion.
Wildcard search paths containing `*` or `?`, empty paths, byte-string paths,
and paths with embedded NUL characters fail closed before any native query.
The validated `os.fspath` result must be an exact built-in `str`: hostile
string subclasses can override membership checks and conceal wildcard syntax.
Ordinary exceptions raised by a caller-controlled `__fspath__` implementation
also become a structured metadata-query HOLD, without swallowing process
interrupts such as `KeyboardInterrupt` or `SystemExit`.
This intentionally also rejects Windows extended-length paths with a `\\?\`
prefix until that namespace is explicitly validated. Native
`ctypes.ArgumentError` marshalling failures also return metadata-query HOLD.
No directory-wide wildcard enumeration is authorized by this probe.

Unknown or future `CF_PLACEHOLDER_STATE` bits are explicitly
`UNKNOWN_STATE_BITS_HOLD` rather than silently classified as a known synced
placeholder. Microsoft's currently documented mask is `0x3F`.

All returned records omit the supplied path and **always** carry
`byte_read_authorized=false`. Offline, recall-on-read, partial, unknown
reparse, inconsistent, and unverifiable sync-root states remain HOLD. Even an
in-sync placeholder or a normal-looking file receives no permission to
open, hash, decompress, copy, download, train, or publish bytes.

## Reproduction and evidence

- Exact BT2 source base `9354b9868d320da71cf2ab0382114f599687b3fb`.
- Windows Python 3.12: 16 existing export-intake tests plus eight new CFAPI
  tests and four existing adjudication-contract tests **28/28 passed**.
- TDD: the simple classifier first failed a synchronized-placeholder test;
  fixing the classifier exposed a Windows real-system false regular-file
  classification. A new regression reproduced the false-regular case, then
  using sync-root lookup closed it.
- Host metadata probe on a synthetic file marked Offline:
  `OFFLINE_OR_RECALL_HOLD`; on a Windows cloud-backed export:
  `CLOUD_SYNC_ROOT_HOLD`. Both results explicitly deny byte-reading.
- No byte stream was opened from the cloud-backed export. No output contains
  its pathname, payload, archive members, checksums, or personal content.
- Local Linux Python 3.12 source-only follow-up (this patch): synthetic
  marshalling-error and wildcard guards reproduced failing behavior before
  the fix, then all 32 intake/adjudication/cloud tests passed. No Windows host
  runtime check is claimed for these follow-up changes.
- Subsequent source-only hostile-string regression: a `str` subclass whose
  membership check hides `*` reached the native-query seam before hardening;
  exact-string validation now blocks it. All 37 source-recovery tests passed
  on Linux/Python 3.12. This is not a Windows runtime or hydration witness.

## Hard limitations

The code makes no direct payload-read call, but a metadata API can have
provider-dependent side effects; this source-only patch cannot demonstrate
that no Cloud Files provider hydrated bytes in every host scenario. In
particular, it does not establish a Windows-host non-hydration guarantee,
and no live cloud-root test was performed for this patch.

This is not a complete local-byte-range check. A cloud placeholder can be
partially or fully present on disk; even an in-sync state is not proof of
local completeness, a trusted digest, rights, or permission to consume it.
A separate safe-range protocol and adversarial host review are needed before
changing the parent `export_intake` cloud/reparse HOLD. This probe is not
automatically invoked by the export scanner or any protected runtime.

Reference:
- https://learn.microsoft.com/en-us/windows/win32/api/cfapi/nf-cfapi-cfgetplaceholderstatefromattributetag
- https://learn.microsoft.com/en-us/windows/win32/api/cfapi/nf-cfapi-cfgetsyncrootinfobypath
- https://learn.microsoft.com/en-us/windows/win32/api/cfapi/ns-cfapi-cf_placeholder_standard_info
