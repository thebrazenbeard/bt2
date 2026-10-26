# WeKnora read-only retrieval boundary (candidate)

Upstream source contract: [Tencent/WeKnora at `26fe2a08`](https://github.com/Tencent/WeKnora/tree/26fe2a08e9f63ae34c79584957e4f375408dea4a).

This standalone standard-library Python adapter calls `POST /api/v1/knowledge-bases/:id/hybrid-search` without reranking. It requires an explicit local knowledge-base ID allowlist, validates every returned hit's KB, preserves source/document/chunk identity, and returns raw WeKnora score rather than a fabricated similarity percentage. It makes no training, neural-weight persistence or shared-representation claim.

```bash
python -m unittest discover -s integrations/weknora -p 'test_*.py' -v
```

Production configuration should use a read-only, KB-scoped WeKnora API key and an authenticated internal HTTPS endpoint. Plain HTTP is accepted for loopback only. The adapter refuses redirects to avoid forwarding credentials. Retrieval text is untrusted input to downstream models; treat citations as pointers requiring source readback, not proof that a model's answer is true.

The current endpoint response does **not** independently attest the exact
corpus snapshot, index generation, chunker/embedding versions, ACL policy
revision, or document-content digest. This source-only adapter therefore must
not be used as a durable evidence epoch or an authoritative HC memory source.
Those identities require a separately verified operator/index manifest and
readback before the retrieved data can participate in a qualified experiment.

## SPM activation contract

`spm_gate.py` consumes a structurally valid WeKnora retrieval batch, checks
the requested KB and unique document/chunk identities, and derives the exact
SPM `memory_adapter_active(count)` source-level decision. `select_spm_view`
revalidates the batch at activation time and calls SPM's real
`view_for_retrieval(count)` method. An empty batch selects
the base view; a nonempty batch selects the gated adapter view.

This **does not** transfer retrieved text into SPM memory, execute the Qwen
weights, or qualify SPM's hardened successor runtime. A caller could forge a
typed batch and the index/ACL epoch remains unverified, so the receipt is
explicitly `UNATTESTED_RETRIEVAL_GATE_ONLY`. A retrieved rank is not a
chronological memory observation. The source-bound SPM adapter's historical
behavioral result and noisy-memory failure must be requalified before a live
effectful integration.

To test this adapter with the pinned `thebrazenbeard/spm` checkout:

```bash
PYTHONPATH=/path/to/spm/src python -m unittest discover \
  -s integrations/weknora -p 'test_*.py' -v
```

**Evidence boundary:** Tests use an in-process HTTP fixture. No WeKnora service, real vector model, data ingestion, ACL integration, or end-to-end retrieval quality benchmark has run. The source commit is a compatibility target, not verification of a deployed WeKnora version.

Integration should run four controlled variants with the same model and held-out queries: no context, keyword-only search, WeKnora hybrid search, and WeKnora hybrid plus rerank. Record retrieval recall@k/MRR, citation correctness, unsupported assertions, latency P50/P95, indexing freshness, and source/weights/config hashes. Do not infer parameter learning from improved answers under retrieval.
