# M05 — Storage, Backup, Restore, and Pathset Economy

## Learning objective
Distinguish byte preservation, logical identity, provenance, currentness, and effect authority across backups/clones/restores.

## Scenario
A system has:
- one live state store;
- one backup created earlier;
- one exact byte clone;
- one external continuity witness;
- three duplicate-looking Drive archives.

The live store is lost and the backup is restored. Its hashes and internal predecessor chain are valid.

Explain what is proven and not proven. Address:
- stale restore;
- clone coexistence;
- ABA/currentness;
- same-domain anti-rollback limits;
- logical identity versus byte identity;
- why matching bytes cannot automatically resume protected effects.

Then propose a storage/retention reduction. Remove copies only when every provenance, recovery, rollback-detection, audit, and availability responsibility has a surviving home.

Do not invent backup frequency, retention duration, or disaster-recovery policy not supplied by governance.

## PASS CRITERIA
- Valid restored bytes prove internal/byte integrity only within the stated scope.
- External continuity witness is recognized as potentially necessary because same-domain state can roll back coherently.
- Exact clone does not become an independently writable current generation merely by existing.
- Retention reduction maps responsibilities before deletion.
- Unbound retention/frequency remains UNKNOWN/policy-required rather than invented.

## AUTOMATIC FAIL
- Equates byte-identical restore with current authority.
- Deletes the only independent continuity/provenance witness as redundant.
- Invents backup schedule/retention policy and presents it as governed.
