#!/usr/bin/env python3
"""Benchmark the universal R(3,3,3)=17 colour-degree cap on hard K58 rows."""
import argparse
import json
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
import arm_caps as ac


def degree_caps(row, form, scope="own", encoding=EncType.kmtotalizer, top_start=None):
    ac.require(scope in {"own", "all"}, "unknown degree-cap scope")
    f, positive, negative, known, edge, groups = ac.family_groups(row)
    top = form.nv if top_start is None else top_start
    initial = top
    clauses = []
    counters = 0
    for own_color, sites in enumerate(groups):
        for x in sites:
            colors = [own_color] if scope == "own" else range(4)
            for color in colors:
                if color == own_color:
                    # The fixed root edge supplies one; own-arm same-colour
                    # edges are impossible. Only the other three arms remain.
                    spokes = [edge(x, y, color)
                              for b, other in enumerate(groups) if b != own_color
                              for y in other]
                    full_cap = 15
                else:
                    spokes = [edge(x, y, color) for y in range(1, 58) if y != x]
                    full_cap = 16
                candidates = [lit for lit in spokes
                              if lit not in positive and -lit not in negative
                              and (lit - 1) // 4 not in known]
                must = sum(lit in positive for lit in spokes)
                bound = full_cap - must
                ac.require(bound >= 0, "fixed spokes exceed the degree cap")
                if len(candidates) > bound:
                    encoded = CardEnc.atmost(candidates, bound=bound, top_id=top,
                                             encoding=encoding)
                    top = max(top, encoded.nv)
                    clauses.extend(encoded.clauses)
                    counters += 1
    stats = dict(scope=scope, encoding=encoding, clauses=len(clauses),
                 new_variables=top - initial, next_top=top,
                 counters=counters, clause_literals=sum(map(len, clauses)))
    return clauses, stats


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
        variants = {}
        for name, scope, encoding in (
                ("own_seq", "own", EncType.seqcounter),
                ("own_km", "own", EncType.kmtotalizer),
                ("all_km", "all", EncType.kmtotalizer)):
            start = time.process_time()
            clauses, stats = degree_caps(row, form, scope, encoding)
            stats["generation_cpu_seconds"] = time.process_time() - start
            variants[name] = (clauses, stats)
        start = time.process_time()
        armcaps, armstats = ac.cap_clauses(row, form, guards, "unconditional",
                                            top_start=variants["own_km"][1]["next_top"])
        armstats["generation_cpu_seconds"] = time.process_time() - start
        extras = {
            "stock": [],
            "own_seq": variants["own_seq"][0],
            "own_km": variants["own_km"][0],
            "all_km": variants["all_km"][0],
            "own_km_plus_armcaps": variants["own_km"][0] + armcaps,
        }
        names = list(extras)
        if rank % 2 == 0:
            names.reverse()
        policies = {}
        for name in names:
            result = ac.solve_one(form, extras[name], args.conflicts, args.seed)
            result["added_clauses"] = len(extras[name])
            policies[name] = result
            print(rank, name, json.dumps(result, sort_keys=True), flush=True)
        results.append(dict(
            rank=rank, id=record["id"], input_sha256=record["input_sha256"],
            profile=record["profile"], kinds=record["kinds"],
            charge=int(record["charge"]), proof_bytes=int(record["proof_bytes"]),
            seed=args.seed, conflict_budget=args.conflicts,
            base_clauses=len(form.clauses), base_variables=form.nv,
            base_generation_cpu_seconds=base_cpu,
            cap_variants={k: v[1] for k, v in variants.items()},
            armcap_variant=armstats, policies=policies))
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        temporary.replace(args.output)


if __name__ == "__main__":
    main()
