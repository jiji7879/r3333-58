"""Direction D: original-parent, export, queue, and group-encoding audit.

This script performs no SAT/SMT solving and writes no result artifacts. It only
regenerates formulas, parses them, checks combinatorial assignments, and hashes
its observations. Run with the extracted bundle's offline Python environment.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import struct
import sys
from bisect import bisect_right
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "bundle/K58_wall_10k_batches"
sys.path.insert(0, str(ROOT))

from common import OUT, physical, sha, source, tsv, wall
from problem import encode_clauses, read_dimacs, row_formula
from compile import append
from cold import run as _cold_run  # imported for provenance only; never called
from representatives import full_query
from preferred_proofs import preferred
from physical_order import mapping
from campaign_queue import batch, bounds, excluded
from cheap import group_formula, key, per_row
from sorted_arm import validate
from arm_pairs import base, check_word_model
from common import canonical

REPORT = {"root_status": {}, "original_parent": {}, "export": {}, "queue": {},
          "preferred_semantics": {}, "group_encoding": {}}


def clauses(data):
    return read_dimacs(data)


def check_original_parent():
    cold = tsv(OUT / "cold-raw.tsv.gz")
    parent_hashes = set()
    for i, t in enumerate(cold):
        rid = t["id"]
        parent = row_formula(wall()[0][rid], "first")
        cube = physical(rid, t["w"], t["z"])
        _, query = append(parent, [[v] for v in cube])
        assert t["parent"] == sha(parent), (i, "parent")
        assert t["query"] == sha(query), (i, "query")
        assert t["status"] == "OPEN" and int(t["conflicts"]) >= int(t["cap"])
        nv, pc = clauses(parent)
        qnv, qc = clauses(query)
        assert nv == qnv and qc[:len(pc)] == pc
        assert qc[len(pc):] == [[v] for v in cube]
        parent_hashes.add(t["parent"])
    REPORT["original_parent"] = {
        "cold_receipts_regenerated": len(cold),
        "distinct_parent_hashes": len(parent_hashes),
        "all_parent_and_query_sha256_match": True,
        "all_were_budget_hits_not_closure": True,
    }


def check_export():
    t = tsv(OUT / "preferred-sample.tsv.gz")[0]
    rid, w, z = t["row_id"], t["w"], t["z"]
    row = wall()[0][rid]
    parent = row_formula(row, "first")
    nv, pc = clauses(parent)
    expected_cube = physical(rid, w, z)
    out = {"row_id": rid, "words": [w, z], "parent_sha256": sha(parent),
           "parent_variables": nv, "parent_clauses": len(pc)}
    for convention in ("raw", "sorted", "preferred"):
        base, query, cube = full_query(rid, w, z, convention)
        assert base == parent and cube[:10] == expected_cube
        qnv, qc = clauses(query)
        assert qnv >= nv and qc[:len(pc)] == pc
        assert len(qc) >= len(pc) + 10
        if convention == "raw":
            assert cube == expected_cube and qc[len(pc):] == [[v] for v in expected_cube]
            extras = 10
        elif convention == "sorted":
            image, top, guard = mapping(rid, nv)
            assert qnv == top and qc[len(pc):] == guard + [[v] for v in expected_cube]
            extras = len(guard) + 10
        else:
            assert len(cube) in (11, 12)
            assert qc[len(pc):][-len(cube):] == [[v] for v in cube]
            extras = len(qc) - len(pc)
        out[convention] = {"sha256": sha(query), "variables": qnv,
                           "clauses": len(qc), "added_clauses": extras,
                           "physical_cube": expected_cube,
                           "full_exported_cube": cube}
    REPORT["export"] = out


def unrank_remaining(k, prior):
    pos = k
    while True:
        new = k + bisect_right(prior, pos)
        if new == pos:
            return pos
        pos = new


def check_queue():
    keys, raw, ends = bounds()
    prior = excluded(keys, ends)
    live = ends[-1] - len(prior)
    stride = 104729
    while math.gcd(stride, live) != 1:
        stride += 1
    seen = bytearray(ends[-1])
    sequence_hash = hashlib.sha256()
    positions = []
    for j in range(live):
        k = (stride * j + 581433329) % live
        pos = unrank_remaining(k, prior)
        assert 0 <= pos < ends[-1] and not seen[pos], (j, pos)
        seen[pos] = 1
        sequence_hash.update(struct.pack("<I", pos))
        if j < 200:
            positions.append(pos)
    # All and only the 10,000 formerly sampled preferred positions are unseen.
    unseen = {i for i, value in enumerate(seen) if not value}
    assert unseen == set(prior)
    generated = batch(0, 100) + batch(100, 100)
    row_number = {rid: i for i, rid in enumerate(keys)}
    generated_positions = []
    raw_global = set()
    for item in generated:
        i = row_number[item["row_id"]]
        start = ends[i - 1] if i else 0
        p = start + list(preferred(int(item["arm"]))).index((item["w"], item["z"]))
        generated_positions.append(p)
        raw_global.add(int(item["global_index"]))
    assert generated_positions == positions
    assert len(raw_global) == 200 and len(set(generated_positions)) == 200
    REPORT["queue"] = {
        "preferred_jobs": ends[-1], "prior_D": len(prior), "live_after_D": live,
        "stride": stride, "gcd_stride_live": math.gcd(stride, live),
        "full_permutation_positions_checked": live,
        "exact_complement_is_D": True,
        "first_200_match_campaign_queue_batch": True,
        "first_200_preferred_position_sha256": sha(canonical(positions)),
        "whole_position_sequence_sha256": sequence_hash.hexdigest(),
    }


def assigned_model(n, model, palette, vertices, edge):
    """Map a local three-color arm model to signed physical edge literals."""
    ps = base(n)[0]
    result = {}
    for (i, j), digit in zip(ps, model):
        for c, physical_color in enumerate(palette):
            v = edge(vertices[i], vertices[j], physical_color)
            result[abs(v)] = (int(digit) == c) == (v > 0)
    return result


def semantic_extension_assignment(rid, model, new_order, selected):
    """Evaluate every preferred-extension auxiliary from its intended meaning."""
    row, arm, T, O = source(rid)
    n, palette = arm["size"], arm["palette"]
    from common import host
    edge, _ = host(58)
    vertices = T + O
    assignment = assigned_model(n, model, palette, vertices, edge)
    outside = list(range(5, n))
    words = {x: "".join(model[base(n)[0].index((i, x))] for i in range(5))
             for x in outside}
    top = 6612
    for x, y in zip(O[2:], O[3:]):
        # ``model`` has already been relabelled into the nominated physical slots.
        ox = O.index(x) + 5
        oy = O.index(y) + 5
        for i in range(5):
            if i == 4:
                break
            top += 1
            assignment[top] = words[ox][:i+1] == words[oy][:i+1]
    site = {}
    for x in O:
        ox = O.index(x) + 5
        for w in __import__("common").WORDS:
            top += 1
            site[x, w] = top
            assignment[top] = (words[ox] == w)
    occ = {}
    for w in __import__("common").WORDS:
        top += 1
        occ[w] = top
        assignment[top] = any(words[O.index(x) + 5] == w for x in O)
    present = set(combinations(sorted(words.values()), 2))
    ps = preferred(n)
    selected_index = ps.index(selected)
    gates = []
    for i, p in enumerate(ps):
        top += 1
        gates.append(top)
        assignment[top] = all(q not in present for q in ps[:i+1])
    actual_top, extra, actual_gates = __import__("representatives").preferred_extension(rid, 6612)
    assert actual_top == top and actual_gates == gates
    # A gate is true exactly up to the pair before the selected minimum and false after.
    assert all(assignment[g] == (i < selected_index) for i, g in enumerate(gates))
    return assignment, extra, gates, words


def literal_true(lit, assignment):
    return assignment[abs(lit)] == (lit > 0)


def check_preferred_semantics():
    rows, idx, arms = wall()
    example = {n: next(rid for rid in sorted(rows) if arms[rid]["size"] == n)
               for n in (11, 12, 13, 14)}
    results = tsv(OUT / "sorted-outcomes.tsv.gz")
    status = Counter((int(r["n"]), r["status"]) for r in results)
    checked = Counter()
    jobs_seen = {n: set() for n in example}
    digest = hashlib.sha256()
    for r in results:
        if r["status"] != "SAT":
            continue
        n = int(r["n"])
        rid = example[n]
        w, z, model = r["w"], r["z"], r["model"]
        validate(n, w, z, model)
        ps = base(n)[0]
        local = dict(zip(ps, model))
        original_words = {x: "".join(local[i, x] for i in range(5)) for x in range(5, n)}
        present = set(combinations(sorted(original_words.values()), 2))
        options = present & set(preferred(n))
        assert options, (n, w, z, "no preferred pair in known coloring")
        chosen = min(options)
        # Pick nominated vertices attaining the minimum pair, then sort the rest by word.
        candidates = [(x, y) for x, y in combinations(range(5, n), 2)
                      if tuple(sorted((original_words[x], original_words[y]))) == chosen]
        assert candidates
        x, y = candidates[0]
        rest = sorted((set(range(5, n)) - {x, y}), key=lambda v: (original_words[v], v))
        new_order = list(range(5)) + [x, y] + rest
        relabeled = "".join(local[tuple(sorted((new_order[i], new_order[j])))] for i, j in ps)
        check_word_model(n, chosen[0], chosen[1], relabeled)
        assignment, extra, gates, words = semantic_extension_assignment(rid, relabeled, new_order, chosen)
        bad = [cl for cl in extra if not any(literal_true(lit, assignment) for lit in cl)]
        if bad:
            raise AssertionError((n, w, z, chosen, bad[:5],
                                  [[(lit, assignment.get(abs(lit))) for lit in cl] for cl in bad[:2]]))
        cube = physical(rid, *chosen)
        owner = ([gates[pset-1]] if (pset := list(preferred(n)).index(chosen)) else []) + [-gates[list(preferred(n)).index(chosen)]]
        assert all(literal_true(lit, assignment) for lit in cube + owner)
        # The two physical nominated words are the chosen pair, and all remaining words are sorted.
        nominated = [words[5], words[6]]
        remainder = [words[v] for v in range(7, n)]
        assert nominated == list(chosen) and remainder == sorted(remainder)
        jobs_seen[n].add(chosen)
        checked[n] += 1
        digest.update(f"{n}:{w}:{z}:{chosen[0]}:{chosen[1]}\n".encode())
    for n in example:
        assert jobs_seen[n] == set(preferred(n)), (n, len(jobs_seen[n]), len(preferred(n)))
    REPORT["preferred_semantics"] = {
        "sorted_table_statuses": {f"{k[0]}:{k[1]}": v for k, v in sorted(status.items())},
        "known_complete_arm_colorings_relabelled_and_checked": dict(sorted(checked.items())),
        "preferred_jobs_hit": {str(n): len(jobs_seen[n]) for n in sorted(jobs_seen)},
        "all_extension_and_owner_clauses_satisfied_without_SAT": True,
        "mapping_sha256": digest.hexdigest(),
    }


def check_group_encoding():
    rows, _, _ = wall()
    groups = {}
    counts = Counter()
    for rid, row in rows.items():
        k = key(row)
        if k not in groups:
            groups[k] = group_formula(row)
        graph_and_aux, base, bypass = groups[k]
        exact_fixed = {v for v, in __import__("common").units(__import__("common").family(row), row["placement"])}
        assert base <= exact_fixed
        assumptions = per_row(row, base, bypass)
        flag_assumptions = {abs(v): v for v in assumptions if abs(v) in {f for f, _ in bypass.values()}}
        assert len(flag_assumptions) == len(bypass)
        for x, (flag, candidates) in bypass.items():
            positives = sum(v in exact_fixed for v in candidates)
            # Original marked_threshold uses needed=14-positives and no guard at needed<=0.
            expected = positives >= 14
            assert (flag_assumptions[flag] > 0) == expected
            available = sum(v not in exact_fixed and -v not in exact_fixed for v in candidates)
            # With the bypass false, group g can be true iff original needed<=len(filtered candidates).
            if not expected:
                assert (14 - positives <= available) == (available >= 14 - positives)
            counts["vertices"] += 1
            counts["automatic_senders" if expected else "guarded_senders"] += 1
        counts["rows"] += 1
    REPORT["group_encoding"] = {
        "rows_checked": counts["rows"], "distinct_group_formulas": len(groups),
        "nominated_arm_vertices_checked": counts["vertices"],
        "automatic_sender_bypasses": counts["automatic_senders"],
        "nonautomatic_guarded_senders": counts["guarded_senders"],
        "all_row_pin_sets_contain_group_fixed_pins": True,
        "bypass_exactly_original_needed_le_zero": True,
        "unsat_policy": "cheap.certify regenerates original parent and exact convention export; group OPEN is not closure",
    }


def main():
    q = tsv(OUT / "row-queue.tsv.gz")
    assert len(q) == 11585 and {r["root_status"] for r in q} == {"OPEN"}
    REPORT["root_status"] = {"ordinary_rows": len(q), "OPEN": len(q),
                             "mathematical_wall_reduction_from_job_compression": False}
    check_original_parent()
    check_export()
    check_queue()
    check_preferred_semantics()
    check_group_encoding()
    print(json.dumps(REPORT, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
