#!/usr/bin/env python3
"""Adapters: repository evidence files -> normalised admission records.

The gate (gate.py) evaluates a normalised record.  These adapters are the only
place that knows the shapes of the artifacts already in the bank:

  lrat  results/next-directions-2026-11-28/lrat/receipt.json
        armA_drat / armB_native_lrat / comparison / controls per closed CNF
  kmt   results/next-directions-2026-11-28/kmt/receipt.json
        benchmark (100k) and benchmark_1m call lists, A/B/B/A order
  sms   results/next-directions-2026-11-28/sms/ab_summary.json + ab_runs.jsonl
        baseline / sms / corrupted arms, two orders per arm

Adapters never invent a value: where the file does not record something (an
input hash, a solver binary hash, a seed) the field is left unpinned and the
deficit is written to provenance.warnings.  The gate then fails closed on it.

Usage:
    python3 adapters.py lrat RECEIPT [--trust cross_checked|single_checker] --out R.json
    python3 adapters.py kmt  RECEIPT --out-prefix R
    python3 adapters.py sms  DIR    --out R.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = 1
MARGIN = 0.10
VERIFIED_PAT = re.compile(r"^\s*s\s+VERIFIED\s*$", re.MULTILINE)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_of_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def probe_verified_line(log_path):
    """Confirm the literal `s VERIFIED` line in a pinned checker log."""
    if not log_path:
        return {"found": False, "reason": "no log path recorded"}
    p = Path(log_path)
    if not p.is_file():
        return {"found": False, "reason": "log file absent", "path": str(p)}
    try:
        text = p.read_text(errors="replace")
    except OSError as exc:  # pragma: no cover - unreadable log
        return {"found": False, "reason": f"log unreadable: {exc}", "path": str(p)}
    if not VERIFIED_PAT.search(text):
        return {"found": False, "reason": "no `s VERIFIED` line", "path": str(p),
                "log_sha256": sha256_file(p)}
    return {"found": True, "path": str(p), "log_sha256": sha256_file(p),
            "line": "s VERIFIED"}


def _run(case, arm, seed, order, cap, status, search=None, check=None, prep=0.0,
         proof_bytes=None, retained_bytes=None, rss_kb=None, counters=None,
         metric_valid=None, solver_sha256=None):
    metrics = {"search_cpu_s": search, "check_cpu_s": check, "prep_cpu_s": prep}
    if proof_bytes is not None:
        metrics["proof_bytes"] = int(proof_bytes)
    if retained_bytes is not None:
        metrics["retained_bytes"] = int(retained_bytes)
    if rss_kb is not None:
        metrics["maxrss_kb"] = float(rss_kb)
    entry = {"case": case, "arm": arm, "seed": seed, "order": order, "cap": cap,
             "status": status, "metrics": metrics}
    if counters:
        entry["counters"] = counters
    if metric_valid:
        entry["metric_valid"] = metric_valid
    if solver_sha256:
        entry["solver_sha256"] = solver_sha256
    return entry


# --------------------------------------------------------------------------
# lrat
# --------------------------------------------------------------------------
def adapt_lrat(path: Path, trust: str) -> dict:
    rec = json.loads(path.read_text())
    pins = rec["pins"]
    cadical_sha = pins["cadical"]["sha256"]
    lrat_sha = pins["lrat_trim"]["sha256"]
    second = pins.get("second_checker", {})
    cap = int(pins["solver_args"]["conflicts"])
    runs, cases, exclusions = [], [], []
    cert_ok, exit_ok, cross_ok, vline_ok = True, True, True, True
    vline_sources = []
    controls = {}
    for cid, d in rec["cases"].items():
        cases.append(cid)
        a, b = d["armA_drat"], d["armB_native_lrat"]
        base_total = float(a["total_cpu_s"])
        treat_total = float(b["total_cpu_s_with_second_checker"] if trust == "cross_checked"
                            else b["total_cpu_s"])
        probe = probe_verified_line((b.get("check") or {}).get("replays", {}).get("replay", {}).get("log"))
        vline_sources.append({"case": cid, **probe})
        if not probe.get("found"):
            vline_ok = False
        exit_code = (b.get("check") or {}).get("replays", {}).get("replay", {}).get("rc")
        if exit_code != 20:
            exit_ok = False
        if (b.get("second_checker") or {}).get("rc") != 20:
            cross_ok = False
        reproduced = bool(d["armC_retained"].get("fresh_drat_matches_retained"))
        if not reproduced:
            exclusions.append(cid)
        both_valid = {"retained_bytes": reproduced}
        shared = d["comparison"].get("counters") or {}
        counters_a = a.get("stats") or shared
        counters_b = b.get("stats") or shared
        runs.append(_run(cid, "baseline", 0, "AB", cap,
                         "VERIFIED_UNSAT" if a.get("rc") == 20 else "CHECK_FAILED",
                         search=float(a["cpu_s"]), check=base_total - float(a["cpu_s"]),
                         proof_bytes=a["bytes"], retained_bytes=a["bytes"],
                         rss_kb=max(float(a.get("maxrss_kb") or 0), float((a.get("verify") or {}).get("maxrss_kb") or 0)),
                         counters=counters_a, metric_valid=both_valid,
                         solver_sha256=cadical_sha))
        runs.append(_run(cid, "treatment", 0, "AB", cap,
                         "VERIFIED_UNSAT" if exit_code == 20 and (b.get("second_checker") or {}).get("rc") == 20
                         else "CHECK_FAILED",
                         search=float(b["cpu_s"]), check=treat_total - float(b["cpu_s"]),
                         proof_bytes=b["retained_bytes"], retained_bytes=b["retained_bytes"],
                         rss_kb=float(b.get("maxrss_kb") or 0), counters=counters_b,
                         metric_valid=both_valid, solver_sha256=cadical_sha))
        for name, c in (d.get("controls") or {}).items():
            if not isinstance(c, dict) or "rejected" not in c:
                continue        # pure metadata (e.g. altered_antecedent_detail) is not a control
            slot = controls.setdefault(name, {"id": name, "role": "unsound_control",
                                              "rejected_cases": [], "accepted_cases": []})
            (slot["rejected_cases"] if c.get("rejected") is True else slot["accepted_cases"]).append(cid)
    control_list = []
    for name, slot in sorted(controls.items()):
        slot["semantics_rejected"] = not slot["accepted_cases"]
        control_list.append(slot)
    inputs = {}
    for cid in cases:
        pin = {"sha256": rec["cases"][cid]["input"]["sha256"],
               "bytes": int(rec["cases"][cid]["input"]["bytes"])}
        inputs[cid] = {"baseline": dict(pin), "treatment": dict(pin)}
    record = {
        "schema": SCHEMA,
        "claim": {
            "id": f"lrat-native-certificate-{trust}",
            "class": "certificate",
            "statement": ("on the pinned already-closed CNFs, native CaDiCaL LRAT checked by the "
                          "pinned lrat-trim costs less CPU/bytes than the incumbent DRAT + drat-trim "
                          f"route at trust={trust}; the search trajectory is identical, so this is "
                          "not a CDCL speedup"),
            "scope": rec.get("scope", ""),
            "closure_claimed": True,
        },
        "prereg": {
            "registered_before_run": None,          # not recorded in the published receipt
            "declared_arms": ["baseline", "treatment"],
            "primary_metric": "composite_cpu_s",
            "margin": MARGIN,
            "max_runs": len(runs),
            "cases": cases, "caps": [cap], "seeds": [0], "orders": ["AB"],
            "declared_exclusions": exclusions,
        },
        "pins": {
            "inputs": inputs,
            "solver": {"id": "cadical", "version": pins["cadical"]["version"],
                       "sha256": cadical_sha},
            "checkers": [
                {"id": "drat-trim", "sha256": pins["drat_trim"]["sha256"]},
                {"id": "lrat-trim", "sha256": lrat_sha,
                 "version": pins["lrat_trim"].get("version")},
                {"id": "lrat_rup_check.py", "sha256": second.get("sha256"),
                 "trust": "unverified-source"},
            ],
        },
        "transform": {
            "kind": "certificate_format",
            "declared_delta": ("proof format only: native CaDiCaL --lrat + lrat-trim vs DRAT + "
                               "drat-trim on byte-identical CNFs; no clause, option or search change"),
            "binding": "none",
            "derivation": None,
        },
        "certificate": {
            "status": "VERIFIED_UNSAT" if (cert_ok and exit_ok and cross_ok) else "CHECK_FAILED",
            "checker_sha256": lrat_sha,
            "checker_exit": 20 if exit_ok else None,
            "verified_line": {"found": vline_ok,
                              "per_case": vline_sources,
                              "log_sha256": (vline_sources[0].get("log_sha256") if vline_sources else None)},
            "relax_used": False,
            "cost_basis": "cross_checked" if trust == "cross_checked" else "single_checker",
            "cross_check": {"status": "VERIFIED_UNSAT" if cross_ok else "CHECK_FAILED",
                            "checker_sha256": second.get("sha256")},
        },
        "runs": runs,
        "controls": control_list,
        "provenance": {
            "source": str(path),
            "source_sha256": sha256_file(path),
            "adapter": "adapters.py lrat",
            "warnings": ["preregistration is not recorded in the published receipt"],
        },
    }
    return record


# --------------------------------------------------------------------------
# kmt
# --------------------------------------------------------------------------
def adapt_kmt(path: Path, tag: str) -> dict:
    rec = json.loads(path.read_text())
    bench = rec[tag]
    cap = int(bench["conflict_budget"])
    src_sha = sha256_file(path)
    sem = rec.get("gadget_semantics", {})
    pres = rec.get("preservation", {})
    deriv_pass = bool(sem.get("all_checks_pass")) and bool(pres.get("logical_comparison_ok")) \
        and bool((pres.get("root_bcp") or {}).get("agreement"))
    arms = {"stock": "baseline", "kmt": "treatment"}
    runs = []
    for call in bench["calls"]:
        order = "AB" if int(call["sequence"]) <= 2 else "BA"
        runs.append(_run("parent-cube", arms[call["arm"]], int(call["seed"]), order, cap,
                         call["status"],
                         search=float(call["search_process_cpu_seconds"]),
                         check=0.0,
                         prep=float(call["bootstrap_process_cpu_seconds"]) + float(call["parse_process_cpu_seconds"]),
                         rss_kb=float(call["maxrss_kib"]),
                         counters=call.get("stats")))
    parents = rec["parents"]
    record = {
        "schema": SCHEMA,
        "claim": {
            "id": f"kmt-sender-only-{tag}",
            "class": "encoding",
            "statement": (f"sender-only KMT encoding reduces search CPU against the stock encoding on the "
                          f"retained parent+cube at a matched {cap}-conflict budget; all runs are OPEN"),
            "scope": (bench.get("analysis") or {}).get("scope", ""),
            "closure_claimed": False,
        },
        "prereg": {
            "registered_before_run": None,
            "declared_arms": ["baseline", "treatment", "stock", "kmt"],
            "primary_metric": "composite_cpu_s",
            "margin": MARGIN,
            "max_runs": len(runs),
            "cases": ["parent-cube"], "caps": [cap], "seeds": [0, 1], "orders": ["AB", "BA"],
            "declared_exclusions": [],
        },
        "pins": {
            "inputs": {"parent-cube": {
                "baseline": {"sha256": parents["stock"]["sha256"],
                             "bytes": int(parents["stock"]["bytes"])},
                "treatment": {"sha256": parents["kmt"]["sha256"],
                              "bytes": int(parents["kmt"]["bytes"])}}},
            "solver": {"id": bench.get("engine", "pysat Cadical195"),
                       "version": rec.get("interpreter", "") and bench.get("engine", ""),
                       "sha256": None},
            "checkers": [],
            "cube": {"literals": parents["cube"].get("literals"),
                     "appended_as_units": parents["cube"].get("appended_as_units"),
                     "baseline_cube_sha256": parents.get("stock_cube", {}).get("sha256"),
                     "treatment_cube_sha256": parents.get("kmt_cube", {}).get("sha256")},
        },
        "transform": {
            "kind": "encoding",
            "declared_delta": ("sender AtLeast(30,10)/AtLeast(41,14) gadgets replaced by totalizers; "
                               f"{parents['kmt']['variables']} vars / {parents['kmt']['clauses']} clauses vs "
                               f"{parents['stock']['variables']} / {parents['stock']['clauses']}"),
            "binding": "budget_hash",
            "derivation": {
                "kind": "in-receipt semantic controls (gadget semantics, root BCP, preservation)",
                "status": "pass" if deriv_pass else "fail",
                "receipt_sha256": src_sha,
                "relax_used": False,
                "source": "same receipt; not independently replayed by this gate",
            },
        },
        "runs": runs,
        "controls": [],
        "provenance": {
            "source": str(path), "source_sha256": src_sha, "adapter": "adapters.py kmt",
            "warnings": ["solver binary is not hash-pinned (PySAT binding records only a version string)",
                         "no unsound/trajectory control arm in this experiment",
                         "order is confounded with seed: each seed is measured in one order only"],
        },
    }
    return record


# --------------------------------------------------------------------------
# sms
# --------------------------------------------------------------------------
def adapt_sms(directory: Path) -> dict:
    summary = json.loads((directory / "ab_summary.json").read_text())
    runs_raw = [json.loads(line) for line in (directory / "ab_runs.jsonl").read_text().splitlines() if line.strip()]
    cap = int(summary["arms"]["baseline"]["conflicts"][0])
    seen = {}
    runs = []
    arm_map = {"baseline": "baseline", "sms": "treatment"}
    for raw in runs_raw:
        if raw["arm"] not in arm_map:
            continue          # the corrupted arm is a control, not a measured arm
        n = seen.get(raw["arm"], 0)
        seen[raw["arm"]] = n + 1
        order = "AB" if n == 0 else "BA"
        runs.append(_run("parent-cube", arm_map[raw["arm"]], 0, order, cap, raw["status"],
                         search=float(raw["solve_cpu_s"]), check=0.0,
                         prep=float(raw["prep_cpu_s"]), rss_kb=float(raw["peak_rss_kb"]),
                         counters=raw.get("stats")) | {"variant": raw["input"]})
    base_mean = summary["arms"]["baseline"]["geomean_solve_cpu_s"]
    sms_mean = summary["arms"]["sms"]["geomean_solve_cpu_s"]
    corr_mean = summary["arms"]["corrupted"]["geomean_solve_cpu_s"]
    gen = directory / "gen_receipt.json"
    record = {
        "schema": SCHEMA,
        "claim": {
            "id": "sms-one-colour-lex",
            "class": "encoding",
            "statement": ("adding 765 one-colour lex-leader clauses to the retained parent+cube lowers "
                          f"search CPU at a matched {cap}-conflict budget; all runs UNKNOWN, none closed"),
            "scope": ("CNF-only bounded performance on the retained parent+cube at a conflict cap; "
                      "UNKNOWN is not UNSAT; no physical model-set invariance, colouring or bound claim"),
            "closure_claimed": False,
        },
        "prereg": {
            "registered_before_run": None,
            "declared_arms": ["baseline", "treatment", "corrupted"],
            "primary_metric": "composite_cpu_s",
            "margin": MARGIN,
            "max_runs": len(runs_raw),
            "cases": ["parent-cube"],
            "caps": [cap], "seeds": [0], "orders": ["AB", "BA"],
            "declared_exclusions": [],
        },
        "pins": {
            "inputs": {"parent-cube": {"baseline": {"sha256": None, "bytes": None},
                                       "treatment": {"sha256": None, "bytes": None}}},
            "solver": {"id": summary["runs"][0]["solver"], "version": summary["runs"][0]["solver"],
                       "sha256": None},
            "checkers": [],
        },
        "transform": {
            "kind": "encoding",
            "declared_delta": "765 one-colour lex-leader clauses appended (non-contiguous variable reindexing)",
            "binding": "budget_hash",
            "derivation": {
                "kind": "lex-leader enumeration over one colour",
                "status": "fail",
                "receipt_sha256": sha256_file(gen) if gen.is_file() else None,
                "relax_used": False,
                "source": "gen_receipt.json; physical model-set invariance is unproved",
            },
        },
        "runs": runs,
        "controls": [{
            "id": "corrupted-one-colour-clauses",
            "role": "unsound_control",
            "semantics_rejected": False,
            "apparent_ratio": corr_mean / base_mean,
            "detail": ("same 765 clauses with one negated literal; unsound instance, run only as a "
                       "trajectory control"),
        }],
        "provenance": {
            "source": str(directory), "source_sha256": sha_of_text(
                (directory / "ab_summary.json").read_text() + (directory / "ab_runs.jsonl").read_text()),
            "adapter": "adapters.py sms",
            "means": {"baseline": base_mean, "treatment": sms_mean, "control": corr_mean},
            "warnings": ["no input CNF hash in ab_summary/ab_runs",
                         "no solver binary hash",
                         "solver seed is not recorded",
                         "the experiment's own summary reports an equally large effect for the "
                         "unsound corrupted control"],
        },
    }
    return record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=("lrat", "kmt", "sms"))
    ap.add_argument("source", help="receipt file, or the sms result directory")
    ap.add_argument("--trust", choices=("cross_checked", "single_checker"), default="cross_checked")
    ap.add_argument("--out", help="write the record here")
    ap.add_argument("--out-prefix", help="(kmt) write PREFIX-100k.json and PREFIX-1m.json")
    args = ap.parse_args(argv)
    src = Path(args.source)
    if args.kind == "lrat":
        records = {"": adapt_lrat(src, args.trust)}
    elif args.kind == "kmt":
        records = {"-100k": adapt_kmt(src, "benchmark"), "-1m": adapt_kmt(src, "benchmark_1m")}
    else:
        records = {"": adapt_sms(src)}
    if args.out_prefix:
        for suffix, rec in records.items():
            out = Path(f"{args.out_prefix}{suffix}.json")
            out.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
            print(f"wrote {out}")
        return 0
    if len(records) != 1 or args.out is None:
        print("use --out (single record) or --out-prefix (kmt)", file=sys.stderr)
        return 2
    Path(args.out).write_text(json.dumps(records[""], indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
