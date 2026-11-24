"""Independent checker for a candidate 58x58 colouring of one pb case.

    python3 tools/pb/check_matrix.py ROW T MATRIX.txt

MATRIX.txt holds 58 lines of 58 characters over "0123" ('.' on the diagonal is
also accepted).  Verifies, from the definition and not from the encoder: the
pins of the (template, D) row, the cell membership for t, exactly-one colour per
edge, no monochromatic triangle, the degree laws (L3) and the red-codegree law
(L4).  Prints one line per check and exits 0 only if every check passes.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pbdata import ROWS, cells
from encode import layout, cellmap, BLUE, GREEN, YELLOW, RED, COLS


def load(path):
    rows = [l.strip() for l in open(path) if l.strip()]
    assert len(rows) == 58, len(rows)
    for r in rows:
        assert len(r) == 58, len(r)
    return rows


def check(M, D, t, rows):
    pins, lab2v, pv, qv, u, v = layout(M, D)
    cellof = cellmap(t)
    ok = True
    def fail(msg):
        nonlocal ok
        ok = False
        print('FAIL', msg)
    # symmetry / alphabet
    for a in range(58):
        for b in range(58):
            if a == b:
                if rows[a][b] not in '.-':
                    fail('diagonal %d' % a)
            else:
                if rows[a][b] not in '0123' or rows[a][b] != rows[b][a]:
                    fail('edge %d,%d not symmetric/alphabet' % (a, b))
    if not ok:
        return False
    C = [[int(rows[a][b]) if a != b else None for b in range(58)] for a in range(58)]
    for (a, b), c in pins.items():
        if C[a][b] != c:
            fail('pin %d-%d = %s, want %d' % (a, b, C[a][b], c))
    for w, (cu, cv) in cellof.items():
        if C[u][w] != cu or C[v][w] != cv:
            fail('cell of %d = (%d,%d), want (%d,%d)' % (w, C[u][w], C[v][w], cu, cv))
    tri = 0
    for a, b, c in itertools.combinations(range(58), 3):
        if C[a][b] == C[a][c] == C[b][c]:
            tri += 1
            if tri <= 5:
                fail('mono triangle %d,%d,%d colour %d' % (a, b, c, C[a][b]))
    deg = {}
    for a in range(58):
        cnt = {c: 0 for c in COLS}
        for b in range(58):
            if b != a:
                cnt[C[a][b]] += 1
        deg[a] = cnt
        if cnt[RED] not in (15, 16):
            fail('vertex %d red degree %d' % (a, cnt[RED]))
        for c in (BLUE, GREEN, YELLOW):
            if cnt[c] > 14:
                fail('vertex %d colour %d degree %d > 14' % (a, c, cnt[c]))
    worst = 0
    for a, b in itertools.combinations(range(58), 2):
        k = sum(1 for w in range(58)
                if w != a and w != b and C[a][w] == RED and C[b][w] == RED)
        worst = max(worst, k)
        if k > 14:
            fail('codegree %d,%d = %d' % (a, b, k))
    print('mono triangles %d, max red codegree %d, degree table of (u,v) %s %s'
          % (tri, worst, [deg[u][c] for c in COLS], [deg[v][c] for c in COLS]))
    if ok:
        print('OK: pins, cells, (L1)-(L4) all hold')
    return ok


if __name__ == '__main__':
    row, t, path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    M, D = [(m, d) for (nm, m, d) in ROWS if nm == row][0]
    sys.exit(0 if check(M, D, t, load(path)) else 1)
