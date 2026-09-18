# TheoryLab v0 design

TheoryLab separates four objects that are easy to blur together.

## 1. Executable component

A node is a reusable mechanism with explicit ports, parameters, an executor and narrow claims. It is analogous to a PerceptionLab/ComfyUI component, except the contract also records scientific role and provenance.

## 2. Theory graph

A theory is not merely a connected workflow. It declares a question, falsifiable hypothesis, assumptions, experiments, attackers, measurements, gates and interpretation boundaries.

The graph is executable, but execution alone does not turn a mechanism into evidence. Evidence is produced by a declared comparison.

## 3. Evidence receipt

Receipts are immutable run artifacts. They keep measurements separate from interpretation and limitations. Theory definitions may survive even when a receipt kills their current claim.

## 4. Discovery history

History records *attempts to discover*, not only successful mechanisms. Each attempt has a parent, cost, outcome and score. That tree can be replayed by alternative exploration policies without rerunning the underlying experiments.

This layer is inspired by **Dream-RSI: Recursive Self-Improvement through Evolving Worlds** (Zheng et al., 2026), whose central move is to use completed discovery trees as replay simulators for improving exploration policy. TheoryLab v0 intentionally preserves the same limitation: replay only reveals outcomes that were actually recorded. It does not hallucinate counterfactual experiment results.

## Why the layers are separate

```text
node library         what can be composed
      ↓
theory graph         what is being claimed/tested
      ↓
evidence receipt     what happened in the run
      ↓
discovery history    how the search itself unfolded
```

Future systems may learn policies over the fourth layer while proposing new compositions in the first two layers.

## AI-first constraints

- Stable JSON entry point at repository root.
- Schemas are plain JSON Schema, not UI-derived state.
- Node IDs and ports are stable machine identifiers.
- The browser is a microscope over the same files used by the runtime.
- No scientific fact exists only in HTML presentation code.
- Replaying history cannot manufacture unseen outcomes.
- Negative controls and failed gates remain available to future theory generation.

## v0 non-goals

- autonomous scientific truth discovery;
- arbitrary Python execution supplied by untrusted theory files;
- automatic import of hundreds of repositories;
- learned exploration policy optimization;
- a claim that the seed noncommuting operator is a biological model.

Those are later gates, not assumptions hidden in the first implementation.
