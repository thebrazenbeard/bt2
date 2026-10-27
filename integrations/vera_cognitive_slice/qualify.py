"""Explicit-source, no-network, no-effect Vera cognitive vertical qualification.

This is a deterministic host fixture, NOT Vera Mono selected-runtime deployment.
Use only reviewed local source checkouts pinned in source_pins.json.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def _verify_sources(repos: Path) -> dict[str, str]:
    pins = json.loads(Path(__file__).with_name("source_pins.json").read_text(encoding="utf-8"))
    if set(pins) != {
        "volition", "pre-active", "meso-crct", "humility", "meta",
        "semiotics", "semanticatlas", "personification",
    }:
        raise ValueError("unexpected source manifest")
    for name, expected in pins.items():
        checkout = repos / name
        if not checkout.is_dir():
            raise ValueError(f"missing source checkout: {name}")
        head = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if head != expected:
            raise ValueError(f"source head drift for {name}: {head} != {expected}")
        dirty = subprocess.run(
            ["git", "-C", str(checkout), "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if dirty:
            raise ValueError(f"dirty source checkout: {name}")
    return pins


def run_slice(repos: Path, state: Path) -> dict[str, object]:
    source_pins = _verify_sources(repos)
    # The eight inputs are read-only source snapshots, not Python cache targets.
    sys.dont_write_bytecode = True
    for name in ("volition", "pre-active", "meso-crct", "semiotics", "personification"):
        sys.path.insert(0, str(repos / name / "src"))
    for name in ("humility", "meta"):
        sys.path.insert(0, str(repos / name))

    from humility.core import EvidenceItem, revise_distinct
    from meta.core import choose, evaluate
    from durable_meso import DurableEventIssuer
    from semiotics import load_registry
    from personification import (
        ActorProfile, Interaction, InteractionKind, Register, plan_interaction,
    )
    from pre_active.context import ContextAssembler
    from pre_active.engine import Engine, ModelResponse
    from pre_active.store import Store
    from pre_active.tools import ToolRegistry
    from pre_active.volition_bridge import VolitionBridge
    from volition import (
        DriveKind, GoalCompletionClaim, GoalCompletionVerifier, ProvenanceClass,
    )
    from volition.operational_drive import (
        ModelWantProposal, ObservationClaim, ObservationVerifier,
        OperationalMotivation,
    )

    atlas_path = repos / "semanticatlas" / "build" / "build_current_view.py"
    spec = importlib.util.spec_from_file_location("verified_atlas_builder", atlas_path)
    atlas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(atlas)

    state.mkdir(parents=True, exist_ok=True)
    fixture = state / "evidence.txt"
    fixture.write_text("needs examination\n", encoding="utf-8")
    original_bytes = fixture.read_bytes()

    # Synthetic inputs, not live perception or independent model-evaluation labels.
    registry = load_registry(repos / "semiotics" / "examples" / "registry.json")
    interpretations = registry.query("red-light", {"studio"})
    assert len(interpretations) == 1
    assert interpretations[0]["interpretation"]["meaning"] == "Recording in progress"

    subject = "NODE-11111111-1111-4111-8111-111111111111"
    adjudication_id = "ADJ-22222222-2222-4222-8222-222222222222"
    atlas_objects = {
        subject: {"id": subject, "object_type": "node", "primary_label": "Fixture"},
        adjudication_id: {
            "id": adjudication_id, "object_type": "adjudication",
            "subject_id": subject, "authority_scope": "CURRENT_CANON",
            "decision": "ACCEPT", "supersedes_adjudication_ids": [],
        },
    }
    active = atlas.active_adjudications(atlas_objects)
    assert [item["id"] for item in active] == [adjudication_id]

    issuer = DurableEventIssuer(state / "meso-events.sqlite")
    observation_id = issuer.issue("bt2-lappy-fixture")
    # Recreate the owner from its SQLite path to demonstrate persisted
    # sequence advancement rather than reissuing from a stale reference.
    second_event = DurableEventIssuer(state / "meso-events.sqlite").issue(
        "bt2-lappy-fixture"
    )
    assert observation_id.sequence == 1 and second_event.sequence == 2
    assert observation_id.event_id != second_event.event_id

    method = choose([(0, 0), (1, 1), (2, 0), (3, 1)])
    heldout_accuracy = evaluate(method, [(4, 0), (5, 1)])
    assert heldout_accuracy == 1.0
    try:
        evaluate(method, [(4, 0), (4, 0)])
    except ValueError:
        duplicate_trials_rejected = True
    else:
        raise AssertionError("Meta accepted duplicated evaluation inputs")

    evidence = EvidenceItem("admitted-semiotic-cue", "registry-fixture", 0.9, 0.1)
    calibrated = revise_distinct(0.5, (evidence,))
    assert calibrated.posterior > 0.8
    try:
        revise_distinct(
            calibrated.posterior, (evidence,),
            seen_evidence_ids=calibrated.evidence_ids,
            seen_source_groups=calibrated.source_groups,
        )
    except ValueError:
        duplicate_evidence_rejected = True
    else:
        raise AssertionError("Humility accepted replayed evidence")

    personification = plan_interaction(
        ActorProfile("fixture.agent", Register.DIRECT),
        Interaction("fixture.agent", "fixture.user", "Inspect the fixture?",
                    InteractionKind.FACT_CHECK),
    )
    assert personification.answer_target == "Inspect the fixture?"
    assert personification.permission_to_act is False
    assert duplicate_trials_rejected and duplicate_evidence_rejected

    digest = "sha256:" + hashlib.sha256(original_bytes).hexdigest()
    claim = ObservationClaim(
        evidence_id="file-v1",
        content_digest=digest,
        target="repair_test_fixture",
        kind=DriveKind.OPEN_LOOP,
        magnitude=0.9,
        confidence=calibrated.posterior,
        source_ref="readonly-fixture:evidence.txt",
        provenance=ProvenanceClass.CURRENT_OBSERVATION,
    )
    admitted = ObservationVerifier([claim], verifier_id="bt2-host-fixture").admit(claim)
    proposal = ModelWantProposal(
        proposal_id="bt2-inspect-1", evidence_id="file-v1",
        target="repair_test_fixture", kind=DriveKind.OPEN_LOOP,
        reason="source fixture requires inspection",
    )
    db = state / "pre-active.db"
    store = Store(db)
    bridge = VolitionBridge(store)
    first = bridge.submit_model_want_proposal(
        proposal=proposal, admitted_observation=admitted, now=1.0,
    )
    assert first["new_evidence"] is True and first["effect_authority"] is False
    before_restart = OperationalMotivation.from_snapshot(
        store.get_operational_motivation_state()["snapshot"]
    )
    assert len(before_restart.wants) == 1
    store.close()

    store = Store(db)
    bridge = VolitionBridge(store)
    after_restart = OperationalMotivation.from_snapshot(
        store.get_operational_motivation_state()["snapshot"]
    )
    assert after_restart.engine.active_goal is not None
    repeated = bridge.submit_model_want_proposal(
        proposal=proposal, admitted_observation=admitted, now=2.0,
    )
    assert repeated["new_evidence"] is False

    class NoToolReasoner:
        called = 0

        def respond(self, *, messages, tools):
            assert tools == [], f"model unexpectedly offered tool(s): {tools!r}"
            self.called += 1
            return ModelResponse(final_text="Inspected report; no repair was performed")

    model = NoToolReasoner()
    engine = Engine(
        store=store, model=model, tools=ToolRegistry(store),
        context=ContextAssembler(store), system_prompt="Fixture, no tools",
        worker_id="bt2-cognitive-qualification", empathy_response_only=True,
    )
    run_id = engine.run_once(now=3.0)
    assert run_id is not None
    engine.run_once(now=4.0)
    assert store.get_run(run_id)["status"] == "COMPLETED"
    assert store.get_run(run_id)["capabilities"] == set()
    assert model.called >= 1

    persisted = OperationalMotivation.from_snapshot(
        store.get_operational_motivation_state()["snapshot"]
    )
    goal = persisted.engine.active_goal
    assert goal is not None and len(persisted.wants) == 1
    assert all(not want.effect_authority for want in persisted.wants)

    # A stale, even verifier-admitted receipt cannot retire a revised goal.
    def completion(event_id: str, revision: int):
        return GoalCompletionClaim(
            outcome_event_id=event_id,
            goal_id=goal.goal_id, choice_id=goal.choice_id,
            goal_revision=revision, target=goal.target,
            result_receipt_id="host-result-" + event_id,
            evidence_ref="fixture-byte-check", source_ref="bt2-host-fixture",
            provenance=ProvenanceClass.CURRENT_OBSERVATION,
        )

    stale = completion("stale", goal.revision + 1)
    stale_admitted = GoalCompletionVerifier(
        [stale], verifier_id="bt2-fixture-verifier"
    ).admit(stale)
    snapshot_before = store.get_operational_motivation_state()
    try:
        bridge.record_operational_goal_completion(admitted=stale_admitted, now=5.0)
    except ValueError:
        stale_completion_rejected = True
    else:
        raise AssertionError("stale completion accepted")
    assert store.get_operational_motivation_state() == snapshot_before

    # Host-controlled fixture mutation is NOT a repair performed by the model.
    fixture.write_text("host-verified fixed state\n", encoding="utf-8")
    assert fixture.read_bytes() != original_bytes
    claim_done = completion("verified-result", goal.revision)
    verified = GoalCompletionVerifier(
        [claim_done], verifier_id="bt2-fixture-verifier"
    ).admit(claim_done)
    recorded = bridge.record_operational_goal_completion(admitted=verified, now=6.0)
    assert recorded["newly_completed"] is True
    store.close()

    store = Store(db)
    bridge = VolitionBridge(store)
    replay = bridge.record_operational_goal_completion(admitted=verified, now=7.0)
    assert replay["newly_completed"] is False
    cleared = OperationalMotivation.from_snapshot(
        store.get_operational_motivation_state()["snapshot"]
    )
    assert not cleared.wants and cleared.engine.active_goal is None
    store.close()

    _verify_sources(repos)  # confirm the run did not mutate checked source
    return {
        "source_heads_verified": True,
        "source_heads": source_pins,
        "synthetic_studio_sign_selected": True,
        "synthetic_atlas_adjudication_selected": True,
        "meso_event_ids_distinct_on_successor": True,
        "meso_local_sequence_persisted": True,
        "meta_heldout_toy_score": heldout_accuracy,
        "duplicate_trials_rejected": duplicate_trials_rejected,
        "duplicate_evidence_rejected": duplicate_evidence_rejected,
        "personification_preserves_literal_request": True,
        "observed_want_survived_restart": True,
        "tool_free_model_turn": True,
        "model_text_not_completion": True,
        "stale_completion_rejected": stale_completion_rejected,
        "independently_admitted_completion": True,
        "idempotent_replay": True,
        "effect_authority_granted": False,
        "runtime_scope": "isolated synthetic host fixture, NOT active Vera deployment",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos", required=True, type=Path)
    parser.add_argument("--state", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run_slice(args.repos, args.state), sort_keys=True))


if __name__ == "__main__":
    main()
