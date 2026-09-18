# V2 predeclared gate — learned adaptation coordinates

This file freezes the first proposal-to-experiment promotion **before** the measured CI run is interpreted.

## Question

Can useful computational coordinates and persistent-write coordinates self-align through experience rather than being supplied?

## Why this gate exists

`FrequencyAddressedState-dependentOperatorComposition` v4 made a same-fast-matrix distinction: arbitrary visible-coordinate adaptation produced a weak written-operator family while modal-aligned adaptation recovered a richer one. That result supplied the useful coordinates.

TheoryLab v1 independently retrieved that unresolved boundary and proposed three missing executable objects:

1. matched recurrent world;
2. coordinate learner;
3. operator-family metrics.

V2 implements exactly those objects rather than changing the question.

## Matched world family

Eight deterministic 4-state dense symmetric recurrent worlds use the same eigenvalue spectrum

```text
0.94, 0.79, 0.54, 0.28
```

with signed/permuted Hadamard hidden bases. White process noise generates passive trajectories; only the resulting covariance is handed to the learned arm.

The Hadamard construction is deliberately harsh for visible-coordinate energy addressing: every hidden address has equal squared energy in every visible coordinate. This makes the visible attacker known to collapse toward rank one.

That choice also limits the claim: this is an **existence/learnability calibration in a favorable PCA-identifiable family**, not a generic dense-RNN benchmark.

## Arms

All arms share the same fast matrices, dimensions, addresses, write law and state budget.

- **learned** — deterministic covariance PCA by power iteration; reads covariance only.
- **visible** — identity coordinate basis.
- **fixed random** — deterministic orthogonal basis, independent per world.
- **oracle** — supplied hidden modal basis; positive upper control.
- **frozen write** — oracle coordinates with persistent write gain set to zero.

## Write/operator test

For each address, squared activity in the candidate coordinate basis weights an orthogonal family of rank-1 write atoms. The written operators are then measured without using the hidden basis for the operator-rank or composition calculations.

Diagnostics:

- permutation/sign-invariant basis alignment;
- addressed activity effective rank;
- written-operator family effective rank;
- write selectivity;
- normalized A→B versus B→A composition separation.

The composition score is the Frobenius separation of the two composed operators, equivalent to a complete canonical probe bank. It is a functional composition readout, but **not an external semantic task**.

## Frozen gates

The measured run passes only if all of the following hold:

1. worst learned operator rank > best fixed-random operator rank over all eight worlds;
2. worst learned composition score > best fixed-random composition score;
3. learned basis alignment > 0.95 in every world;
4. learned median operator rank > visible median;
5. learned median composition > visible median;
6. learned median operator rank <= oracle median;
7. learned median composition <= oracle median;
8. frozen-write composition = 0.

No gate is based solely on similarity to the oracle basis.

## Interpretation boundary

A PASS would establish only:

> In this constructed recurrent family, passive covariance experience is sufficient to discover coordinates that make the downstream persistent-write mechanism almost as separable as when the modal basis is supplied.

It would **not** establish local biological learning, generic nonlinear RNN self-organization, or autonomous theory discovery.

The next attacker after a PASS is obvious: replace batch covariance eigendecomposition with an online/local Oja/Sanger-style learner and then introduce coordinate drift.
