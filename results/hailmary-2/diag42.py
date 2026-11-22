import sys
sys.path.insert(0,'/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
tpl = ladder.load_col(ladder.TPL_DEFAULT)
ordmap = None
W = []
for line in open('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/results/two-arm-interface/a_14_14_lean.wit'):
    t = line.split()
    if t and t[0] == 'word':
        W.append(tuple(int(v) for v in t[2:]))
W = W[:14]
print('words', len(W))
# per-position coverage in the pinned arm
cov = [sum(1 for w in W if w[a] == 0) for a in range(15)]
print('coverage per position', cov)
# copy bound: empty colour of each word
emp = []
for w in W:
    e = [f for f in (1,2,3) if all(w[a] != f for a in range(15))]
    emp.append(e[0] if len(e) == 1 else None)
print('empty colours', emp)
from collections import Counter
print('repeats', [ (w,c) for w,c in Counter(W).items() if c > 1 ])
# pair compatibility within the arm (arm colour 1 banned)
import itertools
bad = 0
for i,j in itertools.combinations(range(14),2):
    ok = False
    for f in (0,2,3):
        pi = {a for a in range(15) if W[i][a]==f}; pj = {a for a in range(15) if W[j][a]==f}
        if not (pi & pj): ok = True; break
    if not ok: bad += 1
print('pairs with no available colour:', bad)
