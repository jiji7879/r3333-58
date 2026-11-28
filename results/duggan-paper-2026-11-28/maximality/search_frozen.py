#!/usr/bin/env python3
"""Search small root-star preconditions for the MCF preservation obstruction.

The scan is only a candidate finder. The chosen CNF pair is saved so the final
UNSAT claim can be independently DRAT-checked. No timeout is treated as UNSAT.
"""
import argparse
import itertools
import json
from pathlib import Path
import subprocess
from mcf_pilot import host_cnf, mcf_cnf, star_units


def cnf_bytes(top, clauses):
    return (f"p cnf {top} {len(clauses)}\n" +
            "".join(" ".join(map(str, cl))+" 0\n" for cl in clauses)).encode()


def solve(solver, blob):
    p = subprocess.run([solver, "-q"], input=blob, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=False)
    if p.returncode not in (10, 20):
        raise RuntimeError(f"solver exit {p.returncode}: {p.stdout.decode(errors='replace')}")
    return "SAT" if p.returncode == 10 else "UNSAT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--solver", default="/opt/lean/bin/cadical")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--require-four-root-colours", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(exist_ok=True)
    top, base = host_cnf(args.n)
    mcf_top, extra = mcf_cnf(args.n, 0, top)
    stars = list(itertools.product(range(4), repeat=args.n-1))
    # Nontrivial, physically coloured pivots first; this is just scan order.
    stars.sort(key=lambda s: (-len(set(s)), max(s.count(c) for c in range(4)), s))
    record = {"n": args.n, "scan_policy": "stop at first non-degenerate counterexample",
              "baseline_SAT": 0, "baseline_UNSAT": 0, "MCF_SAT": 0,
              "baseline_SAT_MCF_UNSAT": 0, "tested_stars": 0}
    for star in stars:
        if args.require_four_root_colours and len(set(star)) < 4:
            continue
        if 0 not in star:
            continue
        units = star_units(star)
        record["tested_stars"] += 1
        baseline = cnf_bytes(top, base+units)
        augmented = cnf_bytes(mcf_top, base+extra+units)
        b = solve(args.solver, baseline)
        record["baseline_"+b] += 1
        if b == "UNSAT":
            continue
        m = solve(args.solver, augmented)
        if m == "SAT":
            record["MCF_SAT"] += 1
            continue
        record["baseline_SAT_MCF_UNSAT"] += 1
        record["chosen"] = {"star": star,
                            "root_degrees": [star.count(c) for c in range(4)],
                            "root_star_status": b, "same_star_colour0_MCF_status": m,
                            "physical_variables": top, "base_clauses": len(base),
                            "mcf_top": mcf_top,
                            "mcf_clauses": len(base)+len(extra)+len(units)}
        (args.out/f"frozen{args.n}_baseline.cnf").write_bytes(baseline)
        (args.out/f"frozen{args.n}_mcf.cnf").write_bytes(augmented)
        (args.out/f"frozen{args.n}_counterexample.json").write_text(json.dumps(record, indent=2)+"\n")
        print(json.dumps(record, indent=2))
        return
    (args.out/f"frozen{args.n}_counterexample.json").write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps(record, indent=2))
    raise SystemExit("no counterexample found in requested scan")


if __name__ == "__main__":
    main()
