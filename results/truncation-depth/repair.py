#!/usr/bin/env python3
"""Local search for a 42-word assignment with no dead pair and no dead triple.

Start from a pair-level witness (coverage 14, five zeros, part independence) and
reword single slots, keeping each slot's colour-0 support, until the depth-3
relaxation is satisfied:

  (T2) every pair of slots has at least one admissible colour,
  (T3) no triple of slots has all three admissible lists equal to one singleton.

Both are necessary for a genuine object (see PROOF.md), so a model here is a
relaxation of the branch that no known witness satisfies.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k58lib import Witness, Template
from extend import words_for_block, ARMS


def armof(x):
    for b, vs in ARMS.items():
        if x in vs:
            return b
    raise KeyError(x)


class State:
    def __init__(self, words):
        self.words = words
        self.bits = [{f: 0 for f in range(4)} for _ in range(42)]
        for x in range(42):
            for p, f in enumerate(words[x]):
                self.bits[x][f] |= 1 << p
        self.recompute()

    def allowed(self, x, y):
        a = [c for c in range(4) if armof(x) != armof(y) or c != armof(x)]
        return [c for c in a if not (self.bits[x][c] & self.bits[y][c])]

    def recompute(self):
        self.sing = {}
        dead_pairs = []
        for x in range(42):
            for y in range(x + 1, 42):
                al = self.allowed(x, y)
                if not al:
                    dead_pairs.append((x, y))
                    self.sing[(x, y)] = None
                elif len(al) == 1:
                    self.sing[(x, y)] = al[0]
                else:
                    self.sing[(x, y)] = -1
        self.dead_pairs = dead_pairs
        self.tri = {}
        for c in range(4):
            adj = {x: set() for x in range(42)}
            for (x, y), s in self.sing.items():
                if s == c:
                    adj[x].add(y)
                    adj[y].add(x)
            cnt = 0
            for x in range(42):
                nb = sorted(adj[x])
                for i in range(len(nb)):
                    for j in range(i + 1, len(nb)):
                        if nb[j] in adj[nb[i]]:
                            cnt += 1
            self.tri[c] = cnt
        self.n_dead_tri = sum(self.tri.values())
        return 1000 * len(dead_pairs) + self.n_dead_tri

    def score(self):
        # dead pairs are much harder than dead triples: weight them heavily
        return 1000 * len(self.dead_pairs) + self.n_dead_tri

    def local(self, x):
        """dead pairs and dead triples involving slot x"""
        dp = [p for p in self.dead_pairs if x in p]
        dt = 0
        for c in range(4):
            nb = [y for y in range(42) if y != x and self.sing[(min(x, y), max(x, y))] == c]
            cnt = 0
            for i in range(len(nb)):
                for j in range(i + 1, len(nb)):
                    if self.sing[(min(nb[i], nb[j]), max(nb[i], nb[j]))] == c:
                        cnt += 1
            dt += cnt
        return len(dp), dt

    def set_word(self, x, w):
        self.words[x] = w
        self.bits[x] = {f: 0 for f in range(4)}
        for p, f in enumerate(w):
            self.bits[x][f] |= 1 << p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start")
    ap.add_argument("--template", required=True)
    ap.add_argument("--seconds", type=float, default=120.0)
    ap.add_argument("--out", default="wit/depth3.wit")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    tmpl = Template(a.template)
    w0 = Witness(a.start)
    words = [list(w0.words[x]) for x in range(42)]
    st = State(words)
    print(f"start: dead pairs {len(st.dead_pairs)}, dead triples {st.n_dead_tri}")
    cand = {}
    for x in range(42):
        block = {p for p, f in enumerate(words[x]) if f == 0}
        cand[x] = [w for w in words_for_block(tmpl, block, limit=100000)]
    print("candidate words per slot:", min(len(c) for c in cand.values()),
          max(len(c) for c in cand.values()))
    t0 = time.time()
    it = 0
    best = st.score()
    while time.time() - t0 < a.seconds and st.score() > 0:
        it += 1
        # choose a slot involved in a violation
        hot = set()
        for (x, y) in st.dead_pairs:
            hot.add(x)
            hot.add(y)
        for x in range(42):
            for c in range(4):
                nb = [y for y in range(42) if y != x and st.sing[(min(x, y), max(x, y))] == c]
                if len(nb) >= 2:
                    hot.add(x)
        if not hot:
            break
        x = rng.choice(sorted(hot))
        old = list(st.words[x])
        opts = rng.sample(cand[x], min(40, len(cand[x])))
        bestw, bestsc = None, None
        for w in opts:
            st.set_word(x, w)
            st.recompute()
            sc = (len(st.dead_pairs), st.n_dead_tri)
            if bestsc is None or sc < bestsc:
                bestw, bestsc = w, sc
        if bestw is not None:
            st.set_word(x, bestw)
            st.recompute()
        else:
            st.set_word(x, old)
            st.recompute()
        best = min(best, st.score())
        if it % 100 == 0:
            print(f"  it {it} t={time.time()-t0:.0f}s best={best} pairs={len(st.dead_pairs)} tri={st.n_dead_tri}", flush=True)
    print(f"iterations {it}, elapsed {time.time()-t0:.1f}s")
    print(f"final: dead pairs {len(st.dead_pairs)}, dead triples {st.n_dead_tri}")
    if st.score() == 0:
        with open(a.out, "w") as fh:
            fh.write(f"template {a.template}\n")
            for b, vs in ARMS.items():
                fh.write(f"arm {b} " + " ".join(str(v) for v in vs) + "\n")
            for x in range(42):
                fh.write(f"word {x} " + " ".join(str(v) for v in st.words[x]) + "\n")
        print("wrote", a.out)
    else:
        with open(a.out + ".partial", "w") as fh:
            fh.write(f"template {a.template}\n")
            for b, vs in ARMS.items():
                fh.write(f"arm {b} " + " ".join(str(v) for v in vs) + "\n")
            for x in range(42):
                fh.write(f"word {x} " + " ".join(str(v) for v in st.words[x]) + "\n")
        print("wrote", a.out + ".partial")


if __name__ == "__main__":
    main()
