> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# BT2

BT2 is a working multi-module cognitive-architecture and qualification workspace.

The current source tree includes modules for cognition, affect, salience/attention, memory, identity, semantics, pragmatics, routing, somatics, behavior, and I/O, together with database/runtime qualification, recovery, and portfolio evidence. It preserves historical Lantern V1-V3/WoWSQL material and carries the provider-neutral PostgreSQL/SQL Connectome V4 source package.

## Current status

This repository previously displayed a copied **Hyperconnectome Brain** README that did not identify BT2 correctly. The repository contents themselves remain the authority for what exists on `main`; this README is an orientation layer, not a claim that every module is installed or active in a runtime.

**Runtime-currentness guard:** Consult the
[source status record](docs/runtime/CURRENTNESS_BACKEND_STATUS_V1.json) before
selecting a database/currentness provider. That record marks WoWSQL **retired**,
names **no active currentness backend**, and records SQL Connectome/PostgreSQL
V4 as a **source-only candidate**. In particular, old native Project V1–V3
files (including copies attached to a chat) cannot reactivate WoWSQL or
Lantern, and ordinary source/engineering work does not require querying either.
This source record is not a live probe of any replacement runtime.

The new [V5 Project-file source package](native/project/INSTALL_V5.md)
repairs obsolete V1 reconstruction/worker-topology pointers, while retaining
the **V4 provider-neutral SQL Connectome/PostgreSQL runtime contract**. Its
[manifest](native/project/PROJECT_FILES_MANIFEST_V5.json) binds exact payload
blobs to a source ancestor. The older V4 Project-file package and V1 paths
remain intact as historical source; they were not overwritten.

V5 is **source-only, not installed**. Until a replacement PostgreSQL runtime is
reconstructed, qualified, connected through the governed V4 interface, and
separately installed as the active Project contract,
`LANTERN_CURRENTNESS = UNKNOWN`.

## Repository shape

Major working areas include:

- cognition and integration/arbitration;
- salience, affect, homeostasis/interoception, and conation;
- current and deep memory;
- self-identity, empathy, personification, and behavioral modeling;
- semantics, pragmatics, phonetics, speech, and adaptable I/O;
- routing, neuroplasticity, kinesis, optics, and somatics;
- native/project qualification artifacts, specifications, tools, and database work.

## Evidence boundary

Source availability, passing tests, installation, runtime selection, runtime consumption, and behavioral effect are separate claims. Treat branch-local or historical artifacts as evidence for their own scope rather than automatic current runtime authority.

## Experimental LGCM / SPM / WeKnora interoperability (source-only)

The [learning-stack conformance probe](conformance/learning_stack/README.md)
records real LGCM numerical prequential predictions, saved-state restart
equivalence, source pinning, and a persistence baseline. The
[WeKnora adapter](integrations/weknora/README.md) exercises scoped read-only
hybrid retrieval through a local HTTP fixture and derives an SPM memory-adapter
activation decision without promoting retrieved text into trusted HC memory.
Mosaic and Noema remain independently owned experimental/review subsystems.
The SPM hardened neural specialist, live WeKnora ingestion, shared neural
learning, and combined behavioral improvement are **not qualified here**.

## AI psychology coordination (source-only)

[Issue #61](https://github.com/thebrazenbeard/bt2/issues/61) is the active hostile gap map for the functional emotion/motivation architecture. The [AI-psychology conformance harness](conformance/ai_psychology/) tests bounded source contracts; [Draft PR #62](https://github.com/thebrazenbeard/bt2/pull/62) tracks cross-repository coordination.

MESO-CRCT → Volition → Pre-Active forward bridges and a durable, **untrusted** outcome-candidate ledger exist in source. They are **not** a qualified installed feedback loop. Independent outcome-witness custody, causal action attribution, one-use goal/need revision binding, and crash-safe MESO/Volition state application remain unverified. Signed model responses, caller-asserted observer identities, and evidence hashes alone cannot establish action success, permit external effects, or justify need/satiation changes. Treat passing in-memory oracle tests separately from real observer, persistence, and behavioral evidence.
