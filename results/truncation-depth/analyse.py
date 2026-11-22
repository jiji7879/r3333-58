#!/usr/bin/env python3
"""Structure of the depth-3 obstructions, plus one written certificate."""
import argparse
import json
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Witness
from depth import allowed_colours, feasible


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wit")
    ap.add_argument("--kmax", type=int, default=3)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    w = Witness(a.wit)
    slots = w.slots
    infeas = []
    for k in (2, 3):
        for S in combinations(slots, k):
            ok, _ = feasible(w, S)
            if not ok:
                infeas.append(S)
        if infeas:
            print(f"depth {k}")
            break
    print(f"{len(infeas)} infeasible subsets at the first size")

    rows = []
    for S in infeas:
        doms = [sorted(allowed_colours(w, S[i], S[j]))
                for i in range(len(S)) for j in range(i + 1, len(S))]
        arms = [w.armof.get(s) for s in S]
        rows.append({"S": list(S), "arms": arms, "domains": doms,
                     "min_dom": min(len(d) for d in doms),
                     "intra_arm": len(set(arms)) == 1})
    n_intra = sum(1 for r in rows if r["intra_arm"])
    hist = {}
    for r in rows:
        hist[r["min_dom"]] = hist.get(r["min_dom"], 0) + 1
    print(f"intra-arm {n_intra}, cross-arm {len(rows) - n_intra}")
    print(f"minimum domain size histogram {dict(sorted(hist.items()))}")

    # how often does a singleton domain alone force the refutation?
    forced = 0
    for r in rows:
        S = r["S"]
        doms = r["domains"]
        pairs = [(i, j) for i in range(len(S)) for j in range(i + 1, len(S))]
        for p, d in zip(pairs, doms):
            if len(d) == 1:
                # pin that pair and re-check
                ok = pin_feasible(w, S, p, d[0])
                if not ok:
                    forced += 1
                break
    print(f"refutations already forced by a singleton pair domain: {forced}")

    if a.out:
        with open(a.out, "w") as fh:
            json.dump(rows, fh)
        print(f"wrote {a.out}")


def pin_feasible(w, S, pair, colour):
    S = list(S)
    pairs = [(i, j) for i in range(len(S)) for j in range(i + 1, len(S))]
    dom = {}
    for (i, j) in pairs:
        d = allowed_colours(w, S[i], S[j])
        if (i, j) == pair:
            d = {colour} & d
        dom[(i, j)] = d
        if not d:
            return False
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
            good = True
            for (i, j, k) in triples:
                aa = val.get((i, j))
                bb = val.get((i, k))
                cc = val.get((j, k))
                if aa is not None and aa == bb and bb == cc:
                    good = False
                    break
            if good and rec(t + 1):
                return True
            del val[p]
        return False

    return rec(0)


if __name__ == "__main__":
    main()
