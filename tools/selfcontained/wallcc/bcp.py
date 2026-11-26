#!/usr/bin/env python3
"""Unit-propagation closure (BCP) check for a DIMACS CNF, gzipped or not.

Why this exists
---------------
The empty clause is RUP with respect to F  <=>  plain unit propagation on F
derives a conflict.  So:

  bcp_conflict(F) is True   =>  drat-trim accepts the EMPTY proof for F,
                                i.e. any certificate for F is vacuous and says
                                nothing about the work a solver did.

  bcp_conflict(F) is False  =>  a replayed DRAT proof is doing real work.

`engine_conformance.unit_conflict` is the same predicate written for clarity on
toy formulas; this file is the linear-time version (counters + occurrence
lists) that can be pointed at pipeline-sized CNFs, and the two are
cross-checked by `python3 bcp.py --selftest`.

Usage:  python3 bcp.py <cnf[.gz]> [--json]
"""

from __future__ import annotations

import gzip
import json
import sys
from array import array


def read_cnf(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    nvars = nclauses = None
    start = array("i", [0])
    lits = array("i")
    dup_clauses = 0
    with opener(path, "rt", errors="replace") as fh:
        cur = []
        for raw in fh:
            s = raw.strip()
            if not s or s[0] == "c":
                continue
            if s[0] == "p":
                parts = s.split()
                nvars, nclauses = int(parts[2]), int(parts[3])
                continue
            for tok in s.split():
                lit = int(tok)
                if lit:
                    cur.append(lit)
                else:
                    if len(set(cur)) != len(cur):
                        dup_clauses += 1
                        cur = list(dict.fromkeys(cur))  # keep counters exact
                    lits.extend(cur)
                    start.append(len(lits))
                    cur = []
        if cur:
            raise ValueError("unterminated clause")
    return nvars, nclauses, start, lits, dup_clauses


def bcp(path):
    nvars, nclauses, start, lits, dup_clauses = read_cnf(path)
    m = len(start) - 1
    if nclauses is not None and nclauses != m:
        pass  # reported, not repaired: the caller decides what a mismatch means
    occ = [[] for _ in range(2 * (nvars or 1) + 2)]

    def idx(lit):
        return 2 * lit if lit > 0 else -2 * lit + 1

    for cid in range(m):
        for k in range(start[cid], start[cid + 1]):
            occ[idx(lits[k])].append(cid)
    cnt = array("i", [0]) * 0
    cnt = array("i", (start[cid + 1] - start[cid] for cid in range(m)))
    val = bytearray((nvars or 0) + 1)  # 0 unassigned, 1 true, 2 false
    trail = 0
    queue = [lits[k] for cid in range(m) if start[cid + 1] - start[cid] == 1
             for k in (start[cid],)]
    conflict = False
    while queue:
        lit = queue.pop()
        v = abs(lit)
        want = 1 if lit > 0 else 2
        if val[v]:
            if val[v] != want:
                conflict = True
                break
            continue
        val[v] = want
        trail += 1
        for cid in occ[idx(lit)]:
            cnt[cid] = -1  # satisfied
        for cid in occ[idx(-lit)]:
            c = cnt[cid]
            if c <= 0:
                continue
            c -= 1
            cnt[cid] = c
            if c == 0:
                conflict = True
                break
            if c == 1:
                for k in range(start[cid], start[cid + 1]):
                    l2 = lits[k]
                    if val[abs(l2)] == 0:
                        queue.append(l2)
                        break
        if conflict:
            break
    return {
        "cnf": str(path),
        "nvars": nvars,
        "header_declared_clauses": nclauses,
        "clauses": m,
        "header_count_ok": nclauses == m,
        "duplicate_literal_clauses": dup_clauses,
        "assigned": trail,
        "bcp_conflict": conflict,
        # If BCP closes the formula, drat-trim accepts an empty proof and any
        # certificate for it is vacuous.
        "certificate_would_be_vacuous": conflict,
    }


def _selftest():
    import engine_conformance as ec
    import os
    import random

    cases = []
    for seed in range(200):
        rng = random.Random(seed)
        nv = rng.randint(2, 7)
        nc = rng.randint(1, 12)
        cls = []
        for _ in range(nc):
            k = rng.randint(1, 3)
            cls.append(tuple(rng.choice([-1, 1]) * rng.randint(1, nv) for _ in range(k)))
        cases.append((nv, cls))
    bad = 0
    for i, (nv, cls) in enumerate(cases):
        want = ec.unit_conflict(cls)
        path = f".scratch/bcp-selftest-{i}.cnf"
        with open(path, "w") as fh:
            fh.write(f"p cnf {nv} {len(cls)}\n")
            for c in cls:
                fh.write(" ".join(map(str, c)) + " 0\n")
        got = bcp(path)["bcp_conflict"]
        os.unlink(path)
        if got != want:
            bad += 1
            print(f"MISMATCH seed={i} want={want} got={got} clauses={cls}")
    print(f"selftest: {len(cases) - bad}/{len(cases)} agree with "
          f"engine_conformance.unit_conflict")
    return bad == 0


def main():
    if "--selftest" in sys.argv:
        import os
        os.makedirs(".scratch", exist_ok=True)
        return 0 if _selftest() else 1
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    rec = bcp(args[0])
    if "--json" in sys.argv:
        print(json.dumps(rec, indent=2))
    else:
        print(f"{rec['cnf']}: vars={rec['nvars']} clauses={rec['clauses']} "
              f"header_ok={rec['header_count_ok']} assigned={rec['assigned']} "
              f"bcp_conflict={rec['bcp_conflict']} "
              f"certificate_vacuous={rec['certificate_would_be_vacuous']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
