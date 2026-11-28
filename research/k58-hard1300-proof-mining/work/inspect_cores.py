"""Bounded core inventory; candidates are not promoted merely by this script."""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import itertools,json
ROOT=Path.cwd(); S=ROOT/'.scratch/hard1300-proof-mining'; OUT=ROOT/'research/k58-hard1300-proof-mining/work'
EDGES=list(itertools.combinations(range(58),2)); EDGE_IDX={x:i for i,x in enumerate(EDGES)}
def cnf(path):
    lines=path.read_bytes().splitlines(); _,_,nv,nc=lines[0].split()
    rows=[]
    for line in lines[1:]:
        v=[int(x) for x in line.split()];assert v[-1]==0
        rows.append(tuple(v[:-1]))
    assert len(rows)==int(nc)
    return int(nv),rows

def read_lemmas(path):
    out=[]
    with path.open() as stream:
        for lineno,line in enumerate(stream,1):
            if not line.strip() or line[0]=='d':continue
            if line[0]=='a':line=line[1:].lstrip()
            if line[0]=='p':continue
            vals=[int(x) for x in line.split()];assert vals[-1]==0
            words=vals[:-1]
            if words:out.append({'line':lineno,'literals':words})
    return out

def identity(path):
    b=path.read_bytes();return {'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':sha256(b).hexdigest()}

def role(l):
    edge,c=divmod(abs(l)-1,4)
    return {'edge':list(EDGES[edge]),'color':c,'sign':'+' if l>0 else '-'}

def one(rank):
    parent_path=S/f'rank{rank}-run/parent.cnf'
    core_path=S/f'rank{rank}-core.cnf'; lemma_path=S/f'rank{rank}-core-lemmas.drat'
    nv,parent=cnf(parent_path);core_nv,core=cnf(core_path)
    parent_set={frozenset(x) for x in parent}
    assert nv==core_nv==29942 and len(parent)==211564
    # drat-trim may emit equivalent clauses in a different literal order.
    assert all(frozenset(x) in parent_set for x in core)
    bywidth={k:set() for k in range(5)}
    for x in parent:
        z=frozenset(x)
        if len(z)<=4:bywidth[len(z)].add(z)
    lemmas=read_lemmas(lemma_path)
    fixed_units={x[0] for x in parent[134995:] if len(x)==1}
    physical=[x for x in lemmas if all(abs(l)<=6612 for l in x['literals'])]
    short=[x for x in physical if len(x['literals'])<=4]
    candidates=[]
    for x in short:
        clause=frozenset(x['literals'])
        if clause in bywidth[len(x['literals'])]:x['is_explicit_parent_clause']=True
        else:
            x['is_explicit_parent_clause']=False
            # A parent clause is subsumed exactly when one of its literals
            # is a subset of the candidate. Indexed subset lookups avoid a
            # quadratic scan through the whole parent for every candidate.
            subsumed=any(frozenset(part) in bywidth[take]
                         for take in range(1,len(clause)+1)
                         for part in itertools.combinations(sorted(clause),take))
            x['subsumed_by_parent']=subsumed
            if not subsumed:
                x['decoded_roles']=[dict(role(l),literal=l) for l in x['literals']]
                x['vertices']=sorted({v for l in x['literals'] for v in EDGES[(abs(l)-1)//4]})
                candidates.append(x)
    prior=[[4687,3590,4034,4673],[-5160,3282,4822]]
    for x in candidates:
        z=set(x['literals']);x['prior_D_exact_match']=next((p for p in prior if set(p)==z),None)
    report={'rank':rank,'parent':identity(parent_path),'core':identity(core_path),'core_lemmas':identity(lemma_path),
      'core_clause_count':len(core),'lemma_additions':len(lemmas),'physical_additions':len(physical),
      'addition_widths':dict(sorted(Counter(len(x['literals']) for x in lemmas).items())),
      'physical_short_additions':len(short),'explicit_short_repetitions':sum(x['is_explicit_parent_clause'] for x in short),
      'subsumed_short_additions':sum(x.get('subsumed_by_parent',False) for x in short),
      'nonsubsumed_short_physical':len(candidates),'fixed_units':len(fixed_units),
      'candidate_excerpt':candidates[:64],
      'scope':'Case-local backward core inventory; decoding and filtering alone never proves a destination transfer'}
    return report,candidates

def main():
    reports={};candidatesets={}
    for rank in (1297,1300):
        p=S/f'rank{rank}-core.cnf'
        assert p.stat().st_size>0, f'no checked core for rank {rank}'
        reports[str(rank)],rows=one(rank);candidatesets[str(rank)]={tuple(sorted(x['literals'])) for x in rows}
        reports[str(rank)]['candidate_excerpt']=rows[:64]
    shared=sorted(candidatesets['1297']&candidatesets['1300'])
    result={'cases':reports,'exact_shared_candidates':shared,
      'exact_shared_count':len(shared),'prior_D_literals':[[4687,3590,4034,4673],[-5160,3282,4822]],
      'candidate_comparison':'Shared literal tuples are still only heuristics. They require semantic roles and native destination implication proofs, and must be distinguished from existing banks.'}
    for rank in (1297,1300):
        with (OUT/f'rank{rank}-core-candidates.json').open('w') as f:
            rep=reports[str(rank)];rep['shared_with_other_rank_count']=len(candidatesets[str(rank)]&candidatesets[str(1300 if rank == 1297 else 1297)]);f.write(json.dumps(rep,indent=2)+'\n')
    result['cases']={rank:{k:v for k,v in report.items() if k!='candidate_excerpt'}
                         for rank,report in reports.items()}
    (OUT/'core-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    compact=dict(result,cases={rank:{k:v for k,v in report.items() if k!='candidate_excerpt'}
                                   for rank,report in reports.items()})
    print(json.dumps(compact,indent=2))
if __name__=='__main__':main()
