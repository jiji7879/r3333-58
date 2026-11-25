#!/usr/bin/env python3
"""Independent semantic-table audit for the common-critical certificate.

Run from the repository root with
PYTHONDONTWRITEBYTECODE=1 python3 paper/audit/common-critical/encoding_audit.py.
The run takes several minutes on the project VM. It needs the supplied
certificate extracted at .scratch/common-critical-audit/K58_common_critical_color_certificate.
The source certificate is read-only. This independently enumerates every
(template, palette, ordered-anchor) embedding used by the slot and four-anchor
word encoders, then compares complete inferred signature sets. It also records
which encoder paths are exercised by all 247 certified orbit formulas.
"""
from collections import Counter
from itertools import combinations, permutations
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
MEMBER = Path(__file__).resolve().parent
REPO = MEMBER.parents[2]
SRC = REPO / ".scratch/common-critical-audit/K58_common_critical_color_certificate"
sys.path.insert(0, str(SRC))

import slot_encoder  # noqa: E402
import tables  # noqa: E402
import word_encoder  # noqa: E402


def mapped_matrix(raw, back):
    source = tables.matrix(raw, 16)
    return [[back[x] if x >= 0 else -1 for x in row] for row in source]


def anchor_enumerations(M, shape, k):
    """Yield every ordered injective anchor matching shape, independently."""
    wanted = dict(zip(combinations(range(k), 2), shape))
    chosen = []

    def visit():
        h = len(chosen)
        if h == k:
            yield tuple(chosen)
            return
        for v in range(16):
            if v in chosen:
                continue
            if all(M[v][chosen[z]] == wanted[z, h] for z in range(h)):
                chosen.append(v)
                yield from visit()
                chosen.pop()

    yield from visit()


def independent_slot(shape, k, omit):
    """All (words, links) obtainable from a physical 16-template embedding."""
    result = set()
    for raw in tables.wordsn(16):
        for back in permutations([d for d in range(4) if d != omit]):
            M = mapped_matrix(raw, back)
            for anchor in anchor_enumerations(M, shape, k):
                free = sorted(
                    set(range(16)) - set(anchor),
                    key=lambda v: (tuple(M[v][a] for a in anchor), v),
                )
                words = tuple(tuple(M[v][a] for a in anchor) for v in free)
                links = tuple(M[x][y] for x, y in combinations(free, 2))
                result.add((words, links))
    return result


def independent_word(pal, shape, k):
    """All projected word types and ordered-pair colour sets."""
    result = set()
    for raw in tables.wordsn(16):
        for back in permutations(pal):
            M = mapped_matrix(raw, back)
            for anchor in anchor_enumerations(M, shape, k):
                free = sorted(set(range(16)) - set(anchor))
                words = {v: tuple(M[v][a] for a in anchor) for v in free}
                types = tuple(sorted(set(words.values())))
                pair_colours = []
                for a in types:
                    for b in types:
                        pair_colours.append(tuple(sorted({
                            M[u][v]
                            for u in free for v in free if u != v
                            if words[u] == a and words[v] == b
                        })))
                result.add((types, tuple(pair_colours)))
    return result


def canonical_shape(shape):
    actual = tuple(sorted(set(shape)))
    to_canonical = {c: i for i, c in enumerate(actual)}
    return tuple(to_canonical[c] for c in shape), actual


def canonical_shape_and_map(shape, palette):
    canonical, used_actual = canonical_shape(shape)
    colour_map = dict(enumerate(used_actual))
    unused_actual = [c for c in palette if c not in used_actual]
    assert len(unused_actual) == 3 - len(used_actual)
    for i, c in enumerate(unused_actual, start=len(used_actual)):
        colour_map[i] = c
    assert len(colour_map) == 3
    return canonical, colour_map


def recolour_slot_mode(mode, colour_map):
    words, links = mode
    n = len(words)
    edge_colours = dict(zip(combinations(range(n), 2), links))
    # Stable sorting retains original-position order inside an equal word class.
    order = sorted(range(n), key=lambda i: (
        tuple(colour_map[c] for c in words[i]), i))
    new_words = tuple(tuple(colour_map[c] for c in words[i]) for i in order)
    new_links = []
    for a, b in combinations(range(n), 2):
        x, y = sorted((order[a], order[b]))
        new_links.append(colour_map[edge_colours[x, y]])
    return new_words, tuple(new_links)


def recolour_word_mode(mode, colour_map):
    types, pairs = mode
    n = len(types)
    recoloured = [tuple(colour_map[c] for c in word) for word in types]
    new_types = tuple(sorted(recoloured))
    old_index = {word: i for i, word in enumerate(recoloured)}
    new_pairs = []
    for a in new_types:
        for b in new_types:
            values = pairs[old_index[a] * n + old_index[b]]
            new_pairs.append(tuple(sorted(colour_map[c] for c in values)))
    return new_types, tuple(new_pairs)


def main():
    items = [json.loads(line) for line in
             (SRC / "data/manifest.jsonl").read_text().splitlines()]
    assert len(items) == 496

    slot_calls = Counter()
    original_catalog = slot_encoder.catalog

    def recording_catalog(shape, k, omit):
        slot_calls[(tuple(shape), k, omit)] += 1
        return original_catalog(shape, k, omit)

    slot_encoder.catalog = recording_catalog
    for item in items:
        if item["domain"] == "slots":
            slot_encoder.build({"i": item["i"], "j": item["j"]})
    slot_encoder.catalog = original_catalog

    word_calls = Counter()
    original_templates = word_encoder.templates

    def recording_templates(pal, shape, k):
        word_calls[(tuple(pal), tuple(shape), k)] += 1
        return original_templates(pal, shape, k)

    word_encoder.templates = recording_templates
    for item in items:
        if item["domain"] == "words":
            word_encoder.build(dict(n=15, m=15, i=item["i"], j=item["j"],
                                    only_five=item["only_five"]))
    word_encoder.templates = original_templates

    # Colour names are immaterial because both encoders quantify over every
    # palette permutation. Enumerate once per canonical shape, then transport
    # the complete result back to every literal palette occurring in a CNF.
    slot_groups = {}
    for shape, k, omit in slot_calls:
        canonical, actual_colours = canonical_shape(shape)
        slot_groups.setdefault((canonical, k), set()).add(actual_colours)
    slot_canonical = {}
    for canonical, k in sorted(slot_groups):
        slot_canonical[canonical, k] = independent_slot(canonical, k, 3)
    slot_results = []
    for (shape, k, omit), calls in sorted(slot_calls.items(), key=lambda x: (x[0][1], x[0][2], x[0][0])):
        canonical, colour_map = canonical_shape_and_map(
            shape, tuple(c for c in range(4) if c != omit))
        expected = {recolour_slot_mode(mode, colour_map)
                    for mode in slot_canonical[canonical, k]}
        actual = set(original_catalog(shape, k, omit))
        assert actual == expected, ("slot signature mismatch", shape, k, omit,
                                    len(actual), len(expected))
        slot_results.append({"k": k, "omit": omit, "calls": calls,
                             "signatures": len(actual)})

    word_groups = {}
    for pal, shape, k in word_calls:
        assert k == 4
        canonical, actual_colours = canonical_shape(shape)
        word_groups.setdefault((canonical, k), set()).add(actual_colours)
    word_canonical = {}
    for canonical, k in sorted(word_groups):
        word_canonical[canonical, k] = independent_word((0, 1, 2), canonical, k)
    word_results = []
    multicolour_same_type_modes = 0
    for (pal, shape, k), calls in sorted(word_calls.items(), key=lambda x: (x[0][2], x[0][0], x[0][1])):
        canonical, colour_map = canonical_shape_and_map(shape, pal)
        expected = {recolour_word_mode(mode, colour_map)
                    for mode in word_canonical[canonical, k]}
        actual = set(original_templates(pal, shape, k))
        assert actual == expected, ("word signature mismatch", pal, shape, k,
                                    len(actual), len(expected))
        for types, pair_colours in actual:
            multicolour_same_type_modes += int(any(
                len(pair_colours[i * len(types) + i]) > 1
                for i in range(len(types))))
        word_results.append({"k": k, "calls": calls, "signatures": len(actual)})

    diagonal_nonempty = 0
    diagonal_multi = 0
    for pal, shape, k in word_calls:
        for types, pairs in original_templates(pal, shape, k):
            for i in range(len(types)):
                values = pairs[i * len(types) + i]
                diagonal_nonempty += int(bool(values))
                diagonal_multi += int(len(values) > 1)

    orbits = tables.orbits()
    for domain in ("slots", "words"):
        keys = {(x["i"], x["j"]) for x in items if x["domain"] == domain}
        assert keys == set(orbits) and len(keys) == 247

    result = {
        "verdict": "PASS",
        "manifest_orbits": len(orbits),
        "placements": sum(map(len, orbits.values())),
        "slot_unique_constraints": len(slot_results),
        "slot_colour_orbits_independently_enumerated": len(slot_groups),
        "slot_constraint_calls": sum(slot_calls.values()),
        "slot_anchor_sizes": dict(Counter({str(k): sum(n for (_, kk, _), n in slot_calls.items() if kk == k) for k in (4, 5)})),
        "slot_signatures_total": sum(x["signatures"] for x in slot_results),
        "word_unique_four_anchor_constraints": len(word_results),
        "word_colour_orbits_independently_enumerated": len(word_groups),
        "word_four_anchor_calls": sum(word_calls.values()),
        "word_signatures_total": sum(x["signatures"] for x in word_results),
        "word_same_type_diagonal_nonempty": diagonal_nonempty,
        "word_same_type_diagonal_multiple_colours": diagonal_multi,
        "word_modes_with_multicolour_same_type_pairs": multicolour_same_type_modes,
        "note": "Repeated four-anchor words are collapsed as types; nonempty diagonal pair sets witness projection over distinct slots, not identification of physical vertices.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
