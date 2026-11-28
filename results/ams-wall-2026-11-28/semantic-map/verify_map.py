#!/usr/bin/env python3
"""Second-process checker for the emitted exact-parent maps; no SAT solver."""
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import hashlib
import json

H = Path(__file__).resolve().parent
R = H / "results"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def line(c):
    return (" ".join(map(str, c)) + (" " if c else "") + "0\n").encode()


def block_hash(cs):
    return sha(b"".join(map(line, cs)))


def load(name):
    return json.loads((R / name).read_text())


raw = (H / "inputs" / "parent.cnf").read_bytes()
assert sha(raw) == "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
assert raw == (R / "reconstructed-parent.cnf").read_bytes()
ls = raw.splitlines()
nv, nc = map(int, ls[0].split()[2:])
parent = [list(map(int, x.split()[:-1])) for x in ls[1:]]
assert (nv, nc) == (19533, 184335) and len(parent) == nc
summary = load("summary.json")
host = summary["sizes"]["host_clauses"]
frozen = summary["sizes"]["frozen_unit_clauses"]
blocks = load("clause-blocks.json")
counters = load("counters.json")
supports = load("support-selectors.json")
units = load("frozen-units.json")
alloc = load("allocations.json")
mcf = load("mcf-config.json")

# Every suffix clause is in exactly one contiguous, correctly hashed block.
pos = host + frozen + 1
for b in blocks:
    assert b["first_clause"] == pos
    cs = parent[pos - 1:b["last_clause"]]
    assert len(cs) == b["clause_count"]
    assert block_hash(cs) == b["sha256"]
    pos = b["last_clause"] + 1
assert pos == nc + 1

# Guard stripping gives each independently generated hard-counter hash, while
# the emitted hash covers the actual parent bytes, including every naive guard.
for c in counters:
    cs = parent[c["first_clause"] - 1:c["last_clause"]]
    assert block_hash(cs) == c["emitted_sha256"]
    assert [x["parent_clause"] for x in c["clauses"]] == list(range(c["first_clause"], c["last_clause"] + 1))
    assert len(c["clauses"]) == len(cs)
    if c["guard"] is not None:
        assert all(x and x[0] == -c["guard"] for x in cs)
        hard = [x[1:] for x in cs]
    else:
        hard = cs
    assert block_hash(hard) == c["hard_sha256"]

# Check actual selector implications directly against physical adjacency and
# the emitted support sets, then check each guarded main disjunction.
edge = {e: 4 * i + 1 for i, e in enumerate(combinations(range(58), 2))}
def lit(u, v, colour):
    return edge[min(u, v), max(u, v)] + colour

block_by_sender = {b["owner"]["sender"]: b for b in blocks
                   if b["kind"] == "guarded_support_family"}
by_sender = defaultdict(list)
for s in supports:
    by_sender[s["sender"]].append(s)
for sender, records in by_sender.items():
    b = block_by_sender[sender]
    assert b["guard"] == records[0]["guard"]
    must, cannot = set(b["must"]), set(b["cannot"])
    for s in records:
        possible = set(s["support"])
        expected = []
        for j in range(16):
            if j in must or j in cannot:
                continue
            v = lit(sender, 1 + j, 1)
            expected.append([-s["selector"], v if j in possible else -v])
        first = s["implication_first_parent_clause"]
        assert len(expected) == s["implication_count"]
        assert parent[first - 1:first - 1 + len(expected)] == expected
    main = b["main_disjunction_parent_clause"]
    assert parent[main - 1] == [-b["guard"], *[s["selector"] for s in records]]

# Frozen-unit manifest points to the exact signed parent unit in each position.
assert len(units) == frozen
for i, u in enumerate(units):
    assert u["clause"] == host + i + 1
    assert parent[u["clause"] - 1] == [u["literal"]]

# Allocation intervals are total and disjoint from 6613 through 19533.
pos = 6613
seen = set()
for a in alloc:
    assert a["first"] == pos
    vals = set(range(a["first"], a["last"] + 1))
    assert not vals & seen
    seen |= vals
    pos = a["last"] + 1
assert pos == nv + 1 and len(seen) == 12921

# The MCF variable set is disjoint from the actual non-host suffix, not merely
# from the separately traced list used to generate it.
modvars = {v for e in mcf["configurable"] for v in e["physical_variables"]}
assert len(mcf["configurable"]) == 126 and len(modvars) == 504
assert len(mcf["excluded_fixed"]) == 20
assert not any(abs(v) in modvars for c in parent[host:] for v in c)

result = {
    "status": "PASS",
    "parent_sha256": sha(raw),
    "working_sha256": sha((H / "inputs" / "working.cnf").read_bytes()),
    "rup_cas_prefix_sha256": sha((H / "inputs" / "cas.drat").read_bytes()),
    "strict_parent_clause_lines": nc,
    "contiguous_suffix_blocks_checked": len(blocks),
    "actual_counter_streams_checked": len(counters),
    "selector_implications_checked": sum(s["implication_count"] for s in supports),
    "selector_main_disjunctions_checked": len(by_sender),
    "frozen_unit_positions_checked": len(units),
    "fresh_allocated_variables_checked": len(seen),
    "mcf_disjoint_physical_variables_checked": len(modvars),
    "solver_queries": 0,
    "proof_checks": 0,
    "scope": "DIMACS/manifest consistency and encoding semantics only; no SAT/UNSAT or physical-row conclusion."
}
(R / "verification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
