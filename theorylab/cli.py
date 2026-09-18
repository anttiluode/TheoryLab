from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import load_catalog, load_json, load_manifest
from .engine import run_theory_file
from .replay import replay_history
from .validate import validate_repository, validate_theory


def _dump(value, as_json=False):
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True))
    else:
        print(value)


def cmd_validate(args) -> int:
    if args.path:
        theory = load_json(args.path)
        errors = validate_theory(theory)
    else:
        errors = validate_repository()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("VALID")
    return 0


def cmd_list(args) -> int:
    catalog = load_catalog()
    manifest = load_manifest()
    print("NODES")
    for node in catalog:
        print(f"  {node['id']:<28} {node['role']:<12} {node['claims'][0]}")
    print("THEORIES")
    for path in manifest["entrypoints"]["theories"]:
        theory = load_json(path)
        print(f"  {theory['id']:<28} {theory['question']}")
    return 0


def cmd_run(args) -> int:
    receipt = run_theory_file(args.path)
    if args.output:
        Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _dump(receipt if args.json else f"{receipt['theory_id']}: {receipt['status'].upper()} ({len(receipt['gates'])} gates)", args.json)
    return 0 if receipt["status"] == "pass" else 2


def cmd_replay(args) -> int:
    history = load_json(args.history)
    result = replay_history(history, args.policy, args.budget)
    _dump(result if args.json else f"{result['policy']}: visited={result['visited']} best={result['best_attempt']} score={result['best_score']} cost={result['cost']}", args.json)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="theorylab")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="validate repository or one theory")
    p.add_argument("path", nargs="?")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("list", help="list node catalog and theories")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("run", help="execute a theory graph")
    p.add_argument("path")
    p.add_argument("--output")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("replay", help="replay recorded discovery history")
    p.add_argument("--history", default="data/discovery_history.json")
    p.add_argument("--policy", choices=["breadth_first", "depth_first", "best_first"], default="best_first")
    p.add_argument("--budget", type=int, default=6)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_replay)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
