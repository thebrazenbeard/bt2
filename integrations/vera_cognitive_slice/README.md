# Vera cognitive vertical-slice qualification

This is a source-bound, no-model-tool, synthetic host integration test.
It is NOT a Vera Mono selected runtime, active deployment, trained neural
model, emotional competence measure, or proof of independent semantic accuracy.

## Source and Lappy reproducibility

source_pins.json specifies eight exact commits. Checkouts must be at those
heads, unmodified, or the runner fails closed before imports. To create an
isolated checkout set on Lappy:

    python integrations/vera_cognitive_slice/prepare_sources.py --out C:\Temp\bt2-cognitive-source-new

Then set BT2_VERA_COGNITIVE_REPOS to that folder and execute:

    python -m unittest discover -s integrations/vera_cognitive_slice -p test_qualify.py -v

The run uses an ephemeral SQLite Store and a deterministic no-tool model
adapter. It exercises actual VolitionBridge, Store and Engine, including
persistence, restart, duplicate evidence admission, stale completion,
host-observed completion, and idempotent replay.

Semiotics, Semantic Atlas, Humility, Meta, MESO-CRCT and Personification
are called through their exact source APIs on explicitly synthetic inputs.
A Meta toy score is not validation of real-world learning or independent
label custody. An immutable MESO EventSequencer requires its owner to
persist the successor and serialize issuance; the fixture tests only
successor issuance, not distributed concurrency.

The host, not the model, edits the fixture to demonstrate externally
verified completion. No model tools or effect authority are granted.
The check does not write or install anything into D:\VERA.

Production activation, real model behavior, cross-host state persistence,
source authentication, and rollout to VN1/VN2 remain separate qualification
gates. Re-run with new exact source pins when a participating main changes.
