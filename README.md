# TheoryLab

**Executable theory graphs for AI-assisted science.**

TheoryLab is a small, machine-readable laboratory for turning reusable mechanisms into executable hypotheses. It borrows the node-composition idea from PerceptionLab, the evidence/lineage discipline from Genealogy, and the history-as-replay idea from Dream-RSI.

The core rule is simple:

> A theory should be more than prose. Its mechanisms, assumptions, interventions, observers, attackers, and gates should be explicit enough for a machine to compose, run, falsify, and remember.

## v0

The first version deliberately stays small. It provides:

- a typed **node contract** for reusable scientific components;
- an executable **theory graph** format with protocols and gates;
- a persistent **evidence receipt** format;
- a **discovery history** tree that can be replayed under alternative search policies;
- a dependency-free Python runtime and validator;
- an AI-facing root manifest (`theorylab.json`) and interface guide (`AI.md`);
- a GitHub Pages microscope for browsing nodes, theories, receipts, and replay history.

The system distinguishes node roles rather than pretending every repository is the same kind of object:

`mechanism · world · source · intervention · learner · observer · attacker · evaluator · transform`

Negative results are first-class receipts. A failed theory can constrain future graph generation instead of disappearing.

## Quick start

```bash
python -m theorylab validate
python -m theorylab list
python -m theorylab run theories/noncommuting_write.json
python -m theorylab propose "Can useful computational coordinates and persistent write self-align through experience?" --json
python -m theorylab run theories/learned_basis_alignment.json --json
python -m theorylab replay --policy best_first --budget 4
python -m unittest discover -s tests -v
```

Open `index.html` locally or visit the GitHub Pages site after deployment.

## AI entry point

An agent should begin with [`theorylab.json`](theorylab.json). It names the schemas, catalogs, theory files, history file, runtime commands, and extension rules.

Then read [`AI.md`](AI.md). The intended loop is:

```text
retrieve compatible nodes
        ↓
compose candidate theory graph
        ↓
validate contracts
        ↓
run protocol
        ↓
apply attackers + gates
        ↓
write evidence receipt
        ↓
append discovery-history attempt
        ↓
replay history to improve where to search next
```

## Theory versus workflow

A workflow merely says what runs next. A TheoryLab graph additionally records:

- the scientific question;
- the hypothesis being tested;
- declared assumptions;
- provenance for reused mechanisms;
- explicit controls/attackers;
- measurements and predeclared gates;
- what observation would support, limit, or kill the claim.

That distinction is the point of the project.

## Current seed experiment

`theories/noncommuting_write.json` is intentionally tiny. Two addressed writes update a persistent operator. The theory compares `A -> B` with `B -> A` after both write sequences and tests whether the resulting probe response differs. A frozen-write attacker should collapse the difference.

This is not offered as a scientific result about biology or physical matter. It is a calibration target for the **TheoryLab machinery**: node execution, state persistence, multi-arm protocols, attackers, measurements, gates, receipts, and replay.

## Extension rule

New scientific components should enter as one of two things:

1. **Executable node** — has a stable input/output contract and an executor callable.
2. **Epistemic record** — a claim, negative result, provenance edge, or constraint that informs theory generation but is not itself executed.

Do not turn an entire repository into one opaque executable node when a smaller surviving mechanism can be exposed instead.

## Layout

```text
theorylab.json              machine entry point
AI.md                       agent protocol
schemas/                    JSON contracts
nodes/                      machine-readable node manifests
  catalog.json
theories/                   executable theory graphs
receipts/                   committed evidence receipts
data/discovery_history.json replayable discovery tree
theorylab/                  Python runtime / validator / replay engine
index.html + assets/         GitHub Pages microscope
tests/                      contract + execution tests
```

## v1 — Genealogy-grounded proposal generation

v1 imports a deliberately small slice of the current Genealogy ledger: **15 reusable objects** plus a separate bank of negative results, attacker rules, and unresolved questions.

The import does **not** claim that those 15 repositories are plug-compatible executables. Each record says:

- what the smallest reusable object appears to be;
- what survived its own attacks;
- what boundary or negative result must travel with it;
- where the record came from.

A deterministic proposer can now start from a natural-language scientific question:

```bash
python -m theorylab propose \
  "Can useful computational coordinates and persistent write self-align through experience?" \
  --json
```

The proposal contains a question family, ranked Genealogy mechanisms, ranked attackers/negative results, a conceptual graph, an experiment design, predeclared gates, and an explicit list of missing executors.

**A proposed graph is not silently treated as executable or evidential.** If required adapters do not exist, the proposal remains `plan-only`.

Current proposal families are learned basis/operator alignment, active mechanism identification, causal algorithm decoding, structure→function, computational matter/persistent medium, and a generic matched-attacker fallback.

The proposer is intentionally simple and auditable: deterministic token/family scoring over committed JSON. It is a calibration baseline for a future smarter theory constructor, not the final search policy.

## Status

v0 made theories executable. v1 makes a first part of the accumulated research history **machine-selectable for theory construction**, while keeping historical claims, negative results, proposal plans, executable theories, and empirical receipts as separate objects.

## v2 — the first proposal becomes an experiment

The exact basis-alignment question used to calibrate v1 no longer stops at `plan-only`.

TheoryLab implemented the proposal's three missing executors:

```text
matched recurrent world
coordinate learner
operator-family metrics
```

and promoted the proposal to [`theories/learned_basis_alignment.json`](theories/learned_basis_alignment.json).

The design and eight gates were frozen in [`docs/BASIS_ALIGNMENT_V2.md`](docs/BASIS_ALIGNMENT_V2.md) before the CI result was interpreted.

### Result

Across eight matched synthetic recurrent worlds:

| metric | learned | fixed random | visible | oracle |
|---|---:|---:|---:|---:|
| median written-operator rank | **3.999918** | 2.385885 | 1.000000 | 4.000000 |
| median composition score | **0.705018** | 0.352504 | 0.000000 | 0.707107 |
| median hidden-basis alignment | **0.997784** | — | 0.250000 | 1.000000 |

The stronger panel-wide comparisons also passed:

- worst learned operator rank **3.995258** > best random **3.768821**;
- worst learned composition **0.695154** > best random **0.588275**;
- minimum learned hidden-basis alignment **0.987275** > frozen 0.95 gate;
- oracle coordinates with persistent write disabled give composition score **0**.

All **8 / 8 predeclared gates passed** in Python 3.11 and 3.12 CI.

See [`results/BASIS_ALIGNMENT_V2.md`](results/BASIS_ALIGNMENT_V2.md) and the committed [`evidence receipt`](receipts/learned_basis_alignment.v2.json).

### Claim boundary

This is deliberately a **narrow existence/learnability result**. The matched worlds are symmetric linear systems with distinct modal variances and Hadamard-mixed visible coordinates, a setting favorable to covariance PCA. The learner is global batch covariance learning, not local biological plasticity.

The next unresolved gate is therefore no longer merely “can coordinates be learned?” It is:

> **Can an online/local learner track useful computational identity when the coordinates themselves drift?**

That is the first place where the older ThirdWay continuation/credit idea becomes a direct experimental component of TheoryLab.
