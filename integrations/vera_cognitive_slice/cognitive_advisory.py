"""Read-only, model-agnostic proposal boundary for pinned Humility source.

This computes a conditional mathematical revision from caller-supplied likelihoods.
It does NOT verify evidence, retrieve memories, grant effects, or judge truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re
import subprocess
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


_SHA = re.compile(r"^[0-9a-f]{40}$")


def _head_commit(repo: Path) -> str:
    """Capture one current source commit before any module execution."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "HEAD^{commit}"],
            capture_output=True, text=True, check=True, timeout=20,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError("cannot capture current source commit") from exc
    commit = proc.stdout.strip()
    if not _SHA.fullmatch(commit):
        raise ValueError("invalid current source commit")
    return commit


def _committed_blob(repo: Path, relative_path: str, *, commit_sha: str) -> str:
    """Resolve the file blob from an exact prior commit, never a mutable HEAD."""
    if type(commit_sha) is not str or not _SHA.fullmatch(commit_sha):
        raise ValueError("valid pinned commit required")
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify",
             f"{commit_sha}:{relative_path}"],
            capture_output=True, text=True, check=True, timeout=20,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError("cannot bind executed source to a pinned commit") from exc
    blob = proc.stdout.strip()
    if not _SHA.fullmatch(blob):
        raise ValueError("invalid committed source blob")
    return blob


def _load_exact_module(path: Path, *, expected_blob: str):
    """Execute only bytes matching the committed blob, including at use time."""
    if not path.is_file() or path.is_symlink():
        raise ValueError("pinned source module not loadable")
    if type(expected_blob) is not str or not _SHA.fullmatch(expected_blob):
        raise ValueError("valid expected Git blob required")
    source = path.read_bytes()
    actual = hashlib.sha1(
        b"blob " + str(len(source)).encode("ascii") + b"\0" + source
    ).hexdigest()
    if actual != expected_blob:
        raise ValueError("source bytes changed after verification")
    name = "_bt2_pinned_humility_" + uuid4().hex
    module = ModuleType(name)
    module.__file__ = str(path)
    code = compile(source, str(path), "exec")
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
    own_repo = Path(__file__).resolve().parents[2]
    own_commit = _head_commit(own_repo)
    guard = _load_exact_module(
        Path(__file__).with_name("qualify.py"),
        expected_blob=_committed_blob(
            own_repo, "integrations/vera_cognitive_slice/qualify.py",
            commit_sha=own_commit,
        ),
    )
    pins = guard._verify_sources(Path(repos), manifest_commit=own_commit)
    humility_repo = Path(repos) / "humility"
    humility = _load_exact_module(
        humility_repo / "humility" / "core.py",
        expected_blob=_committed_blob(
            humility_repo, "humility/core.py", commit_sha=pins["humility"],
        ),
    )
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
