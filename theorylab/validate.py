from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from .catalog import load_catalog, load_json


class ValidationError(ValueError):
    pass


def _port_type(node: dict[str, Any], direction: str, port: str) -> str:
    ports = node.get(direction, {})
    if port not in ports:
        raise ValidationError(f"node {node['id']} has no {direction[:-1]} port {port!r}")
    spec = ports[port]
    return spec if isinstance(spec, str) else spec.get("type", "any")


def _split_endpoint(value: str) -> tuple[str, str]:
    if "." not in value:
        raise ValidationError(f"endpoint must be instance.port: {value!r}")
    return value.split(".", 1)


def validate_catalog(catalog: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for node in catalog:
        node_id = node.get("id")
        if not node_id:
            errors.append("node missing id")
            continue
        if node_id in ids:
            errors.append(f"duplicate node id: {node_id}")
        ids.add(node_id)
        if node.get("role") not in {"mechanism", "world", "source", "intervention", "learner", "observer", "attacker", "evaluator", "transform"}:
            errors.append(f"{node_id}: invalid role {node.get('role')!r}")
        if not node.get("executor"):
            errors.append(f"{node_id}: missing executor")
        if "inputs" not in node or "outputs" not in node:
            errors.append(f"{node_id}: missing inputs/outputs")
    return errors


def validate_theory(theory: dict[str, Any], catalog: list[dict[str, Any]] | None = None) -> list[str]:
    catalog = catalog or load_catalog()
    nodes = {node["id"]: node for node in catalog}
    errors: list[str] = []
    instances: dict[str, dict[str, Any]] = {}

    if not theory.get("id"):
        errors.append("theory missing id")
    if not theory.get("question"):
        errors.append("theory missing question")
    if not theory.get("hypothesis"):
        errors.append("theory missing hypothesis")

    for inst in theory.get("nodes", []):
        iid = inst.get("id")
        ref = inst.get("node")
        if not iid or not ref:
            errors.append("theory node instance missing id/node")
            continue
        if iid in instances:
            errors.append(f"duplicate instance id: {iid}")
        instances[iid] = inst
        if ref not in nodes:
            errors.append(f"unknown node definition: {ref}")

    graph: dict[str, set[str]] = defaultdict(set)
    indegree = {iid: 0 for iid in instances}
    for edge in theory.get("edges", []):
        try:
            si, sp = _split_endpoint(edge["from"])
            ti, tp = _split_endpoint(edge["to"])
        except (KeyError, ValidationError) as exc:
            errors.append(str(exc))
            continue
        if si not in instances or ti not in instances:
            errors.append(f"edge references unknown instance: {edge}")
            continue
        sref = instances[si]["node"]
        tref = instances[ti]["node"]
        if sref in nodes and tref in nodes:
            try:
                st = _port_type(nodes[sref], "outputs", sp)
                tt = _port_type(nodes[tref], "inputs", tp)
                if st != "any" and tt != "any" and st != tt:
                    errors.append(f"type mismatch {edge['from']} ({st}) -> {edge['to']} ({tt})")
            except ValidationError as exc:
                errors.append(str(exc))
        if ti not in graph[si]:
            graph[si].add(ti)
            indegree[ti] += 1

    q = deque([iid for iid, d in indegree.items() if d == 0])
    seen = 0
    while q:
        current = q.popleft()
        seen += 1
        for nxt in graph[current]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)
    if instances and seen != len(instances):
        errors.append("theory graph contains a cycle; v0 runtime requires DAG dataflow")

    experiment_ids: set[str] = set()
    measurement_names: set[str] = set()
    for experiment in theory.get("experiments", []):
        eid = experiment.get("id")
        if not eid:
            errors.append("experiment missing id")
            continue
        if eid in experiment_ids:
            errors.append(f"duplicate experiment id: {eid}")
        experiment_ids.add(eid)
        for phase in experiment.get("protocol", []):
            for endpoint in phase.get("inputs", {}):
                try:
                    iid, port = _split_endpoint(endpoint)
                    if iid not in instances:
                        errors.append(f"phase input references unknown instance: {endpoint}")
                    elif instances[iid]["node"] in nodes:
                        _port_type(nodes[instances[iid]["node"]], "inputs", port)
                except ValidationError as exc:
                    errors.append(str(exc))
        for measurement in experiment.get("measurements", []):
            name = f"{eid}.{measurement.get('name')}"
            measurement_names.add(name)
            try:
                iid, port = _split_endpoint(measurement["source"])
                if iid not in instances:
                    errors.append(f"measurement references unknown instance: {measurement['source']}")
                elif instances[iid]["node"] in nodes:
                    _port_type(nodes[instances[iid]["node"]], "outputs", port)
            except (KeyError, ValidationError) as exc:
                errors.append(str(exc))

    for gate in theory.get("gates", []):
        for side in ("lhs", "rhs"):
            operand = gate.get(side)
            if isinstance(operand, str) and "." in operand and operand not in measurement_names:
                errors.append(f"gate {gate.get('id', '?')} references unknown measurement {operand!r}")

    for attacker in theory.get("attackers", []):
        if attacker.get("experiment") not in experiment_ids:
            errors.append(f"attacker {attacker.get('id', '?')} references unknown experiment")

    return errors


def validate_repository(root: str | Path | None = None) -> list[str]:
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    catalog = load_json(root / "nodes/catalog.json")
    errors = validate_catalog(catalog)
    manifest = load_json(root / "theorylab.json")
    for path in manifest["entrypoints"].get("theories", []):
        theory = load_json(root / path)
        errors.extend(f"{path}: {msg}" for msg in validate_theory(theory, catalog))
    return errors
