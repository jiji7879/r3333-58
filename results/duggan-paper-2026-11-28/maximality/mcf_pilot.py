#!/usr/bin/env python3
"""Dependency-free controls for Duggan's maximal-clique-free (MCF) idea.

All paths passed to this program are explicit. It never writes outside the
requested output directory. For p=3, MCF in colour c says every non-c edge
{u,v} has a c-coloured two-path u-w-v. Greedy adding below does the reverse:
it adds precisely an edge for which no such path currently exists.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path


def edge_list(n):
    return list(itertools.combinations(range(n), 2))


def digest_matrix(m):
    return hashlib.sha256(json.dumps(m, separators=(",", ":")).encode()).hexdigest()


def load_col(path):
    tok = Path(path).read_text().split()
    n, k = map(int, tok[:2])
    vals = list(map(int, tok[2:]))
    assert len(vals) == n*n, "bad .col matrix length"
    m = [vals[i*n:(i+1)*n] for i in range(n)]
    assert n == len(m) and k == 4
    return m


def save_col(path, m):
    n = len(m)
    Path(path).write_text(f"{n} 4\n" + "\n".join(" ".join(map(str, row)) for row in m) + "\n")


def bad_triangles(m, limit=None):
    n = len(m)
    ans = []
    for i, j, k in itertools.combinations(range(n), 3):
        if m[i][j] == m[i][k] == m[j][k]:
            ans.append((i, j, k, m[i][j]))
            if limit is not None and len(ans) >= limit:
                break
    return ans


def assert_symmetric(m):
    n = len(m)
    for i in range(n):
        assert len(m[i]) == n
        for j in range(n):
            if i != j:
                assert 0 <= m[i][j] < 4 and m[i][j] == m[j][i]


def missing_paths(m, c):
    """Non-c edges which could still be added without a c triangle."""
    n = len(m)
    ans = []
    for u, v in edge_list(n):
        if m[u][v] == c:
            continue
        if not any(m[u][w] == c and m[v][w] == c
                   for w in range(n) if w != u and w != v):
            ans.append((u, v))
    return ans


def degrees(m, c):
    return [sum(m[v][w] == c for w in range(len(m)) if w != v)
            for v in range(len(m))]


def root_signature(m):
    return tuple(m[0][v] for v in range(1, len(m)))


def root_profile(m):
    return tuple(degrees(m, c)[0] for c in range(4))


def maximize(m, c):
    """Closure used in the existential MCF reduction, with an auditable trace."""
    work = [row[:] for row in m]
    n = len(work)
    steps = []
    changed = True
    while changed:
        changed = False
        for u, v in edge_list(n):
            old = work[u][v]
            if old == c:
                continue
            # No common c-neighbour <=> adding uv creates no c triangle.
            if any(work[u][w] == c and work[v][w] == c
                   for w in range(n) if w != u and w != v):
                continue
            work[u][v] = work[v][u] = c
            steps.append((u, v, old, c))
            changed = True
    return work, steps


def check_trace(source, steps, final, c):
    work = [row[:] for row in source]
    for pos, (u, v, old, new) in enumerate(steps):
        assert new == c and work[u][v] == work[v][u] == old and old != c
        assert not any(work[u][w] == c and work[v][w] == c
                       for w in range(len(work)) if w != u and w != v), pos
        work[u][v] = work[v][u] = c
    assert work == final
    assert not bad_triangles(final)
    assert not missing_paths(final, c)


def incidence_records(m, c, cap=16):
    n = len(m)
    deg = degrees(m, c)
    rows = []
    for v in range(n):
        cover = sum(deg[w]-1 for w in range(n) if w != v and m[v][w] == c)
        rows.append({"vertex": v, "nonneighbours": n-1-deg[v],
                     "path_capacity": cover, "degree": deg[v]})
    if not missing_paths(m, c):
        assert all(r["nonneighbours"] <= r["path_capacity"] for r in rows)
    return {"minimum_c_degree": min(deg), "maximum_c_degree": max(deg),
            "cap": cap, "global_min_degree_bound_valid":
                all(n-1 <= (cap+1)*d for d in deg), "rows": rows}


def tuple_matrix(values, n):
    es = edge_list(n)
    m = [[0]*n for _ in range(n)]
    for (u, v), c in zip(es, values):
        m[u][v] = m[v][u] = c
    return m


def good_tuples(n):
    """Exhaustive backtracking over 4^(n choose 2), pruning partial triangles."""
    es = edge_list(n)
    eidx = {e: i for i, e in enumerate(es)}
    incident = [[] for _ in es]
    for i, j, k in itertools.combinations(range(n), 3):
        tri = (eidx[i, j], eidx[i, k], eidx[j, k])
        for q in tri:
            incident[q].append(tri)
    values = [-1]*len(es)
    def visit(depth):
        if depth == len(es):
            yield tuple(values)
            return
        for c in range(4):
            values[depth] = c
            if any(values[a] == values[b] == values[d] == c
                   for a, b, d in incident[depth]):
                continue
            yield from visit(depth+1)
        values[depth] = -1
    yield from visit(0)


def exhaustive(n, out):
    assert n == 5, "the shipped exhaustive control is deliberately K5"
    total_good = 0
    max_counts = [0]*4
    all_stars, max_stars = set(), [set() for _ in range(4)]
    all_profiles, max_profiles = set(), [set() for _ in range(4)]
    examples = {}
    greedy_checked = 0
    maximal_incidence_vertices = 0
    for values in good_tuples(n):
        total_good += 1
        m = tuple_matrix(values, n)
        star, profile = root_signature(m), root_profile(m)
        all_stars.add(star)
        all_profiles.add(profile)
        examples.setdefault(star, values)
        if total_good % 100 == 1:
            closed, steps = maximize(m, 0)
            check_trace(m, steps, closed, 0)
            greedy_checked += 1
        for c in range(4):
            if not missing_paths(m, c):
                max_counts[c] += 1
                deg = degrees(m, c)
                for v in range(n):
                    assert n-1 <= sum(deg[w] for w in range(n)
                                      if w != v and m[v][w] == c)
                    maximal_incidence_vertices += 1
                max_stars[c].add(star)
                max_profiles[c].add(profile)
    record = {"n": n, "good_colourings": total_good,
              "maximal_by_colour": max_counts,
              "distinct_root_stars": len(all_stars),
              "distinct_root_profiles": len(all_profiles),
              "greedy_closures_checked": greedy_checked,
              "maximal_incidence_vertices_checked": maximal_incidence_vertices,
              "maximal_incidence_violations": 0,
              "global_existence_equivalence": {}, "counterexamples": {}}
    for c in range(4):
        record["global_existence_equivalence"][str(c)] = (
            (total_good > 0) == (max_counts[c] > 0))
        missing_star = sorted(all_stars-max_stars[c])
        missing_profile = sorted(all_profiles-max_profiles[c])
        record["counterexamples"][str(c)] = {
            "root_stars_lost_under_same_star_MCF": len(missing_star),
            "four_colour_root_stars_lost": sum(len(set(s)) == 4 for s in missing_star),
            "root_profiles_lost_under_same_profile_MCF": len(missing_profile),
            "lost_profiles_with_positive_selected_degree": sum(p[c] > 0 for p in missing_profile)}
        if c == 0 and missing_star:
            eligible = [s for s in missing_star if 0 in s] or missing_star
            star = min(eligible, key=lambda s: (-len(set(s)), max(s.count(c) for c in range(4)), s))
            source = examples[star]
            record["chosen_frozen_control"] = {
                "colour": c, "star": star, "source_good_colouring": source,
                "source_profile": root_profile(tuple_matrix(source, n)),
                "note": "same-star MCF excludes every completion by exhaustive enumeration"}
            save_col(out/"frozen_source.col", tuple_matrix(source, n))
            base_top, base = host_cnf(n)
            units = star_units(star)
            top, mcf = mcf_cnf(n, c, base_top)
            write_cnf(out/"frozen_baseline.cnf", base_top, base+units)
            write_cnf(out/"frozen_mcf.cnf", top, base+mcf+units)
    out.joinpath("exhaustive.json").write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps(record, indent=2))
    assert total_good > 0
    assert all(record["global_existence_equivalence"].values())
    assert "chosen_frozen_control" in record


def host_cnf(n):
    es = edge_list(n)
    def lit(u, v, c):
        if u > v:
            u, v = v, u
        return 4*es.index((u, v))+c+1
    clauses = []
    for i in range(len(es)):
        opts = [4*i+c+1 for c in range(4)]
        clauses.append(opts)
        clauses.extend([-a, -b] for a, b in itertools.combinations(opts, 2))
    for i, j, k in itertools.combinations(range(n), 3):
        for c in range(4):
            clauses.append([-lit(i, j, c), -lit(i, k, c), -lit(j, k, c)])
    return 4*len(es), clauses


def mcf_cnf(n, c, base_top):
    """Duggan's alternate encoding, specialized to p=3 and one colour.

    y[e,w] <-> (uw=c and vw=c), and x[uv,c] OR OR_w y[e,w].
    """
    es = edge_list(n)
    def lit(u, v, cc):
        if u > v:
            u, v = v, u
        return 4*es.index((u, v))+cc+1
    top = base_top
    clauses = []
    ycount = 0
    for u, v in es:
        ys = []
        for w in range(n):
            if w in (u, v):
                continue
            top += 1
            ycount += 1
            y = top
            ys.append(y)
            a, b = lit(u, w, c), lit(v, w, c)
            clauses.extend(([-y, a], [-y, b], [-a, -b, y]))
        clauses.append([lit(u, v, c)]+ys)
    assert top == base_top+ycount
    return top, clauses


def star_units(star):
    n = len(star)+1
    es = edge_list(n)
    return [[4*es.index((0, v))+c+1] for v, c in enumerate(star, 1)]


def write_cnf(path, top, clauses):
    Path(path).write_text(f"p cnf {top} {len(clauses)}\n" +
                          "".join(" ".join(map(str, cl))+" 0\n" for cl in clauses))


def encode(n, out):
    top, base = host_cnf(n)
    mcf_top, extra = mcf_cnf(n, 0, top)
    write_cnf(out/"unpinned_baseline.cnf", top, base)
    write_cnf(out/"unpinned_mcf.cnf", mcf_top, base+extra)
    rec = {"n": n, "physical_variables": top, "base_clauses": len(base),
           "mcf_variables": mcf_top, "mcf_auxiliary_variables": mcf_top-top,
           "mcf_extra_clauses": len(extra), "long_MCF_clauses": n*(n-1)//2,
           "long_MCF_clause_length": n-1}
    out.joinpath("encoding.json").write_text(json.dumps(rec, indent=2)+"\n")
    print(json.dumps(rec, indent=2))


def read_dimacs(path):
    toks = []
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith("c") or line.startswith("p"):
            continue
        toks.extend(map(int, line.split()))
    clauses, cur = [], []
    for t in toks:
        if t == 0:
            clauses.append(cur)
            cur = []
        else:
            cur.append(t)
    assert not cur
    return clauses


def verify_solution(cnf, sol, maximal_colour=None):
    vals = set()
    status = None
    for line in Path(sol).read_text().splitlines():
        if line.startswith("s "):
            status = line
        if line.startswith("v "):
            vals.update(int(x) for x in line.split()[1:] if int(x) != 0)
    assert status and "SATISFIABLE" in status and "UNSAT" not in status, status
    assert all(-v not in vals for v in vals)
    clauses = read_dimacs(cnf)
    for i, cl in enumerate(clauses):
        # CaDiCaL emits a full signed assignment: a literal is true iff present.
        assert any(v in vals for v in cl), (i, cl)
    import re
    match = re.search(r"_n(\d+)", Path(sol).stem)
    assert match, "solution name must contain _n<N>"
    n = int(match.group(1))
    m = [[0]*n for _ in range(n)]
    es = edge_list(n)
    for i, (u, v) in enumerate(es):
        cs = [c for c in range(4) if 4*i+c+1 in vals]
        assert len(cs) == 1
        m[u][v] = m[v][u] = cs[0]
    assert not bad_triangles(m)
    missing = len(missing_paths(m, maximal_colour)) if maximal_colour is not None else None
    if maximal_colour is not None:
        assert missing == 0
    out = Path(str(sol)+".col")
    save_col(out, m)
    print(json.dumps({"clauses_checked": len(clauses), "solution": str(sol),
                      "verified_colouring": str(out), "triangles": 0,
                      "maximal_colour": maximal_colour, "missing_paths": missing}))


def artifacts(out, paths):
    out.mkdir(exist_ok=True)
    records = []
    for raw in paths:
        path = Path(raw)
        source = load_col(path)
        assert_symmetric(source)
        n = len(source)
        triangles = bad_triangles(source, 5)
        if triangles:
            records.append({"file": str(path), "n": n, "valid": False,
                            "triangles_first": triangles,
                            "note": "invalid near-colouring: not used for closure validation"})
            continue
        assert not bad_triangles(source)
        for c in range(4):
            final, steps = maximize(source, c)
            check_trace(source, steps, final, c)
            inc = incidence_records(final, c)
            rec = {"source": str(path), "n": n, "colour": c,
                   "source_sha256_matrix": digest_matrix(source),
                   "final_sha256_matrix": digest_matrix(final),
                   "steps": len(steps), "steps_detail": steps,
                   "old_colours_removed": {str(old): sum(s[2] == old for s in steps)
                                            for old in range(4) if old != c},
                   "initial_missing_paths": len(missing_paths(source, c)),
                   "final_missing_paths": len(missing_paths(final, c)),
                   "source_root_profile": root_profile(source),
                   "final_root_profile": root_profile(final),
                   "incidence": inc}
            target = out/f"{path.stem}_max_c{c}.col"
            save_col(target, final)
            rec["output"] = str(target)
            records.append(rec)
    out.joinpath("artifact_results.json").write_text(json.dumps(records, indent=2)+"\n")
    compact = [{k: v for k, v in r.items() if k not in ("steps_detail", "incidence")} |
               ({"minimum_final_degree": r["incidence"]["minimum_c_degree"]}
                if "incidence" in r else {}) for r in records]
    print(json.dumps(compact, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("exhaustive")
    ex.add_argument("--n", type=int, default=5)
    ex.add_argument("--out", type=Path, required=True)
    en = sub.add_parser("encode")
    en.add_argument("--n", type=int, required=True)
    en.add_argument("--out", type=Path, required=True)
    ar = sub.add_parser("artifacts")
    ar.add_argument("--out", type=Path, required=True)
    ar.add_argument("paths", nargs="+")
    ve = sub.add_parser("verify-solution")
    ve.add_argument("cnf")
    ve.add_argument("solution")
    ve.add_argument("--maximal-colour", type=int)
    args = ap.parse_args()
    if args.cmd == "exhaustive":
        args.out.mkdir(exist_ok=True)
        exhaustive(args.n, args.out)
    elif args.cmd == "encode":
        args.out.mkdir(exist_ok=True)
        encode(args.n, args.out)
    elif args.cmd == "artifacts":
        artifacts(args.out, args.paths)
    else:
        verify_solution(args.cnf, args.solution, args.maximal_colour)


if __name__ == "__main__":
    main()
