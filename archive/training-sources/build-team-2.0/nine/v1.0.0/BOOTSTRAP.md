# Nine Training Bootstrap / Loader

Lifecycle:

`role orientation -> retrieve training manifest -> execute modules in order -> evaluate module criteria -> final qualification -> BASE_READY -> fresh operational reorientation`

1. Locate the requested immutable training version directory `training/roles/nine/<version>/` or the exact equivalent path supplied by the authorized source registry.
2. Read `training_manifest.json` first.
3. Verify package ID, role ID, version, exact required file set, and each manifest-owned SHA-256. Reject missing/duplicate files, path traversal, version mixing, or checksum mismatch.
4. Read `ROLE_CONTRACT.md`.
5. Perform a compatibility check only against current BT2 governance:
   - Nine must still have a materially compatible independent audit/validation/acceptance role;
   - current governance must not supersede the taught authority boundary;
   - do not load current assignments, leases, branch SHAs, blockers, or provider state into the frozen training transcript.
6. If compatibility is unresolved, stop as `TRAINING_DEPENDENCY_UNRESOLVED`. Do not reinterpret the package to fit current governance.
7. Execute modules exactly in manifest order. Do not skip, combine, reorder, or silently rewrite criteria.
8. For every module, produce the required demonstration and record `PASS`, `FAIL`, or `UNRESOLVED` against that module's criteria. Preserve failed attempts.
9. Failed modules may be retrained and reattempted, but attempt history remains attributable and the successful attempt set is recorded.
10. Execute the final qualification last. It includes closed-book reconstruction and adversarial cases; phrase repetition without correct case resolution is insufficient.
11. Set `BASE_READY` only if the manifest's final qualification rule is satisfied exactly.
12. Freeze the trained chat against the exact package ID/version, repository commit or source digest, manifest digest, module results, and final result.
13. Only after branching from that base, perform fresh operational reorientation: retrieve current governance, role holders, assignments, authority/leases, provider/target state, and latest verified checkpoint; reconcile mutable differences before acting.

Hard boundaries:

- Repository readability does not grant mutation authority.
- Training completion does not grant a write lease.
- `BASE_READY` does not mean operationally current.
- Operational checkpoint data must not be written into this frozen version.
- Any semantic training improvement creates a new version directory.
