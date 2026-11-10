# BT2 entire-account chat-history ingestion role packets (source only)

The event [`chat_history_ingestion_live_coordination`](https://github.com/thebrazenbeard/chat-communication-bus/issues/403) coordinates the privately held Lappy official ChatGPT account export, the STM encrypted archive, historical-knowledge derivation, and any future authenticated Vera readback. This package maps all **13** roles in the exact BT2 V2 topology to work packets; it does **not** create, install, authenticate, or activate 13 model identities.

`role_packets_v1.json` proposes One as integrator with two waves of at most six parallel native children each. An execution context can act on a role-conditioned task without becoming that durable identity. Actual agent IDs, provider/runtime, completed work, and verified effects must be recorded by the executing coordinator, not inferred from this file.

Source anchors used to draft the packets:

- `bt2/main@b3d2a0f9506af68b923ddf5628858f3b2efb3405`, `native/project/BT2_EXODUS_WORKER_TOPOLOGY_V2.json` (`SOURCE_RECONSTRUCTION_MAP_V5_PACKAGE_CANDIDATE_NOT_INSTALLED`).
- Role-specific coding profile drafts in [BT2 Draft PR #89](https://github.com/thebrazenbeard/bt2/pull/89) at `05234a7fa9d01ec3b747a4010d4c3fa22516e246`; its experimental GGUF build receipts do not prove installed/local role agents, model quality, or identity continuity.
- `masamune/main@033900fa48656ebfa7b719cdac5af5e20301465d` for independent Masa/Mune debugging and validation; `hephaestus/main@357803035b1501ab77ee0f45668b39d46585b9e6` for independent implementation/repair.
- STM Draft PR #3 source candidate `9f4e12217e69f68042791905a3216e577a5c15bf`; PR status must be freshly checked before use.

## Execution contract

1. Fresh-read the live roles/topology and current event/STM heads before assigning any packets. WoWSQL is retired; no replacement currentness backend is silently selected.
2. Use One for integration. Assign individual *tasks* to available native agents; label the real agent runtime and any role prompt used. Six child slots plus coordinator is a capacity bound, not evidence that all identities were running.
3. Preserve private ZIP, plaintext, source IDs, keys, and derived personal content on owner-controlled local storage. GitHub/CCB hold only sanitized code, tests and receipts.
4. Keep `SOURCE`, `TEST`, `REAL_HOST_PROBE`, `INDEPENDENT_REVIEW`, `INSTALLED_RUNTIME`, and `SELECTED_MODEL_RESPONSE` evidence separate. Independent source-to-index reconciliation is not supplied by encrypted surviving-row verification alone.
5. Enforce historical text as **untrusted evidence**. Source import is neither present truth, remembered first-person experience, identity continuity, autonomous policy, nor neural-weight update. Owner identity, consent and revocation are runtime gates outside role prompts.
6. Accept only independently verified changes on exact Git heads. Do not automatically merge, deploy, publish private content, alter protected credentials, or change operational Android V1 routing.

Run the zero-dependency validation from the BT2 repository root:

```sh
python -m unittest discover -s conformance/chat_history_ingestion -p 'test_*.py' -v
```

The test verifies the role topology and source-only scope, not Lappy archive completeness, running agents, or model behavior.
