#!/usr/bin/env python3
"""Cube and conquer a frozen K58 wall row with a combinatorial oracle and CaDiCaL."""
import argparse
from collections import Counter
from importlib.metadata import version
import json
from pathlib import Path
import sys

from problem import ROOT, external_formula, lookup, require, roster, row_formula
from campaign import execute, store_plan


def positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return value


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest="cmd", required=True)
    listing = commands.add_parser("rows", help="list wall profile counts or IDs")
    listing.add_argument("--profile", help="show IDs for a comma-separated profile")
    listing.add_argument("--limit", type=positive, default=10)
    export = commands.add_parser("export-drat", help="replay and export one proof for a completed UNSAT tree")
    export.add_argument("out", metavar="RUN", type=Path)
    export.add_argument("output", metavar="PROOF", type=Path)
    export.add_argument("--method", choices=("compact", "isolated"), default="compact")
    export.add_argument("--checker", type=Path, default=ROOT / "tools/drat-trim")
    export.add_argument("--check-seconds", type=positive, default=300)
    for name, description in (("prepare", "generate the parent, CAS proof and cube cover"),
                              ("run", "prepare and conquer, or resume a matching run"),
                              ("resume", "conquer existing cubes with new or previous limits"),
                              ("verify", "rebuild the parent and independently replay the cover")):
        cmd = commands.add_parser(name, help=description)
        if name in ("prepare", "run"):
            group = cmd.add_mutually_exclusive_group(required=True)
            group.add_argument("--row", help="unique prefix of a frozen wall row ID")
            group.add_argument("--cnf", type=Path, help="external DIMACS, optionally gzipped")
            cmd.add_argument("--out", type=Path, required=True)
            cmd.add_argument("--tier", choices=("first", "retry"), default="first")
            cmd.add_argument("--cas", choices=("pentagon", "off"),
                             help="defaults to pentagon on frozen rows and off on DIMACS")
            cmd.add_argument("--depth", type=int, default=3, help="maximum split depth; 0 runs the parent")
            cmd.add_argument("--lookahead", type=positive, default=12, help="candidate variables per split")
        else:
            cmd.add_argument("out", metavar="RUN", type=Path)
        if name != "prepare":
            cmd.add_argument("--jobs", type=positive, default=2)
            cmd.add_argument("--checker", type=Path, default=ROOT / "tools/drat-trim")
            cmd.add_argument("--check-seconds", type=positive, default=300)
        if name in ("run", "resume"):
            cmd.add_argument("--seconds", type=positive, default=60, help="wall seconds per SAT pass")
            cmd.add_argument("--conflicts", type=positive, default=100000)
            cmd.add_argument("--proof", choices=("deferred", "eager"), default="deferred")
            cmd.add_argument("--shards", type=positive, default=1)
            cmd.add_argument("--shard", type=int, default=0, help="zero-based cube shard")
            cmd.add_argument("--again", action="store_true", help="retry OPEN cubes at identical limits")
        if name == "verify":
            cmd.add_argument("--expect-sha256", help="require this parent formula hash")
    return p


def main():
    args = parser().parse_args()
    require(version("python-sat") == "1.9.dev22", "requires python-sat==1.9.dev22; run setup.sh")
    if args.cmd == "rows":
        if args.profile:
            result = [r for r in roster().values()
                      if ",".join(map(str, r["family"]["profile"])) == args.profile]
            require(result, "unknown wall profile")
            for r in result[:args.limit]:
                print(r["id"], f"branch={r['branch']}", f"charge={r['charge']}")
        else:
            print("profile\trows")
            counts = Counter(tuple(r["family"]["profile"]) for r in roster().values())
            for profile, n in sorted(counts.items()):
                print(",".join(map(str, profile)), n, sep="\t")
        return 0
    out = args.out.resolve()
    if args.cmd == "export-drat":
        from export_drat import export
        print(json.dumps(export(out, args.output, args.method, args.checker.resolve(), args.check_seconds)))
        return 0
    if args.cmd in ("run", "resume"):
        require(0 <= args.shard < args.shards, "shard must be in [0, shards)")
    if args.cmd in ("run", "prepare"):
        require(args.depth >= 0, "depth must be nonnegative")
        if args.row:
            row = lookup(args.row)
            origin = {"kind": "wall", "id": row["id"], "tier": args.tier}
            base, cas = row_formula(row, args.tier), args.cas or "pentagon"
        else:
            require(args.cas != "pentagon" and args.tier == "first",
                    "DIMACS input has its own recipe; --cas pentagon and --tier retry need --row")
            base, origin = external_formula(args.cnf)
            row, cas = None, "off"
        plan = store_plan(out, base, origin, row, cas, args.depth, args.lookahead)
        print(json.dumps({k: plan[k] for k in ("origin", "parent_sha256", "variables", "clauses",
                                               "cuts", "tables", "depth", "leaf_count")}), flush=True)
        if args.cmd == "prepare":
            return 0
    verify = args.cmd == "verify"
    result = execute(out, args, verify)
    print(json.dumps(result, sort_keys=True))
    if result["counts"].get("CHECK_FAILED"):
        return 1
    return 2 if verify and result["status"] == "OPEN" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"wallcc: {exc}", file=sys.stderr)
        sys.exit(1)
