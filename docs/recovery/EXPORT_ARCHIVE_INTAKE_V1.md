# Read-only export intake (source candidate)

This tool builds a **local metadata inventory** of a user-selected folder. It is
intended for recovery triage, not for automatic ingestion or publication.

`tools/qualification/export_intake.py` uses only Python's standard library.
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
python tools/qualification/export_intake.py --root /path/to/exports --output /private/outside-exports/intake-001
python -m unittest discover -s tests -p test_export_intake.py -v
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
