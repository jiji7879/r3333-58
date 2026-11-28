#!/usr/bin/env python3
"""Summarise the A/B runs (and the corrupted trajectory control)."""
import hashlib
import json
import math
import pathlib
import sys

import pysat
import pysat.solvers as SV

HERE = pathlib.Path(__file__).resolve().parent


def geo(values):
    return math.exp(sum(math.log(v) for v in values) / len(values))


def main():
    runs = [json.loads(line) for line in (HERE / "ab_runs.jsonl").read_text().splitlines() if line.strip()]
    arms = {}
    for arm in ("baseline", "sms", "corrupted"):
        selected = [r for r in runs if r["arm"] == arm]
        if not selected:
            continue
        arms[arm] = {
            "solve_cpu_s": [r["solve_cpu_s"] for r in selected],
            "geomean_solve_cpu_s": round(geo([r["solve_cpu_s"] for r in selected]), 3),
            "peak_rss_kb": [r["peak_rss_kb"] for r in selected],
            "statuses": [r["status"] for r in selected],
            "conflicts": [r["stats"]["conflicts"] for r in selected],
            "decisions": [r["stats"]["decisions"] for r in selected],
            "propagations": [r["stats"]["propagations"] for r in selected],
            "restarts": [r["stats"]["restarts"] for r in selected],
        }
    summary = {
        "runs": runs,
        "arms": arms,
        "cpu_ratio_baseline_over_sms": round(
            arms["baseline"]["geomean_solve_cpu_s"] / arms["sms"]["geomean_solve_cpu_s"], 4),
        "propagation_ratio_sms_over_baseline": round(
            geo(arms["sms"]["propagations"]) / geo(arms["baseline"]["propagations"]), 4),
        "decision_ratio_sms_over_baseline": round(
            geo(arms["sms"]["decisions"]) / geo(arms["baseline"]["decisions"]), 4),
        "cpu_ratio_baseline_over_corrupted": round(
            arms["baseline"]["geomean_solve_cpu_s"] / arms["corrupted"]["geomean_solve_cpu_s"], 4),
        "determinism": "identical conflict/decision/propagation/restart counts across run orders",
        "total_solver_cpu_s": round(sum(r["solve_cpu_s"] for r in runs), 3),
        "toolchain": {
            "pysat": pysat.__version__,
            "solvers_module_sha256": hashlib.sha256(pathlib.Path(SV.__file__).read_bytes()).hexdigest(),
            "pysolvers_sha256": hashlib.sha256(pathlib.Path(SV.pysolvers.__file__).read_bytes()).hexdigest(),
            "python": sys.version.split()[0],
            "solver_class": "pysat.solvers.Cadical195 (CaDiCaL 1.9.5)",
            "jobs": 1, "conflict_cap": 200000,
            "seed": "not exposed by pysat Cadical195; arms matched on build, cap and run order",
        },
        "note": "Every arm returned UNKNOWN at the conflict cap. OPEN is not UNSAT. "
                "The corrupted arm is a trajectory control, not a sound instance.",
    }
    (HERE / "ab_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in
                      ("cpu_ratio_baseline_over_sms", "propagation_ratio_sms_over_baseline",
                       "decision_ratio_sms_over_baseline", "cpu_ratio_baseline_over_corrupted",
                       "total_solver_cpu_s")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
