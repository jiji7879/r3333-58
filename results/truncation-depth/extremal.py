#!/usr/bin/env python3
"""Verify the record's extremal-word claim for a 14-slot arm.

Record (WALL §24): "three copies of one word force its empty colour on all three
pairs, so copies <= 2 per arm, and an all-extremal arm cannot fill 14 slots".

This script enumerates the words with an empty ordinary part ("extremal"), then
searches all size-14 multisets with multiplicity <= 2 whose pairs are all
admissible (a pair is admissible in colour c iff M_c parts are disjoint and c is
not the arm colour), for each of the three arm colours.
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


def admissible(w1, w2, arm):
    for c in range(4):
        if c == arm:
            continue
        if not any(w1[p] == c and w2[p] == c for p in A_POINTS):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="../../../artifacts/k15_link_Tminus_m5.col")
    a = ap.parse_args()
    tmpl = Template(a.template)
    words = all_words(tmpl)
    print(f"all words: {len(words)}")
    ext = [w for w in words if 0 in [sum(1 for v in w if v == f) for f in (1, 2, 3)]]
    ext = [tuple(w) for w in ext]
    ext = sorted(set(ext))
    print(f"extremal words (some ordinary part empty): {len(ext)}")
    for arm in (1, 2, 3):
        adj = [[admissible(ext[i], ext[j], arm) for j in range(len(ext))] for i in range(len(ext))]
        found = []
        cnt = {"nodes": 0}

        def dfs(i0, chosen):
            cnt["nodes"] += 1
            if len(chosen) == 14:
                found.append(tuple(chosen))
                return
            if len(chosen) + 2 * (len(ext) - i0) < 14:
                return
            if i0 >= len(ext):
                return
            for i in range(i0, len(ext)):
                if chosen.count(i) >= 2:
                    continue
                if all(adj[i][j] for j in chosen):
                    chosen.append(i)
                    dfs(i, chosen)
                    chosen.pop()
        dfs(0, [])
        print(f"arm colour {arm}: size-14 multisets with all pairs admissible: {len(found)}"
              f"  (search nodes {cnt['nodes']})")


if __name__ == "__main__":
    main()
