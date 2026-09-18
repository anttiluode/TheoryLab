from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .catalog import load_catalog, load_json
from .executors import execute
from .validate import ValidationError, validate_theory


def _split(endpoint: str) -> tuple[str, str]:
    return endpoint.split(".", 1)


def _topological_order(theory: dict[str, Any]) -> list[str]:
    ids = [node["id"] for node in theory["nodes"]]
    incoming = {iid: 0 for iid in ids}
    outgoing = {iid: [] for iid in ids}
    for edge in theory.get("edges", []):
        src, _ = _split(edge["from"])
        dst, _ = _split(edge["to"])
        incoming[dst] += 1
        outgoing[src].append(dst)
    ready = [iid for iid in ids if incoming[iid] == 0]
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for nxt in outgoing[current]:
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                ready.append(nxt)
    if len(order) != len(ids):
        raise ValidationError("cycle in theory graph")
    return order


def _operand(value: Any, measurements: dict[str, Any]) -> Any:
    if isinstance(value, str) and value in measurements:
        return measurements[value]
    return value


def _compare(lhs: Any, op: str, rhs: Any) -> bool:
    if op == ">": return lhs > rhs
    if op == ">=": return lhs >= rhs
    if op == "<": return lhs < rhs
    if op == "<=": return lhs <= rhs
    if op == "==": return lhs == rhs
    if op == "!=": return lhs != rhs
    raise ValueError(f"unsupported gate operator: {op}")


def run_theory(theory: dict[str, Any], catalog: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    catalog = catalog or load_catalog()
    errors = validate_theory(theory, catalog)
    if errors:
        raise ValidationError("; ".join(errors))

    definitions = {node["id"]: node for node in catalog}
    instances = {node["id"]: node for node in theory["nodes"]}
    order = _topological_order(theory)
    inbound: dict[str, list[dict[str, str]]] = {iid: [] for iid in instances}
    for edge in theory.get("edges", []):
        dst, _ = _split(edge["to"])
        inbound[dst].append(edge)

    all_measurements: dict[str, Any] = {}
    experiment_results: dict[str, Any] = {}

    for experiment in theory.get("experiments", []):
        state: dict[str, dict[str, Any]] = {iid: {} for iid in instances}
        last_outputs: dict[str, dict[str, Any]] = {}
        phase_log: list[dict[str, Any]] = []

        for phase in experiment.get("protocol", []):
            phase_inputs = phase.get("inputs", {})
            phase_outputs: dict[str, dict[str, Any]] = {}
            for iid in order:
                inst = instances[iid]
                definition = definitions[inst["node"]]
                inputs: dict[str, Any] = {}
                for edge in inbound[iid]:
                    src_i, src_p = _split(edge["from"])
                    _, dst_p = _split(edge["to"])
                    source_outputs = phase_outputs.get(src_i, last_outputs.get(src_i, {}))
                    if src_p in source_outputs:
                        inputs[dst_p] = deepcopy(source_outputs[src_p])
                for endpoint, value in phase_inputs.items():
                    target_i, target_p = _split(endpoint)
                    if target_i == iid:
                        inputs[target_p] = deepcopy(value)
                params = deepcopy(definition.get("parameters", {}).get("defaults", {}))
                params.update(inst.get("parameters", {}))
                outputs = execute(definition["executor"], inputs, params, state[iid])
                phase_outputs[iid] = outputs
            last_outputs = phase_outputs
            phase_log.append({"id": phase.get("id"), "outputs": deepcopy(phase_outputs)})

        measurements: dict[str, Any] = {}
        for measurement in experiment.get("measurements", []):
            iid, port = _split(measurement["source"])
            value = last_outputs[iid][port]
            if measurement.get("reduce") == "l2":
                value = execute("observer.l2", {"value": value}, {}, {})["value"]
            measurements[measurement["name"]] = value
            all_measurements[f"{experiment['id']}.{measurement['name']}"] = value

        experiment_results[experiment["id"]] = {
            "measurements": measurements,
            "final_state": deepcopy(state),
            "phases": phase_log,
        }

    gates = []
    for gate in theory.get("gates", []):
        lhs = _operand(gate["lhs"], all_measurements)
        rhs = _operand(gate["rhs"], all_measurements)
        passed = _compare(lhs, gate["op"], rhs)
        gates.append({"id": gate["id"], "passed": passed, "lhs": lhs, "op": gate["op"], "rhs": rhs, "meaning": gate.get("meaning", "")})

    overall = all(gate["passed"] for gate in gates) if gates else True
    return {
        "format": "theorylab-receipt/v0",
        "theory_id": theory["id"],
        "run_id": f"{theory['id']}-runtime",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if overall else "fail",
        "experiments": experiment_results,
        "measurements": all_measurements,
        "gates": gates,
        "claims": {
            "supported": theory.get("interpretation", {}).get("if_pass", []) if overall else [],
            "limited": theory.get("interpretation", {}).get("always_limit", []),
            "killed": theory.get("interpretation", {}).get("if_fail", []) if not overall else [],
        },
        "limitations": theory.get("limitations", []),
    }


def run_theory_file(path: str | Path) -> dict[str, Any]:
    return run_theory(load_json(path))
