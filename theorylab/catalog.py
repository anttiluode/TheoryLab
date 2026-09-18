from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str | Path) -> Any:
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_manifest() -> dict[str, Any]:
    return load_json("theorylab.json")


def load_catalog() -> list[dict[str, Any]]:
    return load_json("nodes/catalog.json")


def node_map() -> dict[str, dict[str, Any]]:
    return {node["id"]: node for node in load_catalog()}
