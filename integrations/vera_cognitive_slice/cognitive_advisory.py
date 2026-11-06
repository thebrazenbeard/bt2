"""Read-only, model-agnostic proposal boundary for pinned Humility source.

This computes a conditional mathematical revision from caller-supplied likelihoods.
It does NOT verify evidence, retrieve memories, grant effects, or judge truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from types import ModuleType
from uuid import uuid4


@dataclass(frozen=True)
class EvidenceSignal:
    evidence_id: str
    source_group: str
    likelihood_if_true: float
    likelihood_if_false: float


@dataclass(frozen=True)
class AdvisoryRequest:
    proposition: str
    prior: float
    evidence: tuple[EvidenceSignal, ...]
    seen_evidence_ids: tuple[str, ...] = ()
    seen_source_groups: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadOnlyAdvisory:
    proposition: str
    prior: float
    posterior: float
    evidence_ids: tuple[str, ...]
    source_groups: tuple[str, ...]
    source_pins: tuple[tuple[str, str], ...]
    status: str = "UNVERIFIED_CALLER_LIKELIHOODS"
    effect_authority: bool = False
    memory_admission: bool = False
    independent_outcome_verified: bool = False


def _load_exact_module(path: Path):
    """Execute only exact file bytes; avoid cached imports and .pyc writes."""
    if not path.is_file() or path.is_symlink():
        raise ValueError("pinned source module not loadable")
    name = "_bt2_pinned_humility_" + uuid4().hex
    module = ModuleType(name)
    module.__file__ = str(path)
    code = compile(path.read_bytes(), str(path), "exec")
    sys.modules[name] = module
    try:
        exec(code, module.__dict__)
    finally:
        sys.modules.pop(name, None)
    return module


def propose(repos: Path, request: AdvisoryRequest) -> ReadOnlyAdvisory:
    """Compute an unverified revision candidate; never execute model/tools."""
    if type(request) is not AdvisoryRequest:
        raise ValueError("typed advisory request required")
    if type(request.proposition) is not str or not request.proposition.strip():
        raise ValueError("nonempty proposition required")
    if type(request.evidence) is not tuple or not request.evidence:
        raise ValueError("nonempty evidence tuple required")
    if any(type(item) is not EvidenceSignal for item in request.evidence):
        raise ValueError("typed evidence signals required")

    # Run the full eight-source byte guard before evaluating the one real donor
    # invoked by this optional API. Other seven repos are NOT claimed active.
    guard = _load_exact_module(Path(__file__).with_name("qualify.py"))
    pins = guard._verify_sources(Path(repos))
    humility = _load_exact_module(Path(repos) / "humility" / "humility" / "core.py")
    signals = tuple(
        humility.EvidenceItem(
            e.evidence_id, e.source_group, e.likelihood_if_true, e.likelihood_if_false
        ) for e in request.evidence
    )
    result = humility.revise_distinct(
        request.prior, signals,
        seen_evidence_ids=request.seen_evidence_ids,
        seen_source_groups=request.seen_source_groups,
    )
    return ReadOnlyAdvisory(
        proposition=request.proposition,
        prior=result.prior,
        posterior=result.posterior,
        evidence_ids=result.evidence_ids,
        source_groups=result.source_groups,
        source_pins=tuple(sorted(pins.items())),
    )
