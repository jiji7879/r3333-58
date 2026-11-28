#!/usr/bin/env python3
"""Independent subset-orbit check for the FKR attachment calibration.

Uses only the pinned template matrices.  It does NOT import the member's Seed,
marked_census, or overlap_census.  Vertex isomorphisms, weak groups, named and
weak subset orbits, representative transports and Burnside's count are all
recomputed here.  This covers all 196,604 nonempty subsets, not a sample.
"""
from itertools import permutations
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "tools/color-resolved-wallcc/frozen"))
import gluing

ID = (0, 1, 2)


def isomorphisms(a, b):
    """All g with a[u][v] = b[g[u]][g[v]], via edge-colour backtracking."""
    n = len(a)
    da = [tuple(sum(u != v and a[u][v] == c for v in range(n)) for c in range(3))
          for u in range(n)]
    db = [tuple(sum(u != v and b[u][v] == c for v in range(n)) for c in range(3))
          for u in range(n)]
    if sorted(da) != sorted(db):
        return []
    candidates = [[w for w in range(n) if da[u] == db[w]] for u in range(n)]
    found = []

    def search(mapping, unused):
        if len(mapping) == n:
            found.append(tuple(mapping[i] for i in range(n)))
            return
        u, choices = min(((u, [w for w in candidates[u] if w not in unused and
                              all(a[u][z] == b[w][mapping[z]] for z in mapping)])
                          for u in range(n) if u not in mapping),
                         key=lambda item: len(item[1]))
        for w in choices:
            mapping[u] = w
            search(mapping, unused | {w})
            del mapping[u]

    search({}, set())
    return found


def weak_group(matrix):
    """All pairs (g,pi) with matrix[g[u]][g[v]] = pi[matrix[u][v]]."""
    out = []
    for pi in permutations(range(3)):
        relabelled = tuple(tuple(pi[c] for c in row) for row in matrix)
        out.extend((g, pi) for g in isomorphisms(relabelled, matrix))
    return out


def permute_mask(g, mask):
    answer = 0
    for u in range(len(g)):
        if mask >> u & 1:
            answer |= 1 << g[u]
    return answer


def compose(g, h):
    return tuple(g[h[i]] for i in range(len(g)))


def inverse(g):
    result = [0] * len(g)
    for i, j in enumerate(g):
        result[j] = i
    return tuple(result)


def subset_orbits(matrix, group):
    """Orbits of (vertex permutation, colour permutation) pairs on marked subsets."""
    n = len(matrix)
    unseen = set(range(1, 1 << n))
    reps = []
    witness = {}
    rep_of = {}
    while unseen:
        first = min(unseen)
        start = {first: tuple(range(n))}
        frontier = [first]
        while frontier:
            mask = frontier.pop()
            old = start[mask]
            for g, _ in group:
                image = permute_mask(g, mask)
                if image not in start:
                    start[image] = compose(g, old)
                    frontier.append(image)
        rep = min(start)
        to_rep = start[rep]
        for mask, path in start.items():
            witness[mask] = compose(to_rep, inverse(path))
            rep_of[mask] = rep
            unseen.remove(mask)
        reps.append(rep)
    profile = [0] * n
    for mask in reps:
        profile[mask.bit_count() - 1] += 1
    # Re-derive every representative and every nonidentity transport, not just
    # the count.  Every source subset must map to its retained representative.
    colour_images = {}
    for g, pi in group:
        colour_images.setdefault(g, []).append(pi)
    for mask, g in witness.items():
        assert sorted(g) == list(range(n))
        assert any(all(matrix[g[u]][g[v]] == pi[matrix[u][v]]
                       for u in range(n) for v in range(u + 1, n))
                   for pi in colour_images[g])
        assert permute_mask(g, mask) == rep_of[mask]
    return {"profile": profile, "reps": reps}


def burnside_profile(matrix, group):
    """Independent count of the SAME direct group action on all subsets."""
    n = len(matrix)
    total = [0] * (n + 1)
    for g, _ in group:
        visited = [False] * n
        lens = []
        for i in range(n):
            if visited[i]:
                continue
            j, length = i, 0
            while not visited[j]:
                visited[j] = True
                j = g[j]
                length += 1
            lens.append(length)
        ways = [1] + [0] * n
        for length in lens:
            for k in range(n, length - 1, -1):
                ways[k] += ways[k - length]
        for k in range(n + 1):
            total[k] += ways[k]
    assert all(x % len(group) == 0 for x in total)
    return [x // len(group) for x in total[1:]]


def main():
    result = {"scope": "all nonempty subsets; no SAT solver; no wall cases", "seeds": {}}
    summary = {}
    for name in ("U16", "T16", "U15", "T15"):
        matrix = gluing.template(16, name[:1]) if name.endswith("16") else gluing.template(15, name[:1])
        weak = weak_group(matrix)
        for g, pi in weak:
            assert all(matrix[g[u]][g[v]] == pi[matrix[u][v]]
                       for u in range(len(matrix)) for v in range(u + 1, len(matrix)))
        named = [g for g, pi in weak if pi == ID]
        direct_named = subset_orbits(matrix, [(g, ID) for g in named])
        direct_weak = subset_orbits(matrix, weak)
        burn = burnside_profile(matrix, weak)
        assert direct_weak["profile"] == burn, (name, direct_weak["profile"], burn)
        result["seeds"][name] = {
            "named_automorphisms": len(named), "weak_automorphisms": len(weak),
            "named_subset_orbits": direct_named["profile"],
            "weak_subset_orbits": direct_weak["profile"],
            "burnside_subset_orbits": burn,
            "all_subset_transports_verified": True,
            "subset_count": 2 ** len(matrix) - 1,
        }
        summary[name] = None
        summary[name] = {
            "strong_total": len(direct_named["reps"]), "weak_total": len(direct_weak["reps"]),
            "subset_count": 2 ** len(matrix) - 1,
        }
        print(name, result["seeds"][name], flush=True)
    # Explicit negative control: a deliberately corrupted matrix is not good.
    bad = [list(row) for row in gluing.template(16, "U")]
    c = bad[0][1]
    bad[0][1] = bad[1][0] = bad[0][2]
    bad[0][2] = bad[2][0] = c
    bad[1][2] = bad[2][1] = c
    result["inserted_triangle_rejected"] = not all(
        bad[u][v] != bad[u][w] or bad[u][v] != bad[v][w]
        for u in range(16) for v in range(u + 1, 16) for w in range(v + 1, 16))
    assert result["inserted_triangle_rejected"]
    # Compare only after all independent computations are finished.
    expected = json.loads((HERE / "fkr/member-run_census.json").read_text())
    for name in ("U16", "T16", "U15", "T15"):
        values = expected["A_templates"][name]
        mine = result["seeds"][name]
        assert mine["named_automorphisms"] == values["aut_named_order"]
        assert mine["weak_automorphisms"] == values["weak_group_order"]
        assert sum(mine["named_subset_orbits"]) == values["strong_subset_classes"]
        assert mine["subset_count"] == expected["B_transport_witnesses"][name]["subsets"]
    assert [sum(result["seeds"][n]["weak_subset_orbits"][k]
                for n in ("U16", "T16")) for k in range(16)] == expected["C_table5"]["printed"]
    marked15 = [sum(result["seeds"][n]["weak_subset_orbits"][k]
                    for n in ("U15", "T15")) for k in range(15)]
    assert marked15 == expected["E_census_15_15"]["marked_per_order_k1_to_15"]
    result["reference_533_matches"] = True
    result["new_15_15_marked_3402_matches"] = sum(marked15)
    result["independent_subset_transports_checked"] = sum(
        values["subset_count"] for values in summary.values())
    result["checked_member_source_sha256"] = hashlib.sha256(
        (HERE / "fkr/member-run_census.json").read_bytes()).hexdigest()
    result["script_sha256_at_runtime"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE / "subset-orbits.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: 196604 independent named-orbit transports plus 196604 weak-orbit transports;", flush=True)
    print("direct weak orbit count and Burnside agree on every per-order row;", flush=True)
    print("member template data and all marked totals match; 15/15 marked =", sum(marked15))


if __name__ == "__main__":
    main()
