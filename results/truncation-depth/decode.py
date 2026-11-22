#!/usr/bin/env python3
"""Decode a solver model of a pair-level CNF into a .wit file."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ARMS = {1: list(range(0, 14)), 2: list(range(14, 28)), 3: list(range(28, 42))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("mapfile")
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default="../../../artifacts/k15_link_Tminus_m5.col")
    a = ap.parse_args()
    meta = {int(k): v for k, v in json.load(open(a.mapfile)).items()}
    lits = [int(t) for t in open(a.model).read().split()]
    true = set(l for l in lits if l > 0)
    word = {x: [None] * 15 for x in range(42)}
    q = {}
    for v, info in meta.items():
        if v not in true:
            continue
        if info[0] == "cell":
            x, p, f = info[1], info[2], info[3]
            if word[x][p] is not None and word[x][p] != f:
                raise SystemExit(f"two colours at cell {x},{p}")
            word[x][p] = f
        elif info[0] == "q":
            q[(info[1], info[2])] = info[3]
    for x in range(42):
        if any(w is None for w in word[x]):
            raise SystemExit(f"incomplete word {x}")
    with open(a.out, "w") as fh:
        fh.write(f"template {a.template}\n")
        for b, vs in ARMS.items():
            fh.write(f"arm {b} " + " ".join(str(v) for v in vs) + "\n")
        for x in range(42):
            fh.write(f"word {x} " + " ".join(str(v) for v in word[x]) + "\n")
        for (x, y), f in sorted(q.items()):
            fh.write(f"pair {x} {y} {f}\n")
    print(f"wrote {a.out}: 42 words, {len(q)} pair colours")


if __name__ == "__main__":
    main()
