"""Every blue edge of either K16 template has the same (colour to u, colour to v)
footprint on the other 14 vertices: 0 in (B,B), 2 in each of (B,G),(B,Y),(G,B),
(Y,B),(G,G),(Y,Y), and 1 in each of (G,Y),(Y,G).  Exits 1 otherwise."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pbdata import U, T
want = ((0, 2, 2), (2, 2, 1), (2, 1, 2))
for nm, A in (('U', U), ('T', T)):
    tab = {}
    for u in range(16):
        for v in range(u + 1, 16):
            if A[u][v] != '0': continue
            m = [[0] * 3 for _ in range(3)]
            for w in range(16):
                if w in (u, v): continue
                m[int(A[u][w])][int(A[v][w])] += 1
            tab.setdefault(tuple(map(tuple, m)), 0)
            tab[tuple(map(tuple, m))] += 1
    print(nm, 'blue edges by footprint:', dict(tab))
    assert list(tab) == [want], (nm, list(tab))
print('OK: one footprint, and it is the handoff table')
