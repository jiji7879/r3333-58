#!/usr/bin/env python3
"""Truncation depth of a pair-level witness.

For a set S of slots, the *local object* is the witness's words on S together
with a colouring of the pairs inside S subject to

  (P1) a pair inside one arm never takes the arm colour,
  (P2) colour(x,y) = f requires M_f(x) cap M_f(y) = empty,
  (X)  no monochromatic triangle inside S.

Every genuine object restricts to such a local object on every one of its slot
subsets, so a subset with no solution is a set of slots that no genuine object
can carry with these words.  The engine searches the subsets in increasing size
and reports the first size at which one is infeasible: the *truncation depth*.
"""
import argparse
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Witness

ARMS = {1: list(range(0, 14)), 2: list(range(14, 28)), 3: list(range(28, 42))}


def allowed_colours(wit, x, y):
    """All colours f with M_f(x) cap M_f(y) = empty, minus the shared arm colour."""
    ok = set()
    for f in range(4):
        if not (wit.part(x, f) & wit.part(y, f)):
            ok.add(f)
    arm = wit.armof.get(x)
    if arm is not None and arm == wit.armof.get(y):
        ok.discard(arm)
    return ok


def feasible(wit, S, domains=None):
    """Is there a valid colouring of the pairs inside S?"""
    S = list(S)
    pairs = [(i, j) for i in range(len(S)) for j in range(i + 1, len(S))]
    dom = {}
    for (i, j) in pairs:
        d = allowed_colours(wit, S[i], S[j])
        dom[(i, j)] = d
        if not d:
            return False, None
    order = sorted(pairs, key=lambda p: len(dom[p]))
    triples = [(i, j, k) for i in range(len(S)) for j in range(i + 1, len(S))
               for k in range(j + 1, len(S))]
    val = {}

    def rec(t):
        if t == len(order):
            return True
        p = order[t]
        for c in sorted(dom[p]):
            val[p] = c
            if triples_ok(S, val, triples):
                if rec(t + 1):
                    return True
            del val[p]
        return False

    def triples_ok(S, val, triples):
        for (i, j, k) in triples:
            a = val.get((i, j), None)
            b = val.get((i, k), None)
            cc = val.get((j, k), None)
            if a is not None and a == b and b == cc:
                return False
        return True

    if rec(0):
        return True, dict(val)
    return False, None


def depth_search(wit, kmax, slots=None):
    slots = slots if slots is not None else wit.slots
    out = {}
    for k in range(2, kmax + 1):
        bad = []
        n = 0
        for S in combinations(slots, k):
            n += 1
            ok, _ = feasible(wit, S)
            if not ok:
                bad.append(S)
        out[k] = (n, bad)
        if bad:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wit")
    ap.add_argument("--kmax", type=int, default=4)
    a = ap.parse_args()
    w = Witness(a.wit)
    print(f"{a.wit}: {len(w.slots)} slots, arms {sorted(w.arms)}")
    res = depth_search(w, a.kmax)
    for k, (n, bad) in sorted(res.items()):
        print(f"k={k}: {n} subsets checked, {len(bad)} infeasible")
        for S in bad[:5]:
            print("   e.g.", S, "arms", [w.armof.get(s) for s in S])
    if res:
        kmin = min(res)
        if res[kmin][1]:
            print(f"TRUNCATION DEPTH = {kmin}")
        else:
            print(f"no infeasible subset up to size {kmin}")


if __name__ == "__main__":
    main()
