from __future__ import annotations

import math
import random
import statistics
from copy import deepcopy
from typing import Any

from .basis_alignment import (
    _column,
    _dot,
    _fast_matrix,
    _hadamard_variant,
    _identity,
    _matmul,
    _matvec,
    _norm,
    _orthonormalize_columns,
    _random_orthogonal,
    _transpose,
    operator_family_metrics,
)


def _rotation4(theta: float) -> list[list[float]]:
    c1, s1 = math.cos(theta), math.sin(theta)
    theta2 = 0.7 * theta
    c2, s2 = math.cos(theta2), math.sin(theta2)
    return [
        [c1, -s1, 0.0, 0.0],
        [s1, c1, 0.0, 0.0],
        [0.0, 0.0, c2, -s2],
        [0.0, 0.0, s2, c2],
    ]


def _angle_at(world: dict[str, Any], t: int) -> float:
    pretrain = int(world["pretrain_steps"])
    drift_steps = int(world["drift_steps"])
    total_angle = float(world["total_angle"])
    if t < pretrain:
        return 0.0
    progress = min(1.0, max(0.0, (t - pretrain) / max(1, drift_steps)))
    return total_angle * progress


def _basis_at(world: dict[str, Any], t: int) -> list[list[float]]:
    return _matmul(world["initial_oracle_basis"], _rotation4(_angle_at(world, t)))


def make_drifting_world_panel(params: dict[str, Any]) -> dict[str, Any]:
    dim = int(params.get("dim", 4))
    if dim != 4:
        raise ValueError("v3 drifting recurrent world currently fixes dim=4")
    panel_size = int(params.get("panel_size", 8))
    pretrain_steps = int(params.get("pretrain_steps", 2000))
    drift_steps = int(params.get("drift_steps", 5000))
    post_steps = int(params.get("post_steps", 500))
    total_angle = float(params.get("total_angle", 1.20))
    noise_std = float(params.get("noise_std", 0.30))
    seed = int(params.get("seed", 100))
    stream_seed = int(params.get("stream_seed", 2000))
    eigenvalues = [float(v) for v in params.get("eigenvalues", [0.94, 0.79, 0.54, 0.28])]
    if len(eigenvalues) != dim:
        raise ValueError("eigenvalue count must equal dim")

    worlds = []
    for index in range(panel_size):
        q0 = _hadamard_variant(seed + index)
        worlds.append({
            "index": index,
            "seed": seed + index,
            "stream_seed": stream_seed + index,
            "initial_oracle_basis": q0,
            "eigenvalues": eigenvalues,
            "pretrain_steps": pretrain_steps,
            "drift_steps": drift_steps,
            "post_steps": post_steps,
            "total_angle": total_angle,
            "noise_std": noise_std,
        })
    return {
        "kind": "drifting-recurrent-mode-panel/v1",
        "dim": dim,
        "panel_size": panel_size,
        "pretrain_steps": pretrain_steps,
        "drift_steps": drift_steps,
        "post_steps": post_steps,
        "total_angle": total_angle,
        "noise_std": noise_std,
        "eigenvalues": eigenvalues,
        "worlds": worlds,
        "boundary": (
            "Constructed symmetric linear recurrent worlds with continuously rotating hidden modal coordinates. "
            "The online learner sees only the streaming state x_t; stale/oracle controls are audit arms."
        ),
    }


def _sanger_step(
    basis: list[list[float]],
    x: list[float],
    eta: float,
) -> list[list[float]]:
    dim = len(basis)
    old = deepcopy(basis)
    old_t = _transpose(old)
    y = [_dot(col, x) for col in old_t]
    updated = deepcopy(basis)
    for i in range(dim):
        recon = [0.0] * dim
        for j in range(i + 1):
            col = _column(old, j)
            for k in range(dim):
                recon[k] += y[j] * col[k]
        delta = [eta * y[i] * (x[k] - recon[k]) for k in range(dim)]
        for k in range(dim):
            updated[k][i] += delta[k]
    return updated


def track_basis(world_panel: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    strategy = str(params.get("strategy", "online_sanger"))
    eta = float(params.get("eta", 0.006))
    decay_scale = float(params.get("decay_scale", 30000.0))
    reorth_every = int(params.get("reorth_every", 20))
    learner_seed_offset = int(params.get("learner_seed_offset", 5000))
    dim = int(world_panel["dim"])
    bases = []

    for world in world_panel["worlds"]:
        total_steps = int(world["pretrain_steps"]) + int(world["drift_steps"]) + int(world["post_steps"])
        final_t = total_steps - 1

        if strategy == "stale_oracle":
            bases.append(deepcopy(world["initial_oracle_basis"]))
            continue
        if strategy == "oracle_moving":
            bases.append(_basis_at(world, final_t))
            continue
        if strategy == "visible":
            bases.append(_identity(dim))
            continue
        if strategy not in {"online_sanger", "frozen_sanger"}:
            raise ValueError(f"unsupported tracking strategy: {strategy}")

        basis = _random_orthogonal(dim, learner_seed_offset + int(world["seed"]))
        rng = random.Random(int(world["stream_seed"]))
        x = [0.0] * dim
        for t in range(total_steps):
            oracle = _basis_at(world, t)
            fast = _fast_matrix(oracle, world["eigenvalues"])
            noise = [rng.gauss(0.0, float(world["noise_std"])) for _ in range(dim)]
            x = [a + b for a, b in zip(_matvec(fast, x), noise)]

            should_update = strategy == "online_sanger" or t < int(world["pretrain_steps"])
            if should_update:
                rate = eta / (1.0 + t / decay_scale)
                basis = _sanger_step(basis, x, rate)
                if reorth_every > 0 and t % reorth_every == 0:
                    basis = _orthonormalize_columns(basis)

        bases.append(_orthonormalize_columns(basis))

    return {
        "kind": "tracking-basis-set/v1",
        "strategy": strategy,
        "bases": bases,
        "panel_size": len(bases),
        "accessed_fields": (
            ["streaming_state"]
            if strategy in {"online_sanger", "frozen_sanger"}
            else ["initial_oracle_basis"]
            if strategy == "stale_oracle"
            else ["moving_oracle_basis"]
            if strategy == "oracle_moving"
            else []
        ),
    }


def tracking_operator_metrics(
    world_panel: dict[str, Any],
    basis_set: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    static_worlds = []
    for world in world_panel["worlds"]:
        total_steps = int(world["pretrain_steps"]) + int(world["drift_steps"]) + int(world["post_steps"])
        static_worlds.append({
            "index": world["index"],
            "oracle_basis": _basis_at(world, total_steps - 1),
        })
    audit_panel = {
        "kind": "drift-final-audit/v1",
        "dim": world_panel["dim"],
        "panel_size": world_panel["panel_size"],
        "worlds": static_worlds,
    }
    metrics = operator_family_metrics(audit_panel, basis_set, params)
    metrics["metrics"] = {
        "strategy": metrics["strategy"],
        "per_world": deepcopy(metrics["per_world"]),
    }
    return metrics


def panel_dominance(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    crows = {int(row["index"]): row for row in candidate["per_world"]}
    brows = {int(row["index"]): row for row in baseline["per_world"]}
    ids = sorted(set(crows) & set(brows))
    keys = ("basis_alignment", "operator_rank", "composition_score")
    out: dict[str, Any] = {"panel_size": len(ids)}
    for key in keys:
        margins = [float(crows[i][key]) - float(brows[i][key]) for i in ids]
        out[f"{key}_wins"] = sum(1 for margin in margins if margin > 0.0)
        out[f"{key}_median_margin"] = statistics.median(margins) if margins else 0.0
        out[f"{key}_min_margin"] = min(margins) if margins else 0.0
    return out
