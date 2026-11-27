#!/usr/bin/env python3
"""Matched CaDiCaL panel for complete guarded sender-count distributions."""
import argparse
import json
from pathlib import Path
import time

import arm_caps as ac


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", default="8,132,255,340")
    parser.add_argument("--conflicts", type=int, default=60000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ac.require(not args.output.exists(), "output exists; refusing to overwrite")
    results = []
    for rank in [int(x) for x in args.ranks.split(",")]:
        record, raw, form, direct, extended, guards, base_cpu = ac.prepare(rank)
        row = ac.probe.geometry[record["id"]]
        start = time.process_time()
        caps, cap_stats = ac.cap_clauses(row, form, guards, "unconditional")
        cap_cpu = time.process_time() - start
        variants = {}
        for kind in ("arm4", "pair9"):
            start = time.process_time()
            lower, stats = ac.lower_clauses(row, form, guards, kind,
                                             top_start=cap_stats["next_top"])
            stats["generation_cpu_seconds"] = time.process_time() - start
            variants[kind] = (caps + lower, stats)
        extras = {
            "stock": [],
            "unconditional_caps": caps,
            "caps_arm4": variants["arm4"][0],
            "caps_pair9": variants["pair9"][0],
            "caps_pair9_plus_direct": variants["pair9"][0] + direct,
        }
        names = list(extras)
        if rank % 2 == 0:
            names.reverse()
        policies = {}
        for name in names:
            extra = extras[name]
            result = ac.solve_one(form, extra, args.conflicts, args.seed)
            result["added_clauses"] = len(extra)
            policies[name] = result
            print(rank, name, json.dumps(result, sort_keys=True), flush=True)
        results.append(dict(
            rank=rank, id=record["id"], input_sha256=record["input_sha256"],
            profile=record["profile"], kinds=record["kinds"],
            charge=int(record["charge"]), proof_bytes=int(record["proof_bytes"]),
            seed=args.seed, conflict_budget=args.conflicts,
            base_clauses=len(form.clauses), base_variables=form.nv,
            base_generation_cpu_seconds=base_cpu,
            cap_stats={**cap_stats, "generation_cpu_seconds": cap_cpu},
            lower_variants={k: v[1] for k, v in variants.items()},
            direct_clauses=len(direct), policies=policies))
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        temporary.replace(args.output)


if __name__ == "__main__":
    main()
