# Adapting external projects into TheoryLab

## From PerceptionLab

Prefer a small executable node whose inputs/outputs can be stated without GUI state. Record nonstandard dependencies and runtime assumptions explicitly. A visualizer may become an `observer`; a dynamical substrate may become a `world` or `mechanism`; a perturbation source may become an `intervention`.

Do not automatically promote every PerceptionLab node into a scientific mechanism. Many are utilities, displays, bridges or exploratory toys.

## From Genealogy

Genealogy has two useful exports:

1. **surviving executable mechanism** → candidate TheoryLab node;
2. **negative result / unresolved question / correction** → epistemic constraint or attacker recipe.

A Genealogy edge such as `corrects` or `converges` is not a signal wire. It should remain provenance unless a concrete data contract exists between the mechanisms.

## From a repository

A good node adapter answers:

- What is the smallest mechanism worth reusing?
- What are its actual inputs and outputs?
- What state persists between calls?
- What intervention resets or perturbs it?
- Which claims did the source repository actually establish?
- Which attacker already narrowed the claim?
- What must not be inferred from the adapter?

The desired result is a reusable scientific component, not a wrapper around an entire repository.
