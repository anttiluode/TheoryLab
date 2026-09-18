# V2 result — learned adaptation coordinates

The first TheoryLab proposal that reached `execution.status=ready` was run in CI against its frozen predeclared gate.

**Classification: PASS, narrow existence/learnability calibration.**

## Headline

The learned arm saw only covariance estimated from passive trajectories. Across eight matched recurrent worlds, its worst written-operator rank and composition score exceeded the best fixed-random-basis control.

| quantity | learned | fixed random | visible | oracle |
|---|---:|---:|---:|---:|
| operator rank, median | **3.999918** | 2.385885 | 1.000000 | 4.000000 |
| operator rank, worst learned / best random | **3.995258** | 3.768821 | — | — |
| composition score, median | **0.705018** | 0.352504 | 0.000000 | 0.707107 |
| composition, worst learned / best random | **0.695154** | 0.588275 | — | — |
| hidden-basis alignment, median | **0.997784** | — | 0.250000 | 1.000000 |
| hidden-basis alignment, minimum | **0.987275** | — | 0.250000 | 1.000000 |

With oracle coordinates but write gain frozen to zero, composition score was exactly **0**.

All **8 / 8 predeclared gates passed** on Python 3.11 and 3.12 CI.

## What this establishes

The v4 ancestor had shown:

```text
same fast matrix
    visible-coordinate persistent write -> weak family
    modal-aligned persistent write       -> rich family
```

but the modal basis was handed to the mechanism.

V2 adds a narrow bridge:

```text
passive recurrent experience
        ↓
trajectory covariance
        ↓
learned basis
        ↓
persistent write in learned coordinates
        ↓
near-oracle written-operator family
        ↓
near-oracle A→B / B→A composition separation
```

So in this constructed family, **the useful coordinates do not have to be supplied explicitly**.

## Why this is not the end of the question

The world was intentionally chosen so covariance learning has a clean target: a symmetric linear recurrent system with distinct modal variances. The hidden basis is a signed/permuted Hadamard family, which also makes visible-coordinate energy addressing maximally bad.

The learner is batch/global PCA implemented by deterministic power iteration. It does not yet show:

- local Oja/Sanger plasticity can learn the same coordinates online;
- the useful coordinates can be tracked while the computation itself drifts;
- the mechanism survives nonlinear recurrent dynamics;
- the learned operator vocabulary transfers to an external semantic task.

Therefore the Genealogy/TheoryLab question should move from **open** to **partially resolved**, not closed.

## Next discriminator

Replace the covariance eigensolver with an online/local learner and then move the hidden basis after initial organization.

The next clean contest is:

```text
online transported learner
vs
online learner without identity transport
vs
frozen learned basis
vs
visible coordinates
vs
oracle moving basis
```

That is where the ThirdWay idea — *identity is continuation, not location* — finally becomes directly testable inside the theory-construction machine rather than merely cited as ancestry.
