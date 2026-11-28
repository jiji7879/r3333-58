"""CAT58 / early-FKR attachment census driver (direction 4, member m4).

Runs, in order:

  A. template audit: the two K16 seeds U (untwisted / FKR T2) and T (twisted /
     FKR T1) as pinned in tools/color-resolved-wallcc/frozen/gluing.py, plus
     their 15-vertex deletions U^- and T^-; goodness, regularity, automorphism
     orders, weak isomorphism controls;
  B. transport witnesses for every nonempty subset of every template: an
     explicit seed automorphism carrying the subset to the retained
     representative, re-verified from scratch;
  C. reference calibration: FKR Table 5 (533 marked colourings) and Table 6
     (724 overlaps), per order, both exact; plus an independent Burnside
     cross-check of the marked counts;
  D. independent brute-force groupoid cross-check of a few overlap orders
     (explicit union-find over labelled triples, copy swap included);
  E. the new 15/15 census (CAT58's second same-degree family);
  F. the K58 early-census verdict against the declared 10^4 engineering cut-off;
  G. negative/positive controls.

No SAT solver is used anywhere in this file.
"""
import hashlib
import itertools
import json
import pathlib
import sys
import time

import templates as T
import census_generic as G

TABLE5 = [2, 3, 7, 21, 34, 66, 83, 99, 83, 66, 34, 21, 7, 3, 2, 2]
TABLE6 = [3, 7, 20, 54, 74, 109, 110, 116, 91, 69, 35, 22, 7, 3, 2, 2]
CUTOFF = 10000


def per_order(d, n):
    return [d.get(k, 0) for k in range(1, n + 1)]


def deletion(col, drop=0):
    idx = [v for v in range(len(col)) if v != drop]
    return tuple(tuple(col[u][v] for v in idx) for u in idx)


def burnside_marked(seed):
    """Independent check: #orbits of k-subsets under the weak group, by Burnside."""
    n = seed.n
    wg = seed.weak
    tot = [0] * (n + 1)
    for phi, _ in wg:
        seen = [False] * n
        lengths = []
        for i in range(n):
            if seen[i]:
                continue
            j, ln = i, 0
            while not seen[j]:
                seen[j] = True
                j = phi[j]
                ln += 1
            lengths.append(ln)
        ways = [0] * (n + 1)
        ways[0] = 1
        for ln in lengths:
            for k in range(n, ln - 1, -1):
                ways[k] += ways[k - ln]
        for k in range(n + 1):
            tot[k] += ways[k]
    assert all(t % len(wg) == 0 for t in tot)
    return [t // len(wg) for t in tot]


_SUB = {}


def submatrix(seed, mask):
    key = (seed.name, mask)
    if key not in _SUB:
        pos = tuple(v for v in range(seed.n) if mask >> v & 1)
        _SUB[key] = G.induced(seed.col, pos)
    return _SUB[key]


def brute_force_overlaps(sa, sb, same_seed, k, ind=None):
    """Independent overlap count at one order by explicit union-find on triples.

    The two seed copies are interchangeable only for the same-seed family; that
    copy swap is included here explicitly, which the groupoid of seed
    automorphisms alone does not generate.
    """
    triples = []
    seen_sub = set()
    for A in range(1, 1 << sa.n):
        if bin(A).count("1") != k:
            continue
        for B in range(1, 1 << sb.n):
            if bin(B).count("1") != k:
                continue
            for th in G.named_isos(submatrix(sa, A), submatrix(sb, B)):
                triples.append((A, B, th))
            seen_sub.add((sa.name, A))
    if not triples:
        return 0

    def gens(seed):
        out = []
        for g in seed.aut_gens:
            out.append(g)
        return out

    def apply(t, g1, g2):
        A, B, th = t
        A2 = G.mask_image(sa.allbit[g1], A)
        B2 = G.mask_image(sb.allbit[g2], B)
        posA = tuple(v for v in range(sa.n) if A >> v & 1)
        posB = tuple(v for v in range(sb.n) if B >> v & 1)
        idxA2 = {v: n for n, v in enumerate(sorted(g1[v] for v in posA))}
        idxB2 = {v: n for n, v in enumerate(sorted(g2[v] for v in posB))}
        p1 = tuple(idxA2[g1[v]] for v in posA)
        p2 = tuple(idxB2[g2[v]] for v in posB)
        inv1 = G.permutation_inverse(p1)
        return (A2, B2, tuple(p2[th[inv1[i]]] for i in range(k)))

    idn = tuple(range(sa.n))
    g1s = gens(sa) + [idn]
    g2s = gens(sb) + [idn]
    S = set(triples)
    seen = set()
    classes = 0
    for t0 in triples:
        if t0 in seen:
            continue
        classes += 1
        seen.add(t0)
        frontier = [t0]
        while frontier:
            t = frontier.pop()
            for g1 in g1s:
                for g2 in g2s:
                    nt = apply(t, g1, g2)
                    assert nt in S
                    if nt not in seen:
                        seen.add(nt)
                        frontier.append(nt)
            if same_seed and sa.name == sb.name:
                A, B, th = t
                sw = (B, A, G.permutation_inverse(th))
                assert sw in S
                if sw not in seen:
                    seen.add(sw)
                    frontier.append(sw)
    return classes


def main():
    t0 = time.process_time()
    out = {"member": "m4", "direction": "early FKR attachment-cover feasibility/calibration"}
    log = []

    # ---------------- A. templates ----------------
    cols = {"U16": T.matrix("U"), "T16": T.matrix("T")}
    cols["U15"] = deletion(cols["U16"])
    cols["T15"] = deletion(cols["T16"])
    seeds = {name: G.Seed(name, col) for name, col in cols.items()}
    audit = {}
    for name, s in seeds.items():
        good = all(s.col[u][v] != s.col[u][w] or s.col[u][v] != s.col[v][w]
                   for u, v, w in itertools.combinations(range(s.n), 3))
        degs = [tuple(sum(1 for v in range(s.n) if v != u and s.col[u][v] == c)
                      for c in range(3)) for u in range(s.n)]
        audit[name] = {
            "order": s.n, "triangle_free": good,
            "degree_triples": sorted({d for d in degs}),
            "aut_named_order": len(s.aut), "weak_group_order": len(s.weak),
            "weak_group_order_over_aut": len(s.weak) // len(s.aut),
            "strong_subset_classes": sum(len(v) for v in s.strong.values()),
        }
    audit["controls"] = {
        "U16_weak_iso_T16": G.named_isos(cols["U16"], cols["T16"]) != [],
        "U15_weak_iso_T15": any(
            G.named_isos(tuple(tuple(pi[cols["U15"][u][v]] for v in range(15))
                               for u in range(15)), cols["T15"]) for pi in G.S3),
        "frozen_gluing_asserts_160_32_10_2": [len(seeds[n].aut) for n in
                                              ("U16", "T16", "U15", "T15")] == [160, 32, 10, 2],
    }
    out["A_templates"] = audit
    log.append(f"A templates audited ({time.process_time()-t0:.1f} s)")

    # ---------------- B. transport witnesses ----------------
    wit = {}
    for name, s in seeds.items():
        failures = s.check_witnesses()
        wit[name] = {"subsets": len(s.witness), "failures": len(failures),
                     "retained_representatives": len(s.reps())}
        assert not failures, (name, failures[:5])
    out["B_transport_witnesses"] = wit
    log.append(f"B transport witnesses verified for {sum(v['subsets'] for v in wit.values())} subsets")

    # ---------------- C. reference calibration ----------------
    mk = {name: G.marked_census(seeds[name]) for name in ("U16", "T16")}
    ref5 = [0] * 16
    for name in ("U16", "T16"):
        for k in range(1, 17):
            ref5[k - 1] += mk[name]["weak"].get(k, 0)
    burn5 = {}
    for name in ("U16", "T16"):
        burn5[name] = [b for b in burnside_marked(seeds[name])[1:17]]
    burn_sum = [a + b for a, b in zip(burn5["U16"], burn5["T16"])]
    assert ref5 == TABLE5, (ref5, TABLE5)
    assert burn_sum == TABLE5, (burn_sum, TABLE5)
    out["C_table5"] = {
        "printed": TABLE5, "reproduced_s3_quotient": ref5,
        "reproduced_burnside_independent": burn_sum,
        "per_seed_s3": {n: per_order(mk[n]["weak"], 16) for n in ("U16", "T16")},
        "per_seed_burnside": burn5,
        "match": ref5 == TABLE5 and burn_sum == TABLE5, "total": sum(ref5),
    }
    log.append(f"C Table 5 matched: {sum(ref5)} ({time.process_time()-t0:.1f} s)")

    fams = {}
    ind16 = {(s.name, c["mask"]): G.induced(s.col, c["pos"])
             for s in (seeds["U16"], seeds["T16"]) for kk in s.strong
             for c in s.strong[kk]}
    for name, (a, b) in (("U16/U16", ("U16", "U16")), ("U16/T16", ("U16", "T16")),
                         ("T16/T16", ("T16", "T16"))):
        fams[name] = G.overlap_census(seeds[a], seeds[b], same_seed=(a == b))
        log.append(f"   overlap family {name}: {fams[name]['weak_total']} weak classes "
                   f"({time.process_time()-t0:.1f} s)")
    ref6 = [0] * 16
    for ov in fams.values():
        for k in range(1, 17):
            ref6[k - 1] += ov["weak"].get(k, 0)
    assert ref6 == TABLE6, (ref6, TABLE6)
    out["C_table6"] = {
        "printed": TABLE6, "reproduced": ref6, "match": ref6 == TABLE6,
        "total": sum(ref6),
        "by_family": {n: {"weak_total": o["weak_total"], "strong_total": o["strong_total"],
                          "per_order": per_order(o["weak"], 16)}
                      for n, o in fams.items()},
    }
    log.append(f"C Table 6 matched: {sum(ref6)} ({time.process_time()-t0:.1f} s)")

    # ---------------- D. independent brute force ----------------
    bf = {}
    for (a, b, ss, ks) in (("U16", "U16", True, (1, 2)), ("U16", "T16", False, (1, 2)),
                           ("T16", "T16", True, (1, 2))):
        for k in ks:
            got = brute_force_overlaps(seeds[a], seeds[b], ss, k, ind16)
            bf[f"{a}/{b}/k{k}"] = got
    out["D_brute_force_crosscheck_16"] = {
        "counts": bf,
        "expected_strong_from_canonical_keys": {
            f"{a}/{b}/k{k}": fams[f"{a}/{b}"]["strong_per_order"].get(k, 0)
            for (a, b) in (("U16", "U16"), ("U16", "T16"), ("T16", "T16")) for k in (1, 2)},
    }
    assert all(bf[f"{a}/{b}/k{k}"] == fams[f"{a}/{b}"]["strong_per_order"].get(k, 0)
               for (a, b) in (("U16", "U16"), ("U16", "T16"), ("T16", "T16"))
               for k in (1, 2)), bf
    out["D_brute_force_crosscheck_16"]["match"] = True
    log.append(f"D brute-force cross-check ok ({time.process_time()-t0:.1f} s)")

    # ---------------- E. 15/15 census ----------------
    mk15 = {n: G.marked_census(seeds[n]) for n in ("U15", "T15")}
    marked15 = [0] * 15
    for n in ("U15", "T15"):
        for k in range(1, 16):
            marked15[k - 1] += mk15[n]["weak"].get(k, 0)
    burn15 = {n: burnside_marked(seeds[n])[1:16] for n in ("U15", "T15")}
    burn15_sum = [a + b for a, b in zip(burn15["U15"], burn15["T15"])]
    assert marked15 == burn15_sum, (marked15, burn15_sum)
    ov55 = {}
    ind15 = {(s.name, c["mask"]): G.induced(s.col, c["pos"])
             for s in (seeds["U15"], seeds["T15"]) for kk in s.strong
             for c in s.strong[kk]}
    for name, (a, b) in (("U15/U15", ("U15", "U15")), ("U15/T15", ("U15", "T15")),
                         ("T15/T15", ("T15", "T15"))):
        ov55[name] = G.overlap_census(seeds[a], seeds[b], same_seed=(a == b))
        log.append(f"   overlap family {name}: {ov55[name]['weak_total']} weak classes "
                   f"({time.process_time()-t0:.1f} s)")
    ov15 = [0] * 15
    for ov in ov55.values():
        for k in range(1, 16):
            ov15[k - 1] += ov["weak"].get(k, 0)
    bf15 = {}
    for (a, b, ss) in (("U15", "U15", True), ("U15", "T15", False), ("T15", "T15", True)):
        for k in (1, 2):
            bf15[f"{a}/{b}/k{k}"] = brute_force_overlaps(seeds[a], seeds[b], ss, k, ind15)
    assert all(bf15[f"{a}/{b}/k{k}"] == ov55[f"{a}/{b}"]["strong_per_order"].get(k, 0)
               for (a, b) in (("U15", "U15"), ("U15", "T15"), ("T15", "T15"))
               for k in (1, 2)), bf15
    out["E_census_15_15"] = {
        "marked_per_order_k1_to_15": marked15,
        "marked_total": sum(marked15),
        "marked_burnside_crosscheck": burn15_sum,
        "marked_burnside_match": marked15 == burn15_sum,
        "marked_per_seed": {n: per_order(mk15[n]["weak"], 15) for n in ("U15", "T15")},
        "overlaps_per_order_k1_to_15": ov15,
        "overlaps_total": sum(ov15),
        "overlaps_by_family": {n: {"weak_total": o["weak_total"],
                                   "strong_total": o["strong_total"],
                                   "per_order": per_order(o["weak"], 15)}
                               for n, o in ov55.items()},
        "brute_force_crosscheck_k1_k2": bf15,
        "brute_force_note": ("brute force enumerates the strong (named-colour) groupoid "
                             "including the copy swap, so it is compared with the strong "
                             "per-order counts; the S_3 layer then gives the weak counts"),
        "brute_force_match": True,
    }
    log.append(f"E 15/15 census done ({time.process_time()-t0:.1f} s)")

    # ---------------- F. K58 verdict ----------------
    def split(lst, s):
        return {"k1_k2_excluded_by_CAT58": sum(lst[:2]),
                "ordinary_3_to_14": sum(lst[2:14]) if s == 16 else sum(lst[2:14]),
                "adjacent_k_s-1": lst[s - 2],
                "high_overlap_k_s": lst[s - 1],
                "k_ge_3": sum(lst[2:])}

    s16, s15 = split(ref6, 16), split(ov15, 15)
    total = s16["k_ge_3"] + s15["k_ge_3"]
    out["F_k58_early_census"] = {
        "families": {"16/16": {"template_pairs": [["U16", "U16"], ["U16", "T16"],
                                                  ["T16", "T16"]],
                               "split": s16},
                     "15/15": {"template_pairs": [["U15", "U15"], ["U15", "T15"],
                                                  ["T15", "T15"]],
                               "split": s15}},
        "excluded_by_CAT58": "mixed 15/16 or 14/16 attachments: degrees differ",
        "normalised_early_census": total,
        "engineering_cutoff": CUTOFF,
        "below_cutoff": total < CUTOFF,
        "ratio_to_cutoff": round(total / CUTOFF, 3),
        "verdict": ("below the declared cut-off" if total < CUTOFF else
                    "ABOVE the declared 10^4 cut-off; the go criterion is not met"),
    }
    log.append(f"F early census {total} vs cut-off {CUTOFF}")

    # ---------------- G. controls ----------------
    ctrl = {}
    # G1: colour-permutation invariance of the whole census (positive control)
    def relabel(col, pi):
        return tuple(tuple(pi[col[u][v]] for v in range(len(col))) for u in range(len(col)))
    pi = (2, 0, 1)
    sU = G.Seed("U16pi", relabel(cols["U16"], pi))
    sT = G.Seed("T16pi", relabel(cols["T16"], pi))
    pi_census = G.marked_census(sU)["weak"]
    ctrl["colour_relabelled_U16_marked_matches"] = (
        per_order(pi_census, 16) == per_order(mk["U16"]["weak"], 16))
    pi_ov = G.overlap_census(sU, sT, same_seed=False)["weak"]
    ctrl["colour_relabelled_U16_T16_overlap_matches_724"] = (
        pi_ov == fams["U16/T16"]["weak"])
    # G2: a corrupted template must be detected (triangle inserted)
    bad = [list(r) for r in cols["U16"]]
    bad[0][1] = bad[1][0] = bad[0][2]
    bad[0][2] = bad[2][0] = bad[1][2]
    bad[1][2] = bad[2][1] = bad[0][1]
    tri = cols["U16"][0][1]
    bad[0][1] = bad[1][0] = tri
    bad[0][2] = bad[2][0] = tri
    bad[1][2] = bad[2][1] = tri
    ctrl["corrupted_template_has_triangle"] = not all(
        bad[u][v] != bad[u][w] or bad[u][v] != bad[v][w]
        for u, v, w in itertools.combinations(range(16), 3))
    # G3: omitting a seed or a family changes the counts (families are not redundant)
    ctrl["marked16_dropping_T"] = sum(mk["U16"]["weak"].values())
    ctrl["marked16_dropping_U"] = sum(mk["T16"]["weak"].values())
    ctrl["overlaps16_dropping_cross_family"] = sum(
        fams[f]["weak_total"] for f in ("U16/U16", "T16/T16"))
    # G4: the K62-excluded orders are nonempty at K58 (so they cannot be dropped)
    ctrl["k56_high_overlap_16_16"] = {"k15": ref6[14], "k16": ref6[15]}
    ctrl["k56_high_overlap_15_15"] = {"k14": ov15[13], "k15": ov15[14]}
    out["G_controls"] = ctrl
    assert ctrl["colour_relabelled_U16_marked_matches"]
    assert ctrl["corrupted_template_has_triangle"]

    out["cpu_seconds"] = round(time.process_time() - t0, 2)
    out["log"] = log
    here = pathlib.Path(__file__).resolve().parent
    for name in ("templates.py", "census_generic.py", "run_census.py"):
        p = here / name
        out.setdefault("script_sha256", {})[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
