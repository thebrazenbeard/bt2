# Local VERA export recovery: metadata-only intake

This tool is a **reusable, read-only preflight** for operator-owned export
directories. It does not migrate project instructions, import memory, run
archive code, assign an authoritative repo, grant rights, or make public
anything that it scans.

**Platform gate:** The current source intentionally refuses *all* native
Windows **and WSL** scans, including metadata-only enumeration, direct byte
opens, and private manifest writes. Windows path traversal may cross an unverified reparse race;
the installed interpreter's directory DACL behavior has not been verified.
This is a source-only safety hold, not proof that any Lappy directory is unsafe.
WSL also exposes Windows-mounted DrvFs paths without usable cloud/recall
attributes; this conservative gate blocks even WSL's ordinary Linux files.
No Windows/WSL/OneDrive inspection should be attempted until a native
no-reparse implementation and destination ACL custody are independently
qualified. The examples below are for trusted, isolated POSIX directories.

```shell
python -m source_recovery.export_intake --root ./synthetic-exports
# Only for a reviewed owner-restricted output location:
python -m source_recovery.export_intake --root ./synthetic-exports \
  --output ./private-review/scan-unique-id --write-private-manifest
python -m unittest discover -s source_recovery/tests -p 'test_*intake*.py' -v
```

Supply an **existing source directory** and a **new, separate output directory**
outside the source. The tool creates three local JSON files:
`private_manifest.json` (relative filenames, byte sizes and optional SHA-256);
`private_duplicate_groups.json` (matching full-file digests);
and `summary.json` (aggregate-only statistics). All items default to
`HOLD_UNREVIEWED`, regardless of filenames or claimed archive validation.
No manifest is uploaded, sent to a network service or committed by this tool.
Keep the private files out of public GitHub.

ZIP files are inspected **only through central-directory metadata**, with
bounded member counts and checks for path traversal, encryption, symlink
metadata and extreme compression ratios. The tool does **not** extract,
unpickle, execute, repair, validate signatures, or load embedded databases.
A readable ZIP is not a verified, trustworthy or publishable artifact.
Likewise, identical SHA-256 values identify byte-identical files, not safe
permission to delete backups. Name-based private flags are only heuristics:
**unflagged files still require human privacy, license, ownership and security
review before publication**.

## Required downstream recovery gates

1. Preserve source paths and full-file hashes privately; identify duplicate
   copies without erasing originals.
2. Inspect selected archives in an isolated, read-only staging context; reject
   unsafe paths, untrusted scripts, secrets and executable payloads.
3. Determine the current owner from **fresh exact Git source and repo-local
   authority**, not historical README claims in an archive.
4. Classify material as historical evidence, original source candidate,
   dataset, private memory, project instructions or visual reference.
5. For public GitHub, publish only reviewed independently lawful, redacted,
   source-integrated code/docs/tests on an isolated branch. Never upload raw
   conversations, private memory SQLite files, credentials, personal images
   or model weights to a public repo.
6. Test any implemented behavior against current code, run hosted checks,
   solicit hostile review, and read back the exact merged source if authorized.

### Evidence classes

- **Inventory:** file and ZIP metadata plus local SHA-256.
- **Archive inspection:** bounded content review, still untrusted source.
- **Source comparison:** historical artifact versus exact Git head.
- **Test:** executed software contract, not installed runtime proof.
- **Real-system probe:** installed host behavior under its own permissions.

A historical export never establishes current Lantern state, a working
installation, identity continuity, or permission for model training.
The retired WoWSQL backend is not a valid currentness provider; source-only
SQL Connectome V4 is not an installed runtime.

**Confidentiality warning:** Default CLI output contains aggregate statistics
only. The private manifest is written only with `--write-private-manifest`
and `--output`. On supported POSIX hosts the writer holds no-follow directory
descriptors, requires an owner-controlled immediate parent without group/other
write bits, creates a fresh `0700` directory, and writes `0600` files relative
to that held descriptor. It refuses unqualified Windows/WSL and unsupported
POSIX descriptor operations. This is not proof against same-UID actors,
bind-mount aliases, wider ancestor ACLs or concurrent directory mutation;
verify destination custody before opting in. A local folder, especially under
shared development roots, does not guarantee privacy.
All three JSON payloads must serialize within the aggregate 16 MiB and chunk
budgets *before* the output directory is created. A later I/O failure such as
disk-full can still leave partial artifacts in the owner-only directory; they
are deliberately not path-deleted after an ambiguous rename/symlink race.
