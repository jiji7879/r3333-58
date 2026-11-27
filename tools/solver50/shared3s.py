#!/usr/bin/env python3
"""Reusable-CaDiCaL-state comparison on the exact direct3s candidate set."""
from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
from time import monotonic, process_time

import pysolvers
from pysat.solvers import Cadical195


def timed_assumptions(sat, assumptions, seconds: float, campaign: Path):
    cap = ctypes.pythonapi.PyCapsule_GetPointer
    cap.argtypes = [ctypes.py_object, ctypes.c_char_p]
    cap.restype = ctypes.c_void_p
    native = ctypes.CDLL(pysolvers.__file__)
    terminate = getattr(native, "_ZN10CaDiCaL1956Solver9terminateEv")
    timer = ctypes.CDLL(str(campaign / "round50" / "deadline.so"))
    timer.arm_deadline.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double]
    timer.arm_deadline.restype = ctypes.c_void_p
    timer.disarm_deadline.argtypes = [ctypes.c_void_p]
    timer.disarm_deadline.restype = None
    handler = timer.arm_deadline(cap(sat.cadical, None), terminate, seconds)
    try:
        return sat.solve_limited(assumptions=assumptions)
    finally:
        timer.disarm_deadline(handler)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--direct-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.campaign.resolve()
    direct = args.direct_root.resolve()
    direct_trials = next(direct.glob("trials.tsv.gz"))
    direct_dest = direct_trials.parent
    assert direct_dest.name == "timed-sorted-next3s"
    assert (direct_dest / "cohort-summary.json").is_file()
    out = args.out.resolve()
    if out.exists():
        parser.error("choose a new output path")
    dest = root / "round50" / "shared-sorted-next3s"
    if dest.exists():
        raise ValueError("refusing to reuse an existing shared run directory")

    import sys
    sys.path.insert(0, str(root))
    from cheap import group_formula, key, per_row
    from collections import defaultdict
    from common import OUT, canonical, physical, put, sha, tabwrite, tsv, wall
    from physical_order import mapping, sort_key


    rows = wall()[0]
    direct_by_rank = {int(r["rank"]): r for r in tsv(direct_dest / "trials.tsv.gz")}
    if len(direct_by_rank) != 24:
        raise ValueError("shared comparison must use the 24 direct receipts")
    dest.mkdir(parents=True)
    started = monotonic()
    grouped = defaultdict(list)
    for rank, r in sorted(direct_by_rank.items()):
        k = key(rows[r["row_id"]])
        grouped[(k, sort_key(r["row_id"]))].append(r)
    results = []
    test_by_rank = {int(r["rank"]): i for i, r in enumerate(direct_by_rank.values())}
    for group_index, (group, tasks) in enumerate(sorted(grouped.items(), key=lambda item: str(item[0]))):
        kind, geometry = group
        first = tasks[0]["row_id"]
        g, base, flags = group_formula(rows[first])
        top = max(abs(v) for c in g for v in c)
        image, newtop, guard = mapping(first, top)
        g += guard
        digest = sha(canonical(group))
        setup_start = monotonic()
        per_row_cache = {}
        with Cadical195(bootstrap_with=g) as sat:
            setup_s = monotonic() - setup_start
            for t in tasks:
                rid, w, z = t["row_id"], t["w"], t["z"]
                if rid not in per_row_cache:
                    per_row_cache[rid] = per_row(rows[rid], base, flags)
                assumptions = per_row_cache[rid] + physical(rid, w, z)
                old = sat.accum_stats()["conflicts"]
                started_call = monotonic()
                cpu_start = process_time()
                response = timed_assumptions(sat, assumptions, 3.0, root)
                elapsed = monotonic() - started_call
                hits = sat.accum_stats()["conflicts"] - old
                direct_receipt = json.loads((direct_dest / f"{test_by_rank[int(t['rank'])]}.json").read_bytes())
                direct_unsat = direct_receipt["status"] == "VERIFIED_UNSAT"
                if response is False:
                    outcome = "SHARED_UNSAT_DIRECT_VERIFIED" if direct_unsat else "SHARED_UNSAT_DIRECT_OPEN"
                elif response is True:
                    outcome = "SHARED_SAT"
                else:
                    outcome = "SHARED_OPEN"
                results.append({
                    "wave": "shared-sorted-3s", "rank": int(t["rank"]), "test": test_by_rank[int(t["rank"])],
                    "row_id": rid, "w": w, "z": z, "group": digest, "block": group_index,
                    "assumptions_sha256": sha(canonical(assumptions)),
                    "cap": 3.0, "conflicts": hits, "search_s": elapsed,
                    "cpu_s": process_time() - cpu_start,
                    "group_setup_s": setup_s,
                    "shared_status": outcome,
                    "direct_status": direct_receipt["status"],
                    "direct_query_sha256": direct_receipt["query_sha"],
                    "direct_proof_sha256": direct_receipt["proof_sha"],
                    "whole_row_claim": False,
                })
    tabwrite(dest / "trials.tsv.gz", results)
    report = {
        "schema": "k58-shared-sorted-3s-cohort/v1",
        "records": len(results),
        "blocks": len(grouped),
        "direct_status_counts": {s: sum(r["direct_status"] == s for r in results)
                                 for s in sorted({r["direct_status"] for r in results})},
        "shared_status_counts": {s: sum(r["shared_status"] == s for r in results)
                                 for s in sorted({r["shared_status"] for r in results})},
        "sum_shared_search_seconds": sum(r["search_s"] for r in results),
        "max_shared_search_seconds": max(r["search_s"] for r in results),
        "sum_shared_conflicts": sum(r["conflicts"] for r in results),
        "whole_original_rows_closed": 0,
    }
    (dest / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    put(dest / "selection.json", canonical(list(direct_by_rank.values())))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(canonical(report))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
