#!/usr/bin/env python3
"""Matched fresh/shared 3-second tests on frozen ARM_WITNESS candidates."""
from __future__ import annotations

import argparse
import csv
import hashlib
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path
from time import monotonic


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reuse-direct-validated", action="store_true")
    args = parser.parse_args()
    root = args.campaign.resolve()
    out = args.out.resolve()
    if out.exists():
        parser.error("choose a new output path")
    import sys
    sys.path.insert(0, str(root))
    import timed50
    import verify50
    from cheap import group_formula, key, per_row
    from common import canonical, host, physical, put, sha, tabwrite, tsv, wall
    from shared3s import timed_assumptions
    from physical_order import mapping, sort_key
    from pysat.solvers import Cadical195

    with args.candidates.open(newline="") as stream:
        candidates = list(csv.DictReader(stream, delimiter="\t"))
    if len(candidates) != 12 or {r["convention"] for r in candidates} != {"sorted"}:
        raise ValueError("expected exactly 12 sorted survivor jobs")
    if any(r["local_arm"] != "ARM_WITNESS" or r["prior_3s"] != "UNTESTED" for r in candidates):
        raise ValueError("candidate eligibility changed")
    if {r["job_id"] for r in candidates} != {f"S13-0{i}" for i in range(6)} | {f"S14-0{i}" for i in range(6)}:
        raise ValueError("unexpected candidate set")
    direct_dest = root / "round50" / "timed-survivors-3s"
    shared_dest = root / "round50" / "shared-survivors-3s"
    if (direct_dest.exists() and not args.reuse_direct_validated) or shared_dest.exists() and any(shared_dest.iterdir()):
        raise ValueError("refusing to reuse/replace existing survivor state")
    direct_dest.mkdir(parents=True, exist_ok=True)
    shared_dest.mkdir(parents=True, exist_ok=True)
    rows = wall()[0]

    # Two fast and independently replayed liveness controls use the supplied IDs.
    control_rows = []
    for original_index in (0, 1):
        original = root / "round50/timed-sorted" / f"{original_index}.json"
        original_receipt = json.loads(original.read_bytes())
        verify50.timed_receipt(original)
        control_rows.append({
            "job_id": f"CONTROL-{original_index}",
            "test": len(candidates) + original_index,
            "row": {k: original_receipt[k] for k in ("row_id", "arm", "w", "z", "profile", "rank")},
        })
    all_jobs = [
        {"job_id": r["job_id"], "test": i,
         "row": {k: r[k] for k in ("row_id", "arm", "w", "z", "profile", "rank")}}
        for i, r in enumerate(candidates)
    ] + control_rows

    direct_records = {}
    if args.reuse_direct_validated:
        for job in all_jobs:
            direct_records[job["job_id"]] = json.loads((direct_dest / f"{job['test']}.json").read_bytes())
            verify50.timed_receipt(direct_dest / f"{job['test']}.json")
    started = monotonic()
    if not args.reuse_direct_validated:
        for job in all_jobs:
            direct_records[job["job_id"]] = timed50.run(
                (job["test"], "fresh-sorted-survivors-3s", "sorted", job["row"]))
            verify50.timed_receipt(direct_dest / f"{job['test']}.json")
    tabwrite(direct_dest / "trials.tsv.gz", list(direct_records.values()))
    if any(direct_records[f"CONTROL-{i}"]["status"] != "VERIFIED_UNSAT" for i in (0, 1)):
        raise AssertionError("a liveness control did not refute")

    # Keep shared state separate for each frozen group. Verify its grouping hashes
    # independently, but do not mistake metadata hashes for formula identity.
    groups = defaultdict(list)
    for r in candidates:
        groups[(int(r["shared_block"]), r["shared_group"])].append(r)
    if sorted(block for block, _ in groups) != [1, 95]:
        raise ValueError("expected the frozen shared blocks 1 and 95")
    shared_results = []
    for (block, group_hash), tasks in sorted(groups.items()):
        tasks.sort(key=lambda r: int(r["rank"]))
        first = tasks[0]["row_id"]
        g, base, flags = group_formula(rows[first])
        group = (key(rows[first]), sort_key(first))
        if sha(canonical(group)) != group_hash:
            raise ValueError("shared grouping metadata mismatch")
        top = max(abs(v) for c in g for v in c)
        _, newtop, guard = mapping(first, top)
        g += guard
        per_row_cache = {}
        with Cadical195(bootstrap_with=g) as sat:
            for r in tasks:
                rid, w, z = r["row_id"], r["w"], r["z"]
                if rid not in per_row_cache:
                    per_row_cache[rid] = per_row(rows[rid], base, flags)
                signed = per_row_cache[rid]
                assumptions = signed + physical(rid, w, z)
                expected_assumptions = sha(canonical(assumptions))
                if expected_assumptions != r["bulk_assumptions_sha256"]:
                    raise ValueError("bulk assumptions proof binding mismatch")
                before = sat.accum_stats()["conflicts"]
                start = monotonic()
                response = timed_assumptions(sat, assumptions, 3.0, root)
                elapsed = monotonic() - start
                actual = sat.accum_stats()["conflicts"] - before
                direct = direct_records[r["job_id"]]
                if response is False:
                    status = "SHARED_UNSAT_DIRECT_VERIFIED" if direct["status"] == "VERIFIED_UNSAT" else "SHARED_UNSAT_DIRECT_OPEN"
                elif response is True:
                    status = "SHARED_SAT"
                else:
                    status = "SHARED_OPEN"
                shared_results.append({
                    "job_id": r["job_id"], "shared_block": block, "group": group_hash,
                    "row_id": rid, "w": w, "z": z, "assumptions_sha256": expected_assumptions,
                    "search_s": elapsed, "conflicts": actual, "shared_status": status,
                    "direct_status": direct["status"], "direct_test": direct["test"],
                    "direct_query_sha": direct["query_sha"], "direct_proof_sha": direct["proof_sha"],
                })
    tabwrite(shared_dest / "trials.tsv.gz", shared_results)
    if any(r["shared_status"] == "SHARED_UNSAT_DIRECT_OPEN" for r in shared_results):
        # Never promote a group-only refutation to a newly certified full representative.
        flag = "shared_only_unsat_without_direct_proof"
    else:
        flag = "no_shared_only_closure_claim"

    # One hash-updated, malformed-prefix proof must still fail strict validation.
    control = next(r for r in all_jobs if r["job_id"] == "CONTROL-0")
    control_path = direct_dest / f"{control['test']}.drat.gz"
    proof = gzip.decompress(control_path.read_bytes())
    bad = b"X\0" + proof
    bad_receipt = json.loads((direct_dest / f"{control['test']}.json").read_bytes())
    bad_receipt.update(proof_sha=hashlib.sha256(bad).hexdigest(), proof_bytes=len(bad))
    (direct_dest / "tampered.json").write_bytes(canonical(bad_receipt))
    (direct_dest / "tampered.drat.gz").write_bytes(gzip.compress(bad, mtime=0))
    try:
        verify50.timed_receipt(direct_dest / "tampered.json")
    except (AssertionError, ValueError, RuntimeError):
        tamper_rejected = True
    else:
        tamper_rejected = False
    if not tamper_rejected:
        raise AssertionError("a hash-matched malformed proof was accepted")
    (direct_dest / "tampered.json").unlink()
    (direct_dest / "tampered.drat.gz").unlink()

    report = {
        "schema": "k58-survivor-fresh-shared-3s/v1",
        "eligible_jobs": len(candidates),
        "direct_status_counts": dict(Counter(r["status"] for r in direct_records.values()
                                             if r["test"] < len(candidates))),
        "shared_status_counts": dict(Counter(r["shared_status"] for r in shared_results)),
        "fast_control_calls_excluded_from_comparison": 2,
        "tamper_rejected": tamper_rejected,
        "direct_search_seconds": sum(r["search_s"] for r in direct_records.values()),
        "shared_search_seconds": sum(r["search_s"] for r in shared_results),
        "total_coordinator_seconds": monotonic() - started,
        "scope": flag,
        "whole_original_rows_closed": 0,
        "next_step": "STOP after this matched cohort; no cap increase or additional split",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(canonical(report))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
