"""Independent branch checker for the (15,14,14,14) profile.

Written from the definition of the uniform fully-sending branch, NOT from any
member's encoder.  Everything here is computed directly from a colouring file
(`.col`) or a witness file (`.wit`).

Conventions (K_58 at a root r with profile (15,14,14,14)):
  * A  = N_0(r), 15 points, indices 0..14 in the arm files;
  * X  = the 42 outside vertices, split into arms 1,2,3 = N_1(r), N_2(r), N_3(r);
  * a *word* of x is the restriction a |-> colour(x,a) for a in A;
  * M_f(x) = {a in A : colour(x,a) = f}.
The branch hypotheses checked: m(x) = |M_0(x)| = 5, every M_f (f = 1,2,3)
f-independent in the template, no monochromatic triangle inside X, the arm
colour never on a pair inside an arm, and M_f(x) cap M_f(y) = empty whenever
colour(x,y) = f.
"""

TEMPLATE_COLOUR_OFFSET = 1  # template files store 0,1,2 for physical 1,2,3


def read_col(path):
    """Read a `.col` file: first line `n k`, then n rows of n colours."""
    with open(path) as fh:
        toks = fh.read().split()
    n = int(toks[0])
    k = int(toks[1])
    vals = [int(t) for t in toks[2:2 + n * n]]
    assert len(vals) == n * n, (path, n, len(vals))
    mat = [vals[i * n:(i + 1) * n] for i in range(n)]
    for i in range(n):
        for j in range(n):
            assert mat[i][j] == mat[j][i], ("asymmetry", path, i, j)
        assert mat[i][i] == 0, ("diagonal", path, i)
    return n, k, mat


class Colouring:
    """A 4-colouring of the complete graph on n vertices given as a matrix."""

    def __init__(self, n, mat):
        self.n = n
        self.c = mat

    def __call__(self, x, y):
        return self.c[x][y]

    def classof(self, v, f):
        return [u for u in range(self.n) if u != v and self.c[v][u] == f]

    def degrees(self, v):
        d = [0, 0, 0, 0]
        for u in range(self.n):
            if u != v:
                d[self.c[v][u]] += 1
        return d

    def triangles(self):
        """Return (total monochromatic triangles, counts per colour)."""
        cnt = [0, 0, 0, 0]
        n, c = self.n, self.c
        for x in range(n):
            for y in range(x + 1, n):
                col = c[x][y]
                for z in range(y + 1, n):
                    if c[x][z] == col and c[y][z] == col:
                        cnt[col] += 1
        return sum(cnt), cnt


class Template:
    """A triangle-free 3-colouring of K_15, physical colours 1,2,3."""

    def __init__(self, path):
        n, k, mat = read_col(path)
        assert n == 15 and k == 3, (path, n, k)
        self.n = n
        self.raw = mat
        # physical colour of the edge inside A
        self.c = [[mat[i][j] + TEMPLATE_COLOUR_OFFSET for j in range(n)] for i in range(n)]
        # independence check for each physical colour
        self.indep = {}
        for f in (1, 2, 3):
            bad = [(i, j) for i in range(n) for j in range(i + 1, n) if self.c[i][j] == f]
            self.indep[f] = bad
        self.edge_counts = {f: len(self.indep[f]) for f in (1, 2, 3)}

    def colour(self, a, b):
        return self.c[a][b]


class Witness:
    """A `.wit` file: template, arms, words, pair colours."""

    def __init__(self, path):
        self.path = path
        self.template_path = None
        self.order = None
        self.arms = {}      # arm colour -> list of slot ids
        self.words = {}     # slot -> list of 15 colours
        self.pairs = {}     # (x,y) with x<y -> colour
        self.extra = []
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                t = line.split()
                if t[0] == "template":
                    self.template_path = t[1]
                elif t[0] == "order":
                    self.order = int(t[1])
                elif t[0] == "arm":
                    self.arms[int(t[1])] = [int(v) for v in t[2:]]
                elif t[0] == "word":
                    self.words[int(t[1])] = [int(v) for v in t[2:]]
                elif t[0] == "pair":
                    x, y, c = int(t[1]), int(t[2]), int(t[3])
                    self.pairs[(min(x, y), max(x, y))] = c
                else:
                    self.extra.append(line)
        self.slots = sorted(self.words)
        self.armof = {}
        for b, vs in self.arms.items():
            for v in vs:
                self.armof[v] = b

    # ---- word helpers -------------------------------------------------
    def part(self, x, f):
        return frozenset(a for a, val in enumerate(self.words[x]) if val == f)

    def zeros(self, x):
        return self.part(x, 0)


def check_witness(wit, tmpl, verbose=True):
    """Check every branch constraint family separately; return a report dict."""
    rep = {}
    slots = wit.slots
    pairs = wit.pairs

    # --- W1: five zeros per word
    rep["W1_five_zeros"] = {x: len(wit.zeros(x)) for x in slots if len(wit.zeros(x)) != 5}

    # --- W2: M_f f-independent in the template
    bad_indep = []
    for x in slots:
        for f in (1, 2, 3):
            P = sorted(wit.part(x, f))
            for i in range(len(P)):
                for j in range(i + 1, len(P)):
                    if tmpl.colour(P[i], P[j]) == f:
                        bad_indep.append((x, f, P[i], P[j]))
    rep["W2_part_independent"] = bad_indep

    # --- D1: coverage of A by colour-0 supports
    cover = [0] * 15
    for x in slots:
        for a in wit.zeros(x):
            cover[a] += 1
    rep["D1_coverage"] = cover

    # --- E: sixth lemma, clique number of the A-part intersection graph
    def maxclique(adj, verts):
        best = []
        verts = list(verts)
        def expand(cl, cand):
            nonlocal best
            if len(cl) + len(cand) <= len(best):
                return
            if not cand:
                if len(cl) > len(best):
                    best = list(cl)
                return
            for i, v in enumerate(cand):
                expand(cl + [v], [u for u in cand[i + 1:] if u in adj[v]])
        expand([], verts)
        return best

    blocked = {}
    for b, vs in sorted(wit.arms.items()):
        for a in (0, 1, 2, 3):
            if a == b:
                continue
            adj = {}
            for x in vs:
                adj[x] = set(y for y in vs if y != x and (wit.part(x, a) & wit.part(y, a)))
            blocked[(b, a)] = len(maxclique(adj, vs))
    rep["E_blocked_clique"] = blocked
    rep["E_blocked_max"] = max(blocked.values()) if blocked else 0

    # --- F: armFar over 14-subsets of A (branch: |M_0| = 5 makes it vacuous)
    rep["F_armFar_14"] = [len([x for x in slots if not (wit.zeros(x) & (set(range(15)) - {d}))])
                          for d in range(15)]

    if not pairs:
        rep["P1_arm_colour_ban"] = []
        rep["P2_pair_disjoint"] = []
        rep["XT_triangles"] = []
        rep["XT_triangle_counts"] = [0, 0, 0, 0]
        rep["D2_overlap"] = [0, 0, 0, 0]
        rep["D3_overlap_total"] = 0
        return rep

    # --- P1: no arm colour on an intra-arm pair
    bad_armcolour = []
    for b, vs in wit.arms.items():
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                x, y = vs[i], vs[j]
                c = pairs.get((min(x, y), max(x, y)))
                if c == b:
                    bad_armcolour.append((x, y, c))
    rep["P1_arm_colour_ban"] = bad_armcolour

    # --- P2: M_c(x) cap M_c(y) = empty when colour(x,y) = c
    bad_disjoint = []
    for (x, y), c in pairs.items():
        inter = wit.part(x, c) & wit.part(y, c)
        if inter:
            bad_disjoint.append((x, y, c, sorted(inter)))
    rep["P2_pair_disjoint"] = bad_disjoint

    # --- C: monochromatic triangles inside X
    tri = [0, 0, 0, 0]
    tri_list = []
    for i in range(len(slots)):
        x = slots[i]
        for j in range(i + 1, len(slots)):
            y = slots[j]
            cxy = pairs[(min(x, y), max(x, y))]
            if not cxy:
                cxy = 0
            for k in range(j + 1, len(slots)):
                z = slots[k]
                if pairs[(min(x, z), max(x, z))] == cxy and pairs[(min(y, z), max(y, z))] == cxy:
                    tri[cxy] += 1
                    tri_list.append((x, y, z, cxy))
    rep["XT_triangles"] = tri_list
    rep["XT_triangle_counts"] = tri

    # --- D2/D3: the colour-split overlap identity
    over = [0, 0, 0, 0]
    for (x, y), c in pairs.items():
        over[c] += len(wit.zeros(x) & wit.zeros(y))
    rep["D2_overlap"] = over
    rep["D3_overlap_total"] = sum(over)

    return rep


def report(wit, tmpl, rep, name=""):
    out = []
    A = out.append
    A(f"=== {name or wit.path}")
    A(f"template {tmpl_path_short(wit.template_path)}  edge counts {tmpl.edge_counts}")
    A(f"slots {len(wit.slots)}  arms { {b: len(v) for b, v in sorted(wit.arms.items())} }  pairs {len(wit.pairs)}")
    A(f"W1 five zeros        : {'OK' if not rep['W1_five_zeros'] else 'VIOLATED ' + str(rep['W1_five_zeros'])}")
    A(f"W2 part independence : {'OK' if not rep['W2_part_independent'] else 'VIOLATED %d cases, e.g. %s' % (len(rep['W2_part_independent']), rep['W2_part_independent'][:3])}")
    A(f"P1 arm colour ban    : {'OK' if not rep['P1_arm_colour_ban'] else 'VIOLATED %d' % len(rep['P1_arm_colour_ban'])}")
    A(f"P2 pair disjointness : {'OK' if not rep['P2_pair_disjoint'] else 'VIOLATED %d' % len(rep['P2_pair_disjoint'])}")
    A(f"C  XT triangles      : {rep['XT_triangle_counts']} (total {sum(rep['XT_triangle_counts'])})")
    A(f"D1 coverage of A     : {sorted(set(rep['D1_coverage']))} min {min(rep['D1_coverage'])} max {max(rep['D1_coverage'])} sum {sum(rep['D1_coverage'])}")
    A(f"D2 overlap per colour: {rep['D2_overlap']} (target 455 per ordinary colour)")
    A(f"D3 overlap total     : {rep['D3_overlap_total']} (target 1365)")
    A(f"E  blocked cliques   : {rep['E_blocked_clique']} max {rep['E_blocked_max']} (bound 5)")
    A(f"F  armFar on 14-sets : {sorted(set(rep['F_armFar_14']))} (bound 4)")
    return "\n".join(out)


def tmpl_path_short(p):
    return p.rsplit("/", 1)[-1] if p else "?"
