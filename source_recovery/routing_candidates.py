"""Conservative, *non-publishing* repository candidates for historical exports.

This pure mapping accepts a reviewed material-class label, not an archive name,
file path, JSON payload, conversation, or purported source authority. It opens
no files and grants no rights or source promotion. A candidate merely directs
the next human/source comparison; it is never a Git destination decision.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteCandidate:
    classification: str
    candidate_repositories: tuple[str, ...]
    source_basis: str = "CLASSIFICATION_ONLY"
    publication: str = "HOLD"
    rights: str = "UNVERIFIED"
    currentness: str = "HISTORICAL_NOT_INSTALLED"
    raw_material_git_eligible: bool = False
    requires_exact_head_review: bool = True


# All repositories here are merely *possible homes for reviewed derivatives*.
# No historical raw material (including private conversation bodies or export
# metadata) is eligible to be uploaded on the strength of this mapping.
# Keep ambiguous code/bundles and private material unrouted by default.
_REVIEW_CANDIDATES: dict[str, tuple[str, ...]] = {
    "historical_project_packet": ("vera-control-plane", "bt2"),
    "semantic_research": ("semanticatlas",),
    "training_evaluation": ("model-training", "labyrinth"),
    "visual_reference": ("selfimage",),
    "temporal_research": ("temporal",),
    "private_conversation": (),
    "model_artifact": (),
    "executable_bundle": (),
    "mixed_archive": (),
}


def propose_route(classification: object) -> RouteCandidate:
    """Return a source-only review queue candidate; never an upload target.

    Unknown classes and raw filenames intentionally return no candidate. The
    caller must independently classify content privately and compare current
    code, licenses, privacy, and repository-local contracts before even
    *considering* a sanitized derivative PR.
    """
    if type(classification) is not str or classification not in _REVIEW_CANDIDATES:
        return RouteCandidate("UNKNOWN", ())
    return RouteCandidate(classification, _REVIEW_CANDIDATES[classification])
