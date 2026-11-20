# BT2 Agent Assurance — source-only action-boundary candidate

**Status: source conformance / no runtime authorization.** This distinct BT2 conformance path was made to combine three earlier private engineering findings without publishing the underlying records or substituting for the existing memory/agent infrastructure.

## Observed problems being represented

1. Codex history: two failed turns had preserved user messages but no complete raw rollout, no indexed assistant answer, and no source/owner qualification for live repair. **Private messages and SQLite backups never belong in this repository.**
2. World model: contradictory or even matching source claims do not prove writer absence, object identity or permission. `AGREEMENT_UNQUALIFIED` is explicitly not a trusted observation.
3. SkillOpt: a frozen local coder model scored 8/12 instead of 5/12 on a newly authored, sealed near-domain holdout, but the stronger prompt missed two `BLOCK` labels, including a paired regression involving credential publication. It was rejected for promotion. These are research observations, **not** evidence of learning, long-term retention or a qualified grader.

## Public API

`gate_v1.decide(evidence)` consumes a typed, bounded source claim and emits a **nonexecuting recommendation**. `gate_v1.parse_evidence(bytes)` additionally rejects duplicate JSON keys, nonfinite values, extra fields and malformed types. Example:

```bash
python conformance/agent_assurance/gate_v1.py conformance/agent_assurance/fixtures/synthetic_partial_hold_v1.json
python -m unittest discover -s conformance/agent_assurance/tests -p 'test_*.py' -v
```

The included fixture is **synthetic** and deliberately contains no identifiable thread, account, credential, host path or recovered message.

The input model has `operation`, `proposed_action_id`, `model_label`, `world_model`, `recovery`, `skillopt` and `authority` fields. All fields are **untrusted**. The explicit action ID must be assigned by a separately qualified dispatcher, not inferred from a model's prose. Known hazardous action IDs are blocked, unknown action IDs held, incomplete recovery prevents archive/repair, conflicting observations hold, and critical SkillOpt failures prevent promotion. The only positive recommendation, `READ_ONLY_CANDIDATE`, still grants no effect: it is an option for a *separate* correctly authorized controller to assess.

**Every output has** `action_authorized=false`, `cleanup_authorized=false`, `qualification_granted=false`. No token, tool, runtime permission, receipt signing, model promotion, memory effect or database mutation is supplied. `authority.owner_approval_verified=true` in caller-supplied JSON does **not** prove approval.

## Scope and integration

The module is a small conformance adapter, not a parallel runtime and not a successor to BT2's source currentness governance. It preserves the existing distinction between `SOURCE`, `TEST`, `REAL_PROBE`, `INSTALL`, and `BEHAVIOR_VERIFIED`. It introduces **no source-of-truth state, no model training, no scheduler, no global memory writer and no network transport**. It deliberately does not read the source-only V7/V8 private trial ZIPs or any live SQLite source at runtime.

Before any real action controller could consume the recommendations, the owner would need a separate action schema controlled by the executable dispatcher, explicit scoped action authorization, authenticated evidence and runtime identity, an auditable hold/override protocol, recovery/rollback tests, and a live readback. These are **not accomplished here**.

## Falsifiers and limitations

- A model could mislabel a dangerous operation with a safe action ID. This module cannot solve that. Neither a safe decision nor a model label is execution authorization.
- Declared public keys, role IDs, approval booleans and source labels are all untrusted unless bound by a verified external authority.
- A failed-turn user-message packet is not a reconstructed conversation. Do not infer missing assistants' answers or user consent.
- Synthetic green tests do not prove correctness on real corrupted Codex data, across different operating systems, or under concurrent writes.
- Failure-closed status classification is intentionally coarse; operational actions require reviewed narrow adapters instead of relaxing this gate.

This candidate does **not** modify Engineer A's scanner, Engineer B's signal ingest or memory-lifecycle PRs, any production service, the private recovered packets, or Lantern V4 currentness.

## V1.1 hostile-input hardening (2026-11-20)

- Reject inconsistent structured claims: `COMPLETE_VERIFIED` requires at least one counted complete conversation **and** a source-row-verification claim; `NONE` cannot declare complete conversations; `REJECT_CRITICAL_BLOCK_MISS` requires a positive miss count. These are **syntactic consistency checks, not independent authentication** of the supplied labels or the real records.
- CLI input is restricted to an ordinary regular file and at most 100,000 bytes, with no-follow on POSIX and a precheck on Windows. The file may still change between path selection and open on systems without OS-level no-follow guarantees. The CLI outputs only `Rejected evidence input` for expected invalid inputs; the programmatic validators raise `ValueError`.
- The gate does not parse or execute arbitrary action payloads, does not bind the caller-selected action ID to a trusted tool call, and **never grants action authority**. A caller can lie about the action identity. Only a separately authenticated dispatcher could establish such a binding; this is not that dispatcher.
- The additional tests are `tests/test_ingress_hostile_v2.py` and `tests/test_cli_errors_v2.py`. The POSIX FIFO probe is skipped on Windows and must run on Linux hosted CI. Red/green development evidence lives in the draft PR and review notes.
