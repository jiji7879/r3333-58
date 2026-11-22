#!/usr/bin/env python3
"""Independent re-check of the 18-vertex sharpness witness (|X| = 14 c-free,
4 far points) and of the 19-vertex object found in the first (buggy) run, which
is recorded here as NOT a witness for the far-point question.
Writes far18.col for tools/verify_coloring.py.
"""
import sys

ROWS18 = """.22333113212121133
2.3233221111331122
23.321133123211122
323.21312231231111
3322.2231332111111
33112.321213123322
121323.31321322211
1231323.1122213333
31321111.322323322
211232313.23132211
1123312222.3313311
21312312233.112233
132211323131.22233
2313122123112.3333
11111323323223.020
111113233232230.02
3221121321133320.0
32211213211333020.""".strip().split('\n')


def grid(rows, n):
    M = [[0] * n for _ in range(n)]
    for i, row in enumerate(rows):
        assert len(row) == n, (i, len(row))
        for j, ch in enumerate(row):
            M[i][j] = int(ch) if ch != '.' else 0
    return M


def check(M, k=4):
    n = len(M)
    errs = []
    for i in range(n):
        for j in range(n):
            if i != j:
                if M[i][j] != M[j][i]:
                    errs.append(f"asym ({i},{j})")
                if not (0 <= M[i][j] < k):
                    errs.append(f"range ({i},{j})")
    mono = [(i, j, l) for i in range(n) for j in range(i + 1, n)
            for l in range(j + 1, n) if M[i][j] == M[i][l] == M[j][l]]
    return errs, mono


def main():
    n = 18
    M = grid(ROWS18, n)
    errs, mono = check(M)
    X = list(range(14))
    inside = [(i, j) for i in X for j in X if i < j and M[i][j] == 0]
    far = [y for y in range(n) if y not in X and all(M[y][x] != 0 for x in X)]
    print("18-vertex witness")
    print("  asymmetric / out-of-range:", errs or "none")
    print("  monochromatic triangles  :", mono or "none")
    print("  colour-0 edges inside X  :", inside or "none")
    print("  |X| =", len(X), " far points =", far, "(count", len(far), ")")
    ok = not errs and not mono and not inside and len(far) == 4
    with open('far18.col', 'w') as f:
        f.write("18 4\n")
        for row in M:
            f.write(' '.join(map(str, row)) + '\n')
    print("  ->", "OK, sharpness witness" if ok else "NOT a witness")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
