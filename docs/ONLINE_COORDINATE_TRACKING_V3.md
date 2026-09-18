# V3 predeclared gate — online coordinate continuation

This gate is frozen before reading its CI measurements.

## Question

Can a local online learner preserve useful computational identity when the resident coordinate system itself drifts?

## Handoff from v2

V2 showed that a batch covariance learner can recover useful write coordinates in a static PCA-friendly recurrent family. Its explicit next discriminator was online/local learning under basis drift.

V3 changes **only that boundary**.

## World

Eight 4-state symmetric recurrent worlds retain the v2 eigenvalue spectrum:

```text
0.94, 0.79, 0.54, 0.28
```

The hidden modal basis is initially a signed/permuted Hadamard basis. After 2,000 stationary steps it rotates smoothly for 5,000 steps, followed by 500 steps at the final orientation.

The primary two-dimensional mode plane rotates by **1.20 radians**; the second plane rotates at 0.7× that angle.

## Learners / attackers

- **online Sanger** — streaming generalized-Hebbian update throughout pretrain and drift; eta 0.006; periodic Gram-Schmidt stabilization every 20 samples.
- **frozen Sanger** — identical initialization, stream, update rule and pretrain; stops adapting exactly when drift begins.
- **stale initial oracle** — starts with the exact modal basis but never moves. This is the direct “identity = original location” attacker.
- **moving oracle** — current hidden basis at final audit; upper positive control.

The online update is not given the drift angle, hidden basis or fast matrix.

## Evaluation

At the final orientation, every basis is inserted into the same persistent-write/operator audit used by v2.

Measurements:

- hidden-basis alignment;
- written-operator effective rank;
- normalized A→B vs B→A composition separation.

A panel-dominance evaluator counts per-world wins of online versus frozen Sanger.

## Frozen gates

1. online alignment beats frozen in at least **7 / 8** worlds;
2. online operator rank beats frozen in at least **7 / 8**;
3. online composition beats frozen in at least **7 / 8**;
4. online median operator rank beats the **perfect-but-stale initial oracle**;
5. online median composition beats the stale initial oracle;
6. online median operator rank does not exceed the moving oracle;
7. online median composition does not exceed the moving oracle.

## Claim boundary

A PASS supports only a narrow continuation statement in this synthetic moving-basis world. Sanger/GHA with periodic orthogonalization is online but not strictly synapse-local, and no delayed reward/eligibility is transported.

A PASS therefore points directly to the next ThirdWay-derived question:

> Does delayed credit have to move with the learned computational coordinates, or is tracking the coordinates themselves enough?
