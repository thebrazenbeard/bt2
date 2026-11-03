# Read-only export intake (source candidate)

**Historical V1 note — superseded by
`source_recovery/EXPORT_INTAKE.md`:** Current `export_intake.py` defaults to
metadata-only and explicitly refuses native Windows/WSL scanning, byte opens, and private
manifest writes pending native no-reparse/ACL qualification. The older
Windows/Linux usage and eager hashing descriptions below are retained for
provenance only and must not be used as current instructions.

This tool builds a **local metadata inventory** of a user-selected folder. It is
intended for recovery triage, not for automatic ingestion or publication.

`source_recovery/export_intake.py` uses only Python's standard library.
It hashes every regular file with SHA-256, groups exact duplicate content, and
inspects ZIP central-directory metadata **without extracting or executing
archive members**. It reports ZIP traversal paths, Windows drive paths,
symlink entries, encrypted entries, extreme compression ratios, and archives
that cannot be read or exceed the member cap.

Archive names and their member names are conservatively screened for private
material. **Every item begins at `HOLD_UNREVIEWED` regardless of screening.**
A filename classifier can miss credentials or personal data inside an ordinary
document, and clean ZIP metadata does not make its payload trustworthy.

## Usage

From the repository root on an authorized Windows or Linux workstation:

```shell
python source_recovery/export_intake.py --root /path/to/exports
# Only after reviewing the destination's ACLs:
python source_recovery/export_intake.py --root /path/to/exports --output /private/outside-exports/intake-001 --write-private-manifest
python -m unittest discover -s source_recovery/tests -p test_export_intake.py -v
```

The output directory must be absent and must be outside the source folder.
Output files are `summary.json`, `private_manifest.json`, and
`private_duplicate_groups.json`. **Keep all three local and private.**
The manifest preserves filenames and checksums that may identify private work.
No GitHub API call, external service, archive extraction, deletion,
credential read, or code execution is performed by the scanner.

## Next-stage admission boundaries

For each recovered artifact, record a candidate owning repo, an exact archive
and member digest, source/rights status, data sensitivity, comparison against
current Git head, source review, executable tests, and independent hostile
review. Old instructions, local memories, conversation exports, and claimed
qualification results remain **historical evidence**, not current operating
authority. Do not publish unredacted manifests or copied code merely because
the source archive was accessible.

A later process may propose reviewed patches on isolated branches. This
scanner deliberately has no flag for publishing or launching recovered work.

## Evidence limits

Unit tests cover duplicate hashing, ZIP path traversal metadata, unreadable
archives, hard file/member caps, private-name detection within innocuously
named ZIPs, output isolation, and no content leakage into generated JSON.
They do not establish archive authenticity, safe ZIP decompression, semantic
data quality, licensing, live runtime state, or scanner safety under active
malicious filesystem races. Use isolated read access for untrusted sources.

**Confidentiality warning:** Default CLI output contains aggregate statistics
only. The private manifest is written only with `--write-private-manifest`
and `--output`. POSIX writing requires no-follow held directory descriptors, an
owner-controlled immediate parent, a new `0700` directory and `0600` files.
Windows and detected WSL remain refused. These checks do not qualify inherited
ACLs, same-UID adversaries, bind-mount aliases or concurrent directory moves.
Before opting in, verify the complete destination's access controls. Merely
using a local folder, especially under shared development roots, does not
guarantee privacy.
The writer validates all three JSON outputs against an aggregate 16 MiB byte
budget before creating a directory. Filesystem I/O errors after creation may
leave partial files within the private directory; no unsafe recursive cleanup
is attempted through a possibly replaced output pathname.
