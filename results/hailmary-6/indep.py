import sys, itertools, collections
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwrmwgf7/m1')
import ladder
tpl = ladder.load_col(ladder.TPL_DEFAULT)   # matrix of colours 0,1,2 on 15 points
n = len(tpl)
for c in (0, 1, 2):
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if tpl[i][j] == c]
    cnt = collections.Counter(); sizes = collections.Counter()
    for S in range(1 << n):
        ok = True
        for i, j in edges:
            if (S >> i) & 1 and (S >> j) & 1:
                ok = False; break
        if ok:
            k = bin(S).count('1'); cnt[k] += 1
    tot = sum(cnt.values())
    print(f'colour {c}: edges {len(edges)} | independent sets by size {dict(sorted(cnt.items()))} | total {tot}')
