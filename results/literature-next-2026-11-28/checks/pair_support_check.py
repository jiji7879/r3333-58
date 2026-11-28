#!/usr/bin/env python3
"""Bounded local two-sender/one-support-arm feasibility census.

This is deliberately an ordinary induced-local CNF experiment, not a wall solve.
It asks whether row-local host clauses plus frozen units reject any pair of 112
P4/C5 supports shared by two distinct senders into the same arm.
"""
import hashlib
import itertools
import json
from pathlib import Path
import time

from pysat.formula import CNF
from pysat.solvers import Cadical195

ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "results/ams-wall-2026-11-28/semantic-map/reconstructed-parent.cnf"
CATALOGUE = ROOT / "results/ams-wall-2026-11-28/semantic-map/support-catalogue.json"
OUT = Path(__file__).with_name("pair_support_check.json")
N = 58
X, Y = 18, 19
ARM = tuple(range(1, 17))
COLOUR = 1

edges = list(itertools.combinations(range(N), 2))
assert len(edges) == 6612 // 4

def lit(u, v, c):
    return 4 * edges.index((min(u, v), max(u, v))) + c + 1

def sha(data):
    return hashlib.sha256(data).hexdigest()

raw = PARENT.read_bytes()
assert sha(raw) == "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
form = CNF(from_string=raw.decode())
local = {0, X, Y, *ARM}
base = []
for clause in form.clauses:
    if all(abs(l) <= 6612 and set(edges[(abs(l) - 1) // 4]) <= local for l in clause):
        base.append(clause)
supports = [tuple(p) for p in json.loads(CATALOGUE.read_text())]
assert len(supports) == 112 and len(set(supports)) == 112

start_cpu = time.process_time()
start_wall = time.perf_counter()
answers = {}
models = []
queries = 0
with Cadical195(bootstrap_with=base) as sat:
    sat.configure({"seed": 0})
    for i, p in enumerate(supports):
        for j, q in enumerate(supports):
            pins = [lit(X, ARM[k], COLOUR) for k in p]
            pins += [lit(Y, ARM[k], COLOUR) for k in q]
            answer = sat.solve(assumptions=pins)
            answers[str(answer)] = answers.get(str(answer), 0) + 1
            queries += 1
            if answer is not True and len(models) < 10:
                models.append({"i": i, "j": j, "p": p, "q": q, "answer": answer})
            if answer is not True:
                continue
            if not models and i == j == 0:
                model = set(sat.get_model())
                assert all(any(l in model for l in clause) for clause in base + [pins])
    # A deliberately overlarge support must contain colour-1 internal T edges,
    # closing a triangle with either sender. This tests that the local CNF is not vacuous.
    bad = list(range(16))
    negative_answer = sat.solve(assumptions=[lit(X, ARM[k], COLOUR) for k in bad])
    stats = sat.accum_stats()

result = {
    "schema": "bounded-two-sender-shared-arm/v1",
    "parent_sha256": sha(raw),
    "scope": "Induced host/frozen-unit CNF on {0,18,19} union arm 1..16 only; no counters, other arms, final floors, cubes, or ChainReady. SAT is local feasibility only; no row or Ramsey inference.",
    "senders": [X, Y],
    "target_vertices": list(ARM),
    "support_color": COLOUR,
    "base_clauses": len(base),
    "catalogue_size": len(supports),
    "queries": queries,
    "answers": answers,
    "first_nonsat": models,
    "negative_control": {"pins": 16, "answer": negative_answer},
    "solver_stats": stats,
    "cpu_seconds": time.process_time() - start_cpu,
    "wall_seconds": time.perf_counter() - start_wall,
}
OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
