#!/usr/bin/env python3
"""Finite audit of K58_two_site_consequences; no SAT/SLS search.

Usage: python3 checks/recompute.py PACKAGE DRAT_TRIM OUTPUT.json FRESH_M2_JSON
Reads only the supplied package and named receipts and writes one JSON receipt.
DRAT checker gate:
no -w, -i -U -t 300, rc=0, exactly one s VERIFIED, and no WARNING or ERROR.
"""
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

PKG = Path(sys.argv[1]).resolve()
DRAT = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
V = [0, *range(1, 16), *range(31, 45)]
EDGES = list(combinations(V, 2))
# Physical edge variables are 4*index + 1 + colour.
EOFF = {e: 4 * i + 1 for i, e in enumerate(combinations(range(58), 2))}
FOUR = [[39, 44], [40, 41], [40, 42], [40, 44]]
report = {"checks": 0, "word_tables": {}, "word_checks": 0,
          "owner_witness_checks": 0, "replays": []}


def check(condition, message):
    report["checks"] += 1
    if not condition:
        raise RuntimeError(message)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def gz(name):
    return gzip.decompress((PKG / name).read_bytes())


def get(name):
    return json.loads((PKG / name).read_bytes())


def edge(a, b, h):
    return EOFF[tuple(sorted((a, b)))] + h


def word_pins(word, edges=FOUR):
    return [edge(*e, int(k)) for e, k in zip(edges, word)]


def clauses(raw):
    return [tuple(map(int, line.split()[:-1])) for line in raw.splitlines()[1:]
            if line.strip()]


def header(raw):
    return list(map(int, raw.split(b"\n", 1)[0].split()[2:]))


def encode_clause(c):
    return (" ".join(map(str, c)) + (" " if c else "") + "0\n").encode()


def add(raw, new):
    h, body = raw.split(b"\n", 1)
    n, m = map(int, h.split()[2:])
    return f"p cnf {n} {m + len(new)}\n".encode() + body + b"".join(map(encode_clause, new))


def pin(raw, units):
    return add(raw, [[u] for u in units])


def cnf(n, cs):
    return f"p cnf {n} {len(cs)}\n".encode() + b"".join(map(encode_clause, cs))


def parent(i, seed):
    delta = json.loads(gz(f"owner-{i:02d}.delta.gz"))
    return delta["header"].encode() + b"\n" + seed.split(b"\n", 1)[1][:delta["prefix"]] + delta["tail"].encode()


def projection(raw, top):
    n = header(raw)[0]
    keep = {edge(*e, h) for e in EDGES for h in range(4)} | set(range(top + 1, n + 1))
    return [c for c in clauses(raw) if all(abs(l) in keep for l in c)]


# The package deliberately treats absent variables as false. This is its finite
# local-witness predicate, not a SAT assignment on all of K58.
def witness(raw, top, item, units, capped=True):
    word, aux = item
    check(len(word) == len(EDGES) and set(word) <= set("0123"), "word alphabet/length")
    check(all(top < l <= header(raw)[0] for l in aux), "auxiliary range")
    check(len({abs(l) for l in aux}) == len(aux), "duplicate auxiliary variable")
    model = {edge(*e, int(k)) for e, k in zip(EDGES, word)} | set(aux)
    yes = lambda l: (l in model) if l > 0 else (-l not in model)
    check(all(yes(l) for l in units), "local witness violates required pins")
    bad = [c for c in projection(raw, top) if not any(yes(l) for l in c)]
    check(not bad, f"local witness violates {len(bad)} projection clauses")
    degree = Counter((x, k) for e, k in zip(EDGES, word) for x in e)
    check((not capped) or max(degree.values()) <= 16, "local degree cap")
    return max(degree.values())


def replay(raw, meta, label, temporary):
    check(sha(raw) == meta["query"], f"query identity: {label}")
    proof = gz(meta["file"])
    check(sha(proof) + ".rup.gz" == meta["file"], f"proof content address: {label}")
    q, p = temporary / (label + ".cnf"), temporary / (label + ".proof")
    q.write_bytes(raw)
    p.write_bytes(proof)
    result = subprocess.run([DRAT, q, p, "-i", "-U", "-t", "300"], capture_output=True)
    text = (result.stdout + result.stderr).decode("latin-1")
    (temporary / (label + ".out")).write_text(text)
    normal = text.replace("\r\n", "\n").replace("\r", "\n")
    ok = (result.returncode == 0 and
          sum(line.strip() == "s VERIFIED" for line in normal.splitlines()) == 1 and
          "WARNING" not in normal.upper() and "ERROR" not in normal.upper() and
          "NOT VERIFIED" not in normal and "UNKNOWN" not in normal and "DERIVATION" not in normal and
          "0 RAT lemmas in core" in normal)
    check(ok, f"strict replay failed: {label}")
    q.unlink()
    p.unlink()
    report["replays"].append({"label": label, "query_sha256": sha(raw),
                             "proof_sha256": sha(proof), "proof_bytes": len(proof)})


seed = gz("signed-parent.cnf.gz")
row = gz("row-0.cnf.gz")
top = header(row)[0]
check(header(seed) == [19218, 178823], "signed-parent header")
check(sha(seed) == "ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931", "signed-parent digest")
check(sha(row) == "160f9fb6c60638443c50d79e4fcaa64e6cdb6460db32fc61406d269a938bec00", "row digest")
p, q = edge(31, 13, 0), edge(42, 13, 1)
check((p, q) == (2721, 2766), "trigger numbering")
check([edge(31, 42, h) for h in range(4)] == [5249, 5250, 5251, 5252], "pivot numbering")

# Actual negative clauses, not an unsigned approximation.
def graph_axioms(vertices):
    cs = set()
    for a, b in combinations(vertices, 2):
        ls = [edge(a, b, h) for h in range(4)]
        cs.add(tuple(ls))
        cs.update(tuple([-x, -y]) for x, y in combinations(ls, 2))
    for a, b, c in combinations(vertices, 3):
        for h in range(4):
            cs.add(tuple([-edge(a, b, h), -edge(a, c, h), -edge(b, c, h)]))
    return cs

axioms58 = graph_axioms(range(58))
seed_set = set(clauses(seed))
check(axioms58 <= seed_set, "full K58 axioms in signed parent")
report["k58"] = {"at_least_one": 1653, "at_most_one": 9918,
                 "monochromatic_triangles": 123424, "verified_in_parent": True}
for h, expected_hash in [(0, "f7e6f5b2cb5a95bf65c16c730f7c4e10bd359b3d413d031bcbf9dd180dd5ff8d"),
                         (3, "e85234ab42705601f1b83a2e6127ecb89dea669ba78865f35ea57e47815ece7a")]:
    branch = gz(f"branch-{h}.cnf.gz")
    check(sha(branch) == expected_hash, f"branch-{h} digest")
    check(set(clauses(seed)) <= set(clauses(branch)), f"branch-{h} strengthens parent")
    check(tuple([edge(31, 42, h)]) in clauses(branch), f"branch-{h} pivot")
    report[f"branch_{h}_clauses_beyond_seed"] = len(set(clauses(branch)) - seed_set)

# Every owner parent is a signed-parent/delta object; its owner guards are in
# that same signed parent. No claim that owner_cube is an ordinary-row unit.
statuses = Counter()
live, dead = [], []
minimal = {}
temporary = OUT.parent / "recompute-work"
temporary.mkdir(parents=True, exist_ok=True)
for i in range(47):
    tr, ev = get(f"transfer-{i:02d}.json"), get(f"events/{i:07}.json")["event"]
    raw = parent(i, seed)
    check(sha(raw) == tr["parent"] == ev["parent"]["query"] == ev["guard"]["representative"], f"parent {i}")
    check(tr["index"] == ev["guard"]["index"] == i and tr["pair"] == ev["guard"]["pair"], f"guard {i}")
    units = {c[0] for c in clauses(raw) if len(c) == 1}
    cube, gates = ev["guard"]["owner_cube"], ev["guard"]["owner_gates"]
    check(set(cube) <= units and set(gates) <= set(cube), f"owner guard units {i}")
    check(axioms58 <= set(clauses(raw)), f"K58 axioms in owner parent {i}")
    a = [edge(1, 42, 3), edge(4, 31, 0), edge(4, 42, 1)]
    g = edge(31, 42, 3)
    check(tr["pins"] == a + [-g], f"owner pin identity {i}")
    statuses[tr["status"]] += 1
    if tr["status"] == "LOCAL_COUNTEREXAMPLE":
        check(witness(raw, top, tr["witness"], tr["pins"]) <= 16, f"LOCAL {i}")
        report["owner_witness_checks"] += 1
    else:
        check(tr["status"] == "FORCED" and tr["proof"]["core"] == a + [-g], f"owner status/core {i}")
        replay(pin(raw, tr["proof"]["core"]), tr["proof"], f"owner-{i:02d}", temporary)
        if "antecedent_witness" in tr:
            live.append(i)
            check(witness(raw, top, tr["antecedent_witness"], a + [g]) <= 16, f"antecedent {i}")
            report["owner_witness_checks"] += 1
        else:
            dead.append(i)
            check(tr["impossible_antecedent"]["core"] == a, f"dead antecedent {i}")
            replay(pin(raw, tr["impossible_antecedent"]["core"]),
                   tr["impossible_antecedent"], f"antecedent-{i:02d}", temporary)
    sub_name = PKG / f"sub-{i:02d}.json"
    if sub_name.exists():
        minimum = {}
        for kind, items in get(sub_name.name).items():
            seen, closed_subsets, representatives = set(), set(), {}
            for item in items:
                pins_here = item["pins"]
                sub = tuple(pins_here[:-1] if kind == "force" else pins_here)
                check(set(sub) <= set(a) and (kind == "dead" or pins_here[-1] == -g), f"sub pins {i}/{kind}")
                seen.add(sub)
                if item["status"] == "LOCAL":
                    check(witness(raw, top, item["witness"], item["pins"]) <= 16, f"sub model {i}/{kind}")
                    report["owner_witness_checks"] += 1
                else:
                    check(item["status"] == "CLOSED" and item["proof"]["core"] == pins_here, f"sub proof identity {i}/{kind}")
                    closed_subsets.add(sub)
                    representatives[sub] = item
            every = [tuple(c) for j in range(4) for c in combinations(a, j)]
            check(all(s in seen or any(set(t) <= set(s) for t in closed_subsets) for s in every), f"complete subset lattice {i}/{kind}")
            if kind == "force":
                minimum[kind] = [s for s in closed_subsets if not any(set(t) < set(s) for t in closed_subsets)]
                for sub in minimum[kind]:
                    item = representatives[sub]
                    replay(pin(raw, item["proof"]["core"]), item["proof"],
                           f"minimal-{i:02d}-" + "-".join(map(str, sub)), temporary)
            elif kind == "dead":
                minimum[kind] = [s for s in closed_subsets if not any(set(t) < set(s) for t in closed_subsets)]
        minimal[i] = minimum

check(statuses == {"FORCED": 14, "LOCAL_COUNTEREXAMPLE": 33}, "owner status totals")
check(live == [0, 3, 5, 7, 11, 12, 19, 23, 24, 25, 32], "live forcing indices")
check(dead == [14, 31, 36], "impossible-antecedent indices")
check(report["owner_witness_checks"] == 157, "total owner local witnesses")
two_site = [i for i in live if sorted(minimal[i]["force"]) == [tuple(sorted((a[0], a[2])))]]
check(two_site == [3, 5, 7, 19, 23, 32], "six live two-site minimums")
three_site = [i for i in live if i not in two_site]
check(all(sorted(minimal[i]["force"]) == [tuple(a)] for i in three_site), "all-three-pin live minimums")
check(all(sorted(minimal[i]["dead"]) == [tuple(a)] for i in dead), "minimal impossible antecedents")
report["owners"] = {"status": dict(statuses), "live": live, "dead": dead,
                    "two_site_live": two_site, "three_site_live": three_site, "local_witnesses_checked": 157}

with (PKG / "SHA256SUMS").open() as stream:
    manifest = [line.split() for line in stream if line.strip()]
check(len(manifest) == 444, "manifest entries")
check(all(sha((PKG / name).read_bytes()) == digest for digest, name in manifest), "all 444 manifest digests")
report["manifest_entries_passed"] = 444

# Independently evaluate all eight witness/cover tables and their exact bases.
table_keys = {}
maxima = []
for h in (0, 3):
    for cond in ("free", "left", "right", "both"):
        name = f"signature-{h}.json" if cond == "both" else f"control-{cond}-{h}.json"
        rec = get(name)
        trigger = {"free": [], "left": [p], "right": [q], "both": [p, q]}[cond]
        check(rec["trigger"] == trigger and rec["edges"] == FOUR and rec["color"] == h, f"metadata {name}")
        check(rec["complete"] is True and set(rec["words"]) == set(rec["all_projected"]), f"table keys {name}")
        base = pin(pin(seed, [edge(31, 42, h)]), trigger)
        check(sha(base) == rec["formula"], f"base formula {name}")
        for word, item in rec["words"].items():
            maxima.append(witness(base, top, item, word_pins(word) + trigger + [edge(31, 42, h)]))
            report["word_checks"] += 1
        blocks = [[-l for l in word_pins(word)] for word in sorted(rec["words"])]
        blocked = add(base, blocks)
        replay(blocked, rec["proof"], f"cover-{h}-{cond}", temporary)
        table_keys[h, cond] = set(rec["words"])
        report["word_tables"][f"{h}-{cond}"] = len(rec["words"])
        if cond == "both":
            report[f"projection_{h}_clauses"] = len(projection(base, top))
            check(report[f"projection_{h}_clauses"] == 24686, f"complete projection {h}")

for h, n in [(0, 57), (3, 36)]:
    check(table_keys[h, "free"] == table_keys[h, "left"] == table_keys[h, "right"], f"single-trigger tables {h}")
    check(len(table_keys[h, "free"]) == n, f"untriggered table size {h}")
check(len(table_keys[0, "free"] & table_keys[3, "free"]) == 29, "overlap without both triggers")
check(len(table_keys[0, "both"] & table_keys[3, "both"]) == 0, "disjoint both-trigger tables")
check(max(maxima) <= 16, "word maximum monochromatic degree")
report["word_numeric_claims"] = {"untriggered": [57, 36], "untriggered_overlap": 29,
                                  "both": [8, 28], "both_overlap": 0,
                                  "models_checked": report["word_checks"], "max_degree": max(maxima)}

expected_closed = {0: ["1113"], 3: sorted(["0133", "1013", "1133", "1333", "3010", "3031", "3101", "3103", "3111", "3133", "3301"])}
closed, opened = {}, {}
for h in (0, 3):
    closed[h], opened[h] = [], []
    for word in sorted(table_keys[h, "both"]):
        rec = get(f"search-{h}-{word}.json")
        wps = word_pins(word)
        query = pin(seed, [edge(31, 42, h), p, q] + wps)
        check(rec["pins"] == [p, q] + wps and sha(query) == rec["query"], f"search identity {h}-{word}")
        if rec["status"] == "CLOSED":
            closed[h].append(word)
            lift = get(f"lift-{h}-{word}.json")["unsplit"]
            check(lift["core"] == [p, q] + wps, f"pivot-free unsplit core {h}-{word}")
            check(sha(pin(seed, lift["core"])) == lift["query"], f"unsplit identity {h}-{word}")
        else:
            check(rec["status"] == "OPEN" and not ({"file", "proof"} & set(rec)), f"OPEN not SAT {h}-{word}")
            opened[h].append(word)
    check(closed[h] == expected_closed[h], f"named closed list {h}")
report["closed"] = {str(h): closed[h] for h in (0, 3)}
report["open"] = {str(h): opened[h] for h in (0, 3)}

frontier = get("conditional-frontier.json")
check(frontier["trigger"] == [p, q] and frontier["edges"] == FOUR, "frontier metadata")
all_open = []
for branch in frontier["branches"]:
    h = branch["color"]
    check(branch["words"] == opened[h], f"frontier branch list {h}")
    all_open += branch["words"]
    base = pin(pin(seed, [edge(31, 42, h)]), [p, q])
    blocked = add(base, [[-l for l in word_pins(w)] for w in opened[h]])
    replay(blocked, branch, f"frontier-{h}", temporary)
check(sorted(set(all_open)) == sorted(all_open) == frontier["all"], "24 distinct residual words")
check(len(all_open) == 24, "frontier length")
blocked = add(pin(seed, [p, q]), [[-l for l in word_pins(w)] for w in frontier["all"]])
replay(blocked, frontier["unsplit"], "frontier-unsplit", temporary)
report["frontier"] = {"all": frontier["all"], "branch_open": {str(h): opened[h] for h in (0, 3)},
                      "unsplit_query_sha256": sha(blocked)}

# Compare to the fresh, separately written m2 runner receipts: this is an
# independent receipt-consistency check, not a substitute for the 24 replays.
fresh_path = Path(sys.argv[4]).resolve()
fresh = json.loads(fresh_path.read_text())
check(sum(len(closed[h]) for h in (0, 3)) == 12 and len(fresh["words"]) == 12, "fresh m2 case count")
for (label, data) in fresh["words"].items():
    for scope in ("search", "unsplit"):
        item = data[scope]
        check(item["ok"] and item["rc"] == 0 and item["warnings"] == 0 and item["proof_fully_read"], f"fresh m2 {label}/{scope}")
report["fresh_m2_closures"] = {"cases": 12, "search_ok": 12, "unsplit_ok": 12, "checks": len(fresh["checks"])}
report["result"] = "PASS"
OUT.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ("replays",)}, indent=1))
print("strict new replays", len(report["replays"]))
