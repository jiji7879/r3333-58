#!/usr/bin/env python3
"""Independent finite audit of K58 arm witnesses and representative semantics.

Stdlib only. Does not call a SAT solver or construct a K58 search query.
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import csv
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE / "extracted" / "K58_wall_10k_batches"


def rows_gz(path):
    with gzip.open(path, "rt", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def validate_local(n, colors):
    """Return outside words after checking the full labeled 3-color arm."""
    ps = list(combinations(range(n), 2))
    assert len(colors) == len(ps) and set(colors) <= set("012")
    edge = dict(zip(ps, map(int, colors)))
    for i, j in combinations(range(5), 2):
        expected = 1 if (j - i) % 5 in (1, 4) else 2
        assert edge[i, j] == expected
    for i, j, k in combinations(range(n), 3):
        assert len({edge[i, j], edge[i, k], edge[j, k]}) > 1
    words = ["".join(str(edge[i, j]) for i in range(5)) for j in range(5, n)]
    return words


def permute_local(n, colors, outside_order):
    """Relabel only outside vertices; outside_order lists old vertex numbers."""
    order = list(range(5)) + list(outside_order)
    assert sorted(order) == list(range(n))
    old = dict(zip(combinations(range(n), 2), colors))
    values = []
    for i, j in combinations(range(n), 2):
        a, b = sorted((order[i], order[j]))
        values.append(old[a, b])
    result = "".join(values)
    assert validate_local(n, result)  # The whole local arm is preserved.
    return result


def main():
    pair_index = rows_gz(BASE / "inputs" / "pair-class-index.tsv.gz")
    raw_pairs = {n: {(r["word_1"], r["word_2"]) for r in pair_index if r[f"arm_{n}"] == "SAT"}
                 for n in (11, 12, 13, 14)}
    preferred = {}
    for n in (11, 12, 13, 14):
        record = json.loads((BASE / "results" / "preferred" / f"{n}.json").read_text())
        ps = list(map(tuple, record["pairs"]))
        assert ps == sorted(set(ps)) and all(w <= z for w, z in ps)
        preferred[n] = ps

    witnesses = [r for r in rows_gz(BASE / "results" / "sorted-outcomes.tsv.gz")
                 if r["status"] == "SAT"]
    by_size = Counter()
    label_counts = Counter()
    owner_choice_histogram = Counter()
    # This records consequences of actually supplied local colorings. It is not
    # an exhaustive enumeration of arm colorings.
    associations = defaultdict(lambda: {"sorted": set(), "preferred": set(), "sources": {}})
    canon_failures = []

    for source_index, r in enumerate(witnesses):
        n = int(r["n"])
        words = validate_local(n, r["model"])
        assert words == sorted(words)
        assert (r["w"], r["z"]) == tuple(words[:2])
        by_size[n] += 1

        occurring = set(combinations(sorted(words), 2))
        # combinations(...,2) omits a repeated equal word, so add it explicitly.
        occurring |= {(w, w) for w in set(words) if words.count(w) >= 2}
        available = occurring & set(preferred[n])
        assert available, (n, r["w"], r["z"])
        first = min(available)
        rank = {p: i for i, p in enumerate(preferred[n])}
        owner_labels = []
        for p in available:
            j = rank[p]
            if not any(q in available for q in preferred[n][:j]):
                owner_labels.append(p)
        assert owner_labels == [first]
        label_counts[n, first] += 1

        positions = [(i, j) for i, j in combinations(range(len(words)), 2)
                     if tuple(sorted((words[i], words[j]))) == first]
        assert positions
        owner_choice_histogram[n, len(positions)] += 1
        # Every choice gives the same canonical word list after sorting the tail.
        canonical_word_lists = set()
        for i, j in positions:
            a, b = (i, j) if words[i] <= words[j] else (j, i)
            tail = sorted(words[k] for k in range(len(words)) if k not in (i, j))
            canonical_word_lists.add(tuple([words[a], words[b]] + tail))
            earlier = set(preferred[n][:rank[first]])
            assert not (occurring & earlier)
        assert len(canonical_word_lists) == 1

        # Any pair of vertices can be renamed to raw physical positions 5 and 6.
        # Keep two orientations because the old raw jobs are oriented.
        for i, j in combinations(range(len(words)), 2):
            old_order = list(range(5, n))
            for oriented in ((i, j), (j, i)) if words[i] != words[j] else ((i, j),):
                a, b = oriented
                new_outside = [5 + a, 5 + b] + [old_order[k] for k in range(len(words))
                                                   if k not in (a, b)]
                model = permute_local(n, r["model"], new_outside)
                raw_words = validate_local(n, model)
                raw_pair = (raw_words[0], raw_words[1])
                assert raw_pair == (words[a], words[b])
                assert raw_pair in raw_pairs[n]
                key = (n, raw_pair)
                entry = associations[key]
                entry["sorted"].add((r["w"], r["z"]))
                entry["preferred"].add(first)
                # Preserve one permuted full witness for each canonical pair.
                source_key = ("P", first) if first not in {v[1] for k, v in entry["sources"].items() if k[0] == "P"} else None
                if source_key:
                    entry["sources"][source_key] = (source_index, a, b, model)
                sorted_pair = (r["w"], r["z"])
                source_key = ("S", sorted_pair) if sorted_pair not in {v[1] for k, v in entry["sources"].items() if k[0] == "S"} else None
                if source_key:
                    entry["sources"][source_key] = (source_index, a, b, model)

    multi_preferred = {k: v for k, v in associations.items() if len(v["preferred"]) > 1}
    multi_sorted = {k: v for k, v in associations.items() if len(v["sorted"]) > 1}
    examples = []
    for (n, raw_pair), entry in sorted(multi_preferred.items())[:3]:
        labels = sorted(entry["preferred"])
        ws = []
        for label in labels[:2]:
            source_index, a, b, model = entry["sources"]["P", label]
            assert validate_local(n, model)[:2] == list(raw_pair)
            ws.append({"source_witness_index": source_index,
                       "preferred_label": list(label),
                       "sorted_label": [witnesses[source_index]["w"], witnesses[source_index]["z"]],
                       "permuted_model_sha256": hashlib.sha256(model.encode()).hexdigest(),
                       "permuted_model": model})
        examples.append({"n": n, "raw_pair": list(raw_pair), "witnesses": ws})

    # Independent exhaustive R(3,3)<=6 check: every 2-coloring of K6 has a
    # monochromatic triangle. Thus a color in a triangle-free graph has degree <=5.
    edges = list(combinations(range(6), 2))
    eindex = {e: i for i, e in enumerate(edges)}
    triangles = [sum(1 << eindex[e] for e in combinations(t, 2))
                 for t in combinations(range(6), 3)]
    exceptions = 0
    for bits in range(1 << len(edges)):
        if not any((bits & t) in (0, t) for t in triangles):
            exceptions += 1
    assert exceptions == 0

    result = {
        "scope": "Finite supplied SAT witnesses only; not a completeness proof",
        "sat_witnesses_checked": len(witnesses),
        "by_size": dict(sorted(by_size.items())),
        "preferred_labels_hit_by_witnesses": {str(n): sum(1 for (m, p), count in label_counts.items() if m == n)
                                               for n in preferred},
        "preferred_catalog_sizes": {str(n): len(p) for n, p in preferred.items()},
        "owner_vertex_choice_histogram_n_and_choice_count": {f"{n},{k}": v for (n, k), v in sorted(owner_choice_histogram.items())},
        "raw_pairs_represented_in_this_witness_set": len(associations),
        "raw_pairs_represented_by_size": {str(n): sum(1 for m, p in associations if m == n)
                                            for n in raw_pairs},
        "raw_table_sizes": {str(n): len(p) for n, p in raw_pairs.items()},
        "raw_pairs_with_multiple_sorted_labels_in_witness_set": len(multi_sorted),
        "raw_pairs_with_multiple_preferred_labels_in_witness_set": len(multi_preferred),
        "raw_nonuniqueness_examples": examples,
        "two_colorings_of_K6_without_monochromatic_triangle": exceptions,
        "canonicalization_failures": canon_failures,
    }
    assert not canon_failures
    out = HERE / "cover_audit_results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "raw_nonuniqueness_examples"}, indent=2, sort_keys=True))
    print("examples", len(examples), "written to", out)


if __name__ == "__main__":
    main()
