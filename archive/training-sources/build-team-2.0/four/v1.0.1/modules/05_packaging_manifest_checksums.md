# Module 05 — Packaging, Manifests, Profiles, and Checksums

## Objective
Build deterministic package/release geometry after source semantics are frozen.

## Required discipline
Model package consequences as a dependency DAG. Generated manifests/checksums are produced after all inputs they bind are final. Exact profile/contract equality must be mechanically verified when required. A clean test result does not excuse a dirty worktree, stale generated manifest, or unbound artifact.

Distinguish:
- source candidate;
- package artifact;
- provider custody;
- release eligibility;
- installation/deployment/effect authority.

## Exercise
A three-path source change requires manifest regeneration and package rebuild. Give the safe production order and read-back gates.

## Pass criteria
- Dependency order is correct.
- Checksums/manifests are generated last relative to their bound inputs.
- Candidate/package/provider/release/install states remain separate.
- Exact byte/hash claims require mechanical evidence.
