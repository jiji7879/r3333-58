"""Calibration: alpha of every colour graph of every real colouring artefact.

Theorem (kernel-free): in a triangle-free 4-colouring of K_n with n >= 17, no
colour class is independent of size 17 (a 17-set with no colour-c edge is a
triangle-free 3-colouring of K_17, and R(3,3,3) = 17).  So alpha(G_c) <= 16.
If this fails on an artefact, either the artefact is not a valid colouring or
the graph construction is wrong.
"""
import sys, os, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mis import max_inset

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"

def load(path):
    toks = open(path).read().split()
    n, k = int(toks[0]), int(toks[1])
    vals = list(map(int, toks[2:2 + n * n]))
    M = [vals[i * n:(i + 1) * n] for i in range(n)]
    return n, k, M

def check(n, k, M):
    for i in range(n):
        for j in range(i + 1, n):
            if M[i][j] != M[j][i]:
                return "asymmetric at (%d,%d)" % (i, j)
    mono = 0
    for i in range(n):
        for j in range(i + 1, n):
            c = M[i][j]
            for l in range(j + 1, n):
                if M[i][l] == c and M[j][l] == c:
                    mono += 1
    return mono

out = []
for p in sorted(glob.glob(os.path.join(ROOT, "artifacts", "*.col"))):
    n, k, M = load(p)
    res = check(n, k, M)
    row = {"file": os.path.basename(p), "n": n, "k": k, "mono_triangles": res}
    if isinstance(res, str):
        row["note"] = res
        print(json.dumps(row)); out.append(row); continue
    alphas = []
    for c in range(k):
        adj = [0] * n
        for i in range(n):
            for j in range(n):
                if i != j and M[i][j] == c:
                    adj[i] |= 1 << j
        a, mask = max_inset(adj, n)
        alphas.append(a)
    row["alphas"] = alphas
    row["max_alpha"] = max(alphas)
    print(json.dumps(row))
    out.append(row)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "alpha_col.json"), "w"), indent=1)
