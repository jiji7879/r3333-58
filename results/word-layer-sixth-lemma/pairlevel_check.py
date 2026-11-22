"""Full definition-level check of an order-58 pair-level witness, plus the
part-family (sixth arm lemma) clique numbers: for colours a and arms b != a,
the largest set of arm-b slots with pairwise INTERSECTING a-parts, and the
mid-2014-style threshold: a violation is a clique of size >= 6."""
import sys, itertools, collections, os
ARTS = os.path.abspath("../../../artifacts") + "/"
def load_col(path):
    p = path if os.path.exists(path) else ARTS + os.path.basename(path)
    t = open(p).read().split(); n = int(t[0])
    v = list(map(int, t[2:2 + n * n]))
    return [v[i * n:(i + 1) * n] for i in range(n)]
def read_wit(path):
    words = {}; pairs = {}; arms = []; tpl = None
    for line in open(path):
        t = line.split()
        if not t or t[0].startswith('#'): continue
        if t[0] == 'template': tpl = t[1]
        elif t[0] == 'arm': arms.append((int(t[1]), list(map(int, t[2:]))))
        elif t[0] == 'word': words[int(t[1])] = list(map(int, t[2:]))
        elif t[0] == 'pair': pairs[(int(t[1]), int(t[2]))] = int(t[3])
    return words, pairs, arms, tpl
def max_clique(adj, verts):
    best = [0]
    def rec(cand, size):
        if not cand:
            best[0] = max(best[0], size); return
        if size + len(cand) <= best[0]: return
        for i, v in enumerate(cand):
            if size + len(cand) - i <= best[0]: return
            rec([u for u in cand[i+1:] if u in adj[v]], size + 1)
    rec(sorted(verts), 0)
    return best[0]
def main(path):
    words, pairs, arms, tpl = read_wit(path)
    Tr = load_col(tpl); om = {0: 1, 1: 2, 2: 3}
    armof = {v: c for c, vs in arms for v in vs}
    bad = collections.Counter()
    for x in words:
        if sum(1 for f in words[x] if f == 0) != 5: bad['five_zeros'] += 1
        for p, q in itertools.combinations(range(15), 2):
            f = om[Tr[p][q]]
            if words[x][p] == f and words[x][q] == f: bad['part_indep'] += 1
    cov = {}
    for a in range(15):
        cov[a] = sum(1 for x in words if words[x][a] == 0)
        if cov[a] != 14: bad['coverage_not_14'] += 1
    for x, y in itertools.combinations(sorted(words), 2):
        f = pairs.get((x, y), pairs.get((y, x)))
        if f is None: bad['no_pair_colour'] += 1; continue
        if armof[x] == armof[y] and f == armof[x]: bad['arm_colour_used'] += 1
        if any(words[x][a] == f and words[y][a] == f for a in range(15)): bad['pair_not_disjoint'] += 1
    print(f"{path.split('/')[-1]}: words {len(words)}, pairs {len(pairs)}, arms {[(c, len(v)) for c, v in arms]}")
    print(f"   violations: {dict(bad) if bad else 'none'}; coverage {sorted(set(cov.values()))}")
    # part-family cliques: for colour a, the a-positions of each word
    pos_of_arm = {c: vs for c, vs in arms}
    worst = 0; table = {}
    for a in (0, 1, 2, 3):
        for b, vs in arms:
            if b == a: continue
            if a == 0:
                part = {x: frozenset(p for p in range(15) if words[x][p] == 0) for x in vs}
            else:
                arm_a = pos_of_arm[a]
                part = {x: frozenset(z for z in arm_a
                                     if (pairs.get((x, z), pairs.get((z, x))) == a)) for x in vs}
            adj = {x: set() for x in vs}
            for x, y in itertools.combinations(vs, 2):
                if part[x] & part[y]:          # intersecting a-parts
                    adj[x].add(y); adj[y].add(x)
            c = max_clique(adj, vs)
            table[(a, b)] = c
            worst = max(worst, c)
    print(f"   part-family max cliques (a,b) -> largest pairwise-a-intersecting set in arm b:")
    print("     " + ", ".join(f"({a},{b}):{c}" for (a, b), c in sorted(table.items())))
    print(f"   worst {worst} (bound is 5; violation iff >= 6) -> {'VIOLATED' if worst >= 6 else 'satisfied'}")
if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p); print()
