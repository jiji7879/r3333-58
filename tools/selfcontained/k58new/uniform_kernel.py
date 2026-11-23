"""The seven twisted fully sending uniform children. Physical labels match gluing.host."""
from collections import Counter
from functools import cache
from itertools import combinations
from pathlib import Path

from pysat.card import CardEnc
from gluing import host, units
from dense import marked_threshold
from profile_kernel import PHYSICAL, PROFILE, family_of, physical_index

A = tuple(range(1,16))
X = tuple(range(16,58))
GROUPS = {c: tuple(range(16+14*(c-1), 16+14*c)) for c in (1,2,3)}
FIRST = frozenset((2,11,13,31,39,46))
BOTH = FIRST | {43,72,155,165,229}
DATA = Path(__file__).with_name("uniform_armtypes14.txt")


def eligible(row):
    f = row["family"]
    return (tuple(f["profile"]) == PROFILE and f["root_kinds"] == ["T","-","-","-"]
            and row["charge"] == 15 and f["arm"] == 0 and f["marked_size"] == 15)


def normalize(raw):
    if not isinstance(raw, dict) or set(raw) - {"zero_sets","arm_types"}:
        raise ValueError("a cube is an object with optional zero_sets and arm_types")
    words, types = {}, {}
    for key, points in raw.get("zero_sets", {}).items():
        x = int(key)
        if (str(x) != key or x not in X or not isinstance(points,list) or len(points)!=5
                or any(type(a) is not int or a not in A for a in points) or len(set(points))!=5):
            raise ValueError("zero_sets maps vertices 16..57 to five distinct labels from 1..15")
        words[x]=tuple(sorted(points))
    for key, i in raw.get("arm_types", {}).items():
        if key not in ("B","C","D") or type(i) is not int or not 0<=i<332:
            raise ValueError("arm_types maps B, C, D to catalogue IDs 0..331")
        types["BCD".index(key)+1]=i
    return dict(sorted(words.items())), dict(sorted(types.items()))


def obstruction(words, types):
    for (c,i),(d,j) in combinations(types.items(),2):
        if (i in FIRST and j in BOTH) or (j in FIRST and i in BOTH):
            return dict(rule="excluded_arm_pair", arms=[c,d], types=[i,j])
    counts = Counter(words.values())
    for s,p in counts.items():
        if p>6:
            return dict(rule="multiplicity", support=s, count=p)
    for (s,p),(u,q) in combinations(counts.items(),2):
        t=len(set(s).intersection(u))
        if t and p+q+t>11:
            return dict(rule="overlap", supports=[s,u], counts=[p,q], intersection=t)
    heavy=[s for s,p in counts.items() if p>=5]
    if len(heavy)>3:
        return dict(rule="fivefold",supports=heavy[:4])
    upper=len(counts)+len(X)-len(words)
    if upper<12:
        return dict(rule="distinct", upper=upper)
    return None


@cache
def catalogue():
    rows=[]
    for line in DATA.read_text().splitlines():
        if line.startswith("#"):continue
        ix,n0,n1,n2,g,h=line.split()
        if int(ix)!=len(rows):raise ValueError("catalogue index")
        def bit(code,i,j):
            n=j*(j-1)//2+i
            return (ord(code[1+n//6])-63)>>(5-n%6)&1
        rows.append(tuple(0 if bit(g,i,j) else 1 if bit(h,i,j) else 2
                          for i,j in combinations(range(14),2)))
    if len(rows)!=332:raise ValueError("catalogue length")
    return rows


class Formula:
    def __init__(self, fixed):
        self.known=set(fixed)
        self.clauses=[]
        self.top=PHYSICAL
    def fresh(self):
        self.top+=1
        return self.top
    def add(self, clause):
        if any(v in self.known for v in clause):return
        self.clauses.append([v for v in clause if -v not in self.known])
    def residual(self, lits, bound):
        return [v for v in lits if v not in self.known and -v not in self.known], bound-sum(v in self.known for v in lits)
    def atmost(self,lits,bound):
        free,k=self.residual(lits,bound)
        if k<0:self.clauses.append([])
        elif k<len(free):
            cnf=CardEnc.atmost(free,bound=k,top_id=self.top)
            self.top=max(self.top,cnf.nv)
            self.clauses.extend(cnf.clauses)
    def threshold(self,lits,demand):
        """Literal implying at least demand true inputs. True and False are constants."""
        free,k=self.residual(lits,demand)
        if k<=0:return True
        if k>len(free):return False
        @cache
        def node(i,j):
            if j==0:return True
            if i<j:return False
            if i==j==1:return free[0]
            same=node(i-1,j)
            less=node(i-1,j-1)
            v=self.fresh()
            for other in (free[i-1],less):
                self.gate([-v,same,other])
            return v
        return node(len(free),k)
    def gate(self,clause):
        if any(t is True for t in clause):return
        self.clauses.append([t for t in clause if t is not False])


@cache
def physical(row_id, fixed):
    base,_,occ,prop=physical_index()
    ok, inferred=prop.propagate(assumptions=list(fixed))
    if not ok:return (), ((),)
    known=set(fixed)|set(inferred)
    removed={i for lit in known for i in occ[lit]}
    clauses=tuple(tuple(v for v in cl if -v not in known) for i,cl in enumerate(base) if i not in removed)
    return tuple(sorted(known)),clauses


def append_types(F,types,edge):
    # Each local vertex chooses an image in the canonical catalogue representative.
    # Injectivity on 14 vertices makes this a permutation. Both palettes are possible.
    for arm,idx in types.items():
        image=[[F.fresh() for j in range(14)] for x in GROUPS[arm]]
        for row in image:F.clauses.append(row)
        for col in zip(*image):
            for u,v in combinations(col,2):F.clauses.append([-u,-v])
        swap=F.fresh()
        colors=sorted({1,2,3}-{arm})
        for (i,j),c in zip(combinations(range(14),2),catalogue()[idx]):
            for x,y in combinations(range(14),2):
                for u,v in ((i,j),(j,i)):
                    prefix=[-image[x][u],-image[y][v]]
                    if c==0:F.add(prefix+[edge(GROUPS[arm][x],GROUPS[arm][y],0)])
                    else:
                        for s in (0,1):
                            F.add(prefix+[swap if not s else -swap,edge(GROUPS[arm][x],GROUPS[arm][y],colors[(c-1)^s])])


def build(row,words,types,variant):
    if not eligible(row):raise ValueError("requires a fully sending uniform child of one of the seven rows")
    edge,_=host(58)
    f=family_of(row)
    fixed=units(f,row["placement"])
    pins=[s[0] for s in fixed]
    for x,s in words.items():
        pins.extend(edge(a,x,0) if a in s else -edge(a,x,0) for a in A)
    if variant=="frozen-reference":
        F=Formula(())
        F.clauses.extend(host(58)[1])
        F.clauses.extend([v] for v in pins)
        suffix=marked_threshold(f,fixed,15,tables=True,total_critical=True,full_root=False)
        F.top=max([PHYSICAL]+[abs(v) for cl in suffix for v in cl])
        F.clauses.extend(suffix)
        for x in X:F.atmost([edge(a,x,0) for a in A],5)
        append_types(F,types,edge)
        return F
    if variant not in ("reference","split","ordered"):
        raise ValueError("unknown uniform encoding")
    # Cache only the shared row layer. Cube-local entries must not accumulate in a long batch.
    key=tuple(sorted(set(pins)))
    known,base=physical.__wrapped__(row["id"],key) if words else physical(row["id"],key)
    F=Formula(known)
    if base==((),):
        F.clauses=[[]]
        return F
    F.clauses.extend(base)
    F.clauses.extend([v] for v in known)
    if variant=="reference":
        extra=marked_threshold(f,fixed,15,tables=True,total_critical=True,full_root=False)
        F.top=max([PHYSICAL]+[abs(v) for cl in extra for v in cl])
        for cl in extra:F.add(cl)
    for x in X:F.atmost([edge(a,x,0) for a in A],5)
    if variant!="reference":
        for a in A:
            fifth=[]
            for vertices in GROUPS.values():
                lits=[edge(a,x,0) for x in vertices]
                # One shared prefix construction for the lower bounds four and five.
                # A padding literal permits a four-set if the deficit is spent here.
                deficit=F.fresh()
                F.gate([F.threshold(lits+[deficit],5)])
                fifth.append(deficit)
            for i,j in combinations(fifth,2):F.clauses.append([-i,-j])
    if variant=="ordered":
        for c,vertices in GROUPS.items():
            # Relabel only unmarked, unpinned slots. Put full words first and own-colour omissions last.
            marked=[x for x in vertices if edge(1+f.mark_position,x,0) in known]
            free=[x for x in vertices if x not in marked and x not in words]
            for index,x in enumerate(free):
                for col in (1,2,3):
                    if index < len(free)-(1 if col==c else 3):
                        F.add([edge(a,x,col) for a in A])
    append_types(F,types,edge)
    return F


def write_cnf(F,path):
    with path.open("w") as out:
        out.write(f"p cnf {F.top} {len(F.clauses)}\n")
        out.writelines(" ".join(map(str,cl))+" 0\n" for cl in F.clauses)
