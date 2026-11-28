#!/usr/bin/env python3
"""Regenerate one exact frozen parent without modifying the source package."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tools", required=True)
    ap.add_argument("--row", required=True)
    ap.add_argument("--tier", choices=("first", "retry"), default="first")
    ap.add_argument("--expect-sha256")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(Path(args.tools).resolve()))
    import problem
    row = problem.lookup(args.row)
    raw = problem.row_formula(row, args.tier)
    sha = hashlib.sha256(raw).hexdigest()
    if args.expect_sha256:
        assert sha == args.expect_sha256, (sha, args.expect_sha256)
    nv, clauses = problem.read_dimacs(raw)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(raw)
    rec = {"row": row["id"], "tier": args.tier, "variables": nv,
           "clauses": len(clauses), "bytes": len(raw), "sha256": sha,
           "output": str(args.out)}
    args.out.with_suffix(".json").write_text(json.dumps(rec, indent=2)+"\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
