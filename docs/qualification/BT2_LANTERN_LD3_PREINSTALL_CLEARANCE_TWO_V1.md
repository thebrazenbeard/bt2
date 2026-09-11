# BT2 Project Lantern L-D3 Pre-Install Clearance — Two V1

Status: PRE-INSTALL SOURCE/BACKEND CLEARANCE / PROJECT ROUTE NOT INSTALLED
Date: 2026-09-11
Systems Architect: Two
Coordinator / execution owner: One
Execution boundary: One + Two only

## Exact installation subject

Frozen successor source subject:
- repository: `thebrazenbeard/bt2`
- commit: `94ad89d05ab1557813ed09d2b6fe65907a4194c5`
- tree: `fa23273a9bd06f96a2057ddc649dc09d1b882a55`
- convenience branch: `candidate/lantern-wowsql-project-runtime-v1` (observed pointing to the exact commit at review time)

Exact successor files:
- `LANTERN_WOWSQL_OPERATOR_HANDSHAKE_V1.md` blob `9df2f7779ae49984510754ea674e7d332abf2fcd`
- `LANTERN_WOWSQL_READ_QUERIES_V1.md` blob `909ddddf68016d10634334dcb029a4b5f4c87e5a`
- `LANTERN_WOWSQL_RUNTIME_CONTRACT_V1.md` blob `5a0c8f893bf54ac93c46325f2f79bdf0289c5b3f`
- `LANTERN_WOWSQL_ACCEPTANCE_V1.md` blob `514a9431f6fecaead6358c9f1f787f5456c537db`

Installation wrapper:
- `docs/runtime/LANTERN_WOWSQL_PROJECT_INSTALLATION_PACKET_V1.md`
- wrapper source commit before this clearance: `ca86ad70c0d14d4d997c0d92b8afc9e968d5e6c7`
- wrapper blob: `5af05fca17fa3303d1073a202fa88785e558885f`

The wrapper binds the exact Project Instructions V2 replacement block and explicitly requires replacement, not coexistence, of the four Supabase-bound runtime files.

## Backend/source review

Reviewed current combined database/runtime subject:
- database package digest `195a7546f508be23e95048682a2d2597eb3c67c44901450701ee17ada05d6e57`;
- corrected migration 0017 blob `b73701ae43cc5141ba9d5be8145be3dfa84839a7`;
- corrected V2 historical archive manifest blob `d20ac718e6ac37cd15173fd4235cb5e78507ed80`;
- V2 loader blob `39b5d129dc6679bf6a971c8f2af89a084013001c`;
- V2 receipt blob `4f78da3e57e5bf3c15031d252688b20217cb9442`;
- clean-room runtime-contract test blob `78bca2f325480b9d8cc7649aa7fc3f13483dac51`;
- rebuild workflow invokes V2 loader and all database tests.

No remaining Lantern-specific backend semantic blocker was found before Project installation.

Observed/accepted backend evidence:
- L-D1 historical preservation = `VERIFIED_V2`;
- Supabase B0 -> payload -> B1 stable on the current two-member cut;
- WoWSQL B0 -> payload -> B1 stable on the same cut;
- complete visible-material rowset digest equal on both providers: `8ecc199ece82f0551d70fe624fdd58d1a4f34ad6b9ee73fad5eb140b210c045b`;
- clean-room successor read semantics passed against live WoWSQL with zero fixture residue;
- current producer authority remains zero;
- V1 historical-load failure evidence remains append-only and V2 alone carries VERIFIED acceptance.

## Rebuild qualification ceiling

GitHub-hosted blank-database execution is still NOT ESTABLISHED because Actions jobs fail before exposing runner steps. This is an external execution gap and supplies neither SQL PASS nor SQL FAIL.

For L-D3 specifically, this does not falsify the already-live successor backend or the exact source contract. It remains a global BT2 rebuild-qualification gap and must stay visible in global migration acceptance. It must not be silently converted into provider-route acceptance evidence.

## L-D3 disposition before protected installation

- P1 Installed provider binding: OPEN. Exact installable source now exists; Project mutation/readback has not occurred.
- P2 Cold-start currentness route: NOT ESTABLISHED. Requires fresh runtime after P1.
- P3 Same-frontier semantic equivalence: PRELIMINARY PASS on current frontier; mandatory final-freeze replay remains.
- P4 Fail-closed/no-fallback runtime behavior: NOT ESTABLISHED. Requires fresh runtime after P1.
- P5 Authority non-amplification: backend precondition PASS; post-install runtime/readback still required.
- P6 Operational dependency zero: OPEN until Project V1 contract is replaced and effective references are classified.

Systems Architect disposition: `NO_REMAINING_PRE_INSTALL_LANTERN_BACKEND_OR_SOURCE_BLOCKER`.

This is not authorization to mutate Project instructions/files, merge, cut over, retire or delete Supabase, or create any producer/write authority. The next protected hinge is deliberate Project installation of the exact frozen successor subject followed by P1/P2/P4/P5/P6 acceptance. Final-freeze P3 and L-D4 remain after that.
