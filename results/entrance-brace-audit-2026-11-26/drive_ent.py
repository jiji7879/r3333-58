"""Enumerate, deduplicate, consistency-check and time the entrance cases."""
import hashlib
import itertools
import os
import subprocess
import sys
import time

import entcases as E
import orbits as O
from gluing import template

REPO = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.scratch', 'ent')
os.makedirs(OUT, exist_ok=True)
AUTS = {k: O.auts(k) for k in ('U', 'T')}


def supports_for(kind, c, pal):
    """Orbit representatives of the reference-admitting supports of size 5."""
    mat = template(16, kind)
    palette = sorted(set(range(4)) - {c})
    ents = []
    for T in itertools.combinations(range(16), 5):
        lab = E.S.reference_labelling(lambda u, v: palette[mat[u][v]], T, c, pal)
        if lab is not None:
            ents.append((tuple(T), tuple(lab)))
    reps, _ = O.orbits(ents, AUTS[kind])
    return reps


def supports_for4(kind, c, pal):
    mat = template(16, kind)
    palette = sorted(set(range(4)) - {c})
    ents = []
    for T in itertools.combinations(range(16), 4):
        lab = E.S.reference_labelling(lambda u, v: palette[mat[u][v]], T, c, pal)
        if lab is not None:
            ents.append((tuple(T), tuple(lab)))
    reps, _ = O.orbits(ents, AUTS[kind])
    return reps


def unit_check(facts):
    """Every edge must receive at most one colour among the positive facts."""
    seen = {}
    for l in facts:
        idx, col = (abs(l) - 1) // 4, (abs(l) - 1) % 4
        if l > 0:
            if idx in seen and seen[idx] != col:
                return False
            seen[idx] = col
    return True


def enumerate_cases(kinds, c_p, shape):
    """shape = support sizes for the three colours != c_p, in increasing colour order."""
    others = [d for d in range(4) if d != c_p]
    pal = sorted(others)
    foreign = [0, 1]
    free = [d for d in others if d not in foreign][0]
    sizes = dict(zip(others, shape))
    sup = {}
    for c in foreign:
        sup[c] = supports_for(kinds[c], c, pal) if sizes[c] == 5 else supports_for4(kinds[c], c, pal)
    free_vertices = tuple(E.GROUPS[free][:sizes[free]])
    out = []
    for r0 in sup[0]:
        for r1 in sup[1]:
            # r0[1]/r1[1] are template POSITIONS; translate to actual vertices
            g0 = E.GROUPS[0]
            g1 = E.GROUPS[1]
            labs0 = ([tuple(g0[q] for q in lab)
                      for lab in (E.dihedral(r0[1]) if sizes[0] == 5 else [r0[1]])])
            labs1 = ([tuple(g1[q] for q in lab)
                      for lab in (E.dihedral(r1[1]) if sizes[1] == 5 else [r1[1]])])
            for lab0 in labs0:
                for lab1 in labs1:
                    labellings = {0: lab0, 1: lab1, free: free_vertices}
                    n = 1 + sum(len(v) for v in labellings.values())
                    tsize = 16 if n == 16 else 15
                    for bk in ('U', 'T'):
                        for base in range(tsize):
                            try:
                                facts, brace, _ = E.case_facts(
                                    c_p, E.GROUPS[c_p][-1], labellings, bk, base)
                            except AssertionError:
                                continue
                            if not unit_check(facts):
                                continue
                            key = hashlib.sha256(
                                b' '.join(str(l).encode() for l in sorted(facts))).hexdigest()
                            out.append((key, facts))
    seen, uniq = set(), []
    for key, facts in out:
        if key in seen:
            continue
        seen.add(key)
        uniq.append((key, facts))
    return sorted(uniq), len(out)


if __name__ == '__main__':
    for kinds in (('U', 'U'), ('U', 'T'), ('T', 'T')):
        for c_p in (2, 3):
            t0 = time.time()
            uniq, raw = enumerate_cases(kinds, c_p, (5, 5, 5))
            print('%s p-in-R%d shape (5,5,5): raw %d, distinct %d  (%.1fs)'
                  % (''.join(kinds), c_p, raw, len(uniq), time.time() - t0), flush=True)
