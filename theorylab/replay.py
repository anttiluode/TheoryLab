from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any


def _children(history: dict[str, Any]) -> dict[str | None, list[dict[str, Any]]]:
    out: dict[str | None, list[dict[str, Any]]] = {}
    for attempt in history.get("attempts", []):
        out.setdefault(attempt.get("parent"), []).append(attempt)
    for values in out.values():
        values.sort(key=lambda item: item.get("created_order", 0))
    return out


def replay_history(history: dict[str, Any], policy: str = "breadth_first", budget: int = 10) -> dict[str, Any]:
    attempts = {item["id"]: item for item in history.get("attempts", [])}
    children = _children(history)
    roots = children.get(None, [])
    visited: list[dict[str, Any]] = []
    frontier = deepcopy(roots)

    while frontier and len(visited) < budget:
        if policy == "depth_first":
            current = frontier.pop()
        elif policy == "breadth_first":
            current = frontier.pop(0)
        elif policy == "best_first":
            frontier.sort(key=lambda item: (item.get("priority_hint", item.get("score", 0.0)), item.get("score", 0.0)), reverse=True)
            current = frontier.pop(0)
        else:
            raise ValueError(f"unknown replay policy: {policy}")

        visited.append(current)
        kids = deepcopy(children.get(current["id"], []))
        if policy == "depth_first":
            frontier.extend(reversed(kids))
        else:
            frontier.extend(kids)

    best = max(visited, key=lambda item: item.get("score", float("-inf"))) if visited else None
    return {
        "policy": policy,
        "budget": budget,
        "visited": [item["id"] for item in visited],
        "cost": sum(float(item.get("cost", 0.0)) for item in visited),
        "best_attempt": best["id"] if best else None,
        "best_score": best.get("score") if best else None,
        "available_attempts": len(attempts),
        "note": "Replay only traverses recorded attempts; it does not invent unseen outcomes."
    }
