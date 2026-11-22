"""The 26-vertex two-arm object (14,12) + cross-arm triangle-freeness ("XT"),
for either critical template.

Definition (all families are sound for the uniform fully-sending child, so the
object is a relaxation of it; the kernel-checked two-arm restriction theorem
says a genuine object restricts to a model of this object):

  A = 15 arm positions carrying a triangle-free 3-colouring (template), its
  colours relabelled 1,2,3.  X = B u C, |B| = 14 with root colour 1, |C| = 12
  with root colour 2.

  W  each x in X carries a word  w_x : A -> {0,1,2,3}  with |M_0(x)| = 5,
     and M_f(x) f-independent inside the template  (f = 1,2,3).
  C  coverage, sound for the branch: for each a in A the number of B-points
     with a in M_0 is 4 or 5 (sender split in a 14-arm) and the number of
     C-points is <= 5 (mixture); the sum over the two arms is 9 or 10,
     because the third arm of the genuine object contributes 4 or 5 of the 14.
  P  each pair x<y carries a colour f with M_f(x) cap M_f(y) = empty and
     f != root colour when x,y share an arm.
  T  no three points of X are pairwise joined in one colour (arm and cross-arm
     triangle-freeness).

variables: cell(x,a,f), q(x,y,f); sequential counters for the cardinalities.
"""
import itertools, sys, os

def load_col(path):
    toks = [t for line in open(path) for t in line.split()]
    n, k = int(toks[0]), int(toks[1])
    vals = list(map(int, toks[2:]))
    M = [vals[i * n:(i + 1) * n] for i in range(n)]
    return M, n


class CNF:
    def __init__(self):
        self.nv = 0
        self.cl = []
        self.unit = 0

    def new(self, k=1):
        v = self.nv + 1
        self.nv += k
        return v if k == 1 else list(range(v, v + k))

    def add(self, *cl):
        self.cl.append(tuple(cl))

    def at_most(self, lits, k):
        n = len(lits)
        if k >= n:
            return
        if k < 0:
            self.add(lits[0]); self.add(-lits[0]); return
        if k == 0:
            for l in lits:
                self.add(-l)
            return
        s = [[0] * (k + 1) for _ in range(n)]
        for i in range(n):
            for j in range(1, k + 1):
                s[i][j] = self.new()
        self.add(-lits[0], s[0][1])
        for j in range(2, k + 1):
            self.add(-s[0][j])
        for i in range(1, n):
            self.add(-lits[i], s[i][1])
            self.add(-s[i - 1][1], s[i][1])
            for j in range(2, k + 1):
                self.add(-lits[i], -s[i - 1][j - 1], s[i][j])
                self.add(-s[i - 1][j], s[i][j])
            self.add(-lits[i], -s[i - 1][k])

    def at_least(self, lits, k):
        self.at_most([-l for l in lits], len(lits) - k)

    def exactly(self, lits, k):
        self.at_most(lits, k)
        self.at_least(lits, k)

    def write(self, path):
        with open(path, 'w') as fh:
            fh.write('p cnf %d %d\n' % (self.nv, len(self.cl)))
            for cl in self.cl:
                fh.write(' '.join(map(str, cl)) + ' 0\n')


def build(tplpath, nB=14, nC=12, colB=1, colC=2, exact_split=True,
          cross_triangles=True, arm_only=False, cross_only=False):
    M, n = load_col(tplpath)
    assert n == 15
    A = list(range(n))
    fedges = {f: [(a, b) for a in A for b in A if a < b and M[a][b] == f - 1]
              for f in (1, 2, 3)}
    X = list(range(nB + nC))
    B = X[:nB]
    C = X[nB:]
    root = {x: (colB if x in B else colC) for x in X}
    nxt = nB + nC
    cnf = CNF()
    cell = {}
    for x in X:
        for a in A:
            for f in range(4):
                cell[x, a, f] = cnf.new()
    for x in X:
        for a in A:
            cnf.add(*[cell[x, a, f] for f in range(4)])
            for f in range(3):
                for g in range(f + 1, 4):
                    cnf.add(-cell[x, a, f], -cell[x, a, g])
    # W: exactly five zeros, parts independent in their own colour
    for x in X:
        cnf.exactly([cell[x, a, 0] for a in A], 5)
        for f in (1, 2, 3):
            for (a, b) in fedges[f]:
                cnf.add(-cell[x, a, f], -cell[x, b, f])
    # C: coverage, sound for the branch.  In the genuine object every a in A
    # has 4 or 5 colour-0 partners in the complete 14-arm B and 4 or 5 in the
    # complete 14-arm C, summing to 14 across the three arms; the restricted
    # object keeps all of B and 12 of C's 14 points, so
    #    B-count in {4,5},  C-count in {2,..,5},  total in {7,..,10}.
    # (Sum over a of the total is 14*5 + 12*5 = 130, average 8.67, so any
    # stronger per-column demand is infeasible by counting alone.)
    for a in A:
        cB = [cell[x, a, 0] for x in B]
        cC = [cell[x, a, 0] for x in C]
        cnf.at_least(cB, 4); cnf.at_most(cB, 5)
        cnf.at_most(cC, 5)
        if exact_split:
            cnf.at_least(cC, 2)
            both = cB + cC
            cnf.at_least(both, 7); cnf.at_most(both, 10)
    # P: pair colours
    q = {}
    for x, y in itertools.combinations(X, 2):
        allowed = [f for f in range(4) if not (root[x] == root[y] == f)]
        for f in allowed:
            q[x, y, f] = cnf.new()
            for a in A:
                cnf.add(-q[x, y, f], -cell[x, a, f], -cell[y, a, f])
        cnf.add(*[q[x, y, f] for f in allowed])
        for i in range(len(allowed)):
            for j in range(i + 1, len(allowed)):
                cnf.add(-q[x, y, allowed[i]], -q[x, y, allowed[j]])
    # T: no monochromatic triangle inside X.  arm_only restricts this to
    # triples lying in a single arm (a sound restriction of the XT object).
    if cross_triangles:
        for x, y, z in itertools.combinations(X, 3):
            if arm_only and not (x < nB and y < nB and z < nB) and \
               not (x >= nB and y >= nB and z >= nB):
                continue
            if cross_only and ((x < nB and y < nB and z < nB) or
                               (x >= nB and y >= nB and z >= nB)):
                continue
            for f in range(4):
                t = []
                for (u, v) in ((x, y), (x, z), (y, z)):
                    t.append(q.get((u, v, f)))
                if any(v is None for v in t):
                    continue
                cnf.add(-t[0], -t[1], -t[2])
    return cnf, cell, q, A, X, B, C, root, fedges


def verify(tplpath, word, pair, nB=14, nC=12, colB=1, colC=2, exact_split=True,
           cross_triangles=True, verbose=True):
    """Check a model from the definition.  word[x] = tuple of 15 colours,
    pair[(x,y)] = colour of xy."""
    M, n = load_col(tplpath)
    A = list(range(n))
    B = list(range(nB))
    C = list(range(nB, nB + nC))
    X = B + C
    root = {x: (colB if x in B else colC) for x in X}
    bad = []
    for x in X:
        w = word[x]
        if len(w) != 15: bad.append(('W length', x))
        if sum(1 for v in w if v == 0) != 5: bad.append(('W five zeros', x, sum(1 for v in w if v == 0)))
        for f in (1, 2, 3):
            part = [a for a in A if w[a] == f]
            for a, b in itertools.combinations(part, 2):
                if M[a][b] == f - 1: bad.append(('W part edge', x, f, a, b))
    for a in A:
        cB = sum(1 for x in B if word[x][a] == 0)
        cC = sum(1 for x in C if word[x][a] == 0)
        if not (4 <= cB <= 5): bad.append(('C B', a, cB))
        if cC > 5: bad.append(('C C', a, cC))
        if exact_split:
            if not (2 <= cC): bad.append(('C C low', a, cC))
            if not (7 <= cB + cC <= 10): bad.append(('C total', a, cB + cC))
    for x, y in itertools.combinations(X, 2):
        f = pair[(x, y)]
        if root[x] == root[y] == f: bad.append(('P root colour', x, y, f))
        for a in A:
            if word[x][a] == f and word[y][a] == f: bad.append(('P disjoint', x, y, f, a))
    if cross_triangles:
        for x, y, z in itertools.combinations(X, 3):
            for f in range(4):
                if pair[(x, y)] == pair[(x, z)] == pair[(y, z)] == f:
                    bad.append(('T triangle', x, y, z, f))
    if verbose:
        print('order', 1 + 15 + len(X), '|B|', len(B), '|C|', len(C))
        print('FAILURES:', bad[:8] if bad else 'none')
    return bad
