# BT2 identity coding models (V1)

These are **source-only role-conditioned coding-agent configurations**, one for each of the 13 durable identities in `native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json`. They are not trained model weights, active agents, imported qualification evidence, current assignments, or permissions. An execution terminal can *use* a profile without *becoming* a durable BT2 identity.

Each JSON profile supplies a coding objective, concrete coding capabilities, an ordered execution protocol, review criteria, evidence requirements, handoff outputs, and authority boundaries. The profiles derive role specialization from the repository's historical source entrypoints while obeying the current `native/project/BT2_CODING_OPERATIONS_V2.md` contract. The live request, actually installed instructions, current assignments, and exact source facts still control execution.

## Usage

From the repository root, with Python 3.10+ and no third-party dependencies:

```sh
python tools/identity_coding_models.py validate
python tools/identity_coding_models.py list
python tools/identity_coding_models.py render --identity three --task "Implement the scoped fix and prove it"
python -m unittest discover -s tests -p test_identity_coding_models.py
```

`render` prints a reusable role-conditioned coding prompt. It performs no model invocation and no external write. `validate` checks the exact 13-member V2 topology, source entrypoint bindings, schema fields, content bounds, and source-only status. It fails closed on missing, extra, or mismatched profiles.

## Integration and evidence boundaries

- Each profile is a specialization, not a replacement for current authority, source inspection, or independent review.
- One owns orchestration, Two supplies independent architectural challenge, and specialist scopes remain distinct.
- Masa and Mune are independent members of a paired reliability unit; Hephaestus is an independent implementation/repair specialist.
- Their additional current source homes are `thebrazenbeard/masamune` (Masa and Mune) and `thebrazenbeard/hephaestus` (Hephaestus). `upstream_role_sources_v1.json` records observed source heads, not runtime state. These are reference sources; model configurations are integrated into this BT2 repository as requested.
- The old training source packages are reference evidence, not proof that a profile was trained, imported, qualified, installed, or activated.
- The current repository status records WoWSQL as retired and no active Lantern currentness backend; these source profiles do not re-enable one.
- Merge, deploy, provider/credential/permission changes, training, canonical promotion, and destructive cleanup require separately established current authority.

To extend or change the roster, update the canonical topology first under its own governance, then update these profiles and the validator/tests together. Do not silently extend authority by editing a coding prompt.

The `training/` directory provides unqualified role-specific SFT candidates and a staged adapter/GGUF path. Neither the coding profiles nor SFT examples are model weight updates.
