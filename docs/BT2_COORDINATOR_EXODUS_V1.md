# BT2 Coordinator — Exodus Interface V1

Status: Patrick-directed source candidate. No merge/cutover implied.

The `BT2 Coordinator` is one of exactly three intended persistent ChatGPT interfaces after the Exodus. It is an engineering-portfolio interface, not the durable identity or memory of One, Two, Three, Four, Noah, Hephaestus, Parallax, or any other worker.

Workers are instantiated from durable GitHub/Bus state and may execute in ephemeral terminals. No worker requires a permanent ChatGPT conversation.

The coordinator fresh-checks current repositories and assignments, dispatches bounded work, collects durable outputs, and surfaces blockers/decisions to Patrick. Source PRs stay canonical in their owning repositories; non-PR work-bearing coordination uses the Bus.

The interface name grants no merge, deployment, provider, credential, permission, or other protected-effect authority.

A fresh replacement chat is considered valid when it can reconstruct active BT2 work from this repository, owning project repositories, and the Bus without opening retired worker chats.
