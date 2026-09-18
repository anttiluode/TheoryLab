from __future__ import annotations

import itertools
import math
import random
import statistics
from copy import deepcopy
from typing import Any


def _identity(n: int) -> list[list[float]]:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _transpose(a: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*a)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def _norm(v: list[float]) -> float:
    return math.sqrt(max(0.0, _dot(v, v)))


def _matvec(a: list[list[float]], x: list[float]) -> list[float]:
    return [sum(float(v) * float(u) for v, u in zip(row, x)) for row in a]


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    bt = _transpose(b)
    return [[_dot(row, col) for col in bt] for row in a]


def _outer(a: list[float], b: list[float]) -> list[list[float]]:
    return [[float(x) * float(y) for y in b] for x in a]


def _add(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def _sub(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def _scale(a: list[list[float]], s: float) -> list[list[float]]:
    return [[s * x for x in row] for row in a]


def _fro(a: list[list[float]]) -> float:
    return math.sqrt(sum(x * x for row in a for x in row))


def _column(a: list[list[float]], j: int) -> list[float]:
    return [row[j] for row in a]


def _from_columns(cols: list[list[float]]) -> list[list[float]]:
    return [list(row) for row in zip(*cols)]


def _orthonormalize_columns(matrix: list[list[float]]) -> list[list[float]]:
    d = len(matrix)
    ncols = len(matrix[0]) if matrix else 0
    cols: list[list[float]] = []
    for j in range(ncols):
        v = _column(matrix, j)
        for q in cols:
            c = _dot(v, q)
            v = [x - c * y for x, y in zip(v, q)]
        nv = _norm(v)
        if nv < 1e-12:
            for axis in range(d):
                candidate = [1.0 if i == axis else 0.0 for i in range(d)]
                for q in cols:
                    c = _dot(candidate, q)
                    candidate = [x - c * y for x, y in zip(candidate, q)]
                nc = _norm(candidate)
                if nc >= 1e-12:
                    v = [x / nc for x in candidate]
                    break
            else:
                raise ValueError("could not complete orthonormal basis")
        else:
            v = [x / nv for x in v]
        cols.append(v)
    return _from_columns(cols)


def _random_orthogonal(dim: int, seed: int) -> list[list[float]]:
    rng = random.Random(seed)
    raw = [[rng.gauss(0.0, 1.0) for _ in range(dim)] for _ in range(dim)]
    return _orthonormalize_columns(raw)


def _hadamard4() -> list[list[float]]:
    return [
        [0.5, 0.5, 0.5, 0.5],
        [0.5, -0.5, 0.5, -0.5],
        [0.5, 0.5, -0.5, -0.5],
        [0.5, -0.5, -0.5, 0.5],
    ]


def _hadamard_variant(seed: int) -> list[list[float]]:
    base = _hadamard4()
    rng = random.Random(seed)
    rows = list(range(4))
    cols = list(range(4))
    rng.shuffle(rows)
    rng.shuffle(cols)
    row_sign = [1.0 if rng.random() < 0.5 else -1.0 for _ in range(4)]
    col_sign = [1.0 if rng.random() < 0.5 else -1.0 for _ in range(4)]
    return [
        [base[rows[i]][cols[j]] * row_sign[i] * col_sign[j] for j in range(4)]
        for i in range(4)
    ]


def _fast_matrix(basis: list[list[float]], eigenvalues: list[float]) -> list[list[float]]:
    diag = [[eigenvalues[i] if i == j else 0.0 for j in range(len(eigenvalues))] for i in range(len(eigenvalues))]
    return _matmul(_matmul(basis, diag), _transpose(basis))


def _simulate_covariance(
    fast: list[list[float]],
    seed: int,
    steps: int,
    burn_in: int,
    noise_std: float,
) -> tuple[list[list[float]], int]:
    dim = len(fast)
    rng = random.Random(seed)
    x = [0.0] * dim
    n = 0
    mean = [0.0] * dim
    m2 = [[0.0] * dim for _ in range(dim)]
    for t in range(steps):
        noise = [rng.gauss(0.0, noise_std) for _ in range(dim)]
        x = [a + b for a, b in zip(_matvec(fast, x), noise)]
        if t < burn_in:
            continue
        n += 1
        delta = [x[i] - mean[i] for i in range(dim)]
        mean = [mean[i] + delta[i] / n for i in range(dim)]
        delta2 = [x[i] - mean[i] for i in range(dim)]
        for i in range(dim):
            for j in range(dim):
                m2[i][j] += delta[i] * delta2[j]
    if n < 2:
        raise ValueError("need at least two retained samples")
    covariance = [[m2[i][j] / (n - 1) for j in range(dim)] for i in range(dim)]
    return covariance, n


def make_world_panel(params: dict[str, Any]) -> dict[str, Any]:
    dim = int(params.get("dim", 4))
    if dim != 4:
        raise ValueError("v2 matched recurrent world currently fixes dim=4 for the Hadamard visibility attacker")
    panel_size = int(params.get("panel_size", 8))
    steps = int(params.get("steps", 4500))
    burn_in = int(params.get("burn_in", 500))
    noise_std = float(params.get("noise_std", 0.30))
    base_seed = int(params.get("seed", 100))
    covariance_seed = int(params.get("covariance_seed", 200))
    eigenvalues = [float(v) for v in params.get("eigenvalues", [0.94, 0.79, 0.54, 0.28])]
    if len(eigenvalues) != dim:
        raise ValueError("eigenvalue count must equal dim")

    worlds = []
    for index in range(panel_size):
        seed = base_seed + index
        oracle_basis = _hadamard_variant(seed)
        fast = _fast_matrix(oracle_basis, eigenvalues)
        covariance, retained = _simulate_covariance(
            fast,
            covariance_seed + index,
            steps,
            burn_in,
            noise_std,
        )
        worlds.append({
            "index": index,
            "seed": seed,
            "fast_matrix": fast,
            "oracle_basis": oracle_basis,
            "addresses": deepcopy(oracle_basis),
            "covariance": covariance,
            "retained_samples": retained,
        })
    return {
        "kind": "matched-recurrent-mode-panel/v1",
        "dim": dim,
        "panel_size": panel_size,
        "eigenvalues": eigenvalues,
        "steps": steps,
        "burn_in": burn_in,
        "noise_std": noise_std,
        "worlds": worlds,
        "boundary": (
            "Constructed symmetric linear worlds with Hadamard-like hidden modes. "
            "Visible coordinates are deliberately maximally mixed with respect to address energy; "
            "this is an existence/learnability calibration, not a generic RNN benchmark."
        ),
    }


def _power_basis(covariance: list[list[float]], iterations: int = 120) -> list[list[float]]:
    dim = len(covariance)
    cols: list[list[float]] = []
    for k in range(dim):
        v = [
            math.sin((k + 1) * (i + 1) * 1.2345) + 0.37 * math.cos((k + 2) * (i + 1))
            for i in range(dim)
        ]
        for q in cols:
            c = _dot(v, q)
            v = [x - c * y for x, y in zip(v, q)]
        nv = _norm(v)
        if nv < 1e-12:
            v = [1.0 if i == k else 0.0 for i in range(dim)]
            nv = 1.0
        v = [x / nv for x in v]
        for _ in range(iterations):
            y = _matvec(covariance, v)
            for q in cols:
                c = _dot(y, q)
                y = [x - c * z for x, z in zip(y, q)]
            ny = _norm(y)
            if ny < 1e-14:
                break
            v = [x / ny for x in y]
        cols.append(v)
    return _from_columns(cols)


def learn_basis(world_panel: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    strategy = str(params.get("strategy", "pca_covariance"))
    iterations = int(params.get("iterations", 120))
    random_seed_offset = int(params.get("random_seed_offset", 10000))
    dim = int(world_panel["dim"])
    bases = []
    for world in world_panel["worlds"]:
        if strategy == "pca_covariance":
            basis = _power_basis(world["covariance"], iterations)
            accessed_fields = ["covariance"]
        elif strategy == "visible":
            basis = _identity(dim)
            accessed_fields = []
        elif strategy == "random":
            basis = _random_orthogonal(dim, int(world["seed"]) + random_seed_offset)
            accessed_fields = ["seed"]
        elif strategy == "oracle":
            basis = deepcopy(world["oracle_basis"])
            accessed_fields = ["oracle_basis"]
        else:
            raise ValueError(f"unsupported coordinate strategy: {strategy}")
        bases.append(basis)
    return {
        "kind": "coordinate-basis-set/v1",
        "strategy": strategy,
        "bases": bases,
        "accessed_fields": accessed_fields,
        "panel_size": len(bases),
    }


def _symmetric_eigenvalues(matrix: list[list[float]], max_sweeps: int = 100, tol: float = 1e-12) -> list[float]:
    a = deepcopy(matrix)
    n = len(a)
    if n == 0:
        return []
    for _ in range(max_sweeps):
        p, q = 0, 1 if n > 1 else 0
        largest = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                value = abs(a[i][j])
                if value > largest:
                    largest = value
                    p, q = i, j
        if largest < tol or n == 1:
            break
        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        angle = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c, s = math.cos(angle), math.sin(angle)

        for k in range(n):
            if k in (p, q):
                continue
            akp, akq = a[k][p], a[k][q]
            a[k][p] = a[p][k] = c * akp - s * akq
            a[k][q] = a[q][k] = s * akp + c * akq
        a[p][p] = c * c * app - 2.0 * s * c * apq + s * s * aqq
        a[q][q] = s * s * app + 2.0 * s * c * apq + c * c * aqq
        a[p][q] = a[q][p] = 0.0
    return sorted((max(0.0, a[i][i]) for i in range(n)), reverse=True)


def _effective_rank(rows: list[list[float]]) -> float:
    if not rows:
        return 0.0
    gram = [[_dot(a, b) for b in rows] for a in rows]
    eigenvalues = _symmetric_eigenvalues(gram)
    total = sum(eigenvalues)
    denom = sum(value * value for value in eigenvalues)
    if total <= 1e-15 or denom <= 1e-15:
        return 0.0
    return total * total / denom


def _best_alignment(oracle: list[list[float]], basis: list[list[float]]) -> float:
    dim = len(oracle)
    overlap = _matmul(_transpose(oracle), basis)
    squared = [[value * value for value in row] for row in overlap]
    best = 0.0
    for perm in itertools.permutations(range(dim)):
        score = sum(squared[i][perm[i]] for i in range(dim)) / dim
        best = max(best, score)
    return best


def _single_world_metrics(
    world: dict[str, Any],
    basis: list[list[float]],
    write_gain: float,
) -> dict[str, float]:
    dim = len(basis)
    oracle = world["oracle_basis"]
    overlap = _matmul(_transpose(oracle), basis)
    address_activity = [[value * value for value in row] for row in overlap]
    address_rank = _effective_rank(address_activity)

    c = [sum(basis[i][j] for j in range(dim)) / math.sqrt(dim) for i in range(dim)]
    ident = _identity(dim)
    write_matrices: list[list[list[float]]] = []
    flattened_delta: list[list[float]] = []
    for activity in address_activity:
        delta = [[0.0] * dim for _ in range(dim)]
        for j, amount in enumerate(activity):
            atom = _outer(_column(basis, j), c)
            delta = _add(delta, _scale(atom, amount))
        write = _add(ident, _scale(delta, write_gain))
        write_matrices.append(write)
        flattened_delta.append([x for row in _sub(write, ident) for x in row])

    operator_rank = _effective_rank(flattened_delta)
    composition = []
    if abs(write_gain) > 1e-15:
        normalizer = write_gain * write_gain
        for i in range(dim):
            for j in range(i + 1, dim):
                ab = _matmul(write_matrices[j], write_matrices[i])
                ba = _matmul(write_matrices[i], write_matrices[j])
                composition.append(_fro(_sub(ab, ba)) / normalizer)
    else:
        composition = [0.0]

    return {
        "basis_alignment": _best_alignment(oracle, basis),
        "address_rank": address_rank,
        "operator_rank": operator_rank,
        "composition_score": sum(composition) / len(composition),
        "write_selectivity": sum(max(row) for row in address_activity) / dim,
    }


def operator_family_metrics(
    world_panel: dict[str, Any],
    basis_set: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    write_gain = float(params.get("write_gain", 0.60))
    bases = basis_set["bases"]
    worlds = world_panel["worlds"]
    if len(bases) != len(worlds):
        raise ValueError("basis panel and world panel must have equal length")

    per_world = [
        {"index": world["index"], **_single_world_metrics(world, basis, write_gain)}
        for world, basis in zip(worlds, bases)
    ]
    output: dict[str, Any] = {
        "strategy": basis_set["strategy"],
        "write_gain": write_gain,
        "panel_size": len(per_world),
        "per_world": per_world,
    }
    for key in ("basis_alignment", "address_rank", "operator_rank", "composition_score", "write_selectivity"):
        values = [float(item[key]) for item in per_world]
        output[f"{key}_median"] = statistics.median(values)
        output[f"{key}_min"] = min(values)
        output[f"{key}_max"] = max(values)
    return output
