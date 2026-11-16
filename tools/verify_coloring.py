#!/usr/bin/env python3
"""Independent verifier for triangle-free (monochromatic-triangle-free) edge colourings.

Usage:
    python3 tools/verify_coloring.py FILE

FILE format: first line "n k" (n vertices, k colours), then n lines of n integers
(entry (i,j) = colour of edge {i,j}, 0<=c<k; diagonal can be 0 or -1 and is ignored).

Exit status 0 iff the colouring is valid: symmetric and no monochromatic triangle.
Prints the number of monochromatic triangles found and one example if any.
"""
import sys

def load(path):
    with open(path) as f:
        toks = f.read().split()
    n, k = int(toks[0]), int(toks[1])
    vals = list(map(int, toks[2:2 + n * n]))
    if len(vals) != n * n:
        raise SystemExit(f"bad file: expected {n*n} entries, got {len(vals)}")
    M = [vals[i * n:(i + 1) * n] for i in range(n)]
    return n, k, M

def check(n, k, M):
    for i in range(n):
        for j in range(n):
            if i != j:
                if not (0 <= M[i][j] < k):
                    return 1, f"colour out of range at ({i},{j}): {M[i][j]}", None
                if M[i][j] != M[j][i]:
                    return 1, f"asymmetric at ({i},{j})", None
    bad = []
    for i in range(n - 2):
        Mi = M[i]
        for j in range(i + 1, n - 1):
            c = Mi[j]
            Mj = M[j]
            for l in range(j + 1, n):
                if c == Mj[l] and c == Mi[l]:
                    bad.append((i, j, l, c))
                    if len(bad) > 1000:
                        return 1, f"more than 1000 monochromatic triangles (e.g. {bad[:3]})", bad
    if bad:
        return 1, f"{len(bad)} monochromatic triangles, e.g. {bad[:5]}", bad
    return 0, f"VALID: {n} vertices, {k} colours, no monochromatic triangle", None

def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    n, k, M = load(sys.argv[1])
    code, msg, _ = check(n, k, M)
    print(msg)
    return code

if __name__ == "__main__":
    sys.exit(main())
