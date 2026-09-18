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
