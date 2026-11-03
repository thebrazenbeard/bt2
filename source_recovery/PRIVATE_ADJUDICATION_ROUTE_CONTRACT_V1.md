# Private class evidence to historical-adjudication route proposal

`adjudication_route_contract.propose_private_adjudication_route()` is a pure,
non-publishing bridge between a **separately reviewed** material class and the
`target_repo_candidate` field of the private historical-adjudication-v1
template. It opens no file, consumes no ZIP member, reads no inventory manifest,
does not write any record, and never invokes Git or a remote service.

Input is an opaque synthetic `artifact_id`, a distinct
`ClassEvidenceAssertion(artifact_id, classification, evidence_class,
private_review_record_id)`, and an **explicit** repository choice. The
assertion must be produced, authenticated, and retained by a separate trusted
private review workflow; merely constructing this ordinary Python dataclass
does **not** establish that review or the reviewer's identity.

The bridge rejects a missing/mismatched class assertion, unsupported evidence
class, malformed IDs, private or unknown class, filename-like guess, and a
repository not in the class's *candidate* set. Even a class with only one
candidate needs an explicit choice; a class with two possible owners cannot
silently select one. Every return has `public_admission=HOLD`,
`rights=UNVERIFIED`, `source_state=HISTORICAL_NOT_INSTALLED`, and
`raw_material_git_eligible=False`. `AdjudicationRouteProposal` is not the full
private adjudication record, an authorization token, or a publication grant.

After **private**, authenticated review, a caller may copy its proposed
`target_repo_candidate` into a separately validated v1 adjudication record.
That record is still HOLD; current repo ownership, file-level rights, privacy,
source provenance, and independent review are different gates. A future
real consumer must prove these gates independently. Classification may not be
inferred from paths, file extensions, names, old Project instructions, or
machine inventory metadata.

Keep actual export paths, filenames, content, exact byte hashes, manifests,
and review-association records outside public Git. This module's synthetic
tests are not evidence of Windows/WSL/OneDrive archive access or source
admission. No production consumer is wired by this source-only candidate.
