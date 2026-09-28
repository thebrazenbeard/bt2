# BT2 Exodus Candidate Reconciliation — 2026-09-20

Status: `SOURCE_RECONCILIATION_CANDIDATE / NO_PROTECTED_EFFECT`

Base: `thebrazenbeard/bt2@30e81cadd94fae117a7f6875523c03251c7c9f6e`

## Reconciled inputs

- PR #24: BT2 Coordinator interface surface.
- PR #26: exact 13-role BT2 source reconstruction map and runtime recovery updates.
- PR #27: exact three-interface topology and coordinator reconstruction contract.
- PR #29: recovery/audit checkpoint; preserved as provenance, not promoted to normative architecture.
- Chat Bus PR #128: three-interface Exodus architecture; now provenance contributor to the stronger Bus Exodus integration line.

## Normative result

The candidate deliberately has two orthogonal normative contracts:

1. `native/project/BT2_EXODUS_WORKER_TOPOLOGY_V1.json`
   - exactly 13 BT2 durable roles;
   - One;
   - Two, Three, Four, Five, Six, Seven, Eight, Nine, Thirteen;
   - Masa, Mune;
   - Hephaestus.
   - Seven is bound to `archive/training-sources/project-achilles/seven/v1.0.0`.

2. `native/project/BT2_PERSISTENT_INTERFACE_TOPOLOGY_V1.json`
   - exactly three persistent human interfaces:
     - Vera
     - Vera Control Plane Coordinator
     - BT2 Coordinator

The #24 coordinator files are retained only as compatibility/interface adapters and explicitly cross-bind to these normative contracts. They are not a second topology authority.

## Repair relative to PR #27

PR #27's prose list omitted Seven even though Seven is part of the intended BT2 workforce. This candidate restores Seven from the exact Project Achilles source path already present on current main and required by PR #26.

## State separation

Source reconstruction does not imply:
- training qualification / BASE_READY;
- installation or activation;
- current assignment;
- provider/runtime currentness;
- merge/deploy/provider/credential authority.

Checkpoints are starting snapshots and not current truth.

## Bus relation

Bus PR #128 correctly defines the three-interface rule but has been superseded as an integration subject by later Bus Exodus composition. Current Bus work must be fresh-checked independently rather than frozen into BT2 source.

## Lantern

The exact WoWSQL target for Lantern remains `bt2-479e4ad9`. During this reconciliation the connector failed internally before a V3 projection preflight could be established, so `LANTERN_CURRENTNESS = UNKNOWN`. No fallback backend was used.

## Authority

This branch is reversible source/governance work only. It performs no merge, deployment, provider/database mutation, credentials/permissions change, model training, Project Settings mutation, Slack activation, or canonical promotion.
