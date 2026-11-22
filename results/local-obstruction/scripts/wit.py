"""Parse the campaign's `.wit` pair-level witnesses and rebuild the colour-0 graph.

Format (all five order-58 witnesses):
    template <path>            (optional)
    order 58                   (optional)
    arm <k> <v0> <v1> ...      one line per arm, k = 1,2,3 = the arm's root colour
    word <x> <w_0> ... <w_14>  one line per outside vertex x,
                               w_a = colour of the edge (x, a), a = arm position
    pair <x> <y> <f>           one line per pair of outside vertices

Vertex set used here: A = 0..n-1 (the 15-arm of the root r), X = 0..m-1
(witness labels, disjoint from A), r = n+m.
Colour-0 adjacency, from the branch definition:
    a--a'  : never                (A = N_0(r) is 0-independent)
    r--a   : always;  r--x : never (X = N_1(r) u N_2(r) u N_3(r))
    a--x   : word[x][a] == 0
    x--y   : pair colour == 0
"""


class Wit:
    def __init__(self, path):
        self.path = path
        self.template = None
        self.order = None
        self.arms = {}
        self.words = {}
        self.pairs = {}
        with open(path) as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln or ln.startswith("#"):
                    continue
                t = ln.split()
                if t[0] == "template":
                    self.template = t[1]
                elif t[0] == "order":
                    self.order = int(t[1])
                elif t[0] == "arm":
                    self.arms[int(t[1])] = [int(v) for v in t[2:]]
                elif t[0] == "word":
                    self.words[int(t[1])] = tuple(int(v) for v in t[2:])
                elif t[0] == "pair":
                    self.pairs[(int(t[1]), int(t[2]))] = int(t[3])
                else:
                    raise ValueError("unknown line: %r" % ln)
        self.armcolour = {}
        for k, vs in self.arms.items():
            for v in vs:
                self.armcolour[v] = k
        self.coverage = None

    def M(self, x, f):
        return frozenset(a for a, c in enumerate(self.words[x]) if c == f)

    def nouts(self):
        return sorted(self.words)

    def n_arm(self):
        return len(next(iter(self.words.values())))

    def check(self):
        errs = []
        n = self.n_arm()
        for x, w in self.words.items():
            if len(w) != n:
                errs.append("word %d has length %d, expected %d" % (x, len(w), n))
            if w.count(0) != 5:
                errs.append("word %d has %d zeros" % (x, w.count(0)))
        xs = sorted(self.words)
        seen = []
        for k in sorted(self.arms):
            seen += self.arms[k]
        if sorted(seen) != xs:
            errs.append("arms do not partition the outside vertices")
        expect = len(xs) * (len(xs) - 1) // 2
        if len(self.pairs) != expect:
            errs.append("have %d pair colours, expected %d" % (len(self.pairs), expect))
        for (x, y), f in self.pairs.items():
            if x >= y:
                errs.append("pair (%d,%d) not increasing" % (x, y))
            if not (0 <= f <= 3):
                errs.append("pair (%d,%d) colour %d out of range" % (x, y, f))
            if self.M(x, f) & self.M(y, f):
                errs.append("pair (%d,%d) colour %d fails M_%d-disjointness" % (x, y, f, f))
        cov = [0] * n
        for x in xs:
            for a in self.M(x, 0):
                cov[a] += 1
        self.coverage = cov
        return errs

    def colour0_graph(self):
        """Vertices A(0..n-1) | X(n..n+m-1) | r(n+m).  Returns (N, adj)."""
        n = self.n_arm()
        xs = self.nouts()
        m = len(xs)
        r = n + m
        N = n + m + 1
        adj = [0] * N
        def add(u, v):
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        for a in range(n):
            add(r, a)
        for i, x in enumerate(xs):
            for a in range(n):
                if self.words[x][a] == 0:
                    add(n + i, a)
        idx = {x: i for i, x in enumerate(xs)}
        for (x, y), f in self.pairs.items():
            if f == 0:
                add(n + idx[x], n + idx[y])
        return N, adj
