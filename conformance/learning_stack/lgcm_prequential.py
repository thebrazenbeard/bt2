"""Reproducible, source-only LGCM learning/persistence probe.

This evaluates online *numeric* RLS updates. It does not exercise a neural
language model, retrieval, a live HC runtime, or protected plasticity.
"""

from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
from tempfile import TemporaryDirectory


def regime_fixture() -> tuple[float, ...]:
    """Development/regression stream, not an independent holdout."""
    return tuple([0.6] * 20 + [-0.6] * 20 + [0.6] * 20)


def _trial(values: tuple[float, ...], *, restart_at: int | None) -> dict:
    import lgcm  # Explicit external dependency. Never vendor upstream code.
    import numpy as np

    config = lgcm.LGCMConfig(
        observation_dim=1,
        action_dim=1,
        regularization=0.1,
        expert_forgetting_factor=0.75,
        residual_decay=0.8,
        residual_floor=0.02,
        min_expert_evidence=3,
        max_experts=4,
        switch_margin=0.1,
        support_penalty=0.0,
        spawn_patience=1,
        mismatch_delta=0.0,
        mismatch_threshold=0.8,
        mismatch_min_evidence=2,
        bootstrap_size=4,
        new_expert_init="neutral",
    )
    model = lgcm.ContextualWorldModel(config)
    baseline = lgcm.PersistencePredictor(observation_dim=1, action_dim=1)
    steps: list[dict] = []
    snapshot = None
    with TemporaryDirectory(prefix="lgcm-prequential-") as temp:
        for sequence, target in enumerate(values):
            observation = np.array([0.0], dtype=np.float64)
            action = np.array([0.0], dtype=np.float64)
            next_observation = np.array([target], dtype=np.float64)
            # Scores MUST use predictions made before the observed outcome is
            # used for the corresponding update.
            prediction = model.predict(observation, action)
            control_prediction = baseline.predict(observation, action)
            experience = lgcm.Experience(
                sequence=sequence,
                observation=observation,
                action=action,
                next_observation=next_observation,
                source="bt2-regression-fixture",
            )
            steps.append({
                "sequence": sequence,
                "prediction": float(prediction.mean[0]),
                "baseline_prediction": float(control_prediction.mean[0]),
                "squared_error": float((prediction.mean[0] - target) ** 2),
                "baseline_squared_error": float((control_prediction.mean[0] - target) ** 2),
                "active_expert": prediction.active_expert,
            })
            model.update(experience)
            baseline.update(experience)
            if restart_at is not None and sequence + 1 == restart_at:
                receipt = lgcm.save_snapshot(model, Path(temp) / "checkpoint")
                snapshot = {
                    "generation": receipt.generation,
                    "manifest_sha256": receipt.manifest_sha256,
                }
                model = lgcm.load_snapshot(receipt.path)
                if model.generation != sequence + 1 or model.last_sequence != sequence:
                    raise AssertionError("checkpoint readback is not at committed boundary")
    if model.generation != len(values) or model.last_sequence != len(values) - 1:
        raise AssertionError("final learner generation/sequence mismatch")
    with TemporaryDirectory(prefix="lgcm-final-") as temp:
        final_receipt = lgcm.save_snapshot(model, Path(temp) / "final")
    config_sha256 = sha256(json.dumps(asdict(config), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "steps": steps,
        "generation": model.generation,
        "config_sha256": config_sha256,
        "snapshot": snapshot,
        "final_manifest_sha256": final_receipt.manifest_sha256,
    }


def _source_revision() -> tuple[str, bool | None]:
    import lgcm

    root = Path(lgcm.__file__).resolve().parents[2]
    try:
        ref = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            check=True, capture_output=True, text=True, timeout=5,
        ).stdout.strip())
        return ref, dirty
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "UNKNOWN", None


def run_probe(values: tuple[float, ...] | None = None, *, restart_at: int = 30) -> dict:
    """Compare uninterrupted and snapshot-restored LGCM, plus no-learning baseline.

    Returns every *prequential* prediction. It is a regression fixture, not
    evidence of generalization to an unseen task or neural state sharing.
    """
    import math

    values = regime_fixture() if values is None else tuple(values)
    if (len(values) < 2 or type(restart_at) is not int
            or not 1 <= restart_at < len(values)):
        raise ValueError("stream must contain at least two events with an interior restart")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not -1 <= v <= 1 for v in values):
        raise ValueError("outcomes must be finite numbers in the LGCM configured bounds")
    uninterrupted = _trial(values, restart_at=None)
    resumed = _trial(values, restart_at=restart_at)
    if uninterrupted["steps"] != resumed["steps"]:
        raise AssertionError("learned predictions differ after snapshot restart")
    if uninterrupted["final_manifest_sha256"] != resumed["final_manifest_sha256"]:
        raise AssertionError("final serialized learned state differs after restart")
    steps = resumed["steps"]
    source_commit, source_dirty = _source_revision()
    import numpy
    return {
        "schema": "BT2_LGCM_PREQUENTIAL_REGRESSION_V1",
        "scope": "NUMERIC_RLS_ONLINE_ADAPTIVE_REGRESSION_ONLY",
        "evaluation_role": "REGRESSION",
        "evaluation_regime": "ONLINE_ADAPTIVE",
        "data_sha256": sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest(),
        "count": len(steps),
        "lgcm_source_commit": source_commit,
        "lgcm_source_dirty": source_dirty,
        "python_version": platform.python_version(),
        "numpy_version": numpy.__version__,
        "model_config_sha256": resumed["config_sha256"],
        "restart_at": restart_at,
        "restart_equivalent": True,
        "generation": resumed["generation"],
        "snapshot": resumed["snapshot"],
        "final_manifest_sha256": resumed["final_manifest_sha256"],
        "mean_squared_error": sum(s["squared_error"] for s in steps) / len(steps),
        "persistence_baseline_mse": sum(s["baseline_squared_error"] for s in steps) / len(steps),
        "steps": steps,
    }
