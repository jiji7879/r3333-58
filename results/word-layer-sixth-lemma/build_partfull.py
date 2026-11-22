"""Order-58 pair level + the sixth arm lemma (part_family_le_five), built from
the definitions.  Families, each branch-implied:

 (W1) one colour per cell; (W2) exactly five 0s per word  [m(x) = 5]
 (W3) ordinary parts independent in the template       [monochromatic triangle]
 (C)  coverage exactly 14 per arm position             [sum m_x = 210, 15 positions]
 (P)  pair condition: some colour f with disjoint f-parts, f not the shared arm
      colour inside an arm; p(x,y,f) -> the f-parts are disjoint
 (F)  part_family_le_five: for a != b, no 6-subset of arm b has pairwise
      intersecting a-parts, where the a-part of x is {z in arm a : col(x,z) = a}
      (a = 0: {p in A : col(x,p) = 0}, which is the word's 0-part)

Kernel facts used: K58.mixture is not needed here; (F) is
K58.part_family_le_five (Blocked.lean, no sorry), (W2)/(W3)/(P) are the
definitions of a triangle-free colouring restricted to the branch.
"""
import argparse, itertools, json, os, sys
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, CNF

R = os.path.abspath("../../..")
ART = R + "/artifacts/"
NSLOT = 42; PER = 14; NPOS = 15

def load_col(path):
    t = open(path).read().split(); n = int(t[0])
    v = list(map(int, t[2:2 + n * n]))
    return [v[i * n:(i + 1) * n] for i in range(n)]

def build(template, nfam, out, fams=None, sort=False, nopair=False, fix=None, fix0=None, armcap=False):
    Tm = load_col(ART + template)
    om = {0: 1, 1: 2, 2: 3}
    pool = IDPool(); C = CNF()
    def cell(x, p, f): return pool.id(('c', x, p, f))
    def pv(x, y, f):   return pool.id(('p', x, min(y, x and y) if False else y, f))
    def dis(a, b, x, y): return pool.id(('d', a, b, x, y))
    def wit(a, x, y, z): return pool.id(('w', a, x, y, z))
    def arm(x): return x // PER
    def armcol(x): return arm(x) + 1
    def armverts(i): return list(range(i * PER, (i + 1) * PER))
    def allowed(x, y):
        al = set(range(4))
        if arm(x) == arm(y): al.discard(armcol(x))
        return sorted(al)
    fam = []
    def mark(name): fam.append((name, len(C.clauses) - sum(k for _, k in fam)))
    # cells
    for x in range(NSLOT):
        for p in range(NPOS):
            C.append([cell(x, p, f) for f in range(4)])
            for f, g in itertools.combinations(range(4), 2):
                C.append([-cell(x, p, f), -cell(x, p, g)])
    mark("cells")
    for x in range(NSLOT):
        C.extend(CardEnc.equals([cell(x, p, 0) for p in range(NPOS)], bound=5,
                                vpool=pool, encoding=EncType.seqcounter).clauses)
    mark("five zeros per word")
    for x in range(NSLOT):
        for p, q in itertools.combinations(range(NPOS), 2):
            f = om[Tm[p][q]]
            C.append([-cell(x, p, f), -cell(x, q, f)])
    mark("part independence")
    for p in range(NPOS):
        C.extend(CardEnc.equals([cell(x, p, 0) for x in range(NSLOT)], bound=PER,
                                vpool=pool, encoding=EncType.seqcounter).clauses)
    mark("coverage 14")
    if armcap:
        # K58.mixture with u = r: |N_0(a) cap arm_i| <= 5 for every a, i
        for i in range(3):
            for p in range(NPOS):
                C.extend(CardEnc.atmost([cell(x, p, 0) for x in armverts(i)], bound=5,
                                        vpool=pool, encoding=EncType.seqcounter).clauses)
    mark("per-arm cap 5")
    # pair condition
    for x, y in (() if nopair else itertools.combinations(range(NSLOT), 2)):
        al = allowed(x, y)
        vs = [pv(x, y, f) for f in al]
        C.append(vs)
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                C.append([-vs[i], -vs[j]])
        for f in al:
            for p in range(NPOS):
                C.append([-pv(x, y, f), -cell(x, p, f), -cell(y, p, f)])
    mark("pair condition")
    # part family
    pairs_fam = [(a, b) for b in (1, 2, 3) for a in (0, 1, 2, 3) if a != b][:nfam]
    if fams is not None:
        pairs_fam = fams
    for (a, b) in pairs_fam:
        vs = armverts(b - 1)          # arm of ROOT COLOUR b is slots (b-1)*PER .. b*PER
        positions = list(range(NPOS)) if a == 0 else armverts(a - 1)
        def atom(x, z, a=a):
            # "x is a-adjacent to z" in the partition that defines the a-part
            if a == 0:
                return cell(x, z, 0)
            return pv(x, z, a)
        for x, y in itertools.combinations(vs, 2):
            dd = dis(a, b, x, y)
            for z in positions:
                C.append([-dd, -atom(x, z), -atom(y, z)])
            ws = [wit(a, x, y, z) for z in positions]
            for z, w in zip(positions, ws):
                C.append([-w, atom(x, z)])
                C.append([-w, atom(y, z)])
                C.append([-atom(x, z), -atom(y, z), w])
            C.append([dd] + [w for w in ws])   # dd is forced when no z is shared
        for S in itertools.combinations(vs, 6):
            C.append([dis(a, b, x, y) for x, y in itertools.combinations(S, 2)])
    mark("part_family_le_five (%d families)" % len(pairs_fam))
    if sort:
        # permuting the slots of an arm is an automorphism of every family above
        # (the words move with the slots; coverage is indexed by A positions), so
        # lex-sorting the words inside each arm is a sound symmetry break.
        for i in range(3):
            vs = armverts(i)
            for x, y in zip(vs, vs[1:]):
                prev = None
                for p in range(NPOS):
                    for val in range(4):
                        lits = [-cell(x, p, val)] + [cell(y, p, w) for w in range(val, 4)]
                        if prev is not None: lits.append(-prev)
                        C.append(lits)
                    eq = pool.id(('eq', x, p))
                    if prev is not None: C.append([-eq, prev])
                    for val in range(4):
                        C.append([-eq, -cell(x, p, val), cell(y, p, val)])
                        C.append([-eq, -cell(y, p, val), cell(x, p, val)])
                        lits = [-cell(x, p, val), -cell(y, p, val), eq]
                        if prev is not None: lits.append(-prev)
                        C.append(lits)
                    prev = eq
    mark("lex sort inside each arm")
    if fix:
        for x, w in enumerate(fix):
            for p, f in enumerate(w):
                C.append([cell(x, p, f)])
    mark("pinned words")
    if fix0:
        for x, Z in enumerate(fix0):
            for p in range(NPOS):
                C.append([cell(x, p, 0) if p in Z else -cell(x, p, 0)])
    mark("pinned 0-parts")
    C.to_file(out)
    C.pool = pool
    print(f"{out}: vars {C.nv} clauses {len(C.clauses)}")
    for name, k in fam:
        print(f"   {k:7d}  {name}")
    return C, pool

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="k15_template_Tminus_aut2_m4.col")
    ap.add_argument("--nfam", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fams", default=None)
    ap.add_argument("--sort", action="store_true")
    ap.add_argument("--nopair", action="store_true")
    ap.add_argument("--fix", default=None)
    ap.add_argument("--fix0", default=None)
    ap.add_argument("--armcap", action="store_true")
    a = ap.parse_args()
    fams = None
    if a.fams:
        fams = [tuple(int(t) for t in f.split("-")) for f in a.fams.split(",")]
    fix = json.load(open(a.fix)) if a.fix else None
    fix0 = [set(b) for b in json.load(open(a.fix0))] if a.fix0 else None
    build(a.template, a.nfam, a.out, fams, a.sort, a.nopair, fix, fix0, a.armcap)
