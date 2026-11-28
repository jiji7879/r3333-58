"""Native RUP checks on a deliberately small sample of shared core clauses."""
from pathlib import Path
import concurrent.futures,hashlib,itertools,json,subprocess
ROOT=Path.cwd();S=ROOT/'.scratch/hard1300-proof-mining';W=ROOT/'research/k58-hard1300-proof-mining/work'
ROOTS=sorted(S/'..',) if False else ROOT
CHECK=ROOT/'tools/color-resolved-wallcc/bin/drat-trim'
EDGES=list(itertools.combinations(range(58),2))

def load(rank):return json.loads((W/f'rank{rank}-core-candidates.json').read_text())
src={rank:load(rank) for rank in (1297,1300)}
by={}
for rank,r in src.items():by[rank]={tuple(x['literals']):x for x in r['candidate_excerpt']}
shared=set(by[1297])&set(by[1300])
def pattern(c):return (len(c),tuple(l>0 for l in c))
chosen=[]
for kind in sorted({pattern(c) for c in shared}):
    pool=sorted((c for c in shared if pattern(c)==kind),key=lambda c:max(by[r][c]['line'] for r in src))[:2]
    chosen.extend(pool)
# Keep a bounded diverse panel, not an induction on its collected failures.
chosen=chosen[:12]
headers={}
for rank,p in ((1297,S/'rank1297-run/parent.cnf'),(1300,S/'rank1300-run/parent.cnf')):
    raw=p.read_bytes();lines=raw.split(b'\n',1);_,_,nv,nc=lines[0].split()
    units=[l for l in lines[1].splitlines()[134995:] if len(l.split())==2]
    headers[rank]=(raw,int(nv),int(nc),len(units))
    assert len(units)==503

def decode(c):
    out=[]
    for l in c:
        edge,col=divmod(abs(l)-1,4)
        out.append({'literal':l,'edge':list(EDGES[edge]),'color':col,'sign':1 if l>0 else -1})
    return out

def check(args):
    idx,rank,number,clause=args;c=list(clause);raw,nv,nc,nu=headers[rank]
    head,body=raw.split(b'\n',1)
    out=S/'common-probes'/f'c{idx:02d}'/f'rank{rank}';out.mkdir(parents=True,exist_ok=True)
    units=b''.join(f'{-l} 0\n'.encode() for l in c)
    query=f'p cnf {nv} {nc+len(c)}\n'.encode()+body+units
    (out/'query.cnf').write_bytes(query)
    proof=out/'false-cube.rup';proof.write_bytes(b'0\n')
    core=out/'native-core.cnf'
    cmd=[str(CHECK),str(out/'query.cnf'),str(proof),'-I','-W','-p','-U','-t','8','-c',str(core)]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=12)
    log=r.stdout.decode(errors='replace');(out/'check.log').write_bytes(r.stdout)
    accepted=r.returncode==0 and 's VERIFIED' in log.splitlines() and 'WARNING' not in log and 'ERROR' not in log
    core_cl=[]
    if core.exists():
        for line in core.read_bytes().splitlines():
            if line[0:1] in (b'c',b'p'):continue
            core_cl.append([int(x) for x in line.split()[:-1]])
    return {'candidate_index':number,'clause':c,'decoded':decode(c),'parent_rank':rank,
       'parent_sha256':headers[rank][0] and hashlib.sha256(headers[rank][0]).hexdigest(),
       'query_sha256':hashlib.sha256(query).hexdigest(),'proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),
       'parent_fixed_unit_prefix':nu,'exit_code':r.returncode,'accepted':accepted,'native_result':'s VERIFIED' if accepted else 'not accepted',
       'native_core_clauses':core_cl,'core_has_aux':any(abs(x)>6612 for cl in core_cl for x in cl),
       'method':'full exact parent + the candidate negated cube; input unit prefix separately available. RUP-only, no -w, no target assumption.'}
idxargs=[]
for idx,c in enumerate(chosen):
    src_roles={str(rank):by[rank][c] for rank in by}
    for rank in (1297,1300):idxargs.append((idx,rank,len(idxargs)//2,c))
# Indexing must associate a candidate, not concatenation order.
idxargs=[(i,r,i,c) for i,c in enumerate(chosen) for r in (1297,1300)]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    records=list(pool.map(check,idxargs))
shared_source={str(i):{str(rank):by[rank][c] for rank in (1297,1300)} for i,c in enumerate(chosen)}
report={'schema':'k58-hard1300-small-common-probe/v1','checker_sha256':hashlib.sha256(CHECK.read_bytes()).hexdigest(),
        'candidates':shared_source,'checks':records,'accepted':sum(x['accepted'] for x in records),'total':len(records),
        'scope':'A native implication sample only. Exact residual literal agreement across two closed inputs is not a general role-transfer proof. OPEN/non-accepted control is not a model, and these results are not a solver policy claim.'}
Path(W/'common-probe.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'total':len(records),'accepted':report['accepted'],
    'candidates':[{'clause':c,'source_line':{str(rank):by[rank][c] for rank in by}} for c in chosen]},indent=2))
print('accepted records:',json.dumps([{'clause':x['clause'],'rank':x['parent_rank'],'core':len(x['native_core_clauses']),'aux':x['core_has_aux']} for x in records if x['accepted']]))
