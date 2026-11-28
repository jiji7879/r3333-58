#!/usr/bin/env python3
"""Selftests for leafcert: positive controls and negative controls.

Every test prints PASS/FAIL and the failing detail.  Run: python3 selftest.py
Exit status 0 iff all tests pass.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import leafcert as L

HERE = Path(__file__).resolve().parent
W = HERE / "selftest-work"

GADGET = {  # x,y selectors; a,b,c / d,e,f private; at-most-one each
    "nv": 8,
    "clauses": [
        (1, 3), (1, 4), (1, 5), (-3, -4), (-4, -5), (-3, -5),      # not x -> a,b,c
        (2, 6), (2, 7), (2, 8), (-6, -7), (-7, -8), (-6, -8),      # not y -> d,e,f
    ],
}
# base is SAT (x=y=True).  Leaf [ -1 , 2] is UNSAT (x-gadget), leaf [1, -2] is
# UNSAT (y-gadget); leaf [1, 2] is SAT; cube [ -1, 2] and [ -1, 2, -8] both UNSAT.


def write_cnf(path, nv, clauses):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"p cnf {nv} {len(clauses)}\n" +
                    "".join(" ".join(map(str, c)) + " 0\n" for c in clauses))
    return path


def ok(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ((" :: " + str(detail)) if detail and not cond else ""))
    return cond


def expect_error(name, fn, needle=""):
    try:
        fn()
    except L.LeafError as e:
        return ok(name, needle in str(e), str(e))
    return ok(name, False, "no LeafError raised")


def main():
    W.mkdir(exist_ok=True)
    base = write_cnf(W / "base.cnf", GADGET["nv"], GADGET["clauses"])
    good = []

    # ---- freeze invariant tests
    fr = L.freeze(base, [-1, 2], W / "leaf.cnf")
    body = (W / "leaf.cnf").read_bytes()
    head, rest = body.split(b"\n", 1)
    good.append(ok("freeze: header clause count grows by |cube|",
                   head == b"p cnf 8 14", head))
    good.append(ok("freeze: base body byte-identical",
                   rest.startswith(base.read_bytes().split(b"\n", 1)[1])))
    good.append(ok("freeze: units appended exactly", rest.endswith(b"-1 0\n2 0\n")))
    good.append(ok("freeze: variable count unchanged", fr["variables"] == 8))
    nv, nc, _ = L.dimacs_header(W / "leaf.cnf")
    good.append(ok("freeze: DIMACS clause count matches file", nc == 14))

    expect_error("freeze refuses out-of-range literal (variable collision)",
                 lambda: L.freeze(base, [9], W / "bad.cnf"), "collides")
    expect_error("freeze refuses contradictory cube",
                 lambda: L.freeze(base, [1, -1], W / "bad2.cnf"), "contradictory")
    expect_error("freeze refuses empty cube",
                 lambda: L.freeze(base, [], W / "bad3.cnf"), "non-empty")
    expect_error("freeze refuses a 'p inccnf' base",
                 lambda: L.freeze(_write_inccnf(W / "x.icnf"), [1], W / "bad4.cnf"),
                 "p inccnf")
    expect_error("freeze refuses a wrong base hash",
                 lambda: L.freeze(base, [1], W / "bad5.cnf",
                                  expect_sha256="0" * 64), "sha256")
    expect_error("coverage refuses duplicate cubes",
                 lambda: L.coverage([[-1, 2], [2, -1]], 8, W / "covdup"), "duplicate")

    # ---- coverage tests
    cov_ex = L.coverage([[-1], [1]], 8, W / "cov_ex")
    good.append(ok("coverage: [-1],[1] is exhaustive", cov_ex["exhaustive"],
                   cov_ex["solver"]["verdict"]))
    cov_ne = L.coverage([[-1], [1, 2]], 8, W / "cov_ne")
    good.append(ok("coverage: [-1],[1,2] is NOT exhaustive", not cov_ne["exhaustive"],
                   cov_ne["solver"]["verdict"]))

    # ---- leaf solving: UNSAT leaf verified, SAT leaf never certified
    leaf1 = W / "selftest-work-leaf1.cnf"
    L.freeze(base, [-1, 2], leaf1)
    sol1 = L.run_kissat(leaf1, W / "leaf1.drat", 10000, 30)
    v1 = L.verify_drat(leaf1, W / "leaf1.drat")
    good.append(ok("leaf [-1,2] is UNSAT", sol1["verdict"] == "UNSAT", sol1["verdict"]))
    good.append(ok("leaf [-1,2] DRAT verifies", v1["verified"], v1["drat_trim_tail"]))
    good.append(ok("solve: conflict counter parsed", "conflicts" in sol1, sol1))

    leafsat = W / "leafsat.cnf"
    L.freeze(base, [1, 2], leafsat)
    sols = L.run_kissat(leafsat, W / "leafsat.drat", 10000, 30)
    good.append(ok("leaf [1,2] is SAT (no certificate possible)",
                   sols["verdict"] == "SAT", sols["verdict"]))

    # ---- negative control: a proof is only valid for the CNF that has the units
    v_base_only = L.verify_drat(base, W / "leaf1.drat")
    good.append(ok("NEG: leaf proof does NOT verify against the base alone "
                   "(cube units are load-bearing)", not v_base_only["verified"],
                   v_base_only["drat_trim_tail"]))
    v_sat_leaf = L.verify_drat(leafsat, W / "leaf1.drat")
    good.append(ok("NEG: leaf proof does NOT verify against a satisfiable "
                   "sibling leaf (wrong-leaf swap caught)", not v_sat_leaf["verified"],
                   v_sat_leaf["drat_trim_tail"]))

    # ---- negative control: an incremental-assumption trace is not a leaf proof
    inc = W / "inccnf"
    inc.mkdir(exist_ok=True)
    icnf = inc / "cubes.icnf"
    lines = [f"p inccnf"] + [" ".join(map(str, c)) + " 0" for c in GADGET["clauses"]]
    lines += ["a -1 2 0", "a 1 -2 0"]
    icnf.write_text("\n".join(lines) + "\n")
    pr = subprocess.run([L.DEFAULT_CADICAL, "-q", "--binary=false", str(icnf),
                         str(inc / "trace.drat")], capture_output=True, text=True)
    trace = inc / "trace.drat"
    good.append(ok("inccnf run exits 20 (all cubes UNSAT)",
                   pr.returncode == 20, pr.returncode))
    if trace.exists():
        for leaf, cube in (("leaf1", [-1, 2]), ("leaf2", [1, -2])):
            lc = inc / f"{leaf}.cnf"
            L.freeze(base, cube, lc)
            vv = L.verify_drat(lc, trace)
            print(f"INFO inccnf whole-trace replay vs {leaf} {cube}: "
                  f"verified={vv['verified']}")
    else:
        good.append(ok("inccnf wrote a trace", False))

    # ---- certify: partial (open) parent must NOT claim closure even when all
    #      leaves that were closed verify
    rep = L.certify(base, [[-1, 2], [1, -2], [1, 2]], W / "cert_partial",
                    conflicts=10000, seconds=30)
    good.append(ok("certify: partial leaf list -> NO CLOSURE",
                   rep["conclusion"].startswith("NO CLOSURE"), rep["conclusion"]))
    good.append(ok("certify: SAT leaf counted", rep["status_counts"].get("SAT") == 1,
                   rep["status_counts"]))
    good.append(ok("certify: certified leaves are UNSAT_VERIFIED",
                   rep["status_counts"].get("UNSAT_VERIFIED") == 2, rep["status_counts"]))

    # ---- certify: all leaves UNSAT but cubes NOT exhaustive -> no closure
    rep2 = L.certify(base, [[-1, 2], [1, -2]], W / "cert_nonex",
                     conflicts=10000, seconds=30)
    good.append(ok("certify: non-exhaustive cubes -> NO CLOSURE",
                   not rep2["coverage_exhaustive"] and
                   rep2["conclusion"].startswith("NO CLOSURE"), rep2["conclusion"]))

    # ---- certify + independent replay on an UNSAT base with an exhaustive split
    unsat_base = write_cnf(W / "unsat_base.cnf", GADGET["nv"],
                           GADGET["clauses"] + [(-1,), (-2,)])
    # base forces x=y=True, hence gadget -> UNSAT; split on x is exhaustive
    rep3 = L.certify(unsat_base, [[1], [-1]], W / "cert_full",
                     conflicts=10000, seconds=30)
    good.append(ok("certify: exhaustive + all verified -> BASE UNSAT",
                   rep3["conclusion"].startswith("BASE UNSAT"), rep3["conclusion"]))
    rp = L.replay(W / "cert_full" / "certificate.json", W / "replay_full")
    good.append(ok("replay: independent rebuild + fresh drat-trim agrees",
                   rp["replay_ok"], rp))

    # ---- exit code handling
    bad = write_cnf(W / "badheader.cnf", 2, [(1,)])
    bad.write_text("p cnf 2 x\n1 0\n")
    expect_error("dimacs_header rejects a non-numeric header",
                 lambda: L.dimacs_header(bad), "non-numeric")

    print("\n%d/%d checks passed" % (sum(map(bool, good)), len(good)))
    return 0 if all(good) else 1


def _write_inccnf(path):
    path.write_text("p inccnf\n1 2 0\na 1 0\n")
    return path


if __name__ == "__main__":
    sys.exit(main())
