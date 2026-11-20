"""Replay the deletion and Hall assumptions and tally the rooted-pair scope."""
from collections import Counter, defaultdict
from itertools import combinations_with_replacement,permutations,combinations
from pathlib import Path
from functools import reduce
from operator import or_
import json, subprocess
from template import ROOT,decode
from catalog_pairs import autos
REGULAR=set(range(1,116))-{17,19,20,22,23,24,25,40,69,70,77}
def get_catalog(n):
    return [decode(s) for s in (ROOT/f'data/r333_{n}.mc').read_text().splitlines()]
def verify_15(cat,targets):
    def embeds(a,b):
        for p in permutations(range(3)):
            deg=[[r.count(c) for c in range(3)] for r in b]
            opts=[[j for j in range(15) if all(row.count(c)==deg[j][p[c]] for c in range(3))] for row in a]
            order=sorted(range(15),key=lambda i:len(opts[i]))
            assigned={}
            def walk(k,used):
                if k==15:return True
                i=order[k]
                for j in opts[i]:
                    if used>>j&1 or any(p[a[i][v]]!=b[j][u] for v,u in assigned.items()):continue
                    assigned[i]=j
                    if walk(k+1,used|(1<<j)):return True
                    del assigned[i]
                return False
            if walk(0,0):return True
        return False
    counts=Counter()
    for M in cat:
        word=[]
        def extend():
            i=len(word)
            if i==14:
                G=[r+[c] for r,c in zip(M,word)]+[word.copy()+[-1]]
                hit=next((j for j,t in enumerate(targets) if embeds(G,t)),None)
                assert hit is not None
                counts[hit]+=1
                return
            for c in range(3):
                if any(old==c==M[i][j] for j,old in enumerate(word)):continue
                word.append(c);extend();word.pop()
        extend()
    return dict(counts)
def main():
    cat=get_catalog(14);targets=get_catalog(15);work=ROOT/'work';work.mkdir(exist_ok=True)
    binaries={}
    for name in ('plane_masks','cap'):
        exe=work/name
        subprocess.run(['g++','-O3','-std=c++20',str(ROOT/f'src/{name}.cpp'),'-o',exe],check=True)
        binaries[name]=exe
    classes=verify_15(cat,targets);print('K15 ordinary spoke completions by class',classes,flush=True)
    matrix=lambda m:' '.join(str(x) for row in m for x in row)
    inp=''.join(f'{len(m)} {j+1}\n'+matrix(m)+'\n' for group in (targets,cat) for j,m in enumerate(group))
    run=subprocess.run([binaries['plane_masks']],input=inp,capture_output=True,text=True,check=True)
    blocks=defaultdict(list)
    for line in run.stdout.splitlines():
        j,mask=map(int,line.split());blocks[j].append(mask)
    counts={j:len(blocks[j]) for j in sorted(REGULAR)}
    covered={j:reduce(or_,blocks[j],0).bit_count() for j in sorted(REGULAR)}
    assert max(covered.values())<13 and not blocks[42]
    print('Union of admissible deletions, largest over regular templates:',max(covered.values()),flush=True)
    # Enumerate all colour-spoke words and compatible tuples to obtain the small-set capacity.
    subsets=[m for m in range(1<<14) if m.bit_count()<=3]
    qs=[]
    for j in sorted(REGULAR):
        qs.extend((f'{j} -1 0',matrix(cat[j-1])))
        qs.extend(f'{j} {m} {m.bit_count()+1}' for m in subsets)
    run=subprocess.run([binaries['cap']],input='\n'.join(qs)+'\n',capture_output=True,text=True,check=True)
    answers=set()
    for line in run.stdout.splitlines():
        j,m,words,k=map(int,line.split())
        assert k<=m.bit_count() and (j,m) not in answers
        answers.add((j,m))
    assert answers=={(j,m) for j in REGULAR for m in subsets}
    # Burnside for unordered pairs of rooted, named-palette types.
    perms=list(permutations(range(3)));who={};types=[]
    for j in sorted(REGULAR):
        M=cat[j-1]
        actions=[(tuple(p.index(i) for i in range(3)),f) for p in perms for f in autos(M,p)]
        for pole in range(14):
            for p in perms:
                if (j,pole,p) in who:continue
                i=len(types);types.append((j,pole,p))
                for q,f in actions:who[j,f[pole],tuple(p[c] for c in q)]=i
    seeds=[r[1] for r in json.loads((ROOT/'data/core-cover.json').read_text())]
    tally=Counter()
    for g in perms:
        perm=[who[j,v,tuple(g[c] for c in p)] for j,v,p in types]
        fixed=Counter(seeds[types[i][0]-1] for i,k in enumerate(perm) if i==k)
        for a,b in combinations_with_replacement(fixed,2):
            tally[min(a,b)]+= fixed[a]*(fixed[a]+1)//2 if a==b else fixed[a]*fixed[b]
        for i,j in enumerate(perm):
            if i<j and perm[j]==i:tally[min(seeds[types[k][0]-1] for k in (i,j))]+=1
    assert all(n%6==0 for n in tally.values())
    scope={j:tally[j]//6 for j in range(1,13)}
    result=dict(k15_extensions=classes,small_support_checks=len(answers),admissible_deletions=counts,deletion_union_sizes=covered,rooted_pairs_by_seed=scope,total_rooted_pairs=sum(scope.values()))
    print('Verified',len(answers),'capacity bounds. Rooted-pair scope',scope,sum(scope.values()),flush=True)
    (ROOT/'results/global.json').write_text(json.dumps(result,indent=1)+'\n')
if __name__=='__main__':main()
