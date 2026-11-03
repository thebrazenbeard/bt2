# Historical export routing candidates — source-only

`routing_candidates.propose_route()` is a **pure, non-publishing review aid**.
It accepts an already-reviewed material-class label, not a filename or payload,
and returns possible repository owners for a *future sanitized derivative*.
Every output hard-codes `publication=HOLD`, `rights=UNVERIFIED`,
`currentness=HISTORICAL_NOT_INSTALLED`, and
`raw_material_git_eligible=False`. An unrecognized class yields no candidate.

Examples (synthetic class labels only):

| Class | Possible owner(s) for *reviewed derivative* | Why it is still on HOLD |
| --- | --- | --- |
| `historical_project_packet` | `vera-control-plane`, `bt2` | Historical instructions cannot become installed Project/runtime authority; verify the exact owning contract first. |
| `semantic_research` | `semanticatlas` | Old semantic labels are research evidence, not current canon. |
| `training_evaluation` | `model-training`, `labyrinth` | Rights, evaluator custody, held-out separation, source comparisons and positive learning claims remain unverified. |
| `visual_reference` | `selfimage` | File-level image/model rights, adult status where applicable, and asset privacy require independent review. |
| `temporal_research` | `temporal` | Timestamp records are producer claims, not currentness or trusted history. |
| `private_conversation`, `model_artifact`, `executable_bundle`, `mixed_archive` | None | Raw private, weighted, executable and heterogeneous material is not a Git population candidate. |
| Unknown or a filename | None | Classify privately first; never route by name. |

The list is **not authoritative repository ownership**. It is grounded in the
current READMEs at research time and must be refreshed against exact live Git
heads, local `AGENTS.md`, scope, licensing and code before any PR. A source
comparison, source-level tests and independent review still do **not** grant
publication or training rights. The separate
`historical_adjudication_v1.schema.json` remains the private review record;
this router does not mutate or validate it.

Keep private filenames, paths, SHA-256 values, conversations, duplicate groups,
credentials, extracted archive bodies and real review records off public Git.
Do not use this module to read the OneDrive Downloads source; the source scanner
has independent Windows/WSL/CFAPI qualification holds.
