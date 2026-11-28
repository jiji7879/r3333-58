#!/usr/bin/env python3
"""Reproduce the admission audit of the evidence already in the bank.

Reads only the published receipts under results/next-directions-2026-11-28/,
normalises them with adapters.py, runs gate.evaluate, writes one verdict JSON
per candidate into receipts/, and checks each decision against the pinned
expectation below.  Exit 0 only when every expected decision is reproduced.

    python3 run_audit.py            # write receipts/, verify expectations
    python3 run_audit.py --print    # also print the per-cell ratio tables

No solver is run. Only the selected output directory is written.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def find_repo(start: Path) -> Path:
    """Locate the repository root from wherever this file was copied."""
    for candidate in (start, *start.parents):
        if (candidate / "results/next-directions-2026-11-28").is_dir() and \
                (candidate / "tools/color-resolved-wallcc").is_dir():
            return candidate
    raise SystemExit("cannot locate the repository root from " + str(start))


REPO = find_repo(HERE)
RESULTS = REPO / "results/next-directions-2026-11-28"

sys.path.insert(0, str(HERE))
import adapters  # noqa: E402
import gate  # noqa: E402

# name, source, adapt, trust, primary-metric override, expected decision
PLAN = [
    ("lrat-cpu-cross",       "lrat/receipt.json", "lrat", "cross_checked",  None,             "REJECT"),
    ("lrat-cpu-single",      "lrat/receipt.json", "lrat", "single_checker", None,             "OPT_IN_EVIDENCE_BACKED"),
    ("lrat-bytes-cross",     "lrat/receipt.json", "lrat", "cross_checked",  "retained_bytes", "OPT_IN_SINGLE_CASE"),
    ("kmt-100k",             "kmt/receipt.json",  "kmt",  "cross_checked",  None,             "REJECT"),
    ("kmt-1m",               "kmt/receipt.json",  "kmt",  "cross_checked",  None,             "REJECT"),
    ("sms-one-colour-lex",   "sms",               "sms",  "cross_checked",  None,             "REJECT"),
]


def build(source: str, kind: str, trust: str):
    path = RESULTS / source
    if kind == "lrat":
        return {"": adapters.adapt_lrat(path, trust)}
    if kind == "kmt":
        return {"-100k": adapters.adapt_kmt(path, "benchmark"),
                "-1m": adapters.adapt_kmt(path, "benchmark_1m")}
    return {"": adapters.adapt_sms(path)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", dest="show", action="store_true", help="print per-cell tables")
    ap.add_argument("--out", type=Path, default=HERE / "receipts",
                    help="destination for computed audit receipts (default: alongside this tool)")
    args = ap.parse_args(argv)
    receipts = args.out
    receipts.mkdir(parents=True, exist_ok=True)
    rows, failures = [], 0
    for name, source, kind, trust, metric, expected in PLAN:
        records = build(source, kind, trust)
        if kind == "kmt":
            record = records["-1m"] if name.endswith("1m") else records["-100k"]
        else:
            record = records[""]
        if metric:
            record["prereg"]["primary_metric"] = metric
        verdict = gate.evaluate(record, trust=trust, mode="audit")
        verdict["record_sha256"] = adapters.sha_of_text(json.dumps(record, sort_keys=True))
        out = receipts / f"{name}.json"
        out.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
        ok = verdict["decision"] == expected
        failures += 0 if ok else 1
        agg = verdict.get("aggregate") or {}
        try:
            displayed_receipt = str(out.resolve().relative_to(REPO))
        except ValueError:
            displayed_receipt = str(out)
        rows.append({
            "candidate": name,
            "source": source,
            "trust": trust,
            "metric": agg.get("primary_metric"),
            "pairs": agg.get("pairs"),
            "geomean_ratio": agg.get("geomean_ratio"),
            "max_ratio": agg.get("max_ratio"),
            "min_ratio": agg.get("min_ratio"),
            "decision": verdict["decision"],
            "expected": expected,
            "ok": ok,
            "blocking": verdict["blocking"],
            "receipt": displayed_receipt,
        })
        print(f"{'ok  ' if ok else 'FAIL'} {name:22s} {verdict['decision']:24s} "
              f"metric={agg.get('primary_metric')} geomean={_f(agg.get('geomean_ratio'))} "
              f"worst={_f(agg.get('max_ratio'))} blocking={','.join(verdict['blocking']) or '-'}")
        if args.show:
            for cell in agg.get("per_cell", []):
                print(f"     {cell['case']:>6s} seed {cell['seed']} {cell['order']:2s} cap {cell['cap']:>7d} "
                      f"ratio {cell['ratio']:.4f}")
            for cell in agg.get("excluded_cells", []):
                print(f"     excluded cell: {cell}")
    (receipts / "audit-summary.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    print(f"\n{len(rows) - failures}/{len(rows)} decisions reproduced; summary in {receipts / 'audit-summary.json'}")
    return 0 if failures == 0 else 1


def _f(x):
    return "n/a" if x is None else f"{x:.4f}"


if __name__ == "__main__":
    sys.exit(main())
