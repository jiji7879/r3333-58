#!/usr/bin/env python3
"""Bounded, solver-free checks for the K58_square_six catalog and selection metadata."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import gzip
import hashlib
import json
import sys

# Do not create __pycache__ in the coordinator-owned source directory.
sys.dont_write_bytecode = True
if len(sys.argv) != 2:
    raise SystemExit("usage: audit_catalog.py /path/to/K58_square_six")
P = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(P))
from catalog import hexagons, maximal_independent, spread, verify_catalog  # noqa: E402
from marked_hexagons import verify_bound  # noqa: E402

study = json.loads((P / "evidence/study.json").read_text())
wedges = json.loads((P / "evidence/wedges.json").read_text())

# Package bytes and original-parent identity.
manifest = {}
for line in (P / "SHA256SUMS").read_text().splitlines():
    wanted, name = line.split(maxsplit=1)
    manifest[name] = wanted
assert len(manifest) == 38
for name, wanted in manifest.items():
    got = hashlib.sha256((P / name).read_bytes()).hexdigest()
    assert got == wanted, (name, got, wanted)
parent = gzip.decompress((P / "evidence/parent.cnf.gz").read_bytes())
parent_hash = hashlib.sha256(parent).hexdigest()
assert parent_hash == study["parent_sha256"]
print(f"PASS: 38 manifest hashes; original parent SHA-256 {parent_hash}")

# Bind every encoded template edge to a positive unit pin in that exact parent.
geometries = {g["kind"]: g for g in study["geometry"]}
edges = {e: i for i, e in enumerate(combinations(range(58), 2))}
pins = {
    int(line.split()[0])
    for line in parent.splitlines()[1:]
    if len(line.split()) == 2
}
pinned_edges = 0
for g in geometries.values():
    vertices, m = g["vertices"], g["matrix"]
    for i, j in combinations(range(len(vertices)), 2):
        var = 1 + 4 * edges[tuple(sorted((vertices[i], vertices[j])))] + m[i][j]
        assert var in pins, (g["kind"], vertices[i], vertices[j], var)
        pinned_edges += 1
print(f"PASS: {pinned_edges} template edges match positive unit pins in the packaged parent")

# The packaged finite-template verifier, unmodified.
verify_catalog(study["geometry"])
print("PASS: packaged all-subsets/two-triangle and minimal-support/rim checks")

# The actual matrices are symmetric complete edge colorings. For each full
# 16-arm and color, check the SRG(16,5,0,2) parameters directly.
for kind, g in geometries.items():
    m = g["matrix"]
    n = len(m)
    assert len(set(g["vertices"])) == n
    assert all(m[i][j] == m[j][i] for i in range(n) for j in range(n))
for kind in ("16T", "16U"):
    m = geometries[kind]["matrix"]
    n = len(m)
    colors = sorted({m[i][j] for i, j in combinations(range(n), 2)})
    for color in colors:
        for i in range(n):
            assert sum(m[i][k] == color for k in range(n) if k != i) == 5
        for i, j in combinations(range(n), 2):
            common = sum(
                m[i][k] == color and m[j][k] == color
                for k in range(n) if k != i and k != j
            )
            assert common == (0 if m[i][j] == color else 2), (kind, color, i, j, common)
    print(f"PASS: {kind} uses SRG(16,5,0,2) graphs in every color (Clebsch parameters)")


def assignment_count(g, sites, pair):
    """Count abstract pair-colored outside spokes avoiding a triangle inside sites."""
    ids = [g["vertices"].index(v) for v in sites]
    m = g["matrix"]
    count = 0
    for assignment in product(pair, repeat=len(ids)):
        if all(
            not (assignment[j] == assignment[k] == m[ids[j]][ids[k]])
            for j, k in combinations(range(len(ids)), 2)
        ):
            count += 1
    return count


# Independent brute force on the two README examples, not the MIS construction.
examples = [
    ("square", "16T", [2, 4, 9, 11], (2, 3), [3, 3, 3, 3]),
    ("paired triangles", "15T", [35, 37, 8, 33, 1, 5], (0, 3), [9, 9, 1, 1, 1, 1]),
]
for label, kind, sites, pair, expected_deletions in examples:
    g = geometries[kind]
    assert assignment_count(g, sites, pair) == 0
    deletion_counts = [
        assignment_count(g, sites[:i] + sites[i + 1 :], pair)
        for i in range(len(sites))
    ]
    assert deletion_counts == expected_deletions, deletion_counts
    print(f"PASS: README {label} example is abstractly non-extendable and minimal; deletion counts {deletion_counts}")

# Supplement the packaged rim check: it examines rims[a] only for pair (a,b).
# Check both rim colors in every pair, including the largest color omitted by
# the packaged comparison, and confirm that the numerical table is still true.
expected_hex = {
    "16T": (320, 128),
    "15T": (200, 80),
    "16U": (320, 80),
    "15U": (200, 50),
}
blocks = {kind: g["matrix"] for kind, g in geometries.items()}
blocks["15U"] = [row[:15] for row in blocks["16U"][:15]]
for kind, m in blocks.items():
    n = len(m)
    colors = sorted({m[i][j] for i, j in combinations(range(n), 2)})
    rims = {c: hexagons(m, c) for c in colors}
    assert {c: len(rims[c]) for c in colors} == {c: expected_hex[kind][0] for c in colors}
    for a, b in combinations(colors, 2):
        ok = bytearray(1 << n)
        for ma in maximal_independent(m, a):
            for mb in maximal_independent(m, b):
                ok[ma | mb] = 1
        spread(ok, n, downward=True)
        got = {c: sum(ok[s] for s in rims[c]) for c in (a, b)}
        assert got == {a: expected_hex[kind][1], b: expected_hex[kind][1]}, (kind, a, b, got)
    print(f"PASS: {kind} rim totals and extendability for BOTH colors in every pair: {expected_hex[kind]}")

# Abstract marked-cycle arithmetic, not a frozen-row node enumeration.
verify_bound()

# Selection metadata and actual retained records: report rather than treating
# candidate/scoring totals as an exhaustive node census.
cuts = study["cuts"]
assert len(cuts) == 384
assert len({tuple(r["goal"]) for r in cuts}) == 384
assert Counter(r["shape"] for r in cuts) == {"square": 192, "paired-triangles": 192}
short = wedges["clauses"]
assert len(short) == 1020 == len({tuple(sorted(c)) for c in short})
assert Counter(map(len, short)) == {3: 364, 4: 306, 5: 350}
assert len(study["stock"]) == 189 == len({tuple(c) for c in study["stock"]})
selected_kinds = Counter((r["shape"], r["kind"]) for r in cuts)
six_x = sorted({r["x"] for r in cuts if r["shape"] == "paired-triangles"})
assert selected_kinds == {
    ("square", "16T"): 6,
    ("square", "15T"): 132,
    ("square", "16U"): 54,
    ("paired-triangles", "15T"): 192,
}
assert len(six_x) == 16
print("PASS: 384 unique direct goals; 1020 unique short clauses (widths 364/306/350); 189 unique stock clauses")
print(f"SELECTION ONLY: stored candidates {study['candidates']}, cap {study['cap']}; selected kinds {dict(selected_kinds)}")
print(f"SELECTION ONLY: all 192 six-site cuts are 15T and their outside-x set has size {len(six_x)}: {six_x}")
print("SCOPE: candidate-generation/scoring and full shape-subcount regeneration are not supplied in catalog.py")
print("ALL BOUNDED CHECKS PASSED; no solver or wall search was run")
