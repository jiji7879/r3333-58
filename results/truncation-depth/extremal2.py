#!/usr/bin/env python3
"""All-extremal 14-slot arms under the depth-3 condition.

Same search as extremal.py, but additionally requiring that no triple of slots has
all three admissible-colour lists equal to one singleton (the branch-necessary
condition proved in PROOF.md, Lemma 1).  If this returns 0, the record's
"an all-extremal arm cannot fill 14 slots" is true in the strong form; if it
returns a positive count, the sentence needs the pin to be true.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Template
from extend import words_for_block

A_POINTS = list(range(15))


def all_words(tmpl):
    from itertools import combinations
    out = []
    for block in combinations(A_POINTS, 5):
        out.extend(words_for_block(tmpl, set(block), limit=100000))
    return out


def alist(w1, w2, arm):
    return frozenset(c for c in range(4) if c != arm
                     and not any(w1[p] == c and w2[p] == c for p in A_POINTS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="../../../artifacts/k15_link_Tminus_m5.col")
    ap.add_argument("--arm", type=int, default=1)
    a = ap.parse_args()
    tmpl = Template(a.template)
    words = all_words(tmpl)
    ext = sorted(set(tuple(w) for w in words
                     if 0 in [sum(1 for v in w if v == f) for f in (1, 2, 3)]))
    n = len(ext)
    L = [[alist(ext[i], ext[j], a.arm) if i != j else None for j in range(n)] for i in range(n)]
    ok = [[bool(L[i][j]) for j in range(n)] for i in range(n)]
    count = 0
    nodes = 0

    def dfs(i0, chosen):
        nonlocal count, nodes
        nodes += 1
        if len(chosen) == 14:
            count += 1
            return
        if len(chosen) + 2 * (n - i0) < 14:
            return
        for i in range(i0, n):
            if chosen.count(i) >= 2:
                continue
            if not all(ok[i][j] for j in chosen):
                continue
            lists = [L[i][j] for j in chosen]
            if any(len(s) == 1 for s in lists):
                bad = False
                for x in range(len(chosen)):
                    if len(lists[x]) != 1:
                        continue
                    c = next(iter(lists[x]))
                    for y in range(x + 1, len(chosen)):
                        if lists[y] == frozenset([c]) and L[chosen[x]][chosen[y]] == frozenset([c]):
                            bad = True
                            break
                    if bad:
                        break
                if bad:
                    continue
            chosen.append(i)
            dfs(i, chosen)
            chosen.pop()

    dfs(0, [])
    print(f"extremal words {n}, arm colour {a.arm}: "
          f"size-14 multisets with pairwise admissibility AND no equal-singleton triple: {count}"
          f"  (nodes {nodes})")


if __name__ == "__main__":
    main()
