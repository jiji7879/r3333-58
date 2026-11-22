#!/usr/bin/env python3
"""Extract the design model (the 42 colour-0 supports) and verify it exactly."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ARMS = {1: list(range(0, 14)), 2: list(range(14, 28)), 3: list(range(28, 42))}


def main(cnf_model, mappath, out=None):
    meta = {int(k): v for k, v in json.load(open(mappath)).items()}
    model = [int(l) for l in open(cnf_model).read().split()]
    true = set(l for l in model if l > 0)
    blocks = {x: set() for x in range(42)}
    for v, info in meta.items():
        if info[0] == "cell" and v in true:
            blocks[info[1]].add(info[2])
    # verify
    assert all(len(blocks[x]) == 5 for x in blocks), [len(blocks[x]) for x in blocks]
    cover = [sum(1 for x in range(42) if p in blocks[x]) for p in range(15)]
    assert cover == [14] * 15, cover
    # per-arm clique number of the intersection graph
    def maxclique(vs):
        best = 0
        vs = list(vs)
        adj = {x: set(y for y in vs if y != x and (blocks[x] & blocks[y])) for x in vs}
        def expand(cl, cand):
            nonlocal best
            if len(cl) + len(cand) <= best:
                return
            if not cand:
                best = max(best, len(cl))
                return
            for i, v in enumerate(cand):
                expand(cl + [v], [u for u in cand[i + 1:] if u in adj[v]])
        expand([], vs)
        return best
    cl = {b: maxclique(vs) for b, vs in ARMS.items()}
    print("block sizes 5, coverage 14 each: OK")
    print("per-arm a=0 clique numbers:", cl, "(bound 5)")
    if out:
        with open(out, "w") as fh:
            for x in range(42):
                fh.write(f"{x} " + " ".join(str(p) for p in sorted(blocks[x])) + "\n")
        print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
