#!/usr/bin/env python3
"""Independent finite checks for the Duggan/Graver--Yackel transfer audit.

Read-only with respect to the repository.  Run from this directory:
    python3 full_vertex_audit.py
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts"


def ceil_frac(a: int, b: int) -> int:
    return -((-a) // b)


def caro_wei_floor(m: int, alpha_max: int = 15) -> int:
    """Edge lower bound from alpha >= m^2/(2E+m), for alpha <= alpha_max."""
    if m <= alpha_max:
        return 0
    return ceil_frac(m * (m - alpha_max), 2 * alpha_max)


def load_colouring(path: Path):
    values = list(map(int, path.read_text().split()))
    n, k = values[:2]
    matrix_values = values[2:]
    assert len(matrix_values) == n * n, (path, n, len(matrix_values))
    M = [matrix_values[n * i:n * (i + 1)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            assert 0 <= M[i][j] < k, (path, i, j, M[i][j])
            assert M[i][j] == M[j][i], (path, i, j)
    for i, j, l in combinations(range(n), 3):
        assert not (M[i][j] == M[i][l] == M[j][l]), (path, i, j, l)
    return M, k


def induced_edges(adj, vertices) -> int:
    return sum(adj[i][j] for i, j in combinations(vertices, 2))


def independent(adj, vertices) -> bool:
    return all(not adj[i][j] for i, j in combinations(vertices, 2))


def graph_from_edges(n: int, bits: int):
    adj = [[False] * n for _ in range(n)]
    edges = list(combinations(range(n), 2))
    for z, (i, j) in enumerate(edges):
        if bits >> z & 1:
            adj[i][j] = adj[j][i] = True
    return adj, edges


def small_graph_checks():
    checked_graphs = 0
    checked_roots = 0
    naive_failures = 0
    triangle_free_graphs = 0
    k3_phi = None
    for n in range(2, 6):
        edges = list(combinations(range(n), 2))
        for bits in range(1 << len(edges)):
            adj, _ = graph_from_edges(n, bits)
            deg = [sum(row) for row in adj]
            E = sum(deg) // 2
            tf = all(not (adj[i][j] and adj[i][l] and adj[j][l])
                     for i, j, l in combinations(range(n), 3))
            triangle_free_graphs += int(tf)
            sum_h2 = sum_d2 = sum_e1 = 0
            for v in range(n):
                H1 = [u for u in range(n) if adj[v][u]]
                H2 = [u for u in range(n) if u != v and not adj[v][u]]
                e1 = induced_edges(adj, H1)
                h2 = induced_edges(adj, H2)
                d = deg[v]
                Z = sum(deg[u] for u in H1)
                naive = h2 + d * d + sum(deg[u] - d for u in H1)
                assert E == naive - e1, (n, bits, v, E, naive, e1)
                assert E == h2 + Z - e1, (n, bits, v)
                if tf:
                    assert e1 == 0 and E == naive
                naive_failures += int(E != naive)
                checked_roots += 1
                sum_h2 += h2
                sum_d2 += d * d
                sum_e1 += e1
            assert n * E == sum_h2 + sum_d2 - sum_e1
            if n == 3 and bits == 7:
                # Here H2 is empty at each root, hence e(4,2;0)=0.
                k3_phi = n * E - sum_d2
            checked_graphs += 1
    assert k3_phi == -3
    return {
        "graphs_orders_2_to_5": checked_graphs,
        "root_identities": checked_roots,
        "naive_identity_failures": naive_failures,
        "triangle_free_graphs": triangle_free_graphs,
        "K3_naive_phi": k3_phi,
    }


def clebsch_catalogue_bound():
    component_data = []
    for name in ["k16_link_U_m5.col", "k16_link_T_m5.col"]:
        M, k = load_colouring(ART / name)
        assert len(M) == 16 and k == 3
        for c in range(3):
            adj = [[i != j and M[i][j] == c for j in range(16)] for i in range(16)]
            assert all(sum(row) == 5 for row in adj), (name, c, [sum(r) for r in adj])
            assert induced_edges(adj, range(16)) == 40
            independent5 = 0
            for S in combinations(range(16), 5):
                independent5 += int(independent(adj, S))
            assert independent5 > 0, (name, c, "no independent 5-set")
            for S in combinations(range(16), 6):
                assert not independent(adj, S), (name, c, S)
            component_data.append((name, c, independent5))

    # Three disjoint copies of any checked component constitute the constructive
    # upper-bound graph.  Use U, colour 0 explicitly and independently recheck it.
    M, _ = load_colouring(ART / "k16_link_U_m5.col")
    base = [[i != j and M[i][j] == 0 for j in range(16)] for i in range(16)]
    adj = [[False] * 48 for _ in range(48)]
    for b in range(3):
        for i in range(16):
            for j in range(16):
                adj[16 * b + i][16 * b + j] = base[i][j]
    assert induced_edges(adj, range(48)) == 120
    assert all(not (adj[i][j] and adj[i][l] and adj[j][l])
               for i, j, l in combinations(range(48), 3))
    # alpha <= 15 follows additively from the three component checks above.
    # Every induced subgraph therefore has alpha <= 15 and at most 120 edges.
    for m in range(41, 49):
        assert induced_edges(adj, range(m)) <= 120
    return {
        "components_checked": component_data,
        "construction": "3 disjoint K16-link colour-0 Clebsch graphs",
        "vertices": 48,
        "edges": 120,
        "independence_at_most": 15,
        "e_3_16_m_upper_for_41_to_48": 120,
    }


def k58_deficit_check():
    rows = []
    for d in range(9, 17):
        m = 57 - d
        assert 41 <= m <= 48
        L = caro_wei_floor(m)
        degree_moment = 29 * d - d * d
        rows.append({
            "d": d,
            "m": m,
            "Caro_Wei_L": L,
            "29d_minus_d2": degree_moment,
            "minus_120": degree_moment - 120,
        })
    min_moment = min(r["29d_minus_d2"] for r in rows)
    min_margin = min(r["minus_120"] for r in rows)
    assert min_moment == 180 and min_margin == 60
    return {
        "per_degree": rows,
        "min_degree_moment": min_moment,
        "min_margin_after_e_min_upper_120": min_margin,
        "phi_lower_bound_each_colour": 58 * min_margin,
        "full_vertices_forced_by_58_minus_phi": 0,
    }


def artifact_checks():
    results = {}
    names = [
        "k50_z4z4_m6.col",
        "k50_blockcayley_Z4xZ4_m4.col",
        "k50_sanity_f2.col",
        "n48_z4z4_f0.col",
        "k49_from_n48_m5.col",
    ]
    for name in names:
        M, k = load_colouring(ART / name)
        assert k == 4
        n = len(M)
        single_identities = 0
        pair_identities = 0
        naive_pair_roots = 0
        max_pair_H1_edges = 0
        min_caro_slack = None
        phi_lower_bounds = []
        for c in range(4):
            adj = [[i != j and M[i][j] == c for j in range(n)] for i in range(n)]
            deg = [sum(row) for row in adj]
            E = sum(deg) // 2
            sum_h2 = 0
            for v in range(n):
                H1 = [u for u in range(n) if adj[v][u]]
                H2 = [u for u in range(n) if u != v and not adj[v][u]]
                h2 = induced_edges(adj, H2)
                Z = sum(deg[u] for u in H1)
                assert E == h2 + Z, (name, c, v, E, h2, Z)
                m = n - 1 - deg[v]
                slack = h2 - caro_wei_floor(m)
                assert slack >= 0, (name, c, v, h2, m, caro_wei_floor(m))
                min_caro_slack = slack if min_caro_slack is None else min(min_caro_slack, slack)
                sum_h2 += h2
                single_identities += 1
            assert n * E == sum_h2 + sum(d * d for d in deg)
            # Same constructive upper bound applies at these smaller orders,
            # since every anti-neighbourhood has at most 48 vertices.
            phi_lower_bounds.append(sum_h2 - 120 * n)

        for S in combinations(range(4), 2):
            S = set(S)
            adj = [[i != j and M[i][j] in S for j in range(n)] for i in range(n)]
            deg = [sum(row) for row in adj]
            E = sum(deg) // 2
            for v in range(n):
                H1 = [u for u in range(n) if adj[v][u]]
                H2 = [u for u in range(n) if u != v and not adj[v][u]]
                e1 = induced_edges(adj, H1)
                h2 = induced_edges(adj, H2)
                d = deg[v]
                naive = h2 + d * d + sum(deg[u] - d for u in H1)
                assert E == naive - e1, (name, S, v, E, naive, e1)
                naive_pair_roots += int(e1 != 0)
                max_pair_H1_edges = max(max_pair_H1_edges, e1)
                pair_identities += 1
        results[name] = {
            "n": n,
            "single_colour_identities": single_identities,
            "corrected_pair_union_identities": pair_identities,
            "pair_union_roots_where_paper_form_fails": naive_pair_roots,
            "max_internal_H1_edges_in_pair_union": max_pair_H1_edges,
            "minimum_H2_Caro_Wei_slack": min_caro_slack,
            "phi_lower_bounds_by_colour_using_e_min_le_120": phi_lower_bounds,
        }
    return results


def main():
    report = {
        "small_graph_exhaustion": small_graph_checks(),
        "constructive_catalogue_bound": clebsch_catalogue_bound(),
        "K58_arithmetic": k58_deficit_check(),
        "repository_artifact_checks": artifact_checks(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
