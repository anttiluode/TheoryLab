# TheoryLab AI interface

Start with `theorylab.json`. Do not infer hidden interfaces from filenames when a contract is available.

## 1. Discover nodes

Read `nodes/catalog.json`. A node definition has:

- `id`: stable machine identifier;
- `role`: scientific role (`mechanism`, `world`, `source`, `intervention`, `learner`, `observer`, `attacker`, `evaluator`, `transform`);
- `inputs` / `outputs`: named semantic ports;
- `parameters`: defaults and descriptions;
- `executor`: runtime callable identifier;
- `provenance`: origin repository / evidence / notes;
- `claims`: deliberately narrow statement of what the node implements.

Compatibility begins with port types, not node names.

## 2. Compose a theory

Write a JSON document matching `schemas/theory.schema.json`.

A useful candidate theory should contain at least:

- one scientific `question`;
- one falsifiable `hypothesis`;
- explicit `assumptions`;
- node instances and typed edges;
- at least one control or attacker when a stronger explanation is plausible;
- measurements;
- one or more gates that can fail.

Prefer changing one causal ingredient at a time.

## 3. Validate before running

```bash
python -m theorylab validate path/to/theory.json
```

Validation checks node IDs, instance IDs, ports, type compatibility, experiment references, measurements, attackers, and gates.

## 4. Execute

```bash
python -m theorylab run path/to/theory.json --json
```

Each experiment gets isolated node state. Protocol phases preserve state *within* an experiment, allowing a theory to test history-dependent mechanisms.

Phase `inputs` inject values directly into instance input ports. Graph edges supply all other inputs.

## 5. Interpret receipts conservatively

A passing gate means only that the declared synthetic test passed. Use the receipt fields to separate:

- observed measurements;
- gate outcomes;
- supported/limited/killed claims;
- limitations and provenance.

Do not promote a calibration result into a biological or physical claim unless the theory explicitly tests that claim.

## 6. Append discovery history

A discovery attempt should record:

- parent attempt;
- theory/variant identifier;
- score;
- execution cost;
- outcome (`support`, `limit`, `kill`, `inconclusive`);
- short observation.

The history is a realized tree, not a generative world model. Replay may reorder traversal of recorded branches, but it must not fabricate outcomes for branches that were never run.

## 7. Replay exploration

```bash
python -m theorylab replay --policy breadth_first --budget 6
python -m theorylab replay --policy depth_first --budget 6
python -m theorylab replay --policy best_first --budget 6
```

This is the first Dream-RSI-inspired layer: accumulated discovery is reusable as an environment for evaluating *where to spend search*, distinct from the scientific mechanisms being tested.

## 8. Future import rule

When importing from Genealogy, prefer the smallest surviving mechanism plus its known attackers, not the entire repository story.

When importing from PerceptionLab, adapt an existing executable node only when its runtime contract is deterministic enough to test and its dependencies are explicit.

A textual insight can enter as an epistemic constraint even when no executable implementation exists yet.


## 9. Retrieve historical mechanisms and constraints

Before composing from scratch, read:

- `knowledge/genealogy_components.json` — curated reusable objects from 15 well-characterized repositories;
- `knowledge/constraints.json` — negative results, matched attackers and epistemic boundaries;
- `knowledge/open_questions.json` — unresolved discriminators.

The component import is **not** an executable node catalog. A historical component may be conceptually relevant while still needing an adapter.

Never drop the `boundary` field when reusing a component. The boundary is part of the reusable scientific object.

## 10. Generate a grounded proposal

Use:

```bash
python -m theorylab propose "YOUR QUESTION" --json
```

The proposer returns a `theorylab-proposal/v1` object containing a deterministic question-family classification, ranked historical components, ranked constraints/attackers, a conceptual graph, a candidate experiment, predeclared gates, and an explicit execution status with missing executors.

A proposal is not a receipt. Do not cite its hypothesis as an observed result.

## 11. Promotion rule: proposal → executable theory

Promote a proposal only after every required mechanism has an executable adapter or declared external runner, ports and state semantics are explicit, matched attackers exist, the executable graph validates, and gates are fixed before the measured run.

If any required executor is missing, preserve the proposal as `plan-only`.

## 12. Discovery-policy separation

TheoryLab now has two different search spaces:

```text
composition search
    choose mechanisms + attackers + experiments
    may propose combinations never run before

replay search
    choose where to spend attention in recorded discovery history
    may NOT invent outcomes
```

Do not mix them. A composition proposal becomes part of replay history only after it is actually executed and an outcome is recorded.

## 13. First completed promotion

The `basis_alignment` family is no longer plan-only.

For the canonical question:

```text
Can useful computational coordinates and persistent write self-align through experience?
```

the proposal now returns:

```text
execution.status      ready
execution.executable  true
theory_path           theories/learned_basis_alignment.json
```

Run the promoted theory rather than treating the proposal as evidence:

```bash
python -m theorylab run theories/learned_basis_alignment.json --json
```

The committed v2 receipt is `receipts/learned_basis_alignment.v2.json`.

The PASS resolves only the constructed batch-covariance case. The remaining high-value discriminator is online/local coordinate learning under basis drift.
