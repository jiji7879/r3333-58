"""Check a repo `.col` artefact against the Cayley claim at n = 50.

A vertex-transitive colouring has the same colour-degree profile at every vertex, so a
good colouring of K_50 whose colour-0 degrees are not all equal is not Cayley over any
group of order 50 -- which is exactly what the abelian UNSAT instances say.  This checks
`artifacts/k50_blockcayley_Z4xZ4_m4.col` from the artefact alone (no repo code).
"""
import itertools
import sys


def load(path):
    with open(path) as fh:
        n, k = map(int, fh.readline().split())
        rows = [list(map(int, fh.readline().split())) for _ in range(n)]
    assert all(len(r) == n for r in rows)
    return n, k, rows


def main(path):
    n, k, a = load(path)
    sym = all(a[i][j] == a[j][i] for i in range(n) for j in range(n))
    diag = all(a[i][i] == 0 for i in range(n))
    bad = 0
    for x, y, z in itertools.combinations(range(n), 3):
        if a[x][y] == a[y][z] == a[z][x]:
            bad += 1
    print(f"{path}: n={n} k={k} symmetric={sym} zero diagonal={diag} "
          f"triangles={n * (n - 1) * (n - 2) // 6} monochromatic={bad}")
    profiles = {}
    for v in range(n):
        prof = tuple(sum(1 for u in range(n) if u != v and a[v][u] == c)
                     for c in range(k))
        profiles.setdefault(prof, 0)
        profiles[prof] += 1
    print("colour-degree profiles (sum = n-1 = 49):")
    for prof, cnt in sorted(profiles.items()):
        print(f"  {prof}  x{cnt}")
    print(f"vertex-transitive? {len(profiles) == 1} "
          f"(a vertex-transitive colouring has one profile)")
    if len(profiles) > 1:
        print("=> NOT vertex-transitive => not Cayley over any group of order 50")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1
         else "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/"
              "repo/artifacts/k50_blockcayley_Z4xZ4_m4.col")
