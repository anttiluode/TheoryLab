# V3 result — online coordinate continuation

The v2 result left one explicit boundary: batch covariance could recover useful coordinates in a static world, but it did not show that a learner could keep those coordinates useful while the resident computation moved.

V3 froze that discriminator before measurement and ran it in CI.

**Classification: PASS, narrow continuation result.**

## Headline

Across eight matched slowly drifting recurrent worlds, an online Sanger/GHA learner beat the identical learner frozen before drift in **8 / 8 worlds** on all three paired diagnostics:

- final hidden-basis alignment;
- written-operator effective rank;
- A→B versus B→A composition separation.

The stronger attacker also failed: a **perfect initial modal basis left stale** became worse than the imperfect basis that kept adapting.

| final metric | online Sanger | frozen Sanger | perfect initial basis left stale | moving oracle |
|---|---:|---:|---:|---:|
| basis alignment, median | **0.933199** | 0.856282 | 0.711595 | 1.000000 |
| written-operator rank, median | **3.826453** | 3.644081 | 2.844856 | 4.000000 |
| composition score, median | **0.646431** | 0.576472 | 0.476548 | 0.707107 |

All **7 / 7 predeclared gates passed** on Python 3.11 and 3.12.

## What changed from v2

```text
v2: passive history -> batch covariance -> static learned basis -> near-oracle writable operator family
v3: streaming state -> online Sanger/GHA -> hidden basis moves -> learner keeps moving -> later write coordinates stay useful
```

The important attacker is not merely another random basis. It is a basis that was **exactly right in the past**.

After the supplied 1.20-radian drift, that stale oracle ends at operator rank **2.844856** and composition **0.476548**, while the continuing learner retains **3.826453** and **0.646431**.

That is the concrete version of the ThirdWay sentence:

> **Identity is continuation, not location.**

Within this synthetic world, being the right computational mode in the past is not enough. The useful identity has to follow the moving computation.

## What this does not establish

The recurrence is linear and symmetric. Drift is smooth and slow. The learner receives the full state stream. Periodic Gram-Schmidt stabilization means the implementation is online but not strictly synapse-local. The write law and final composition audit remain synthetic.

Most importantly, **no delayed credit moves yet**.

So v3 tests coordinate continuation, not the stronger ThirdWay T2 claim about transporting delayed eligibility or credit with that continuation.

## Next discriminator

Keep the same drifting substrate and add delayed task consequence. Compare:

```text
tracked coordinates + transported eligibility
tracked coordinates + stale eligibility
frozen coordinates + stale eligibility
moving-oracle identity + oracle credit
```

The key attacker is subtle: both adaptive systems may correctly track the current basis, but one leaves its credit trace in the coordinates where the computation used to live.
