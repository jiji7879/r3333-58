#!/usr/bin/env python3
"""Reconstruct all 91 spoke-rule queries and compare complete strict receipts.

Usage: independent_replay_audit.py PACKAGE STRICT_DIR OUTPUT.json [OLD_PACKAGE]
This is independent of replay.py. It imports only the audited pure proof
remapper and frozen metadata helper (bindings). No solver or new SAT search.
"""
import csv
import gzip
import hashlib
import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path

P, D, OUTPUT = map(Path, sys.argv[1:4])
OLD = Path(sys.argv[4]).resolve() if len(sys.argv) > 4 else None
P, D = P.resolve(), D.resolve()
sys.path.insert(0, str(P))
from transport import remap
from placements import bindings

sha = lambda x: hashlib.sha256(x).hexdigest()
expected = {}


def require(c, msg):
    if not c:
        raise RuntimeError(msg)


def read(name):
    return json.loads((P / name).read_bytes())


def gz(name):
    return gzip.decompress((P / name).read_bytes())


def add(raw, clauses):
    head, body = raw.split(b"\n", 1)
    n, m = map(int, head.split()[2:])
    return f"p cnf {n} {m + len(clauses)}\n".encode() + body + b"".join(
        (" ".join(map(str, c)) + (" " if c else "") + "0\n").encode() for c in clauses)


def units(raw, lits):
    return add(raw, [[l] for l in lits])


def offer(label, raw, record, proof=None):
    require(sha(raw) == record["query"], f"query mismatch {label}")
    if proof is None:
        proof = gz("proofs/" + record["proof"])
    require(sha(proof) == record["proof"].split(".")[0], f"proof mismatch {label}")
    require(label not in expected, f"duplicate label {label}")
    expected[label] = {"query": sha(raw), "proof": sha(proof), "proof_bytes": len(proof)}


# Manifest and ordinary/parent identities.
manifest = [line.split() for line in (P / "SHA256SUMS").read_text().splitlines() if line.strip()]
require(len(manifest) == 150 and all(sha((P / name).read_bytes()) == digest
                                    for digest, name in manifest), "manifest mismatch")
require(len([x for x in P.rglob("*") if x.is_file()]) == 151, "archive file count")
parent = gz("parents/0.cnf.gz")
require(sha(parent) == "ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931", "case0 parent")

E58 = list(itertools.combinations(range(58), 2))
OFF = {e: 4*i+1 for i, e in enumerate(E58)}
edge = lambda a, b, h: OFF[tuple(sorted((a, b)))] + h
ARM = list(itertools.combinations(range(31, 45), 2))
arm_pins = lambda s: [edge(*e, int(k)) for e, k in zip(ARM, s)]

# Physical representatives and canonical forced-edge proofs.
for i, r in enumerate(read("examples.json")):
    raw = gz(f"parents/{r['index']}.cnf.gz")
    require(sha(raw) == r["parent"], f"example parent {r['index']}")
    pins = [edge(r["x"], r["u"], r["alpha"]), edge(r["x"], r["v"], r["beta"])]
    offer(f"physical-{r['index']}", units(raw, pins), r)

rules = read("canonical/rules.json")
example_classes = {(r["n"], tuple(r["pair"])) for r in read("examples.json")}
required_classes = {(r["n"], tuple(r["pair"])) for r in rules}
require(len(rules) == 6 and len(required_classes) == 6, "six canonical classes")
require(len(read("examples.json")) == 8 and required_classes <= example_classes,
        "eight examples cover all six classes")
for r in rules:
    raw = gz("canonical/" + r["base"] + ".cnf.gz")
    require(sha(raw) == r["base"], "canonical base")
    require(r["goal"] == 1 + 3*list(itertools.combinations(range(r["n"]), 2)).index((4, r["n"]-3)),
            "canonical local goal literal")
    offer(f"canonical-{r['n']}-{r['pair'][0]}-{r['pair'][1]}", units(raw, [-r["goal"]]), r)
    previous = json.loads(gz("canonical/" + str(r["n"]) + "-" + "-".join(r["pair"]) + ".json.gz"))
    require(all([4, r["n"]-3, k] in previous["root"]["forbidden"] for k in [1, 2]),
            "inherited color exclusions on canonical local a-v")

# Both pivot-elimininations carried from the case-0 event.
event = read("case0/event.json")
require(event["parent"]["query"] == sha(parent) and event["pivot"] == [31, 42], "case0 event identity")
for child in event["children"]:
    h = child["color"]
    require(child["literal"] == edge(31, 42, h), "pivot child literal")
    if h in [1, 2]:
        require(child["status"] == "CLOSED", "actual eliminated pivot")
        offer(f"pivot-{h}", units(parent, [child["literal"]]),
              {"query": child["query"], "proof": child["proof"] + ".rup.gz"})
    else:
        require(h in [0, 3] and child["status"] == "OPEN_UNKNOWN", "unconditional branches remain open")

# Owner identity on the original 983,774-entry roster, retained as a boundary.
rr, roster, arms, labels = bindings()
require(len(roster) == 11585 and sum(int(q["live_end_exclusive"]) - int(q["live_begin"])
                                      for q in roster.values()) == 983774, "frozen roster size")
def owner_at(index, row):
    q = roster[row]
    assert int(q["live_begin"]) <= index < int(q["live_end_exclusive"])
    rank = int(q["live_ranks"].split(",")[index - int(q["live_begin"])])
    return labels[int(q["arm"])][rank]

# Transferred cores and their regenerated proofs on actual recipient formulas.
maps = sum([read(f"hard-maps-{h}.json") for h in [36, 40]], [])
by_index = {m["index"]: m for m in maps}
transfers = read("transfers.json")
require(len(maps) == len(by_index) == len(transfers) == 53, "transfer census")
require(sum(m["donor"] == 36 for m in maps) == 26 and sum(m["donor"] == 40 for m in maps) == 27,
        "26/27 core splits incl. the donors")
rows = {r["row"] for r in transfers}
require(len(rows) == 27, "27 distinct recipient walls")
by_core = {h: (read(f"canonical/core-{h}.json"), gz("proofs/" + read(f"canonical/core-{h}.json")["proof"]))
           for h in [36, 40]}
transfer_rows = []
for r in transfers:
    m = by_index[r["index"]]
    require((m["index"], m["row"], m["donor"]) == (r["index"], r["row"], r["donor"]), "map/recipient binding")
    require(owner_at(r["index"], r["row"]) == owner_at(r["donor"], event["guard"]["row"]),
            "donor/recipient owner pair")
    raw_delta = gz(f"parents/hard-{r['index']}.delta.gz")
    head, tail = raw_delta.split(b"\n", 1)
    raw = head + b"\n" + parent.split(b"\n", 1)[1][:r["parent_common_bytes"]] + tail
    require(sha(raw) == r["parent"], "recipient parent reconstruction")
    core, source = by_core[m["donor"]]
    pins, trace = remap(core, source, m, int(head.split()[2]) - (19218 - 18387))
    require(pins == r["pins"] == [edge(r["x"], r["u"], r["colors"][0]),
                                   edge(r["x"], r["v"], r["colors"][1])], "transfer pin semantics")
    offer(f"transfer-{r['index']}", units(raw, pins), r, trace)
    transfer_rows.append({"index": r["index"], "donor": r["donor"], "row": r["row"],
                          "parent_sha256": sha(raw), "clause_literals": [-l for l in pins]})

# The direct case-0 cube refutations use no trigger units and no pure_query ad-hoc base.
exclusions = read("case0/exclusions.json")
require(len(exclusions) == 20 and all(r["cut"] is False for r in exclusions), "20 direct final cubes")
for r in exclusions:
    offer(f"case0-exclusion-{r['i']}", units(parent, r["pins"]), r)
pin_lengths = dict(sorted(Counter(len(r["pins"]) for r in exclusions).items()))
require(pin_lengths == {13: 1, 14: 4, 15: 3, 16: 1, 82: 11}, "actual 13-16/82-pin cube sizes")
arm_frontier = {}
arm_total = 0
for h in [0, 3]:
    record = read(f"case0/arm-{h}.json")
    models = record["models"]
    require(record["complete"] and len(models) == len(set(models)), f"pivot {h} complete unique arms")
    cover = read(f"case0/arm-cover-{h}.json")
    require(cover["ids"] == list(range(len(models))), f"pivot {h} arm cover identities")
    base = units(parent, [edge(31, 42, h)])
    offer(f"arm-cover-{h}", add(base, [[-l for l in arm_pins(s)] for s in models]), cover["proof"])
    closed, open_arms = {}, []
    for i, model in enumerate(models):
        require(len(model) == 91 and set(map(int, model)) <= set(event["guard"]["palette"]), "arm type")
        colour = dict(zip(ARM, map(int, model)))
        require(colour[31, 42] == h, "arm pivot")
        require(all(not colour[a,b] == colour[b,c] == colour[a,c]
                    for a,b,c in itertools.combinations(range(31,45), 3)), "triangle-free arm")
        pins = set(arm_pins(model))
        hits = [r["i"] for r in exclusions if set(r["pins"]) <= pins]
        if hits:
            closed[str(i)] = hits
        else:
            open_arms.append(i)
    actual = read("case0/frontier.json")[str(h)]
    require(actual == {"closed": closed, "open": open_arms}, "arm frontier recomputation")
    arm_frontier[str(h)] = {"arm_colours": len(models), "excluded": len(closed), "open": len(open_arms)}
    survivors = {''.join(model[list(ARM).index(tuple(sorted(e))) ]
                         for e in [[39,44],[40,41],[40,42],[40,44]])
                 for i, model in enumerate(models) if i in open_arms}
    arm_frontier[str(h)]["surviving_word_groups"] = len(survivors)
    if OLD is not None:
        previous = json.loads((OLD / f"control-free-{h}.json").read_bytes())
        require(previous["edges"] == [[39,44],[40,41],[40,42],[40,44]], "old word edges")
        require(set(previous["words"]) == survivors, "all earlier unguarded word groups survive")
    arm_total += len(models)
require(arm_frontier == {"0": {"arm_colours": 1417, "excluded": 0, "open": 1417, "surviving_word_groups": 57},
                          "3": {"arm_colours": 345, "excluded": 20, "open": 325, "surviving_word_groups": 36}},
        "case0 frontier and word-group numbers")

# Regenerated placement supply is deterministic; each clause is scoped to its own owner.
text = "".join(__import__("placements").formatted())
table = list(csv.DictReader(text.splitlines(), delimiter="\t"))
require(len(table) == 9288 and len({int(r["index"]) for r in table}) == 6617 and
        len({r["row"] for r in table}) == 6489, "catalogue census")
require(len({(int(r["index"]), int(r["literal_1"]), int(r["literal_2"])) for r in table}) == 9288,
        "distinct representative/clause pairs")
for r in read("examples.json"):
    require((r["index"], -edge(r["x"],r["u"],r["alpha"]), -edge(r["x"],r["v"],r["beta"]))
            in {(int(x["index"]), int(x["literal_1"]), int(x["literal_2"])) for x in table}, "example in catalogue")

# Exact comparison to the strict proxy's independent raw output.
actual = [json.loads(s) for s in (D / "strict-receipts.jsonl").read_text().splitlines() if s.strip()]
expected_map = Counter((x["query"], x["proof"]) for x in expected.values())
actual_map = Counter((x["query_sha256"], x["proof_sha256"]) for x in actual)
require(expected_map == actual_map, "native receipt set differs from independently reconstructed set")
require(len(expected) == len(actual) == 91 and all(x["accepted"] and x["exit"] == 0 for x in actual),
        "91 strict query checks")
proof_specs = {(x["query"], x["proof"]): x["proof_bytes"] for x in expected.values()}
outer = []
for path in sorted((D / "strict-logs").glob("*.json")):
    receipt = json.loads(path.read_text())
    text_out = path.with_suffix(".out").read_bytes().decode("latin1")
    normal = text_out.replace("\r\n", "\n").replace("\r", "\n")
    reads = [int(m.group(1)) for m in re.finditer(r"read (\d+) bytes from proof file", normal)]
    expected_read = proof_specs[(receipt["query_sha256"], receipt["proof_sha256"])]
    require(reads == [expected_read], "full proof not read")
    require([l for l in normal.splitlines() if l.startswith("s ")] == ["s VERIFIED"], "exact status")
    require("WARNING" not in normal.upper() and "ERROR" not in normal.upper(), "checker warning/error")
    require("0 RAT lemmas in core" in normal, "RUP-only core")
    outer.append({"query": receipt["query_sha256"], "proof": receipt["proof_sha256"],
                  "proof_bytes": expected_read, "seconds": receipt["seconds"]})
require(len(outer) == 91, "output log count")

out = {"result": "PASS", "archive_manifest_checks": 150,
       "strict_calls": len(outer), "strict_checker_seconds": sum(x["seconds"] for x in outer),
       "categories": {"canonical": 6, "physical_examples": 8, "transfers": 53,
                       "pivot_eliminations": 2, "arm_covers": 2, "case0_cubes": 20},
       "transfers": {"total": 53, "donor_36": 26, "donor_40": 27, "distinct_wall_rows": 27,
                     "geometry": "conditional binary clause per specifically named signed parent"},
       "catalogue": {"distinct_representative_clause_pairs": 9288, "representatives": 6617,
                      "wall_rows": 6489, "rule_classes": 6, "eight_examples_cover_all_six_classes": True,
                      "full_physical_examples_replayed": 8,
                      "not_a_9288_proof_sweep": True},
       "case0": {"exclusion_cube_sizes": pin_lengths, "cubes_without_trigger_pins": 20,
                  "arm_assignments": arm_total, "frontier": arm_frontier},
       "explicitly_not_derived": ["full K58 SAT/UNSAT", "a representative or wall-row closure",
                                   "general new two-site theorem", "Ramsey bound change"],
       "native_records": outer, "transferred_clauses": transfer_rows}
OUTPUT.write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k not in ["native_records", "transferred_clauses"]}, indent=1))
