# BT2 Adversarial Collaboration Posture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Patrick's supplied adversarial-collaboration posture a reconstructible, testable BT2-wide native Project behavior without rewriting historical V3 package identity or claiming installation before it occurs.

**Architecture:** Preserve the uploaded posture byte-for-byte as a collision-safe native Project file, introduce Project Instructions V4 containing a compact complete operational form of the posture, and bind the exact source file plus instructions with a V4 manifest/install contract. A stdlib Python qualification test fails closed on wording drift, missing bindings, stale hashes, installation overclaim, or accidental V3 mutation.

**Tech Stack:** Markdown, JSON, Python 3 stdlib `unittest`, Git/GitHub.

**Spec:** `docs/bt2/ADVERSARIAL_COLLABORATION_POSTURE_V1.md`

## Global Constraints

- Uploaded source SHA-256 is `828a3995dd0e49999c7ebc51753cfa17508935b45b99c01c79f456845994826f`.
- The literal posture is normative; do not weaken, reinterpret, or silently improve it before testing.
- V3 Project Instructions, manifest, and install artifacts remain unchanged historical subjects.
- Source/package readiness must not be reported as Project installation or behavioral verification.
- No merge, Project-settings mutation, deploy, provider mutation, credential change, or other protected effect is authorized by this plan.

---

### Task 1: Add failing V4 integration qualification

**Files:**
- Create: `tools/qualification/test_bt2_adversarial_collaboration_posture_v1.py`

**Interfaces:**
- Consumes: exact uploaded posture digest and current V3 native package.
- Produces: executable qualification that requires the V4 package and rejects wording/binding/installation-status drift.

- [ ] **Step 1:** Write tests for missing V4 files, exact posture SHA/text, instruction-level operational coverage, manifest hashes, install language, and V3 immutability.
- [ ] **Step 2:** Run `python -m unittest tools.qualification.test_bt2_adversarial_collaboration_posture_v1 -v` and require failure because V4 is absent.
- [ ] **Step 3:** Do not relax assertions to obtain green; implement the missing V4 package in Task 2.

### Task 2: Build the native V4 package

**Files:**
- Create: `native/project/BT2_ADVERSARIAL_COLLABORATION_POSTURE_V1.md`
- Create: `native/project/PROJECT_INSTRUCTIONS_V4.md`
- Create: `native/project/PROJECT_FILES_MANIFEST_V4.json`
- Create: `native/project/INSTALL_V4.md`

**Interfaces:**
- Consumes: V3 instructions as predecessor and the exact uploaded posture.
- Produces: collision-safe source package installable into the BT2 ChatGPT Project.

- [ ] **Step 1:** Copy the uploaded posture exactly, preserving its SHA-256.
- [ ] **Step 2:** Derive V4 instructions from V3 and insert a compact complete operational form under a BT2-wide mandatory behavior section; the exact supplied wording remains separately bound as the Project file.
- [ ] **Step 3:** Add explicit trigger/non-trigger, authority-separation, and evidence-state language without altering the supplied normative posture.
- [ ] **Step 4:** Create V4 manifest bindings from actual Git blob/SHA-256 values and document the V3 predecessor.
- [ ] **Step 5:** Create install instructions that replace Project Instructions with V4 and add the collision-safe posture file while preserving V1-V3 material.
- [ ] **Step 6:** Run the focused qualification and require PASS.

### Task 3: Adversarially challenge the package

**Files:**
- Modify as required by findings: V4 package and focused qualification only.

**Interfaces:**
- Consumes: exact V4 candidate head.
- Produces: defect findings bound to exact source and repaired candidate.

- [ ] **Step 1:** Attack scope ambiguity, quiet-repair escape hatches, direct-command interaction, role bypasses, authority amplification, evidence-state collapse, stale-manifest risk, and downgrade-to-V3 behavior.
- [ ] **Step 2:** Route the exact candidate head to Two over the Chat Communication Bus with `requires_reply: true` for independent hostile review.
- [ ] **Step 3:** Patch every load-bearing finding with the smallest coherent change and add or strengthen a regression assertion before/with the fix.
- [ ] **Step 4:** Re-run focused qualification after every patch round.

### Task 4: Verify and package exact-head evidence

**Files:**
- Modify: PR #23 description/status evidence as needed.
- Create/update: Bus review/qualification receipt on One's writer branch.

**Interfaces:**
- Consumes: final reviewed branch head.
- Produces: exact-head source/build qualification with installation and behavior states kept separate.

- [ ] **Step 1:** Run focused qualification from a clean exact-head checkout.
- [ ] **Step 2:** Run static JSON parsing, SHA-256 recomputation, `git diff main...HEAD`, and confirm V3 artifacts are unmodified.
- [ ] **Step 3:** Read back PR head and all durable Bus writes.
- [ ] **Step 4:** Report `SOURCE_CANDIDATE/QUALIFIED` only for what is proved; leave `PROJECT_INSTRUCTIONS_INSTALLED` and `BEHAVIOR_VERIFIED` not established until an authorized Project install and fresh-chat acceptance occur.
