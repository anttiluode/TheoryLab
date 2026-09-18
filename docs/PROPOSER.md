# TheoryLab v1 proposer

The v1 proposer is intentionally less clever than the AI systems TheoryLab is meant to support.

Its job is to establish a **grounded baseline**:

1. normalize the words in a scientific question;
2. classify the question into one of a few experiment families;
3. rank curated Genealogy mechanisms by overlap plus family-specific priors;
4. rank negative results / attacker rules separately;
5. emit a conceptual graph, experiment plan and predeclared gates;
6. state which executors are still missing.

The proposer does **not** invent experimental outcomes, mark its own hypothesis as supported, or silently convert a historical repository into an executable adapter.

## Why deterministic first?

A future language-model proposer should be compared against something auditable. If an AI selects a surprising cross-lineage combination, TheoryLab should be able to ask whether that combination is better than a simple retrieval-and-template baseline rather than merely admiring the prose.

## Families

- `basis_alignment` — endogenous discovery of computational/adaptation coordinates.
- `active_identification` — paid interventions versus random/fixed/passive controls.
- `causal_decoding` — extraction of compact executable abstractions.
- `structure_function` — fine structure versus coarse summary attackers.
- `computational_matter` — address → resident dynamics → persistent write → later probe.
- `generic` — matched simple baseline when none of the above dominates.

## CLI

```bash
python -m theorylab propose "Can useful computational coordinates self-align with persistent write?"
python -m theorylab propose "When does active probing beat a fixed cover after probe cost?" --json
python -m theorylab propose "Can we decode a compact causal program from a trained recurrent network?" --output proposal.json
```

## Promotion boundary

`theorylab-proposal/v1` and `theorylab-theory/v0` are different formats on purpose.

A proposal may reference mechanisms that are only historical/epistemic objects. An executable theory may reference only actual node/runtime contracts. Promotion therefore requires adapter work and another validation step.

This prevents the central category error the project is trying to avoid:

```text
a plausible connection
        ≠
an executable mechanism
        ≠
an experimental result
```
