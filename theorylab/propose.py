from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .catalog import load_json

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")

STOP = {
    "a","an","and","are","as","at","be","by","can","do","does","for","from","how",
    "if","in","into","is","it","of","on","or","our","should","that","the","their",
    "then","this","to","under","we","what","when","where","which","with"
}

SYNONYMS = {
    "coordinates": "basis",
    "coordinate": "basis",
    "modes": "modal",
    "mode": "modal",
    "probing": "probe",
    "probes": "probe",
    "interventions": "intervention",
    "intervene": "intervention",
    "identify": "identification",
    "identified": "identification",
    "geometry": "structure",
    "morphology": "structure",
    "dendrite": "structure",
    "dendritic": "structure",
    "decode": "decoder",
    "decompile": "decoder",
    "algorithmic": "algorithm",
    "waves": "field",
    "oscillation": "field",
    "oscillations": "field",
    "memory": "persistent-state",
    "persistent": "persistent-state",
}

FAMILY_HINTS = [
    ("basis_alignment", {"basis","modal","operator","write","adaptation","alignment","frequency"}),
    ("active_identification", {"probe","intervention","identification","diagnose","bayesian","information","budget"}),
    ("causal_decoding", {"decoder","algorithm","abstraction","state-machine","causal","decompilation"}),
    ("structure_function", {"structure","compiler","transport","topology","branch","function"}),
    ("computational_matter", {"field","phase","frequency","fluid","matter","medium","wave"}),
]

FAMILY_TEMPLATES: dict[str, dict[str, Any]] = {
    "basis_alignment": {
        "hypothesis": "A learned coordinate system can become useful when it aligns persistent adaptation with resident dynamical directions rather than arbitrary visible coordinates.",
        "graph": [
            ("resident_dynamics", "world"),
            ("coordinate_learner", "learner"),
            ("persistent_write", "mechanism"),
            ("visible_coordinate_attacker", "attacker"),
            ("random_basis_attacker", "attacker"),
            ("oracle_basis_control", "attacker"),
            ("operator_observer", "observer"),
            ("held_out_composition_gate", "evaluator"),
        ],
        "edges": [
            ("resident_dynamics", "coordinate_learner", "observed trajectories"),
            ("coordinate_learner", "persistent_write", "learned coordinates"),
            ("resident_dynamics", "persistent_write", "addressed activity"),
            ("persistent_write", "operator_observer", "written operator"),
            ("visible_coordinate_attacker", "held_out_composition_gate", "matched control"),
            ("random_basis_attacker", "held_out_composition_gate", "matched control"),
            ("oracle_basis_control", "held_out_composition_gate", "upper-bound control"),
            ("operator_observer", "held_out_composition_gate", "measured operator family"),
        ],
        "experiment": "Hold fast dynamics, state budget, write budget and stimulation protocol fixed. Compare oracle modal coordinates, fixed random coordinates, visible-unit adaptation and learned coordinates. Evaluate address rank, written-operator rank, held-out A->B versus B->A effects and task transfer after fast-state settling.",
        "attackers": ["same-fast-matrix visible-coordinate adaptation", "fixed random basis", "oracle modal basis", "equal-state linear/modal control"],
        "gates": [
            "learned coordinates beat visible/random coordinates on held-out written-operator structure under equal budgets",
            "the learned-basis effect survives a task or composition readout rather than only a basis-similarity metric",
            "the result is below or comparable to the oracle in a way consistent with partial discovery rather than hidden extra capacity"
        ],
        "missing_executors": [],
        "theory_path": "theories/learned_basis_alignment.json"
    },
    "active_identification": {
        "hypothesis": "Active intervention is useful only where information gained per paid probe exceeds matched passive, random, balanced and fixed-cover alternatives.",
        "graph": [
            ("hidden_world", "world"),
            ("hypothesis_family", "mechanism"),
            ("active_selector", "learner"),
            ("balanced_random", "attacker"),
            ("fixed_cover", "attacker"),
            ("passive_observer", "attacker"),
            ("budget_meter", "observer"),
            ("identification_gate", "evaluator"),
        ],
        "edges": [
            ("hidden_world", "active_selector", "observations"),
            ("hypothesis_family", "active_selector", "candidate mechanisms"),
            ("active_selector", "hidden_world", "chosen intervention"),
            ("balanced_random", "hidden_world", "matched interventions"),
            ("fixed_cover", "hidden_world", "matched interventions"),
            ("passive_observer", "identification_gate", "baseline posterior/decision"),
            ("budget_meter", "identification_gate", "total cost"),
            ("hidden_world", "identification_gate", "ground truth after audit"),
        ],
        "experiment": "Sweep hidden-cause density and intervention price. Compare expected-information selection with balanced random, round-robin/fixed cover and passive observation at equal total cost.",
        "attackers": ["balanced random", "fixed cover", "passive observation", "probe-cost sweep", "dense-cause sweep"],
        "gates": [
            "active identification improves quality-cost frontier rather than raw sample count only",
            "advantage persists over balanced and fixed-cover controls in at least a declared region",
            "outside that region the system reports the boundary instead of universalizing the advantage"
        ],
        "missing_executors": ["generic intervention world adapter", "expected-information selector", "cost-density sweep evaluator"]
    },
    "causal_decoding": {
        "hypothesis": "A compact executable abstraction is earned only if it preserves behavior and declared intervention responses on held-out cases; otherwise the correct output may be NOT_IDENTIFIABLE.",
        "graph": [
            ("black_box", "world"),
            ("intervention_generator", "intervention"),
            ("candidate_decoder", "learner"),
            ("behavior_only_attacker", "attacker"),
            ("alias_attacker", "attacker"),
            ("counterfactual_evaluator", "evaluator"),
            ("description_length_evaluator", "evaluator"),
        ],
        "edges": [
            ("intervention_generator", "black_box", "counterfactual probes"),
            ("black_box", "candidate_decoder", "responses"),
            ("candidate_decoder", "counterfactual_evaluator", "executable surrogate"),
            ("behavior_only_attacker", "counterfactual_evaluator", "weaker explanation"),
            ("alias_attacker", "counterfactual_evaluator", "non-identifiable case"),
            ("candidate_decoder", "description_length_evaluator", "program"),
        ],
        "experiment": "Fit the smallest executable surrogate from observed/interventional traces, then freeze it and test held-out behavior, hidden-state interventions, disagreement cases and deliberately aliased worlds.",
        "attackers": ["behavior-only fit", "hidden-geometry clustering", "deliberately aliased hidden mechanisms"],
        "gates": [
            "surrogate preserves declared intervention behavior on held-out cases",
            "simpler behavior-only explanations fail where the causal surrogate succeeds",
            "aliased cases return NOT_IDENTIFIABLE rather than forced labels"
        ],
        "missing_executors": ["black-box trace adapter", "causal abstraction search", "counterfactual test harness"]
    },
    "structure_function": {
        "hypothesis": "Fine structure carries additional functional information only if matched coarse summaries fail to predict the downstream operator or response.",
        "graph": [
            ("paired_structure_generator", "world"),
            ("structure_compiler", "mechanism"),
            ("coarse_summary_attacker", "attacker"),
            ("world_embedding_attacker", "attacker"),
            ("downstream_probe", "intervention"),
            ("response_evaluator", "evaluator"),
        ],
        "edges": [
            ("paired_structure_generator", "structure_compiler", "fine structure"),
            ("structure_compiler", "downstream_probe", "compiled operator"),
            ("coarse_summary_attacker", "response_evaluator", "coarse prediction"),
            ("world_embedding_attacker", "response_evaluator", "intrinsic/world-space control"),
            ("downstream_probe", "response_evaluator", "held-out responses"),
        ],
        "experiment": "Generate paired structures matched on node/edge count, rank, spectral radius and coarse path statistics while changing fine placement/branch geometry. Compile each with the same forward law and test held-out transfer/nonlinear responses.",
        "attackers": ["matched coarse graph summaries", "matched spectrum", "pure world-space re-embedding", "nearest coarse neighbor"],
        "gates": [
            "fine structure predicts held-out functional differences after coarse summaries are matched",
            "pure re-embedding is separated from intrinsic metric/topology changes",
            "the claimed effect survives across multiple structures rather than one hand-picked pair"
        ],
        "missing_executors": ["paired-structure generator", "structure compiler adapter", "coarse-summary matcher"]
    },
    "computational_matter": {
        "hypothesis": "A small external address can select resident dynamics that write persistent matter, and the changed matter can directly alter a later probe.",
        "graph": [
            ("resident_medium", "world"),
            ("address_source", "intervention"),
            ("persistent_write", "mechanism"),
            ("later_probe", "intervention"),
            ("frozen_state_attacker", "attacker"),
            ("explicit_addressing_boundary", "attacker"),
            ("bounded_observer", "observer"),
        ],
        "edges": [
            ("address_source", "resident_medium", "space/frequency/phase address"),
            ("resident_medium", "persistent_write", "local activity"),
            ("persistent_write", "resident_medium", "slow state"),
            ("later_probe", "resident_medium", "query"),
            ("resident_medium", "bounded_observer", "later response"),
            ("frozen_state_attacker", "bounded_observer", "no-write control"),
            ("explicit_addressing_boundary", "bounded_observer", "supplied-coupling control"),
        ],
        "experiment": "Write with matched addresses, settle fast state, issue a later probe and compare against frozen-state, mismatched-address and no-coupling controls.",
        "attackers": ["frozen state", "mismatched frequency/phase/space", "explicit-coupling boundary", "ordinary filter-bank control"],
        "gates": [
            "later response depends on persistent state after fast transients decay",
            "address selectivity survives matched energy controls",
            "claims remain about the supplied synthetic medium unless emergent addressing is separately demonstrated"
        ],
        "missing_executors": ["field/medium adapter", "settling protocol", "matched address-control generator"]
    },
    "generic": {
        "hypothesis": "A candidate mechanism should survive a matched simpler explanation under a predeclared measurement and cost budget.",
        "graph": [
            ("candidate_mechanism", "mechanism"),
            ("simpler_attacker", "attacker"),
            ("intervention", "intervention"),
            ("observer", "observer"),
            ("gate", "evaluator"),
        ],
        "edges": [
            ("intervention", "candidate_mechanism", "probe"),
            ("candidate_mechanism", "observer", "response"),
            ("simpler_attacker", "gate", "matched baseline"),
            ("observer", "gate", "candidate result"),
        ],
        "experiment": "Define a narrow falsifiable witness, match the strongest simple attacker on state/cost/data budget, and evaluate held-out outcomes.",
        "attackers": ["matched simple baseline", "budget control"],
        "gates": ["candidate beats the matched attacker on the predeclared witness"],
        "missing_executors": ["question-specific mechanism adapter"]
    },
}


def _tokens(text: str) -> set[str]:
    out: set[str] = set()
    for raw in _TOKEN_RE.findall(text.lower()):
        if raw in STOP or len(raw) < 2:
            continue
        raw = SYNONYMS.get(raw, raw)
        out.add(raw)
        if "-" in raw:
            out.update(raw.split("-"))
    return out


def _family(question: str) -> str:
    tokens = _tokens(question)
    best = ("generic", 0)
    for name, hints in FAMILY_HINTS:
        score = len(tokens & hints)
        if score > best[1]:
            best = (name, score)
    return best[0]


def _component_score(question_tokens: set[str], component: dict[str, Any], family: str) -> tuple[float, list[str]]:
    haystack = " ".join([
        component.get("repo", ""),
        component.get("kind", ""),
        component.get("reusable_object", ""),
        component.get("survived", ""),
        component.get("boundary", ""),
        " ".join(component.get("tags", [])),
    ])
    tokens = _tokens(haystack)
    overlap = sorted(question_tokens & tokens)
    score = float(len(overlap))
    family_boosts = {
        "basis_alignment": {"genealogy.frequency_addressed_operator_composition", "genealogy.third_way", "genealogy.gax", "genealogy.anttis_neuron", "genealogy.not_so_simple_neuron"},
        "active_identification": {"genealogy.evox", "genealogy.another_odd_thing", "genealogy.rajoitusten_hierarkia", "genealogy.alternative_neuron"},
        "causal_decoding": {"genealogy.neural_algorithm_decoding", "genealogy.evox", "genealogy.another_odd_thing"},
        "structure_function": {"genealogy.operaattori", "genealogy.anttis_neuron"},
        "computational_matter": {"genealogy.information_flow", "genealogy.stored_medium_operator", "genealogy.artificial_cortex", "genealogy.dendrite_iterated_feedback"},
    }
    if component["id"] in family_boosts.get(family, set()):
        score += 2.0
    if component.get("confidence") == "high":
        score += 0.15
    reasons = overlap[:8]
    if component["id"] in family_boosts.get(family, set()):
        reasons.append(f"family:{family}")
    return score, reasons


def _constraint_score(question_tokens: set[str], constraint: dict[str, Any], family: str) -> tuple[float, list[str]]:
    tokens = _tokens(constraint.get("statement", "") + " " + " ".join(constraint.get("tags", [])))
    overlap = sorted(question_tokens & tokens)
    score = float(len(overlap))
    family_tags = {
        "basis_alignment": {"basis","alignment","operator","modal"},
        "active_identification": {"active-probing","intervention","cost","fixed-cover"},
        "causal_decoding": {"identifiability","decoder","causal-abstraction","intervention"},
        "structure_function": {"structure","geometry","spectrum","operator"},
        "computational_matter": {"field","frequency","phase","addressing"},
    }
    if set(constraint.get("tags", [])) & family_tags.get(family, set()):
        score += 1.0
    return score, overlap[:8]


def propose(question: str, *, top_components: int = 6, top_constraints: int = 4) -> dict[str, Any]:
    components_doc = load_json("knowledge/genealogy_components.json")
    constraints_doc = load_json("knowledge/constraints.json")
    family = _family(question)
    question_tokens = _tokens(question)

    ranked_components = []
    for item in components_doc["components"]:
        score, reasons = _component_score(question_tokens, item, family)
        ranked_components.append((score, item["id"], reasons, item))
    ranked_components.sort(key=lambda x: (-x[0], x[1]))

    ranked_constraints = []
    for item in constraints_doc["constraints"]:
        score, reasons = _constraint_score(question_tokens, item, family)
        ranked_constraints.append((score, item["id"], reasons, item))
    ranked_constraints.sort(key=lambda x: (-x[0], x[1]))

    chosen_components = [
        {
            "id": item["id"],
            "repo": item["repo"],
            "kind": item["kind"],
            "score": round(score, 3),
            "why_selected": reasons,
            "reusable_object": item["reusable_object"],
            "boundary": item["boundary"],
            "url": item["url"],
        }
        for score, _, reasons, item in ranked_components[:top_components]
    ]
    chosen_constraints = [
        {
            "id": item["id"],
            "kind": item["kind"],
            "score": round(score, 3),
            "why_selected": reasons,
            "statement": item["statement"],
            "source": item["source"],
        }
        for score, _, reasons, item in ranked_constraints[:top_constraints]
    ]

    template = FAMILY_TEMPLATES[family]
    graph = {
        "nodes": [{"id": node_id, "role": role} for node_id, role in template["graph"]],
        "edges": [{"from": a, "to": b, "meaning": meaning} for a, b, meaning in template["edges"]],
    }
    missing = list(template.get("missing_executors", []))
    theory_path = template.get("theory_path")
    executable_now = bool(theory_path) and not missing
    execution = {
        "status": "ready" if executable_now else "plan-only",
        "executable_now": executable_now,
        "missing_executors": missing,
        "note": (
            "All declared executors for this proposal family are now available; validate and run the promoted theory before treating it as evidence."
            if executable_now
            else "A proposal is not evidence. It becomes evidence only after adapters exist, the graph validates, and the declared experiment is actually run."
        ),
    }
    if theory_path:
        execution["theory_path"] = theory_path
        execution["run_command"] = f"python -m theorylab run {theory_path} --json"

    return {
        "format": "theorylab-proposal/v1",
        "question": question,
        "family": family,
        "hypothesis": template["hypothesis"],
        "selected_components": chosen_components,
        "selected_constraints": chosen_constraints,
        "candidate_graph": graph,
        "experiment": template["experiment"],
        "attackers": template["attackers"],
        "predeclared_gates": template["gates"],
        "execution": execution,
        "grounding": {
            "component_source": "knowledge/genealogy_components.json",
            "constraint_source": "knowledge/constraints.json",
            "selection_method": "deterministic token/family scoring; no LLM-generated hidden evidence",
        }
    }


def propose_to_path(question: str, output: str | Path) -> dict[str, Any]:
    proposal = propose(question)
    Path(output).write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return proposal
