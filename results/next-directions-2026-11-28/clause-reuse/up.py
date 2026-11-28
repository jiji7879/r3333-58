"""Cheap propagator: (a) root UP closure of the retained request, (b) is each
appended clause already unit-propagation-refutable under its own negation?

Deterministic, no solver, no search. Clause C is 'UP-trivial at the
destination' for base B when UP(B and not C) conflicts, i.e. C is a RUP
consequence of the exact retained request; otherwise its derivation needs case
analysis, so it can add propagation.
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent

def read(path):
    clauses, nv = [], None
    for line in open(path, "rb"):
        line = line.strip()
        if not line or line.startswith(b"c"): continue
        if line.startswith(b"p"):
            nv = int(line.split()[2]); continue
        v = list(map(int, line.split())); assert v[-1] == 0
        clauses.append(tuple(v[:-1]))
    return nv, clauses

class UP:
    def __init__(self, clauses, nv):
        self.nv, self.clauses = nv, clauses
        self.occ = [[] for _ in range(2 * nv + 2)]
        for i, c in enumerate(clauses):
            for l in c: self.occ[self.ix(l)].append(i)
        self.val = [0] * (nv + 1)
        self.unit_clauses = [c[0] for c in clauses if len(c) == 1]
    @staticmethod
    def ix(l): return 2 * abs(l) + (1 if l > 0 else 0)
    def lit_value(self, l):
        s = self.val[abs(l)]
        return s if l > 0 else -s
    def assign(self, l):
        v = abs(l)
        if self.val[v] == (1 if l > 0 else -1): return True
        if self.val[v] != 0: return False
        self.val[v] = 1 if l > 0 else -1
        self.trail.append(l)
        return True
    def run(self, assumptions):
        self.val = [0] * (self.nv + 1)
        self.trail = []
        if not assumptions:
            for c in self.unit_clauses:
                if not self.assign(c): return True, len(self.trail)
        for l in assumptions:
            if not self.assign(l): return True, len(self.trail)
        head = 0
        while head < len(self.trail):
            l = self.trail[head]; head += 1
            for ci in self.occ[self.ix(-l)]:
                c = self.clauses[ci]
                unassigned = None; sat = False; count = 0
                for x in c:
                    s = self.lit_value(x)
                    if s == 1: sat = True; break
                    if s == 0:
                        count += 1; unassigned = x
                        if count > 1: break
                if sat or count > 1: continue
                if count == 0: return True, len(self.trail)
                if not self.assign(unassigned): return True, len(self.trail)
        return False, len(self.trail)

nv, clauses = read(HERE / "parent-cube.cnf")
assert nv == 19533 and len(clauses) == 184337
up = UP(clauses, nv)
conflict, trail = up.run([])
root_units = sum(1 for x in up.val if x)
print("unit clauses", len(up.unit_clauses))
print("root closure assigned", root_units, "conflict", conflict, "trail", trail, flush=True)

cand = [tuple(map(int, l.split()[:-1])) for l in open(HERE / "clauses.txt")]
trivial = 0; detail = []
for c in cand:
    conf, tr = up.run([-l for l in c])
    trivial += bool(conf)
    detail.append({"clause": list(c), "up_refuted": conf, "trail": tr})
nontrivial = len(cand) - trivial
print("appended clauses", len(cand), "UP-trivial at destination", trivial, "nontrivial", nontrivial)
json.dump({"root_closure_assigned": root_units, "root_conflict": conflict,
           "n": len(cand), "up_trivial": trivial, "nontrivial": nontrivial,
           "detail": detail}, open(HERE / "up.json", "w"), indent=1)
