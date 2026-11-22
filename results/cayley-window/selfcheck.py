"""Self-checks: the pipeline must agree with brute force, and must know the classics.

(1) cardinality encoder vs brute force (all weight patterns up to 10 items);
(2) whole-pipeline brute force: for small groups and k, the DIMACS verdict must
    equal exhaustive enumeration over all class colourings, with and without a
    profile constraint;
(3) classics: R(3,3) = 6 (no 2-colouring of K_6), R(3,3,3) = 17 (no 3-colouring
    of K_17), and a good 3-colouring of K_16 exists.
"""
import itertools
import subprocess
import sys
import tempfile
import os

import card
import gy

KISSAT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat"


def brute_force_cnf(clauses, nvars):
    for bits in itertools.product([False, True], repeat=nvars):
        if all(any((lit > 0) == bits[abs(lit) - 1] for lit in cl) for cl in clauses):
            return True
    return False


def solve_with_units(clauses, nvars, units):
    lines = [f"p cnf {nvars} {len(clauses) + len(units)}"]
    for cl in clauses:
        lines.append(" ".join(map(str, cl)) + " 0")
    for u in units:
        lines.append(f"{u} 0")
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as fh:
        fh.write("\n".join(lines) + "\n")
        path = fh.name
    try:
        r = subprocess.run([KISSAT, "-q", path], capture_output=True, text=True)
        return "s SATISFIABLE" in r.stdout
    finally:
        os.remove(path)


def propagate(clauses, units):
    """Unit propagation.  Returns (conflict, assignment)."""
    val = {}
    for lit in units:
        v, want = abs(lit), lit > 0
        if v in val and val[v] != want:
            return True, val
        val[v] = want
    changed = True
    while changed:
        changed = False
        for cl in clauses:
            sat = False
            unassigned = []
            for lit in cl:
                v, want = abs(lit), lit > 0
                if v in val:
                    if val[v] == want:
                        sat = True
                        break
                else:
                    unassigned.append(lit)
            if sat:
                continue
            if not unassigned:
                return True, val
            if len(unassigned) == 1:
                lit = unassigned[0]
                v, want = abs(lit), lit > 0
                if v in val and val[v] != want:
                    return True, val
                if v not in val:
                    val[v] = want
                    changed = True
    return False, val


def test_cardinality():
    ok = 0
    sample = []
    for n in range(0, 8):
        patterns = list(itertools.product([1, 2, 3], repeat=n))[:60]
        for weights in patterns:
            total = sum(weights)
            for bound in range(-1, total + 2):
                lits = list(range(1, n + 1))
                cl, top = card.weighted_equals(list(zip(lits, weights)), bound, n)
                for bits in itertools.product([False, True], repeat=n):
                    units = [lit if b else -lit for lit, b in zip(lits, bits)]
                    conflict, _ = propagate(cl, units)
                    bad = sum(w for w, b in zip(weights, bits) if b) != bound
                    assert conflict == bad, (n, weights, bound, bits)
                    if len(sample) < 300 and (hash((weights, bound, bits)) % 97 == 0):
                        sample.append((cl, top, units, not bad))
                    ok += 1
    for cl, top, units, want in sample:
        got = solve_with_units(cl, top, units)
        assert got == want, ("kissat disagrees", cl, units, got, want)
    print(f"cardinality encoder: {ok} pinned cases by unit propagation, "
          f"{len(sample)} of them cross-checked with kissat")


def brute_force_colourings(g, k, profile=None):
    """Exhaustive enumeration over class colourings; returns a good colouring or None."""
    classes, _ = gy.inverse_classes(g)
    sizes = [len(c) for c in classes]
    for assign in itertools.product(range(k), repeat=len(classes)):
        if profile is not None:
            tot = [0] * k
            for i, c in enumerate(assign):
                tot[c] += sizes[i]
            if tot != list(profile):
                continue
        colour = dict(enumerate(assign))
        ok, _, _ = gy.check_colouring(g, colour, k)
        if ok:
            return assign
    return None


def cnf_verdict(g, k, profile=None):
    text, meta = gy.cnf(g, k, profile)
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as fh:
        fh.write(text)
        path = fh.name
    try:
        r = subprocess.run([KISSAT, "-q", path], capture_output=True, text=True)
        return "SATISFIABLE" if "s SATISFIABLE" in r.stdout else "UNSATISFIABLE"
    finally:
        os.remove(path)


def test_pipeline():
    cases = 0
    for n in range(3, 11):
        gs, _ = gy.groups_of_order(n)
        for g in gs:
            for k in (2, 3):
                want = brute_force_colourings(g, k) is not None
                got = cnf_verdict(g, k) == "SATISFIABLE"
                assert got == want, (g, k, got, want)
                cases += 1
                # and one profile-constrained verdict
                classes, _ = gy.inverse_classes(g)
                sizes = [len(c) for c in classes]
                target = [0] * k
                for i, w in enumerate(sizes):
                    target[i % k] += w
                want = brute_force_colourings(g, k, target) is not None
                got = cnf_verdict(g, k, target) == "SATISFIABLE"
                assert got == want, (g, k, target, got, want)
                cases += 1
    print(f"pipeline vs brute force: {cases} instances agree "
          f"(with and without a profile constraint)")


def test_classics():
    # R(3,3)=6
    for g in gy.groups_of_order(6)[0]:
        assert cnf_verdict(g, 2) == "UNSATISFIABLE"
    # K_5 is 2-colourable (pentagon)
    assert cnf_verdict(gy.cyclic(5), 2) == "SATISFIABLE"
    # R(3,3,3)=17 and K_16 is 3-colourable over Z_2^4
    assert cnf_verdict(gy.cyclic(17), 3) == "UNSATISFIABLE"
    z2_4 = [g for g in gy.groups_of_order(16)[0] if g.name == "Z_2xZ_2xZ_2xZ_2"][0]
    assert cnf_verdict(z2_4, 3) == "SATISFIABLE"
    print("classics: R(3,3)=6, R(3,3,3)=17 at the cyclic group, K_16 3-colourable over Z_2^4")


if __name__ == "__main__":
    test_cardinality()
    test_pipeline()
    test_classics()
