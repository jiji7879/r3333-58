#!/usr/bin/env python3
"""Solve the one-critical profiles directly, with a chosen encoding and budget.

`(15,14,14,14)` and `(16,14,14,13)` are the profiles where the ticket argument
is weakest: 469 cases, none closed.  This drives `dense.solve_case` directly so a
single tier can be used without the first-pass/retry two-step, and reports the
closure rate and per-case cost.

    python3 solve_weak.py --bundle K58 --out work --limit 40 --seconds 60 --workers 3
    python3 solve_weak.py --bundle K58 --out work --workers 3 --full-root
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

WEAK = {(15, 14, 14, 14), (16, 14, 14, 13)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--kissat", required=True)
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--seconds", type=int, default=60)
    p.add_argument("--budget", type=int, default=2400000)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--full-root", action="store_true",
                   help="add H(r) >= w(r); for a one-critical root this is the only real constraint")
    p.add_argument("--shuffle", type=int, default=0)
    a = p.parse_args()

    bundle = Path(a.bundle).resolve()
    sys.path.insert(0, str(bundle))
    import cover_evidence as ce
    from dense import solve_case
    from gluing import Family

    rows = []
    for r in ce.records(bundle / "case-ledger.jsonl.gz"):
        if tuple(r["family"]["profile"]) in WEAK:
            rows.append(r)
    rows.sort(key=lambda r: r["id"])
    if a.shuffle:
        import random
        random.Random(a.shuffle).shuffle(rows)
    if a.limit:
        rows = rows[:a.limit]
    print(f"{len(rows)} cases, {a.workers} workers, {a.seconds}s / {a.budget} conflicts, "
          f"full_root={a.full_root}", flush=True)

    cfg = argparse.Namespace(kissat=a.kissat, tables=True, total_critical=True,
                             full_root=a.full_root, seconds=a.seconds, budget=a.budget,
                             solver_identity=None)
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    def one(row):
        fam = dict(row["family"])
        fam["profile"] = tuple(fam["profile"])
        fam["root_kinds"] = tuple(fam["root_kinds"])
        family = Family(**fam)
        dest = out / ("full_root" if a.full_root else "first_pass") / f"{a.seconds}s-{a.budget}"
        t0 = time.monotonic()
        try:
            solve_case(family, row["placement"], row["branch"], row["charge"], cfg, dest)
        except RuntimeError as e:
            return dict(id=row["id"], status="ERROR", error=str(e)[:200])
        stem = dest / f"{''.join(family.root_kinds)}_{family.arm}_{row['branch']}"
        rec = json.loads(stem.with_suffix(".jsonl").read_text())
        return dict(id=row["id"], status=rec["status"], cpu=rec["cpu_seconds"],
                    elapsed=time.monotonic() - t0, proof=rec.get("proof_bytes", 0),
                    profile=list(row["family"]["profile"]))

    t0 = time.monotonic()
    results = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for i, r in enumerate(pool.map(one, rows), 1):
            results.append(r)
            if i % 10 == 0 or i == len(rows):
                done = [x for x in results if x["status"] != "ERROR"]
                unsat = sum(1 for x in done if x["status"] == "UNSAT")
                print(f"  {i}/{len(rows)}  UNSAT {unsat}  OPEN {sum(1 for x in done if x['status']=='OPEN')}",
                      flush=True)
    wall = time.monotonic() - t0
    unsat = [x for x in results if x["status"] == "UNSAT"]
    print(json.dumps(dict(cases=len(results), unsat=len(unsat),
                          open=len(results) - len(unsat),
                          rate=round(len(unsat) / max(1, len(results)), 3),
                          wall_seconds=round(wall, 1),
                          mean_cpu=round(sum(x.get("cpu", 0) for x in results) / max(1, len(results)), 2),
                          median_cpu=sorted(x.get("cpu", 0) for x in results)[len(results) // 2] if results else 0,
                          mean_proof_mb=round(sum(x.get("proof", 0) for x in unsat) / max(1, len(unsat)) / 1e6, 2),
                          full_root=a.full_root, seconds=a.seconds), indent=1))
    (out / f"summary-{'fr' if a.full_root else 'fp'}-{a.seconds}s.json").write_text(json.dumps(results))


if __name__ == "__main__":
    main()
