#!/usr/bin/env python3
"""Selected matched CaDiCaL policies, including optional second seeds."""
import argparse
import json
from pathlib import Path
import time

import arm_caps as ac


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", required=True)
    parser.add_argument("--policies", default="stock,caps,caps_arm4,caps_pair9,caps_direct")
    parser.add_argument("--conflicts", type=int, required=True)
    parser.add_argument("--seeds", default="0")
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
        lower = {}
        for kind in ("arm4", "pair9"):
            start = time.process_time()
            clauses, stats = ac.lower_clauses(row, form, guards, kind,
                                               top_start=cap_stats["next_top"])
            stats["generation_cpu_seconds"] = time.process_time() - start
            lower[kind] = (clauses, stats)
        extras = {
            "stock": [], "caps": caps,
            "caps_arm4": caps + lower["arm4"][0],
            "caps_pair9": caps + lower["pair9"][0],
            "caps_direct": caps + direct,
            "direct": direct, "extended": extended,
        }
        selected = args.policies.split(",")
        ac.require(all(name in extras for name in selected), "unknown policy")
        for seed in [int(x) for x in args.seeds.split(",")]:
            names = list(selected)
            if (rank + seed) % 2 == 0:
                names.reverse()
            for name in names:
                start = time.process_time()
                result = ac.solve_one(form, extras[name], args.conflicts, seed)
                generation_setup_cpu = time.process_time() - start - result["search_cpu_seconds"]
                result.update(rank=rank, id=record["id"], policy=name, seed=seed,
                              input_sha256=record["input_sha256"],
                              conflict_budget=args.conflicts,
                              added_clauses=len(extras[name]),
                              base_clauses=len(form.clauses), base_variables=form.nv,
                              setup_cpu_seconds=generation_setup_cpu)
                results.append(result)
                print(json.dumps(result, sort_keys=True), flush=True)
                temporary = args.output.with_suffix(args.output.suffix + ".tmp")
                temporary.write_text(json.dumps(dict(
                    cap_stats={**cap_stats, "generation_cpu_seconds": cap_cpu},
                    lower_variants={k: v[1] for k, v in lower.items()},
                    direct_clauses=len(direct), extended_clauses=len(extended),
                    results=results), indent=2, sort_keys=True) + "\n")
                temporary.replace(args.output)


if __name__ == "__main__":
    main()
