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

## Status

v0 is infrastructure. It does **not** autonomously invent good theories yet. It makes the objects required for that next step explicit and executable.
