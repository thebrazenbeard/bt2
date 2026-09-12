# Module 02 — Evidence and Authority Ladder

**Learning objective:** Prevent false promotion between identity, currentness, execution, authorization, custody, device behavior, and release authority.

## Core model

Different evidence objects prove different propositions. Do not silently collapse them.

Examples of distinct evidence classes:

- proposal or specification text;
- source bytes;
- content hash;
- Git blob;
- Git tree;
- Git commit;
- mutable Git ref/branch;
- CI/test result;
- environment approval/protection evidence;
- built artifact;
- provider readback;
- operator screenshot/presentation;
- device observation;
- target-qualified manager-effect evidence;
- independent cessation evidence;
- release/acceptance verdict;
- active writer/effect lease.

A valid review states a **claim ceiling**: the strongest proposition actually supported by the evidence in hand.

## Trainee task

Create an evidence ladder for every evidence class above. For each item state:

1. what it can prove;
2. what it cannot prove;
3. what additional evidence is needed to promote the claim one level further.

Then classify and correct these claims:

1. "The commit hash matches, therefore the branch is currently at that commit."
2. "The workflow passed, therefore the device behaved correctly."
3. "The candidate receipt says `replay_safe=true`, therefore recovery is authorized."
4. "The environment approved the job, therefore BT2 governance authorized publication."
5. "The exact source labels a timing value `qualified`, therefore target timing semantics are established."
6. "The screenshot shows `Stopped`, therefore the exact manager STOP operation completed."
7. "A file exists at the expected Drive path, therefore this is the exact frozen source revision."
8. "A role can execute a database function, therefore that role is authorized to perform the protected transition."

For each, provide the corrected strongest claim ceiling.

Finally, create one new cross-plane false-authority example that mixes at least three evidence classes.

## Pass criteria

PASS requires:

- Clear distinction among immutable content identity, mutable currentness, authorization, execution, and observation.
- Explicit recognition that hashes/commits do not prove current branch state.
- Explicit recognition that CI/provider evidence does not prove device effects.
- Explicit rejection of self-attestation as authority.
- Explicit separation of environment/platform permission from BT2 governance authority.
- Explicit separation of presentation/screenshot evidence from underlying manager/effect evidence.
- A defensible claim ceiling for every scenario.
- A novel three-plane counterexample with a correct correction path.

Promotion beyond the available evidence is a critical failure.
