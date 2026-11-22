#!/usr/bin/env python3
"""Extend a colour-0 design to full words and emit a .wit skeleton (words only).

Word of a slot: M_0 (given by the design) plus a partition of the remaining ten
arm points into M_1, M_2, M_3, each independent in the template's colour graph.
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Template

ARMS = {1: list(range(0, 14)), 2: list(range(14, 28)), 3: list(range(28, 42))}


def words_for_block(tmpl, block, limit=100000):
    rest = [p for p in range(15) if p not in block]
    # independent sets per colour, membership test
    bad = {f: tmpl.indep[f] for f in (1, 2, 3)}
    out = []

    def ok(f, cur, p):
        for q in cur:
            pair = (min(p, q), max(p, q))
            if pair in bad[f] or (pair[1], pair[0]) in bad[f]:
                return False
        return True

    part = {1: [], 2: [], 3: []}

    def rec(i):
        if len(out) >= limit:
            return
        if i == len(rest):
            w = [None] * 15
            for p in block:
                w[p] = 0
            for f in (1, 2, 3):
                for p in part[f]:
                    w[p] = f
            out.append(w)
            return
        p = rest[i]
        for f in (1, 2, 3):
            if ok(f, part[f], p):
                part[f].append(p)
                rec(i + 1)
                part[f].pop()

    rec(0)
    return out


def wit_armof(x):
    for b, vs in ARMS.items():
        if x in vs:
            return b
    raise KeyError(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("blocks")
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--mode", default="random",
                    help="random | small (prefer small ordinary parts) | big")
    a = ap.parse_args()
    tmpl = Template(a.template)
    blocks = {}
    for line in open(a.blocks):
        t = [int(v) for v in line.split()]
        blocks[t[0]] = set(t[1:])
    rng = random.Random(a.seed)
    chosen = {}
    stats = []
    cand = {}
    for x in range(42):
        ws = words_for_block(tmpl, blocks[x])
        stats.append(len(ws))
        if not ws:
            raise SystemExit(f"no word extends block {x}: {sorted(blocks[x])}")
        cand[x] = ws
    if a.mode == "random":
        for x in range(42):
            chosen[x] = rng.choice(cand[x])
    elif a.mode == "small":
        for x in range(42):
            chosen[x] = min(cand[x], key=lambda w: sorted((sum(1 for v in w if v == f) for f in (1, 2, 3)), reverse=True))
    elif a.mode == "big":
        for x in range(42):
            chosen[x] = max(cand[x], key=lambda w: sorted((sum(1 for v in w if v == f) for f in (1, 2, 3))))
    elif a.mode == "spread":
        cnt = {(b, f, p): 0 for b in ARMS for f in (1, 2, 3) for p in range(15)}
        for x in range(42):
            b = wit_armof(x)
            best = None
            for w in cand[x]:
                pen = 0
                for f in (1, 2, 3):
                    for p in range(15):
                        if w[p] == f:
                            pen = max(pen, cnt[(b, f, p)] + 1)
                score = (pen, rng.random())
                if best is None or score < best[0]:
                    best = (score, w)
            w = best[1]
            chosen[x] = w
            for f in (1, 2, 3):
                for p in range(15):
                    if w[p] == f:
                        cnt[(b, f, p)] += 1
        over = {k: v for k, v in cnt.items() if v > 5}
        if over:
            print("column counts above 5:", over)
    else:
        raise SystemExit("unknown mode")
    with open(a.out, "w") as fh:
        fh.write(f"template {a.template}\n")
        for b, vs in ARMS.items():
            fh.write(f"arm {b} " + " ".join(str(v) for v in vs) + "\n")
        for x in range(42):
            fh.write(f"word {x} " + " ".join(str(v) for v in chosen[x]) + "\n")
    print(f"words per block: min {min(stats)} max {max(stats)} total {sum(stats)}")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
