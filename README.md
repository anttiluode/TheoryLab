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
