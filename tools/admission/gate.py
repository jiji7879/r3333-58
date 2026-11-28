#!/usr/bin/env python3
"""Admission gate for K58 solver-speedup claims (policy k58-admission-1).

The gate decides, from a *normalised evidence record* only, whether a claimed
speedup or cost change is eligible to become an opt-in production override.
It never runs a solver, never edits the tree, and never upgrades a status:
a capped OPEN search stays OPEN, and a certificate is admissible only with a
pinned checker, exit 20 and the checker's literal success line.

Two modes:

  admission     prospective: everything is required.  Used by the coordinator
                before merging an override.  Missing pre-registration blocks.
  audit         retrospective: a deficit that cannot be repaired after the fact
                (pre-registration, arm list) is recorded as a warning, but every
                other rule still blocks.  Used on already-published receipts.

Exit codes: 0 = opt-in eligible (evidence-backed or single-case limited),
2 = rejected on the evidence, 3 = incomplete / fail-closed.

Standard library only.  Deterministic: no clock, no randomness, no network.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

POLICY_VERSION = "k58-admission-1"
SCHEMA = 1
HEX = set("0123456789abcdef")

CLASSES = {
    "certificate",      # same CNF, different proof/checking pipeline
    "search",           # solver-search change (clauses, restart order, ...)
    "options",          # solver option values
    "engine",           # solver binary / version
    "encoding",         # formula encoding or added derived clauses
    "preprocessing",    # one-shot CNF preprocessing
    "policy",           # human-facing admission policy itself: not measurable
}
TRANSFORMS = {"none", "certificate_format", "encoding", "preprocessing", "engine", "options"}
CLOSED_STATUS = {"VERIFIED_UNSAT", "CHECKED_UNSAT", "UNSAT"}
OPEN_STATUS = {
    "OPEN", "UNKNOWN", "TIMEOUT", "PROOF_PENDING", "COVER_READY", "MODEL_READY",
    "SAT", "CHECKED_SAT", "VERIFIED_SAT", "CHECK_FAILED", "PLACEHOLDER",
}
METRICS = {"composite_cpu_s", "search_cpu_s", "check_cpu_s", "proof_bytes",
           "retained_bytes", "maxrss_kb", "conflicts"}

CPU_PARTS = ("search_cpu_s", "check_cpu_s", "prep_cpu_s")

DECISION_EXIT = {
    "OPT_IN_EVIDENCE_BACKED": 0,
    "OPT_IN_SINGLE_CASE": 0,
    "REJECT": 2,
    "INCOMPLETE": 3,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_hex64(value) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value.lower()) <= HEX


def is_num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def geomean(values):
    values = list(values)
    if not values:
        return None
    if any(v <= 0 for v in values):
        return None
    return math.exp(sum(math.log(v) for v in values) / len(values))


def metric_value(run: dict, metric: str):
    """Value of `metric` for one run, or None when it is not recorded/valid."""
    if not run.get("metric_valid", {}).get(metric, True):
        return None
    m = run.get("metrics", {})
    if metric == "composite_cpu_s":
        parts = [m.get(k) for k in CPU_PARTS]
        if any(p is None for p in parts):
            return None
        if any(not is_num(p) or p < 0 for p in parts):
            return None
        return float(sum(parts))
    if metric == "conflicts":
        c = run.get("counters", {}).get("conflicts")
        return float(c) if is_num(c) else None
    v = m.get(metric)
    return float(v) if is_num(v) else None


def run_key(run: dict):
    return (run.get("case"), run.get("seed"), run.get("order"), run.get("cap"))


def paired(runs, arm_a, arm_b, metric):
    """Per-key (value_a, value_b) pairs; keys must match exactly."""
    a = {run_key(r): r for r in runs if r.get("arm") == arm_a}
    b = {run_key(r): r for r in runs if r.get("arm") == arm_b}
    out = []
    for k in sorted(set(a) & set(b), key=lambda x: tuple(str(y) for y in x)):
        va, vb = metric_value(a[k], metric), metric_value(b[k], metric)
        if va is None or vb is None or vb <= 0:
            continue
        out.append((k, va, vb))
    return out


def input_pins(pins):
    """Normalise pins.inputs to {case_or_None: {"baseline": pin, "treatment": pin}}.

    Two accepted forms:

      flat      {"baseline": PIN, "treatment": PIN}                     (one case)
      per-case  {"<case>": {"baseline": PIN, "treatment": PIN}, ...}    (several cases)
    """
    raw = pins.get("inputs") if isinstance(pins, dict) else None
    if not isinstance(raw, dict) or not raw:
        return {}, ["pins.inputs missing"]
    if set(raw) <= {"baseline", "treatment"}:
        pair = {k: raw[k] for k in ("baseline", "treatment") if k in raw}
        missing = [k for k in ("baseline", "treatment") if k not in pair]
        return ({None: pair} if not missing else {}), [f"pins.inputs lacks {missing}"] if missing else []
    out, bad = {}, []
    for case, pair in raw.items():
        if not isinstance(pair, dict) or not {"baseline", "treatment"} <= set(pair):
            bad.append(f"pins.inputs.{case} must hold baseline and treatment pins")
            continue
        out[case] = pair
    return out, bad


def _validate_structure(rec) -> list:
    """Structural problems that make the record unevaluable (fail closed)."""
    bad = []
    if not isinstance(rec, dict):
        return ["record is not a JSON object"]
    if rec.get("schema") != SCHEMA:
        bad.append(f"schema {rec.get('schema')!r} != {SCHEMA}")
    claim = rec.get("claim")
    if not isinstance(claim, dict):
        return bad + ["missing claim block"]
    for k in ("id", "class", "statement", "scope"):
        if not isinstance(claim.get(k), str) or not claim.get(k).strip():
            bad.append(f"claim.{k} missing/empty")
    if claim.get("class") not in CLASSES:
        bad.append(f"claim.class {claim.get('class')!r} not in {sorted(CLASSES)}")
    if not isinstance(claim.get("closure_claimed"), bool):
        bad.append("claim.closure_claimed must be a bool")

    prereg = rec.get("prereg")
    if not isinstance(prereg, dict):
        bad.append("missing prereg block")
    else:
        if prereg.get("primary_metric") not in METRICS:
            bad.append(f"prereg.primary_metric {prereg.get('primary_metric')!r} not in {sorted(METRICS)}")
        if not is_num(prereg.get("margin")) or not (0.0 < float(prereg["margin"]) < 1.0):
            bad.append("prereg.margin must be a number in (0,1)")


    pins = rec.get("pins")
    if not isinstance(pins, dict):
        bad.append("missing pins block")
    else:
        if not isinstance(pins.get("inputs"), dict) or not pins["inputs"]:
            bad.append("pins.inputs missing")

    tr = rec.get("transform")
    if not isinstance(tr, dict):
        bad.append("missing transform block")
    elif tr.get("kind") not in TRANSFORMS:
        bad.append(f"transform.kind {tr.get('kind')!r} not in {sorted(TRANSFORMS)}")

    runs = rec.get("runs")
    if not isinstance(runs, list) or not runs:
        bad.append("runs must be a non-empty list")
    else:
        for i, r in enumerate(runs):
            if not isinstance(r, dict):
                bad.append(f"runs[{i}] not an object")
                continue
            for k in ("case", "arm", "order", "status"):
                if not isinstance(r.get(k), str) or not r.get(k):
                    bad.append(f"runs[{i}].{k} missing")
            if not isinstance(r.get("seed"), int):
                bad.append(f"runs[{i}].seed must be an int")
            if not isinstance(r.get("cap"), int) or r["cap"] <= 0:
                bad.append(f"runs[{i}].cap must be a positive int")
            if r.get("status") not in CLOSED_STATUS | OPEN_STATUS:
                bad.append(f"runs[{i}].status {r.get('status')!r} unknown")
            if not isinstance(r.get("metrics"), dict):
                bad.append(f"runs[{i}].metrics missing")
    if not isinstance(rec.get("controls", []), list):
        bad.append("controls must be a list")
    return bad


def evaluate(rec: dict, trust: str = "cross_checked", mode: str = "admission") -> dict:
    checks = []

    def add(rule, status, detail):
        checks.append({"rule": rule, "status": status, "detail": detail})

    def blocked(status):
        return status in ("fail", "incomplete")

    structural = _validate_structure(rec)
    if structural:
        add("R1_schema", "fail", "; ".join(structural))
        return _verdict(rec, trust, mode, checks)
    add("R1_schema", "pass", f"schema {SCHEMA}, claim class {rec['claim']['class']}")

    claim = rec["claim"]
    prereg = rec["prereg"]
    pins = rec["pins"]
    tr = rec["transform"]
    runs = rec["runs"]
    arms = sorted({r["arm"] for r in runs})
    base, treat = "baseline", "treatment"
    metric = prereg["primary_metric"]
    margin = float(prereg["margin"])

    # ---- R2 pins ---------------------------------------------------------
    miss = []
    pin_map, pin_problems = input_pins(pins)
    miss.extend(pin_problems)
    for case, pair in pin_map.items():
        for arm, pin in pair.items():
            tag = f"{case or '<flat>'}/{arm}"
            if not isinstance(pin, dict) or not is_hex64(pin.get("sha256")):
                miss.append(f"pins.inputs.{tag}.sha256 is not a sha256 hex digest")
            elif not isinstance(pin.get("bytes"), int) or pin["bytes"] <= 0:
                miss.append(f"pins.inputs.{tag}.bytes must be a positive int")
    solver_pin = pins.get("solver") if isinstance(pins.get("solver"), dict) else {}
    if not is_hex64(solver_pin.get("sha256")):
        miss.append("pins.solver.sha256 missing (solver not binary-pinned)")
    elif not str(solver_pin.get("version", "")).strip():
        miss.append("pins.solver.version missing")
    checkers = pins.get("checkers") if isinstance(pins.get("checkers"), list) else []
    if not checkers and (claim.get("closure_claimed") or claim["class"] == "certificate"):
        miss.append("pins.checkers missing for a refutation-bearing claim")
    for i, c in enumerate(checkers):
        if not isinstance(c, dict) or not is_hex64(c.get("sha256")):
            miss.append(f"pins.checkers[{i}].sha256 missing")
    if claim.get("closure_claimed") or claim["class"] == "certificate":
        cert = rec.get("certificate")
        if not isinstance(cert, dict):
            miss.append("certificate block required for a refutation-bearing claim")
        else:
            if not is_hex64(cert.get("checker_sha256")):
                miss.append("certificate.checker_sha256 missing")
            if cert.get("checker_exit") != 20:
                miss.append(f"certificate.checker_exit {cert.get('checker_exit')!r} != 20")
            if cert.get("status") not in CLOSED_STATUS:
                miss.append(f"certificate.status {cert.get('status')!r} is not a closed refutation")
            if cert.get("relax_used") is not False:
                miss.append("certificate.relax_used must be explicitly false")
            vline = cert.get("verified_line")
            if not isinstance(vline, dict) or vline.get("found") is not True:
                miss.append("certificate.verified_line not confirmed from a pinned log")
            else:
                if not is_hex64(vline.get("log_sha256")):
                    miss.append("certificate.verified_line.log_sha256 missing")
            if trust == "cross_checked":
                cc = cert.get("cross_check")
                if not isinstance(cc, dict) or cc.get("status") not in CLOSED_STATUS:
                    miss.append("cross_check required at trust=cross_checked")
                else:
                    if not is_hex64(cc.get("checker_sha256")):
                        miss.append("cross_check.checker_sha256 missing")
                    elif cc["checker_sha256"].lower() == cert["checker_sha256"].lower():
                        miss.append("cross_check is the same binary as the primary checker")
            basis = cert.get("cost_basis")
            want = "cross_checked" if trust == "cross_checked" else "single_checker"
            if basis != want:
                miss.append(f"certificate.cost_basis {basis!r} != required {want!r}")
    if claim["class"] == "engine":
        shas = {str(r.get("solver_sha256") or "") for r in runs}
        if "" in shas or len(shas) < 2:
            miss.append("engine claim needs a per-run solver_sha256 on both arms (two distinct binaries)")
    known = {c.get("sha256", "").lower() for c in pins["checkers"] if isinstance(c, dict)}
    cert_block = rec.get("certificate") if isinstance(rec.get("certificate"), dict) else {}
    for body in (cert_block, cert_block.get("cross_check") if isinstance(cert_block.get("cross_check"), dict) else {}):
        h = str(body.get("checker_sha256", "")).lower()
        if h and h not in known:
            miss.append(f"checker {h[:12]} used but not pinned in pins.checkers")
    if miss:
        add("R2_pins", "incomplete", "; ".join(miss))
    else:
        add("R2_pins", "pass", f"inputs {len(pins['inputs'])}, checker hashes pinned, trust={trust}")

    # ---- R3 pre-registration / arm discipline ----------------------------
    defects = []
    if prereg.get("registered_before_run") is not True:
        defects.append(f"registered_before_run={prereg.get('registered_before_run')!r}")
    raw_arms = prereg.get("declared_arms")
    declared = set(map(str, raw_arms)) if isinstance(raw_arms, list) else set()
    if not declared:
        defects.append("prereg.declared_arms not declared")
    if not {base, treat} <= declared:
        defects.append(f"declared arms {sorted(declared)} do not include {base}/{treat}")
    extra = set(arms) - declared
    if extra:
        defects.append(f"undeclared arms measured: {sorted(extra)}")
    max_runs = prereg.get("max_runs")
    if not isinstance(max_runs, int) or max_runs <= 0:
        defects.append("prereg.max_runs not a positive int")
    elif len(runs) > max_runs:
        defects.append(f"{len(runs)} runs exceed prereg.max_runs={max_runs}")
    for field in ("cases", "caps", "seeds", "orders"):
        if not isinstance(prereg.get(field), list) or not prereg[field]:
            defects.append(f"prereg.{field} not declared")
    if defects:
        status = "pass" if mode == "audit" else "incomplete"
        add("R3_prereg", status, "; ".join(defects))
        if status == "pass":
            checks[-1]["waived"] = True
    else:
        add("R3_prereg", "pass", f"arms {sorted(declared)}, max_runs {prereg.get('max_runs')}")

    # declared case/cap/seed/order sets must cover what was run
    for field, key in (("cases", "case"), ("caps", "cap"), ("seeds", "seed"), ("orders", "order")):
        want = {tuple(x) if isinstance(x, list) else x for x in prereg.get(field, [])}
        got = {r[key] for r in runs}
        if want and not got <= want:
            add(f"R3_prereg_{field}", "incomplete", f"measured {sorted(map(str, got))} not in declared {sorted(map(str, want))}")

    # ---- R4 comparability -------------------------------------------------
    comp = []
    solver_pin = pins.get("solver") if isinstance(pins.get("solver"), dict) else {}
    solver_sha = str(solver_pin.get("sha256") or "").lower()
    for r in runs:
        rs = r.get("solver_sha256")
        if rs is not None and str(rs).lower() != solver_sha:
            if claim["class"] != "engine":
                comp.append(f"run {run_key(r)} used solver {str(rs)[:12]} != pinned {solver_sha[:12]}")
    if claim["class"] == "engine":
        for arm in (base, treat):
            vals = {str(r.get("solver_sha256") or "") for r in runs if r["arm"] == arm}
            if len(vals) != 1:
                comp.append(f"{arm} arm mixes {len(vals)} solver binaries: an engine panel needs one binary per arm")
    run_cases = sorted({r["case"] for r in runs})
    pin_map, _ = input_pins(pins)
    for case in run_cases:
        pair = pin_map.get(case, pin_map.get(None, {}))
        if not pair:
            comp.append(f"no input pin for case {case}")
            continue
        def _sha(arm):
            body = pair.get(arm) if isinstance(pair.get(arm), dict) else {}
            val = body.get("sha256")
            return val.lower() if is_hex64(val) else None
        base_sha, treat_sha = _sha(base), _sha(treat)
        if base_sha is None or treat_sha is None:
            comp.append(f"case {case}: inputs not hash-pinned "
                        f"(baseline={str(base_sha)[:8]}, treatment={str(treat_sha)[:8]})")
        elif tr["kind"] in ("none", "certificate_format"):
            if base_sha != treat_sha:
                comp.append(f"case {case}: transform claims no formula change but input hashes differ")
        elif base_sha == treat_sha:
            comp.append(f"case {case}: transform.kind={tr['kind']} but the two input hashes are identical")
    kb = {run_key(r) for r in runs if r["arm"] == base}
    kt = {run_key(r) for r in runs if r["arm"] == treat}
    if kb != kt:
        comp.append(f"unpaired keys: baseline-only {sorted(map(str, kb - kt))[:3]}, treatment-only {sorted(map(str, kt - kb))[:3]}")
    if not kb:
        comp.append("no baseline runs")
    caps_b = {r["cap"] for r in runs if r["arm"] == base}
    caps_t = {r["cap"] for r in runs if r["arm"] == treat}
    if caps_b != caps_t:
        comp.append(f"cap sets differ: {sorted(caps_b)} vs {sorted(caps_t)}")
    if comp:
        add("R4_comparability", "incomplete", "; ".join(comp))
    else:
        add("R4_comparability", "pass", f"{len(kb)} paired cells, caps {sorted(caps_b)}, transform {tr['kind']}")

    # ---- R5 status discipline --------------------------------------------
    statuses = sorted({r["status"] for r in runs})
    open_runs = [r for r in runs if r["status"] in OPEN_STATUS]
    bad = []
    if claim.get("closure_claimed") and open_runs:
        bad.append(f"closure claimed but {len(open_runs)} run(s) are {sorted({r['status'] for r in open_runs})}")
    closed_runs = [r for r in runs if r["status"] in CLOSED_STATUS]
    if closed_runs and not isinstance(rec.get("certificate"), dict):
        bad.append(f"{len(closed_runs)} closed run(s) without a certificate block")
    if any(r["status"] in ("CHECK_FAILED",) for r in runs):
        bad.append("a run reported CHECK_FAILED")
    if bad:
        add("R5_status", "fail", "; ".join(bad))
    else:
        add("R5_status", "pass", f"statuses {statuses}")

    # ---- R6 controls ------------------------------------------------------
    ctl_bad = []
    controls = rec.get("controls", [])
    for c in controls:
        if not isinstance(c, dict):
            ctl_bad.append("malformed control entry")
            continue
        if c.get("role") != "unsound_control":
            continue
        if c.get("semantics_rejected") is not True:
            ctl_bad.append(f"control {c.get('id')!r} was not rejected by the semantics check")
        ar = c.get("apparent_ratio")
        if is_num(ar) and float(ar) <= 1.0 - margin / 2.0:
            ctl_bad.append(
                f"control {c.get('id')!r} shows an apparent gain {float(ar):.4f} <= 1 - margin/2: "
                "the measured effect is not attributable to the declared mechanism")
    unsound = [c for c in controls if isinstance(c, dict) and c.get("role") == "unsound_control"]
    if ctl_bad:
        add("R6_control", "fail", "; ".join(ctl_bad))
    elif unsound:
        add("R6_control", "pass", f"{len(unsound)} unsound control(s) rejected, none mimics the gain")
    else:
        add("R6_control", "incomplete", "no unsound_control designated for a mechanism claim")

    # ---- R7 semantic premise ---------------------------------------------
    sem_bad = []
    if tr["kind"] in ("encoding", "preprocessing"):
        der = tr.get("derivation")
        if not isinstance(der, dict):
            sem_bad.append(f"transform.kind={tr['kind']} without a derivation block")
        else:
            if der.get("status") != "pass":
                sem_bad.append(f"derivation status {der.get('status')!r}")
            if der.get("relax_used") is not False:
                sem_bad.append("derivation must state relax_used=false")
            if not is_hex64(der.get("receipt_sha256")):
                sem_bad.append("derivation.receipt_sha256 missing")
            if not str(der.get("kind", "")).strip():
                sem_bad.append("derivation.kind missing")
    if tr["kind"] in ("engine", "options"):
        if tr.get("binding") != "budget_hash":
            sem_bad.append("an engine/option override must be hash-bound into the cached leaf budget (binding=budget_hash)")
    if tr["kind"] == "certificate_format" and not str(tr.get("declared_delta", "")).strip():
        sem_bad.append("certificate_format needs an explicit declared_delta")
    if sem_bad:
        add("R7_semantics", "fail", "; ".join(sem_bad))
    else:
        add("R7_semantics", "pass", f"transform {tr['kind']} premise satisfied")

    # ---- R8 cost ----------------------------------------------------------
    pairs = paired(runs, base, treat, metric)
    ratios = [(k, vb / va) for (k, va, vb) in pairs]   # treatment / baseline; <= 1 is a gain
    geomean_ratio = geomean([r for _, r in ratios])
    max_ratio = max((r for _, r in ratios), default=None)
    min_ratio = min((r for _, r in ratios), default=None)
    cost_fail, cost_notes = [], []
    if metric == "conflicts":
        cost_fail.append("conflicts are not a policy-invariant unit of work (NATIVE.md: search-only "
                         "made 1.65x the conflicts in the same wall budget); report them, do not adopt on them")
    need = 4 if claim["class"] != "certificate" else 2
    if len(ratios) < need:
        cost_fail.append(f"{len(ratios)} usable {metric} pairs < {need}")
    if geomean_ratio is None:
        cost_fail.append(f"no usable {metric} values")
    else:
        if geomean_ratio > 1.0 - margin:
            cost_fail.append(f"geomean ratio {geomean_ratio:.4f} > 1 - margin ({1.0 - margin:.4f})")
        if max_ratio > 1.0:
            cost_fail.append(f"worst cell ratio {max_ratio:.4f} > 1.0: a regression is hidden in the mean")
        bad_cells = [(k, r) for k, r in ratios if r > 1.0]
        if bad_cells:
            cost_fail.append(f"{len(bad_cells)} cell(s) regress: {[(str(k), round(r, 4)) for k, r in bad_cells][:3]}")
        by_seed = {}
        for k, r in ratios:
            by_seed.setdefault(k[1], []).append(r)
        if len(by_seed) >= 2:
            seed_means = {s: geomean(v) for s, v in by_seed.items()}
            spread = max(seed_means.values()) - min(seed_means.values())
            cost_notes.append(f"per-seed ratios {[round(v, 4) for v in seed_means.values()]}, spread {spread:.4f}")
            if spread > margin:
                cost_fail.append(f"per-seed spread {spread:.4f} > margin {margin:.4f}: sign not stable across seeds")
    add("R8_cost", "fail" if cost_fail else "pass",
        "; ".join(cost_fail) if cost_fail else
        f"{metric} geomean {geomean_ratio:.4f} <= 1 - {margin:.2f} over {len(ratios)} paired cells"
        + ("; " + "; ".join(cost_notes) if cost_notes else ""))

    # ---- R9 measurement quality -----------------------------------------
    qual = []
    if claim["class"] == "certificate":
        for case in sorted({r["case"] for r in runs}):
            blocks = [json.dumps(r.get("counters") or {}, sort_keys=True) for r in runs if r["case"] == case]
            if len(set(blocks)) > 1:
                qual.append(f"certificate claim must hold search fixed; case {case} has differing counters")
            elif not any(json.loads(b) for b in blocks):
                qual.append(f"case {case} records no search counters: identical search is unproven")
    else:
        reps = {}
        for r in runs:
            if r["arm"] == base:
                reps.setdefault((r["case"], r["seed"], r["cap"]), set()).add(r["order"])
        thin = sorted(str(k) for k, v in reps.items() if len(v) < 2)
        if thin:
            qual.append(f"no order replication (A/B and B/A) for {len(thin)} baseline cell(s), e.g. {thin[:3]}")
        if claim["class"] in ("options", "engine", "search"):
            # the PySAT binding accepts unknown option names silently (board d4/f1), so an arm that
            # leaves the counter fingerprint untouched is a no-op, however its CPU moved
            fp = {}
            for r in runs:
                fp.setdefault(r["arm"], {})[run_key(r)] = json.dumps(r.get("counters") or {}, sort_keys=True)
            common = set(fp.get(base, {})) & set(fp.get(treat, {}))
            touched = [k for k in common if fp[base][k] != fp[treat][k]]
            if not touched:
                qual.append("baseline and treatment counters are identical in every cell: the option/engine "
                            "change is inert or was silently ignored, so it cannot explain a cost change")
        if len({r["seed"] for r in runs}) >= 2:
            by_seed_fp = {}
            for r in runs:
                if r["arm"] == base:
                    by_seed_fp.setdefault((r["case"], r["cap"]), set()).add(
                        json.dumps(r.get("counters") or {}, sort_keys=True))
            inert = [str(k) for k, v in by_seed_fp.items() if len(v) < 2]
            if inert:
                qual.append(f"seeds do not diverge in the baseline arm at this cap ({inert[:3]}): the panel "
                            "is effectively single-seed and cannot separate seed from treatment")
    spread_ok = True
    worst = 0.0
    for (case, seed, cap) in {(r["case"], r["seed"], r["cap"]) for r in runs if r["arm"] == base}:
        vals = [metric_value(r, metric) for r in runs
                if r["arm"] == base and (r["case"], r["seed"], r["cap"]) == (case, seed, cap)]
        vals = [v for v in vals if v is not None and v > 0]
        if len(vals) >= 2:
            s = max(vals) / min(vals)
            worst = max(worst, s - 1.0)
    if worst > margin / 2.0:
        spread_ok = False
        qual.append(f"baseline order-replicate spread {worst:.4f} > margin/2 {margin / 2.0:.4f}: cannot resolve the margin")
    if qual:
        add("R9_quality", "incomplete", "; ".join(qual))
    else:
        detail = (f"order-replicate spread {worst:.4f} <= margin/2"
                  if worst else "no order replicates; single-cell measurement")
        add("R9_quality", "pass", detail)

    # ---- R10 excluded cells ----------------------------------------------
    excluded = sorted({f"{r['case']}/{r['arm']}/{metric}"
                       for r in runs if not r.get("metric_valid", {}).get(metric, True)})
    declared_ex = set(map(str, prereg.get("declared_exclusions", []) or []))
    if excluded:
        undeclared = [e for e in excluded if e.split("/")[0] not in declared_ex]
        add("R10_exclusions", "incomplete" if undeclared else "pass",
            f"{len(excluded)} excluded {metric} cell(s), undeclared: {undeclared[:3]}")
        if not undeclared:
            checks[-1]["limits"] = True
        add("R10_exclusions", "pass", f"no excluded {metric} cells")

    # ---- R11 generality ---------------------------------------------------
    cases = sorted({r["case"] for r in runs})
    add("R11_generality", "pass",
        f"{len(cases)} distinct case(s): {cases}" + ("" if len(cases) >= 2 else " (single-case evidence: opt-in limited)"))

    agg = {"primary_metric": metric, "margin": margin, "pairs": len(ratios),
           "geomean_ratio": geomean_ratio, "max_ratio": max_ratio, "min_ratio": min_ratio,
           "per_cell": [{"case": k[0], "seed": k[1], "order": k[2], "cap": k[3], "ratio": r}
                        for k, r in ratios],
           "cases": cases,
           "baseline_order_spread": worst,
           "excluded_cells": excluded}
    return _verdict(rec, trust, mode, checks, aggregate=agg)


def _verdict(rec, trust, mode, checks, aggregate=None) -> dict:
    failures = [c for c in checks if c["status"] == "fail"]
    incompletes = [c for c in checks if c["status"] == "incomplete"]
    if failures:
        decision = "REJECT"
    elif incompletes:
        decision = "INCOMPLETE"
    else:
        cases = (aggregate or {}).get("cases") or []
        decision = "OPT_IN_EVIDENCE_BACKED" if len(cases) >= 2 else "OPT_IN_SINGLE_CASE"
        if decision == "OPT_IN_EVIDENCE_BACKED" and any(c.get("limits") for c in checks):
            decision = "OPT_IN_SINGLE_CASE"
    claim = rec.get("claim") if isinstance(rec, dict) else None
    if not isinstance(claim, dict):
        claim = {}
    agg = aggregate or {}
    statement = str(claim.get("statement", "<no statement>"))
    cases = (aggregate or {}).get("cases") or []
    excluded = agg.get("excluded_cells") or []
    required_scope = (
        f"Opt-in experimental override only, on the pinned inputs {cases}, licensed metric "
        f"{agg.get('primary_metric')}"
        + (f", excluding declared-invalid cells {excluded}" if excluded else "")
        + ". Production defaults, ledger states, frozen coverage and the accepted interval "
        "51 <= R_4(3) <= 62 are unchanged. A capped OPEN/UNKNOWN run is not UNSAT. "
        f"The licensed statement is exactly: {statement}"
    )
    return {
        "policy_version": POLICY_VERSION,
        "mode": mode,
        "trust_level": trust,
        "claim": {"id": claim.get("id"), "class": claim.get("class"), "statement": statement,
                  "scope": claim.get("scope")},
        "decision": decision,
        "exit_code": DECISION_EXIT[decision],
        "opt_in_eligible": decision.startswith("OPT_IN"),
        "default_eligible": False,
        "checks": checks,
        "aggregate": aggregate,
        "required_scope": required_scope,
        "blocking": [c["rule"] for c in failures] + [c["rule"] for c in incompletes],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("record", help="normalised evidence record (JSON)")
    ap.add_argument("--trust", choices=("cross_checked", "single_checker"), default="cross_checked")
    ap.add_argument("--mode", choices=("admission", "audit"), default="admission")
    ap.add_argument("--json", action="store_true", help="print the whole verdict as JSON")
    ap.add_argument("--out", help="write the verdict JSON here")
    ap.add_argument("--primary-metric", help="override the declared primary metric (sensitivity run)")
    args = ap.parse_args(argv)

    path = Path(args.record)
    try:
        rec = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INCOMPLETE: cannot read record: {exc}", file=sys.stderr)
        return 3
    if args.primary_metric:
        if args.primary_metric not in METRICS:
            print(f"INCOMPLETE: unknown metric {args.primary_metric}", file=sys.stderr)
            return 3
        rec.setdefault("prereg", {})["primary_metric"] = args.primary_metric
    verdict = evaluate(rec, trust=args.trust, mode=args.mode)
    verdict["record"] = str(path)
    verdict["record_sha256"] = sha256_file(path)
    if args.out:
        Path(args.out).write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    if args.json:
        print(json.dumps(verdict, indent=2, sort_keys=True))
    else:
        agg = verdict.get("aggregate") or {}
        print(f"{verdict['claim']['id']}: {verdict['decision']} (exit {verdict['exit_code']}, mode {args.mode}, trust {args.trust})")
        if agg:
            print(f"  metric {agg['primary_metric']}, pairs {agg['pairs']}, geomean "
                  f"{_fmt(agg['geomean_ratio'])}, worst {_fmt(agg['max_ratio'])}, margin {agg['margin']}")
        for c in verdict["checks"]:
            if c["status"] != "pass":
                print(f"  {c['status'].upper():10s} {c['rule']}: {c['detail']}")
        if verdict["opt_in_eligible"]:
            print(f"  scope: {verdict['required_scope']}")
    return verdict["exit_code"]


def _fmt(x):
    return "n/a" if x is None else f"{x:.4f}"


if __name__ == "__main__":
    sys.exit(main())
