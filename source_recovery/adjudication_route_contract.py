"""Pure private-review bridge from class evidence to a held repo candidate.

This has no scanner, reader, writer, Git, or authorization capability. A class
assertion must originate from a separately governed private review. The
dataclass cannot authenticate its creator and a structurally valid decision
never establishes rights, a privacy grant, or publication eligibility.
"""

from dataclasses import dataclass
import re

from .routing_candidates import propose_route


_ID = re.compile(r"^[A-Z0-9_-]{4,48}$")


@dataclass(frozen=True)
class ClassEvidenceAssertion:
    """Caller-declared private review reference; NOT a trust credential."""

    artifact_id: str
    classification: str
    evidence_class: str
    private_review_record_id: str


@dataclass(frozen=True)
class AdjudicationRouteProposal:
    """A non-admitting projection, not a full adjudication-v1 record."""

    artifact_id: str | None
    classification: str
    possible_repositories: tuple[str, ...]
    target_repo_candidate: str | None
    reason: str
    public_admission: str = "HOLD"
    rights: str = "UNVERIFIED"
    source_state: str = "HISTORICAL_NOT_INSTALLED"
    raw_material_git_eligible: bool = False


def _valid_id(value: object) -> bool:
    return type(value) is str and _ID.fullmatch(value) is not None


def propose_private_adjudication_route(
    artifact_id: object,
    class_evidence: object,
    *,
    selected_repository: object = None,
) -> AdjudicationRouteProposal:
    """Return only a held possible target from an explicitly reviewed class.

    Identity and selection checks protect the structural bridge, not the
    reviewer's identity or authority. The caller must authenticate and retain
    the actual private review record in its separately authorized custody.
    Neither inventory filename nor ZIP metadata is a classification input.
    """
    if not _valid_id(artifact_id):
        return AdjudicationRouteProposal(None, "UNKNOWN", (), None,
                                         "INVALID_ARTIFACT_ID")
    if type(class_evidence) is not ClassEvidenceAssertion:
        return AdjudicationRouteProposal(artifact_id, "UNKNOWN", (), None,
                                         "MISSING_CLASS_EVIDENCE")
    evidence = class_evidence
    if (not _valid_id(evidence.artifact_id)
            or evidence.artifact_id != artifact_id
            or not _valid_id(evidence.private_review_record_id)
            or type(evidence.evidence_class) is not str
            or evidence.evidence_class != "SOURCE_INSPECTION"
            or type(evidence.classification) is not str):
        return AdjudicationRouteProposal(artifact_id, "UNKNOWN", (), None,
                                         "INVALID_CLASS_EVIDENCE")

    route = propose_route(evidence.classification)
    if not route.candidate_repositories:
        return AdjudicationRouteProposal(artifact_id, route.classification, (), None,
                                         "UNROUTABLE_CLASS")
    if (type(selected_repository) is not str
            or selected_repository not in route.candidate_repositories):
        return AdjudicationRouteProposal(
            artifact_id, route.classification, route.candidate_repositories,
            None, "EXPLICIT_REVIEWER_SELECTION_REQUIRED")

    return AdjudicationRouteProposal(
        artifact_id, route.classification, route.candidate_repositories,
        selected_repository, "REVIEW_CANDIDATE_ONLY")
