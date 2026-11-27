#!/usr/bin/env python3
"""Run fresh three-second direct CaDiCaL beyond the supplied six controls."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
from time import monotonic


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("campaign", type=Path)
    p.add_argument("--count", type=int, default=24)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    root = args.campaign.resolve()
    out = args.out.resolve()
    if out.exists() or args.count < 1:
        p.error("choose a positive count and a new output path")
    import sys
    sys.path.insert(0, str(root))
    import timed50
    import verify50
    from common import OUT, canonical, put, tabwrite, tsv

    dest = root / "round50" / "timed-sorted-next3s"
    if dest.exists():
        raise ValueError("refusing to reuse an existing three-second run directory")
    source = tsv(OUT / "round50-sorted-sample.tsv.gz")
    cheap = tsv(OUT / "round50-cheap-sorted.tsv.gz")
    selected = []
    for row, result in zip(source, cheap, strict=True):
        if result["status"] != "OPEN":
            continue
        r = {k: row[k] for k in ("row_id", "arm", "w", "z", "profile", "rank")}
        if int(r["rank"]) < 6:
            continue  # The supplied fresh-sorted batch; no double counting.
        selected.append(r)
        if len(selected) >= args.count:
            break
    if len(selected) != args.count:
        raise ValueError("not enough fresh cap-OPEN candidates")
    dest.mkdir(parents=True)
    started = monotonic()
    jobs = [(i, "fresh-sorted-3s-open", "sorted", row) for i, row in enumerate(selected)]
    put(dest / "selection.json", canonical(jobs))
    receipts = []
    try:
        for job in jobs:
            receipts.append(timed50.run(job))
        # Receipts are canonicalized only after each actual solver call. Validate
        # exact full query, timing, and every produced proof independently.
        for rec in sorted(dest.glob("[0-9]*.json")):
            verify50.timed_receipt(rec)
        tabwrite(dest / "trials.tsv.gz", receipts)
        successes = [r for r in receipts if r["status"] == "VERIFIED_UNSAT"]
        tampered_ok = None
        if successes:
            rec = successes[0]
            i = rec["test"]
            old = json.loads((dest / f"{i}.json").read_bytes())
            proof = gzip.decompress((dest / f"{i}.drat.gz").read_bytes())
            assert proof.startswith(b"a"), "expected binary proof for tamper control"
            bad = b"X\0" + proof
            badrec = dict(old, proof_sha=hashlib.sha256(bad).hexdigest(),
                          proof_bytes=len(bad))
            (dest / "tampered.json").write_bytes(canonical(badrec))
            (dest / "tampered.drat.gz").write_bytes(gzip.compress(bad, mtime=0))
            try:
                verify50.timed_receipt(dest / "tampered.json")
            except (AssertionError, ValueError, RuntimeError):
                tampered_ok = True
            else:
                tampered_ok = False
            if not tampered_ok:
                raise AssertionError("hash-matched malformed proof was accepted")
            (dest / "tampered.json").unlink()
            (dest / "tampered.drat.gz").unlink()
        summary = {
            "schema": "k58-fresh-sorted-3s-cohort/v1",
            "records": len(receipts),
            "status_counts": {s: sum(r["status"] == s for r in receipts)
                              for s in sorted({r["status"] for r in receipts})},
            "new_cap_open_candidates_outside_supplied_six": len(receipts),
            "search_budget_seconds_per_call": 3.0,
            "workers": 1,
            "total_coordinator_seconds": monotonic() - started,
            "sum_search_seconds": sum(r["search_s"] for r in receipts),
            "max_search_seconds": max(r["search_s"] for r in receipts),
            "sum_proof_bytes": sum(r["proof_bytes"] for r in receipts),
            "tampered_proof_rejected": tampered_ok,
            "whole_original_rows_closed": 0,
        }
    finally:
        if "summary" in locals():
            (dest / "cohort-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(canonical(summary))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
