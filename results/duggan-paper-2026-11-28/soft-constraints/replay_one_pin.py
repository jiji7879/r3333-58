#!/usr/bin/env python3
"""Independently regenerate and strictly DRAT-check one logged one-pin branch."""
from pathlib import Path
import itertools
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ROUNDS = 80
GUIDE = ROOT / "artifacts/k51_relax_m3_1defect_NOT_a_valid_colouring.col"
LOG = HERE / "k51_one_pin_80.jsonl"
CNF = HERE / "one_pin_round80.cnf"
DRAT = HERE / "one_pin_round80.drat"
REPLAY = HERE / "one_pin_round80_replay.log"

tokens = GUIDE.read_text().split()
n, k = map(int, tokens[:2])
assert (n, k) == (51, 4) and len(tokens) == 2 + n*n
flat = list(map(int, tokens[2:]))
a = [flat[i*n:(i+1)*n] for i in range(n)]
edges = list(itertools.combinations(range(n), 2))
eid = {e: q for q, e in enumerate(edges)}
def var(e, c): return 4*eid[e] + c + 1

def defects():
    return sum(a[i][j] == a[i][l] == a[j][l]
               for i, j, l in itertools.combinations(range(n), 3))
assert defects() == 1
records = [json.loads(line) for line in LOG.read_text().splitlines()]
rounds = [r for r in records if r.get("event") == "round"]
assert len(rounds) == ROUNDS
removed = set()
for r in rounds:
    assert r["status"] == "UNSAT_ASSUMPTIONS" and r["removed"] == 1
    assert r["unpinned_edges"] == r["round"] + 1
    i, j, c = r["removed_first_edge_colour"]
    v = var(tuple(sorted((i, j))), c)
    assert v not in removed
    removed.add(v)
assert len(removed) == ROUNDS and rounds[-1]["active_after"] == 1275-ROUNDS

clauses = []
for e in edges:
    es = var(e, 0)-1  # colour 0 variable minus one
    clauses.append([es+c+1 for c in range(k)])
    for c in range(k):
        for d in range(c+1, k): clauses.append([-(es+c+1), -(es+d+1)])
for i, j, l in itertools.combinations(range(n), 3):
    for c in range(k): clauses.append([-var((i,j),c), -var((i,l),c), -var((j,l),c)])
base_count = len(clauses)
for e in edges:
    v = var(e, a[e[0]][e[1]])
    if v not in removed: clauses.append([v])
assert base_count == 92225 and len(clauses) == base_count + 1195
with CNF.open("w") as f:
    f.write(f"p cnf {4*len(edges)} {len(clauses)}\n")
    for cl in clauses: f.write(" ".join(map(str, cl)) + " 0\n")

p = subprocess.run(["cadical", "-q", "--binary=true", str(CNF), str(DRAT)],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
assert p.returncode == 20, p.stdout
raw_dr = ROOT/"tools/color-resolved-wallcc/bin/drat-trim"
normalizer = ROOT/"tools/color-resolved-wallcc/helpers/strip_binary_drat.py"
clean = HERE/"one_pin_round80_additions.drat"
norm_json = HERE/"one_pin_round80_normalization.json"
with (HERE/"one_pin_round80_normalization.stdout").open("w") as norm_out:
    p = subprocess.run(["python3", str(normalizer), str(DRAT), str(clean), str(norm_json)],
                       stdout=norm_out, stderr=subprocess.STDOUT, text=True)
assert p.returncode == 0
meta = json.loads(norm_json.read_text())
assert meta["complete_parse"] and meta["empty_additions"] == 1
with REPLAY.open("w") as out:
    cmd = [str(raw_dr), str(CNF), str(clean), "-i", "-U", "-W", "-t", "60"]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out.write("COMMAND: drat-trim one_pin_round80.cnf one_pin_round80_additions.drat -i -U -W -t 60\n")
    out.write(p.stdout); out.write(f"EXIT: {p.returncode}\n")
    assert p.returncode == 0 and p.stdout.splitlines().count("s VERIFIED") == 1, p.stdout
    assert not any(x in p.stdout.upper() for x in ("WARNING", "ERROR")), p.stdout
    assert f"read {clean.stat().st_size} bytes from proof file" in p.stdout, p.stdout
    assert "c 0 RAT lemmas in core" in p.stdout, p.stdout
wrong = HERE/"one_pin_round80_WRONG_PARENT.cnf"
wrong.write_text("p cnf 5100 1\n1 0\n")  # SAT: variable 1 is not fixed false anywhere.
p = subprocess.run([str(raw_dr), str(wrong), str(clean), "-i", "-U", "-W", "-t", "60"],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
(HERE/"one_pin_round80_wrong_parent.log").write_text(p.stdout+f"EXIT: {p.returncode}\n")
assert p.returncode != 0 and "s VERIFIED" not in p.stdout.splitlines()
summary = {"round": ROUNDS, "base_variables": 5100, "base_clauses": base_count,
           "active_unit_pins": 1195, "unpinned_edges": 80,
           "raw_drat_bytes": DRAT.stat().st_size, "normalized_drat_bytes": clean.stat().st_size,
           "raw_deletion_commands_removed": meta["commands"]["d"]["commands"],
           "addition_commands_preserved": meta["commands"]["a"]["commands"],
           "solver_exit": 20, "checker_exit": 0, "strict_verified": True,
           "wrong_parent_exit": p.returncode, "wrong_parent_rejected": True,
           "scope": "only this frozen 1195-pin branch; not base K51 UNSAT"}
(HERE/"one_pin_round80_replay.json").write_text(json.dumps(summary, indent=2)+"\n")
print(json.dumps(summary))
