"""Standalone verifier for out/hall_certificates.json.

Reads only the .wit file and the certificate; shares no code with the search.
Checks, for each certificate:
  * I and J are colour-0 independent sets, |I| = 15
  * S subset of J \\ I and S is colour-0 independent
  * |N_0(S) cap I| < |S| - 1        (the Hall inequality fails)
"""
import sys, json, os

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"

def load(path):
    words, pairs, arms = {}, {}, {}
    for ln in open(path):
        t = ln.split()
        if not t or t[0].startswith("#"):
            continue
        if t[0] == "word":
            words[int(t[1])] = tuple(map(int, t[2:]))
        elif t[0] == "pair":
            pairs[(int(t[1]), int(t[2]))] = int(t[3])
        elif t[0] == "arm":
            arms[int(t[1])] = list(map(int, t[2:]))
    return words, pairs, arms

def colour(words, pairs, n, u, v):
    """Edge colour, or None if not determined at the pair level."""
    if u[0] == 'r' and v[0] == 'r':
        return None
    if u[0] == 'r' or v[0] == 'r':
        o = v if u[0] == 'r' else u
        return 0 if o[0] == 'a' else None
    if u[0] == 'a' and v[0] == 'a':
        return None
    if u[0] == 'x' and v[0] == 'x':
        a, b = sorted([u[1], v[1]])
        return pairs.get((a, b))
    if u[0] == 'x':
        u, v = v, u
    return words[v[1]][u[1]]

def indep(words, pairs, n, vs):
    for i in range(len(vs)):
        for j in range(i + 1, len(vs)):
            if colour(words, pairs, n, vs[i], vs[j]) == 0:
                return False
    return True

def check(path, cert, tag):
    words, pairs, arms = load(path)
    n = len(next(iter(words.values())))
    I = [tuple(v) for v in cert["I"]]
    J = [tuple(v) for v in cert["J"]]
    S = [tuple(v) for v in cert["S"]]
    errs = []
    if len(I) != 15:
        errs.append("|I| != 15")
    if not indep(words, pairs, n, I):
        errs.append("I is not colour-0 independent")
    if not indep(words, pairs, n, J):
        errs.append("J is not colour-0 independent")
    if not indep(words, pairs, n, S):
        errs.append("S is not colour-0 independent")
    if not set(S) <= set(J) - set(I):
        errs.append("S is not a subset of J \\ I")
    Nb = {y for s in S for y in I if colour(words, pairs, n, s, y) == 0}
    if not (len(Nb) < len(S) - 1):
        errs.append("|N0(S) cap I| = %d is not < |S|-1 = %d" % (len(Nb), len(S) - 1))
    print("  %-6s |I|=%2d |J|=%2d |S|=%2d |N0(S)capI|=%2d needs>=%2d  %s"
          % (tag, len(I), len(J), len(S), len(Nb), len(S) - 1,
             "OK" if not errs else "FAIL " + "; ".join(errs)))
    return not errs

certs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "hall_certificates.json")))
ok = True
for c in certs:
    print("%s  (%s)" % (c["witness"], c["path"]))
    ok &= check(os.path.join(ROOT, c["path"]), c["cert_general"], "gen")
    ok &= check(os.path.join(ROOT, c["path"]), c["cert_I_eq_A"], "I=A")
print()
print("ALL CERTIFICATES VERIFIED" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)
