#!/usr/bin/env python3
"""Deterministic tests for gate.py, including the adversarial records.

Run:  python3 tests/test_gate.py
Exit: 0 when every case yields the expected decision and exit code.

Each case is a normalised admission record built from one template; the name
names the real-world defect it models.  Nothing here runs a solver, and no
numeric value here is evidence about K58: these records exist only to pin the
gate's decision function.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import gate  # noqa: E402


def h(tag: str) -> str:
    return hashlib.sha256(tag.encode()).hexdigest()


SOLVER = h("solver-binary")
CHECKER = h("checker-binary")
CROSS = h("cross-checker-binary")


def template():
    return {
        "schema": 1,
        "claim": {
            "id": "synthetic",
            "class": "options",
            "statement": "synthetic statement",
            "scope": "synthetic bounded sample",
            "closure_claimed": False,
        },
        "prereg": {
            "registered_before_run": True,
            "declared_arms": ["baseline", "treatment"],
            "primary_metric": "composite_cpu_s",
            "margin": 0.10,
            "max_runs": 64,
            "cases": ["c1", "c2"],
            "caps": [50000],
            "seeds": [0, 1],
            "orders": ["AB", "BA"],
            "declared_exclusions": [],
        },
        "pins": {
            "inputs": {"baseline": {"sha256": h("cnf"), "bytes": 1000},
                       "treatment": {"sha256": h("cnf+delta"), "bytes": 1010}},
            "solver": {"id": "cadical", "version": "2.1.2", "sha256": SOLVER},
            "checkers": [],
        },
        "transform": {"kind": "options", "declared_delta": "--phase=false", "binding": "budget_hash",
                      "derivation": None},
        "certificate": None,
        "runs": [],
        "controls": [{"id": "unsound", "role": "unsound_control", "semantics_rejected": True}],
    }


def add_pair(rec, case, seed, order, base, treat, status="OPEN", cap=50000, counters=None,
             inert_arm=False, inert_seed=False):
    for arm, value in (("baseline", base), ("treatment", treat)):
        if counters is not None:
            ctr = counters
        elif inert_arm:                      # the option changes nothing: same fingerprint
            ctr = {"conflicts": cap, "decisions": 1000}
        elif inert_seed:                     # seeds do not diverge at this cap
            ctr = {"conflicts": cap}
        else:
            ctr = ({"conflicts": cap + seed, "decisions": 1000 + seed} if arm == "baseline"
                   else {"conflicts": cap - 500 + seed, "decisions": 990 + seed})
        rec["runs"].append({
            "case": case, "arm": arm, "seed": seed, "order": order, "cap": cap,
            "status": status,
            "metrics": {"search_cpu_s": value, "check_cpu_s": 0.0, "prep_cpu_s": 0.0},
            "counters": ctr,
        })


def grid(rec, ratio=0.80, cases=("c1", "c2"), seeds=(0, 1), orders=("AB", "BA")):
    """A clean 2-case x 2-seed x 2-order grid at a fixed cost ratio."""
    for i, case in enumerate(cases):
        for seed in seeds:
            for j, order in enumerate(orders):
                base = 10.0 + 0.05 * i + 0.02 * j
                add_pair(rec, case, seed, order, base, base * ratio)
    return rec


def rec_clean(ratio=0.80):
    return grid(template(), ratio=ratio)


def rec_single_case(ratio=0.80):
    return grid(template(), ratio=ratio, cases=("c1",), seeds=(0, 1), orders=("AB", "BA"))


def rec_single_order(ratio=0.80):
    return grid(template(), ratio=ratio, orders=("AB",))


def rec_cap_as_unsat():
    rec = rec_clean()
    rec["claim"]["closure_claimed"] = True     # claims a refutation ...
    for r in rec["runs"]:
        r["status"] = "OPEN"                   # ... but every run hit the conflict cap
    return rec


def rec_drifted_hash():
    rec = rec_clean()
    rec["claim"]["class"] = "encoding"
    rec["transform"] = {"kind": "encoding", "declared_delta": "added clauses",
                        "binding": "budget_hash",
                        "derivation": {"kind": "RUP", "status": "pass",
                                       "receipt_sha256": h("derivation"), "relax_used": False}}
    rec["pins"]["inputs"]["treatment"]["sha256"] = h("cnf")   # no byte change at all
    return rec


def rec_unpinned_solver():
    rec = rec_clean()
    rec["pins"]["solver"]["sha256"] = None
    return rec


def rec_control_mimics():
    rec = rec_clean(ratio=0.80)
    rec["controls"] = [{"id": "corrupted", "role": "unsound_control",
                        "semantics_rejected": True, "apparent_ratio": 0.771}]
    return rec


def rec_unproven_derivation():
    rec = rec_clean()
    rec["claim"]["class"] = "encoding"
    rec["transform"] = {"kind": "encoding", "declared_delta": "765 added clauses",
                        "binding": "budget_hash",
                        "derivation": {"kind": "lex", "status": "fail",
                                       "receipt_sha256": h("gen"), "relax_used": False}}
    return rec


def rec_hidden_regression():
    rec = rec_clean(ratio=0.80)
    for r in rec["runs"]:
        if r["arm"] == "treatment" and r["case"] == "c2" and r["seed"] == 1 and r["order"] == "BA":
            r["metrics"]["search_cpu_s"] *= 1.56      # one cell at 1.25x while the mean still gains
    return rec


def rec_seed_instability():
    rec = grid(template(), ratio=0.80)
    for r in rec["runs"]:
        if r["arm"] == "treatment" and r["seed"] == 1:
            base = [x for x in rec["runs"] if x["arm"] == "baseline" and x["case"] == r["case"]
                    and x["seed"] == 1 and x["order"] == r["order"]][0]["metrics"]["search_cpu_s"]
            r["metrics"]["search_cpu_s"] = base * 1.02
    return rec


def rec_prereg_unrecorded():
    rec = rec_clean()
    rec["prereg"]["registered_before_run"] = None
    return rec


def rec_undeclared_exclusion():
    rec = rec_clean()
    for r in rec["runs"]:
        r["metrics"]["proof_bytes"] = 100 if r["arm"] == "baseline" else 80
        if r["arm"] == "treatment" and r["case"] == "c2":
            r["metric_valid"] = {"proof_bytes": False}
    rec["prereg"]["primary_metric"] = "proof_bytes"
    rec["prereg"]["declared_exclusions"] = []
    return rec


def rec_declared_exclusion():
    rec = rec_undeclared_exclusion()
    rec["prereg"]["declared_exclusions"] = ["c2"]
    return rec


def rec_certificate(relax=False, same_cross=False, cost_basis="cross_checked"):
    rec = template()
    rec["claim"].update({"class": "certificate", "closure_claimed": True,
                         "statement": "certificate pipeline on already-closed CNFs"})
    rec["pins"]["inputs"]["treatment"]["sha256"] = rec["pins"]["inputs"]["baseline"]["sha256"]
    rec["transform"] = {"kind": "certificate_format", "declared_delta": "drat -> lrat",
                        "binding": "none", "derivation": None}
    rec["prereg"].update({"cases": ["H1", "H2"], "seeds": [0], "orders": ["AB"]})
    rec["pins"]["checkers"] = [{"id": "lrat-trim", "sha256": CHECKER},
                               {"id": "second", "sha256": CROSS}]
    counter = {"conflicts": 49226}
    for case in ("H1", "H2"):
        for arm, scale in (("baseline", 1.0), ("treatment", 0.70)):
            rec["runs"].append({
                "case": case, "arm": arm, "seed": 0, "order": "AB", "cap": 50000,
                "status": "VERIFIED_UNSAT",
                "metrics": {"search_cpu_s": 1.0 * scale, "check_cpu_s": 1.0 * scale, "prep_cpu_s": 0.0},
                "counters": counter,
            })
    rec["certificate"] = {
        "status": "VERIFIED_UNSAT",
        "checker_sha256": CHECKER,
        "checker_exit": 20,
        "verified_line": {"found": True, "log_sha256": h("log")},
        "relax_used": relax,
        "cost_basis": cost_basis,
        "cross_check": {"status": "VERIFIED_UNSAT",
                        "checker_sha256": CHECKER if same_cross else CROSS},
    }
    return rec


def rec_inert_option():
    rec = template()
    for case in ("c1", "c2"):
        for seed in (0, 1):
            for j, order in enumerate(("AB", "BA")):
                base = 10.0 + 0.02 * j
                add_pair(rec, case, seed, order, base, base * 0.80, inert_arm=True)
    return rec


def rec_inert_seeds():
    rec = template()
    for case in ("c1", "c2"):
        for seed in (0, 1):
            for j, order in enumerate(("AB", "BA")):
                base = 10.0 + 0.05 * seed + 0.02 * j
                add_pair(rec, case, seed, order, base, base * 0.80, inert_seed=True)
    return rec


def rec_engine_swap_undeclared():
    rec = rec_clean()
    for r in rec["runs"]:
        if r["arm"] == "treatment":
            r["solver_sha256"] = h("other-solver")
    return rec


def rec_engine_declared(swap_within_arm=False):
    rec = rec_clean()
    rec["claim"]["class"] = "engine"
    rec["transform"] = {"kind": "engine", "declared_delta": "cadical 1.9.5 -> 2.1.2",
                        "binding": "budget_hash", "derivation": None}
    for r in rec["runs"]:
        r["solver_sha256"] = SOLVER if r["arm"] == "baseline" else h("solver-2.1.2")
        if swap_within_arm and r["arm"] == "treatment" and r["seed"] == 1:
            r["solver_sha256"] = h("solver-other")
    return rec


def rec_closed_without_certificate():
    rec = rec_clean()
    rec["claim"]["closure_claimed"] = True
    for r in rec["runs"]:
        r["status"] = "VERIFIED_UNSAT"
    rec["certificate"] = None
    return rec


def rec_conflicts_as_gain():
    rec = rec_clean(ratio=0.80)
    rec["prereg"]["primary_metric"] = "conflicts"
    for r in rec["runs"]:
        r["counters"] = {"conflicts": 100000} if r["arm"] == "baseline" else {"conflicts": 70000}
    return rec


CASES = [
    ("clean 2-case 2-seed 2-order gain", rec_clean(), "OPT_IN_EVIDENCE_BACKED", 0),
    ("single-case gain is limited, not general", rec_single_case(), "OPT_IN_SINGLE_CASE", 0),
    ("no order replication", rec_single_order(), "INCOMPLETE", 3),
    ("cap-as-UNSAT", rec_cap_as_unsat(), "REJECT", 2),
    ("encoding claim with identical input bytes", rec_drifted_hash(), "INCOMPLETE", 3),
    ("solver binary not pinned", rec_unpinned_solver(), "INCOMPLETE", 3),
    ("unsound control mimics the gain", rec_control_mimics(), "REJECT", 2),
    ("added clauses without a derivation", rec_unproven_derivation(), "REJECT", 2),
    ("one regressing cell hidden by the mean", rec_hidden_regression(), "REJECT", 2),
    ("seeds disagree in sign", rec_seed_instability(), "REJECT", 2),
    ("pre-registration unrecorded (admission)", rec_prereg_unrecorded(), "INCOMPLETE", 3),
    ("undeclared excluded metric cell", rec_undeclared_exclusion(), "INCOMPLETE", 3),
    ("declared excluded cell limits the claim", rec_declared_exclusion(), "OPT_IN_SINGLE_CASE", 0),
    ("certificate with relaxed check", rec_certificate(relax=True), "INCOMPLETE", 3),
    ("certificate whose cross-check is the same binary", rec_certificate(same_cross=True), "INCOMPLETE", 3),
    ("certificate cost basis mismatch", rec_certificate(cost_basis="single_checker"), "INCOMPLETE", 3),
    ("clean certificate at cross-checked trust", rec_certificate(), "OPT_IN_EVIDENCE_BACKED", 0),
    ("conflicts alone as the primary metric", rec_conflicts_as_gain(), "REJECT", 2),
    ("option arm whose counters never move", rec_inert_option(), "INCOMPLETE", 3),
    ("seeds that do not diverge at the evaluation cap", rec_inert_seeds(), "INCOMPLETE", 3),
    ("solver swapped without declaring engine class", rec_engine_swap_undeclared(), "INCOMPLETE", 3),
    ("closure claimed with no certificate block", rec_closed_without_certificate(), "REJECT", 2),
    ("engine panel with one pinned binary per arm", rec_engine_declared(), "OPT_IN_EVIDENCE_BACKED", 0),
    ("engine panel mixing two binaries in one arm", rec_engine_declared(swap_within_arm=True), "INCOMPLETE", 3),
]


def main() -> int:
    failed = 0
    for name, rec, want_decision, want_exit in CASES:
        verdict = gate.evaluate(copy.deepcopy(rec), trust="cross_checked", mode="admission")
        ok = verdict["decision"] == want_decision and verdict["exit_code"] == want_exit
        failed += 0 if ok else 1
        detail = "" if ok else " blocking=" + ",".join(verdict["blocking"])
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {verdict['decision']} (want {want_decision}){detail}")

    audit = gate.evaluate(copy.deepcopy(rec_prereg_unrecorded()), mode="audit")
    ok = audit["decision"] == "OPT_IN_EVIDENCE_BACKED"
    failed += 0 if ok else 1
    print(f"{'ok  ' if ok else 'FAIL'} audit mode waives prereg only: {audit['decision']}")
    if not ok:
        print("   blocking:", ",".join(audit["blocking"]))

    a = json.dumps(gate.evaluate(copy.deepcopy(rec_clean()), mode="audit"), sort_keys=True)
    b = json.dumps(gate.evaluate(copy.deepcopy(rec_clean()), mode="audit"), sort_keys=True)
    ok = a == b
    failed += 0 if ok else 1
    print(f"{'ok  ' if ok else 'FAIL'} verdict is deterministic")

    total = len(CASES) + 2
    print(f"\n{total - failed}/{total} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
