#!/usr/bin/env python3
"""Independent DAG and proof-identity audit for the 24-pattern package.

No use of the bundled replay.py is made. This reconstructs all query formulas,
expected case constituents and proof/hash links, checks both old predecessor
proof bytes, and compares the complete expected receipt set against the
strict no-warning proxy execution. It launches no SAT/SLS search.

Usage: independent_audit.py NEW_PACKAGE OLD_PACKAGE STRICT_RECEIPTS OUTPUT.json
"""
import gzip
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

NEW, OLD, RECEIPTS, OUTPUT = map(Path, sys.argv[1:])
new = json.loads((NEW / "frontier.json").read_text())
parent = gzip.decompress((NEW / "signed-parent.cnf.gz").read_bytes())
old_parent = gzip.decompress((OLD / "signed-parent.cnf.gz").read_bytes())
receipt_rows = [json.loads(line) for line in RECEIPTS.read_text().splitlines() if line.strip()]
receipt_map = Counter((r["query_sha256"], r["proof_sha256"], r["accepted"], r["exit"])
                      for r in receipt_rows)
used_receipts = []
receipts = []
checks = 0


def check(condition, label):
    global checks
    checks += 1
    if not condition:
        raise RuntimeError(label)


def sha(x):
    return hashlib.sha256(x).hexdigest()


def header(raw):
    return list(map(int, raw.split(b"\n", 1)[0].split()[2:]))


def clauses(raw):
    return [tuple(map(int, line.split()[:-1])) for line in raw.splitlines()[1:]
            if line.strip()]


def append(raw, extra):
    h, body = raw.split(b"\n", 1)
    n, m = map(int, h.split()[2:])
    text = b"".join((" ".join(map(str, c)) + (" " if c else "") + "0\n").encode()
                    for c in extra)
    return f"p cnf {n} {m + len(extra)}\n".encode() + body + text


def pin(raw, literals):
    return append(raw, [[l] for l in literals])


E58 = list(combinations(range(58), 2))
OFF = {e: 4 * i + 1 for i, e in enumerate(E58)}
ARM_EDGES = list(combinations(range(31, 45), 2))


def edge(a, b, colour):
    return OFF[tuple(sorted((a, b)))] + colour


def signature(word):
    return [edge(*e, int(k)) for e, k in zip(new["signature_edges"], word)]


def arm(model):
    return [edge(*e, int(k)) for e, k in zip(ARM_EDGES, model)]


def register(label, raw, record):
    check(sha(raw) == record["query"], "query identity: " + label)
    filename = record["proof"] + ".rup"
    proof = (NEW / "proofs" / filename).read_bytes()
    check(sha(proof) == record["proof"], "proof content address: " + label)
    check(receipt_map[(record["query"], record["proof"], True, 0)] > 0,
          "missing successful strict receipt: " + label)
    check((record["query"], record["proof"]) not in {(q, p) for q, p, _ in receipts},
          "duplicate case receipt: " + label)
    receipts.append((record["query"], record["proof"], label))
    used_receipts.append({"label": label, "query_sha256": sha(raw),
                          "proof_sha256": record["proof"], "proof_bytes": len(proof)})


check(sha(parent) == new["parent"], "parent header")
check(parent == old_parent, "previous full parent byte identity")
check(header(parent) == [19218, 178823], "parent dimensions")
manifest = [line.split() for line in (NEW / "SHA256SUMS").read_text().splitlines()
            if line.strip()]
check(len(manifest) == 244, "manifest entries")
check(all(sha((NEW / name).read_bytes()) == digest for digest, name in manifest),
      "all manifest hashes")
check(len(list(NEW.rglob("proofs/*.rup"))) == 236, "proof file count")

# The entire K58 graph constraint core, not just its physical at-least-one clause.
parent_clauses = set(clauses(parent))
graph_core = set()
for a, b in E58:
    ls = [edge(a, b, h) for h in range(4)]
    graph_core.add(tuple(ls))
    graph_core.update((-x, -y) for x, y in combinations(ls, 2))
for a, b, c in combinations(range(58), 3):
    for h in range(4):
        graph_core.add((-edge(a, b, h), -edge(a, c, h), -edge(b, c, h)))
check(len(graph_core) == 1653 + 9918 + 123424, "K58 core cardinality")
check(graph_core <= parent_clauses, "parent contains entire K58 core")
check(new["trigger"] == [edge(31, 13, 0), edge(42, 13, 1)] == [2721, 2766],
      "literal site/polarity of each trigger")
pivot_vars = [edge(31, 42, h) for h in range(4)]
check(pivot_vars == [5249, 5250, 5251, 5252], "pivot literal mapping")
check(tuple(pivot_vars) in parent_clauses, "pivot at-least-one is in parent")
check(all(tuple([-a, -b]) in parent_clauses
          for a, b in combinations(pivot_vars, 2)), "pivot at-most-one clauses")

previous = new["previous"]
check(previous["edges"] == new["signature_edges"] ==
      [[39, 44], [40, 41], [40, 42], [40, 44]], "four signature edges")
event = json.loads((NEW / "event.json").read_text())["event"]
check(event["parent"]["query"] == sha(parent) and event["pivot"] == [31, 42],
      "event parent and pivot")
check(event["variables"] == pivot_vars, "event variable group")
closed = {c["color"]: c for c in event["children"] if c["status"] == "CLOSED"}
check(set(closed) == {1, 2}, "actually eliminated pivot colours")
for hs, record in previous["eliminated_colors"].items():
    h = int(hs)
    check(h in {1, 2} and record["proof"] == closed[h]["proof"] and
          record["query"] == closed[h]["query"], "pivot elimination metadata")
    register(f"previous-eliminated-{h}", pin(parent, [pivot_vars[h]]), record)

pattern_words = {h: [] for h in (0, 3)}
for r in new["patterns"]:
    check(r["color"] in {0, 3}, "remaining pivot values only")
    pattern_words[r["color"]].append(r["word"])
check(all(ws == sorted(ws) for ws in pattern_words.values()), "word order")
previous_branch_proofs_match = []
for branch in previous["branches"]:
    h = branch["color"]
    check(h in {0, 3}, "previous branch pivot")
    check(branch["words"] == pattern_words[h], "branch equals new word partition")
    base = pin(pin(parent, [pivot_vars[h]]), new["trigger"])
    blocked = [[-l for l in signature(w)] for w in branch["words"]]
    register(f"previous-word-cover-{h}", append(base, blocked), branch)
    prior = json.loads((OLD / "conditional-frontier.json").read_text())
    old_branch = next(x for x in prior["branches"] if x["color"] == h)
    old_proof = gzip.decompress((OLD / old_branch["file"]).read_bytes())
    check(old_branch["words"] == branch["words"] and
          old_branch["query"] == branch["query"] and
          sha(old_proof) == branch["proof"] and
          old_proof == (NEW / "proofs" / (branch["proof"] + ".rup")).read_bytes(),
          f"predecessor branch {h} bytes and word scope")
    previous_branch_proofs_match.append(h)

check(sorted(pattern_words[0] + pattern_words[3]) == previous["all"] ==
      json.loads((OLD / "conditional-frontier.json").read_text())["all"],
      "exact earlier OPEN 24-word set")
blocked = [[-l for l in signature(w)] for w in previous["all"]]
register("previous-unsplit-24-word-cover",
         append(pin(parent, new["trigger"]), blocked), previous["unsplit"])
old_unsplit = json.loads((OLD / "conditional-frontier.json").read_text())["unsplit"]
check(old_unsplit["query"] == previous["unsplit"]["query"] and
      sha(gzip.decompress((OLD / old_unsplit["file"]).read_bytes())) == previous["unsplit"]["proof"],
      "old unsplit bridge")

# Check every new word, its exhaustive arm-cover, and each terminal leaf.
# Since all arms are CLOSED here, forced_groups/tree are deliberately absent:
# no disjunction guard can accidentally be promoted to a set of unit clauses.
status_counts = Counter()
leaf_types = Counter()
arm_count_by_pivot = Counter()
direct_words = []
for r in new["patterns"]:
    h, word = r["color"], r["word"]
    status_counts[r["status"]] += 1
    base = pin(parent, [pivot_vars[h], *new["trigger"], *signature(word)])
    models = r["arm_colorings"]
    arm_count_by_pivot[h] += len(models)
    check(len(models) == len(set(models)), "distinct arm models")
    for model in models:
        check(len(model) == len(ARM_EDGES) == 91 and set(model) <= set("0123"),
              "well-typed complete arm assignment")
        lits = arm(model)
        check(len(lits) == 91 and all(abs(l) <= 6612 for l in lits),
              "physical arm literals")
    blocks = [[-l for l in arm(model)] for model in models]
    register(f"arm-cover-{h}-{word}", append(base, blocks), r["arm_cover"])
    if r["status"] == "CLOSED_DIRECT":
        direct_words.append((h, word))
        leaf_types["direct"] += 1
        register(f"direct-{h}-{word}", base, r["closure"])
        continue
    check(r["status"] == "REFINED", "known pattern status")
    check(len(models) == len(r["arms"]), "every recorded arm has an alternative")
    for i, (model, cell) in enumerate(zip(models, r["arms"])):
        check(cell["status"] == "CLOSED", "terminal arm is a refutation")
        check(not cell.get("forced_groups") and not cell.get("forced"),
              "no unsupported grouped unit promotion")
        check(cell.get("tree") in ({}, None), "no hidden residual split")
        register(f"arm-{h}-{word}-{i}", pin(base, arm(model)), cell)
        leaf_types["arm"] += 1

check(status_counts == {"REFINED": 20, "CLOSED_DIRECT": 4}, "word status counts")
check(arm_count_by_pivot == {0: 69, 3: 148}, "217 arm alternatives")
check(leaf_types == {"arm": 203, "direct": 4}, "terminal counts")
check(new["open_patterns"] == [], "no claimed residual cases")
check(len(receipts) == 236, "complete reconstructed receipt count")
check(len({r[1] for r in receipts}) == 236, "every receipt references a unique proof")
check({r[1] + ".rup" for r in receipts} ==
      {p.name for p in (NEW / "proofs").glob("*.rup")}, "every proof used, none missing/orphaned")
expected_map = Counter((q, p, True, 0) for q, p, _ in receipts)
check(expected_map == receipt_map, "strict receipts exactly match all expected cases")

# Propositional case-combination. A block-cover of every assignment exhausts
# all possibilities because the parent's ALO/AMO clauses make each edge's
# colour unique. For each fixed pivot/witness word the exhaustive arm cover
# therefore gives an actual disjunction, and each disjunct is refuted on the
# full parent. The previous pivot 1/2 refutations and two word covers complete
# the remaining cases. Hence P AND trigger is unsatisfiable, equivalently the
# parent entails [-2721,-2766]. This is an entailment, not a full parent UNSAT
# result nor a production transfer to other owners.
clauses_export = new["conditional_clauses"]
check(clauses_export == [[-2721, -2766]], "the one scoped binary clause")
check((NEW / "conditional-clauses.cnf").read_text() == "p cnf 19218 1\n-2721 -2766 0\n",
      "exported CNF byte identity")
check((NEW / "open-leaves.tsv").read_text().splitlines() ==
      ["representative\tpivot_color\tword\tarm_index\tarm_91_colors\ttrigger_and_pivot_literals\tforced_and_split_literals"],
      "open-leaf table header only")

out = {
    "result": "PASS",
    "checks": checks,
    "parent_sha256": sha(parent),
    "parent_matches_previous_audited_parent": True,
    "archive_files_and_proofs": {"manifest_ok": 244, "total_files": 245, "proof_files": 236},
    "all_proof_queries_reconstructed": True,
    "strict_receipts_match_complete_expected_DAG": True,
    "strict_proof_calls": len(used_receipts),
    "strict_checker_seconds": sum(r["seconds"] for r in receipt_rows),
    "physical_literals": {"trigger": [2721, 2766], "pivot": pivot_vars},
    "eliminated_pivot_colours": [1, 2],
    "word_partition": {str(h): pattern_words[h] for h in (0, 3)},
    "same_previous_open_words": True,
    "previous_cover_proofs_match_byte_for_byte": previous_branch_proofs_match,
    "previous_unsplit_query_sha256": previous["unsplit"]["query"],
    "previous_unsplit_proof_matches": True,
    "arm_alternatives": dict(arm_count_by_pivot),
    "arm_cover_proofs": 24,
    "direct_word_refutations": direct_words,
    "arm_refutations": leaf_types["arm"],
    "active_forced_groups_or_splits": 0,
    "remaining_open_cases": [],
    "clause": [-2721, -2766],
    "derived_entailment": "On this one full signed parent: NOT both E[31,13]=0 and E[42,13]=1.",
    "not_derived": ["full K58 unsatisfiability or SAT", "either unconditional pivot branch closed",
                     "representative 0 fully excluded", "transfer to other owners/wall rows",
                     "any Ramsey bound change"],
    "receipts": used_receipts,
}
OUTPUT.write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "receipts"}, indent=1))
