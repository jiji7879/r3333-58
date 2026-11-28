#!/usr/bin/env python3
"""Bounded physical calibration for the K58 critical-attaching proposal.

Reads only the repository's small verified .col artifacts.  No SAT solver and no
search are used.  A positive pair here is a semantic control, not wall evidence.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = [
    "n48_z4z4_f0.col",
    "k49_from_n48_m5.col",
    "k50_z4z4_m6.col",
    "k50_blockcayley_Z4xZ4_m4.col",
    "k50_sanity_f2.col",
]


def load(path):
    tokens = path.read_text().split()
    n, k = map(int, tokens[:2])
    values = list(map(int, tokens[2:2 + n * n]))
    assert len(values) == n * n
    matrix = [values[i*n:(i+1)*n] for i in range(n)]
    for i in range(n):
        for j in range(n):
            assert i == j or (0 <= matrix[i][j] < k and matrix[i][j] == matrix[j][i])
    for i in range(n-2):
        for j in range(i+1, n-1):
            for z in range(j+1, n):
                assert not (matrix[i][j] == matrix[i][z] == matrix[j][z]), (i, j, z)
    return n, k, matrix


def analyse(path):
    n, k, matrix = load(path)
    degree = [[[j != v and matrix[v][j] == c for j in range(n)].count(True)
               for c in range(k)] for v in range(n)]
    pairs = []
    for c in range(k):
        for u in range(n-1):
            if degree[u][c] not in (15, 16):
                continue
            for v in range(u+1, n):
                if degree[v][c] != degree[u][c]:
                    continue
                attachment = sum(
                    z != u and z != v and matrix[u][z] == c and matrix[v][z] == c
                    for z in range(n)
                )
                if attachment < 3:
                    continue
                other_u = sum(d >= 15 for color, d in enumerate(degree[u]) if color != c)
                other_v = sum(d >= 15 for color, d in enumerate(degree[v]) if color != c)
                gamma = matrix[u][v]
                pairs.append({
                    "color": c, "u": u, "v": v, "degree": degree[u][c],
                    "attachment": attachment, "other_critical_at_u": other_u,
                    "other_critical_at_v": other_v,
                    "edge_color": gamma, "edge_degree_at_u": degree[u][gamma],
                    "edge_degree_at_v": degree[v][gamma],
                })
    rich = [p for p in pairs if p["other_critical_at_u"] >= 2 and p["other_critical_at_v"] >= 2]
    bounded = [p for p in pairs if p["attachment"] <= 14]
    chosen = max(pairs, key=lambda p: (min(p["other_critical_at_u"], p["other_critical_at_v"]),
                                      p["attachment"]), default=None)
    return {
        "file": path.name, "n": n,
        "all_vertices_have_a_critical_color": all(max(d) >= 15 for d in degree),
        "critical_vertices_by_color": [sum(d[c] >= 15 for d in degree) for c in range(k)],
        "same_degree_attaching_pairs_ge3": len(pairs),
        "same_degree_attaching_pairs_3_to_14": len(bounded),
        "example_pair_3_to_14": bounded[0] if bounded else None,
        "example_pair_selected_for_max_min_other_criticality": chosen,
        "pairs_with_two_other_critical_colours_at_both_endpoints": len(rich),
        "example_with_two_other_critical_at_both_endpoints": rich[0] if rich else None,
        "max_attachment_over_eligible_pairs": max((p["attachment"] for p in pairs), default=None),
    }


if __name__ == "__main__":
    results = [analyse(ROOT / "artifacts" / name) for name in ARTIFACTS]
    output = {
        "scope": "physical calibration only; no K58 search and no unsatisfiability evidence",
        "results": results,
    }
    out = Path(__file__).with_name("fit_checks.json")
    out.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
