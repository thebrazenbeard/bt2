# Historical export adjudication (source-only)

`historical_adjudication_v1.schema.json` is a **private review template** for
deciding whether historical exported material has a useful, independently
reviewable derivative in the current source portfolio. The companion JSON is
entirely synthetic. No private filename, source excerpt, hash, conversational
content, machine path, or third-party data is committed here.

This is deliberately downstream of inventory. It does **not** scan, hash,
extract, execute, stage, ingest, install, grant rights, grant GPU ownership, or
publish any artifact. Source packages from older ChatGPT Project versions are
`HISTORICAL_NOT_INSTALLED` by default; they do not establish current Project
instructions, Lantern state, or PostgreSQL/SQL Connectome runtime currentness.

## One review record per candidate

1. Keep raw bytes, full source identifiers, filenames, content hashes, and
   duplicate mapping in a **protected local** repository or storage location
   under verified access controls. Never place actual personal-export records
   in a public GitHub repository (even if filename or hash alone seems harmless).
2. Use a local opaque ID in `artifact_id` and an optional local duplicate-group
   ID, not a filename, public URL, checksum, or personal name. `private_locator`
   stays exactly `REDACTED` in any shared record.
3. Select one evidence class. An inventory record is not source inspection;
   a source review is not an installed-runtime probe or independently granted
   rights. The schema intentionally contains no positive authorization state.
4. Identify a **candidate** owner from fresh exact Git source and repository
   instructions, then perform a separate reviewed source diff and legal/privacy
   check. A candidate destination is not a decision to publish.
5. Keep `public_admission=HOLD` and `rights=UNVERIFIED`. If a derivative is
   actually cleared, create a new reviewable PR against its exact owner repo,
   with its own evidence, authorization, tests, and independent review.

Do **not** run `source_recovery/export_intake.py` against a live OneDrive Files
On-Demand collection without further host qualification: at the current source
head its default traversal hashes every regular file in full and does not
guard against cloud-placeholder hydration. A private manifest must not be
written to an unverified shared working directory. A separate bounded
placeholder-aware inventory tool can be used only after Windows validation.

## Evidence limits

The schema and sample define a conservative review shape. They do not verify
truthfulness of manually entered status strings, source authenticity, dataset
rights, a secure filesystem, or behavioral model effects. The example is
synthetic and exists solely to validate the schema and documentation.
