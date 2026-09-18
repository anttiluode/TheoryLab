from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, Callable

from .basis_alignment import learn_basis, make_world_panel, operator_family_metrics
from .coordinate_tracking import (
    make_drifting_world_panel,
    panel_dominance,
    track_basis,
    tracking_operator_metrics,
)


def _as_vector(value: Any) -> list[float]:
    if isinstance(value, (int, float)):
        return [float(value)]
    return [float(x) for x in value]


def _identity(n: int) -> list[list[float]]:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(float(a) * float(b) for a, b in zip(row, vector)) for row in matrix]


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    bt = list(zip(*b))
    return [[sum(float(x) * float(y) for x, y in zip(row, col)) for col in bt] for row in a]


def _outer(a: list[float], b: list[float]) -> list[list[float]]:
    return [[x * y for y in b] for x in a]


def _add(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def _scale_matrix(a: list[list[float]], s: float) -> list[list[float]]:
    return [[s * x for x in row] for row in a]


def _l2(value: Any) -> float:
    if isinstance(value, (int, float)):
        return abs(float(value))
    if value and isinstance(value[0], (list, tuple)):
        return math.sqrt(sum(float(x) ** 2 for row in value for x in row))
    return math.sqrt(sum(float(x) ** 2 for x in value))


def _sub(a: Any, b: Any) -> Any:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) - float(b)
    if a and isinstance(a[0], (list, tuple)):
        return [[float(x) - float(y) for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]
    return [float(x) - float(y) for x, y in zip(a, b)]


def source_input(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {"value": deepcopy(inputs.get("value", params.get("value")))}


def transform_linear(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    vector = _as_vector(inputs["vector"])
    matrix = [[float(x) for x in row] for row in params["matrix"]]
    return {"vector": _matvec(matrix, vector)}


def transform_basis(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    vector = _as_vector(inputs["vector"])
    basis = [[float(x) for x in row] for row in params["basis"]]
    transpose = [list(col) for col in zip(*basis)]
    return {"vector": _matvec(transpose, vector)}


def state_rank1_operator_write(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    seed_value = inputs.get("write") if inputs.get("write") is not None else inputs.get("probe")
    inferred_dim = len(_as_vector(seed_value)) if seed_value is not None else 2
    dim = int(params.get("dim", inferred_dim))
    eta = float(params.get("eta", 0.25))
    frozen = bool(params.get("frozen", False))
    operator = state.get("operator")
    if operator is None:
        operator = _identity(dim)

    if "write" in inputs and inputs["write"] is not None and not frozen:
        drive = _as_vector(inputs["write"])
        if len(drive) != dim:
            raise ValueError(f"write dimension {len(drive)} != {dim}")
        # A fixed cyclic permutation creates a rank-1 update whose left-compositions
        # generally do not commute for different drives.
        rotated = drive[1:] + drive[:1]
        write_op = _add(_identity(dim), _scale_matrix(_outer(drive, rotated), eta))
        operator = _matmul(write_op, operator)
        state["operator"] = operator

    outputs: dict[str, Any] = {"operator": deepcopy(operator)}
    if "probe" in inputs and inputs["probe"] is not None:
        probe = _as_vector(inputs["probe"])
        outputs["response"] = _matvec(operator, probe)
    return outputs


def world_matched_recurrent_modes(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {"world": make_world_panel(params)}


def learner_coordinate_basis(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {"basis_set": learn_basis(inputs["world"], params)}


def observer_operator_family_metrics(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return operator_family_metrics(inputs["world"], inputs["basis_set"], params)


def world_drifting_recurrent_modes(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {"world": make_drifting_world_panel(params)}


def learner_online_coordinate_tracking(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {"basis_set": track_basis(inputs["world"], params)}


def observer_tracking_operator_metrics(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return tracking_operator_metrics(inputs["world"], inputs["basis_set"], params)


def evaluator_panel_dominance(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return panel_dominance(inputs["candidate"], inputs["baseline"])


def observer_l2(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {"value": _l2(inputs["value"])}


def evaluator_difference(inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    delta = _sub(inputs["a"], inputs["b"])
    return {"value": _l2(delta), "delta": delta}


EXECUTORS: dict[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "source.input": source_input,
    "transform.linear": transform_linear,
    "transform.basis": transform_basis,
    "state.rank1_operator_write": state_rank1_operator_write,
    "world.matched_recurrent_modes": world_matched_recurrent_modes,
    "learner.coordinate_basis": learner_coordinate_basis,
    "observer.operator_family_metrics": observer_operator_family_metrics,
    "world.drifting_recurrent_modes": world_drifting_recurrent_modes,
    "learner.online_coordinate_tracking": learner_online_coordinate_tracking,
    "observer.tracking_operator_metrics": observer_tracking_operator_metrics,
    "evaluator.panel_dominance": evaluator_panel_dominance,
    "observer.l2": observer_l2,
    "evaluator.difference": evaluator_difference,
}


def execute(name: str, inputs: dict[str, Any], params: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    try:
        fn = EXECUTORS[name]
    except KeyError as exc:
        raise ValueError(f"unsupported executor: {name}") from exc
    return fn(inputs, params, state)
