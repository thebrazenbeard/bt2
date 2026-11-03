# Export intake bounded defaults (R203 source-only)

`source_recovery/export_intake.py` is a local **metadata-only by default**
inventory. It neither extracts ZIP members nor admits data for training or
publication. The original export source remains private and historical.

**Current qualification hold:** The native Windows and WSL scanner and
private-manifest writer now fail closed before path traversal or output
creation. The WSL hold includes otherwise-local Linux paths because DrvFs
Windows mounts cannot be distinguished safely with this scanner. Earlier R203
attribute/size checks were not sufficient to defeat Windows ancestor-reparse
races, and the actual destination DACL remains unverified. The commands below
are for an isolated, authorized POSIX test directory only; do not run this
intake on Lappy or OneDrive until a separately reviewed native Windows
scanner and private-output custody are qualified.

```console
python -m source_recovery.export_intake --root ./synthetic-exports
```

The default command reports aggregate counts only. Python callers can inspect
the returned `private_manifest` in a trusted local process; it is **not safe
to publish**, even though individual file contents are absent. Paths, sizes,
hashes, names, extensions, and private metadata can identify personal data.
On the supported POSIX path, to persist a private manifest the operator must explicitly pass both
`--write-private-manifest` and `--output` to a new destination outside the
source. Directory creation mode is not a substitute for readback of actual
effective host access controls.

Hashing and ZIP central-directory inspection are now separate explicit opt-ins:

```console
python -m source_recovery.export_intake --root ./synthetic-exports \
  --hash-local --inspect-zip-local --max-files 100 \
  --max-read-bytes 1048576 --max-total-read-bytes 4194304 \
  --max-zip-members 2048
```

`--max-files` caps the **combined directory and file entries traversed**, not
just returned files. Byte-read budgets account separately for hashing and ZIP
inspection. ZIP inputs have a stricter 2 MiB ceiling; no member data is
extracted. Offline, reparse, and recall-on-access entries are rejected or
skipped before deliberate file reads. Unknown Windows cloud attributes are a
hold, and races with malicious filesystem changes require OS isolation.

**Compatibility note:** Before R203, direct `scan_folder(root)` eagerly hashed
every file and inspected ZIPs even without user opt-in. New calls must pass
`hash_local=True` or `inspect_zip_local=True` explicitly to request those
behaviors. Do not use the pre-R203 version on a live OneDrive Files On-Demand
directory: it can hydrate files and spend substantial disk/network resources.

**R208 POSIX confinement extension (source-only):** On POSIX systems that
support descriptor-relative opens, the scanner now holds the source directory
descriptor and reopens each child with `O_DIRECTORY | O_NOFOLLOW` relative to
that anchor. The initial root is itself opened component-by-component from
the filesystem anchor, rejecting symlinks in any supplied ancestor and
ambiguous `..` components. It checks directory and file identities and rejects changed
entries. Synthetic tests reproduce both a queued-directory symlink swap and a
parent swap immediately before hashing, plus a symlinked root ancestor;
no outside-root names or bytes are
accepted after the change. This is not a stable snapshot or a guarantee
against in-place edits, unexpected mounts, or adversarial filesystem drivers.

**Windows/WSL HOLD:** Windows currently retains the non-atomic path-based
metadata traversal; Windows-native no-reparse directory handles and actual
OneDrive Files On-Demand qualification are required before scanning an
adversarial/concurrently mutable export directory. Under WSL, Linux `stat`
does not independently establish Windows cloud hydration state. Never use
this source-only POSIX result to justify optional byte reads on OneDrive.

The new defaults are source-level safety properties, **not** evidence of a
qualified Lappy Windows/OneDrive runtime, corpus rights, current installed
ChatGPT Project package, protected evaluator, or GPU lease.
