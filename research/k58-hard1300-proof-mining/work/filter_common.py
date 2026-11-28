"""Bounded UP triage only; no SAT model or clause theorem is inferred here."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from time import process_time
import itertools,json,pysat
from pysat.formula import CNF
from pysat.solvers import Cadical195
ROOT=Path.cwd();S=ROOT/'.scratch/hard1300-proof-mining';W=ROOT/'research/k58-hard1300-proof-mining/work'
r=json.loads((W/'core-comparison.json').read_text());shared=[tuple(x) for x in r['exact_shared_candidates']]
assert len(shared)==2346
EDGES=list(itertools.combinations(range(58),2))
def one(rank):
    parent=CNF(from_file=str(S/f'rank{rank}-run/parent.cnf').encode())
    rejected=[];remaining=[];started=process_time()
    with Cadical195(bootstrap_with=parent.clauses) as solver:
        # Controls whose native RUP cores are already known, before triage.
        for clause in ([-3225,-3385],[3849,3850,3852]):
            solver.conf_budget(0)
            assert solver.solve_limited(assumptions=[-x for x in clause]) is False
        for index,clause in enumerate(shared):
            solver.conf_budget(0)
            ans=solver.solve_limited(assumptions=[-x for x in clause])
            assert ans in (False,None), (rank,index,clause,ans)
            if ans is False:rejected.append(index)
            else:
                roles=[]
                for lit in clause:
                    edge,c=divmod(abs(lit)-1,4)
                    roles.append({'literal':lit,'edge':list(EDGES[edge]),'color':c,'sign':int(lit>0)})
                remaining.append({'index':index,'clause':list(clause),'decoded':roles,
                    'vertices':sorted({v for lit in clause for v in EDGES[(abs(lit)-1)//4]})})
    return {'rank':rank,'shared_candidates':len(shared),'up_refuted':len(rejected),'up_unresolved':len(remaining),
            'cpu_seconds':process_time()-started,'remaining':remaining,
            'scope':'PySAT conflicts=0 only filters direct UP consequences. None means UP-unresolved, never SAT or implication-failure; the solver proof is not used as the native certificate.'}
with ThreadPoolExecutor(max_workers=2) as pool:
    reports={str(rank):x for rank,x in zip((1297,1300),pool.map(one,(1297,1300)))}
both=set()
for rank,r in reports.items():both={x['index'] for x in r['remaining']} if not both else both&{x['index'] for x in r['remaining']}
excerpt=next(x for x in reports['1297']['remaining'] if x['index'] in both) if both else None
richly=sorted((x for x in reports['1297']['remaining'] if x['index'] in both),
              key=lambda x:(len(x['clause'])!=4,len(x['clause']),-len(x['vertices']),x['index']))
result={'reports':reports,'up_unresolved_both':len(both),'indices_both':sorted(both),'excerpt':richly[:120],
        'pysat_version':pysat.__version__,
        'scope':'Complete propagation triage of all 2,346 shared short clauses per parent. Native DRAT proofs of the event, parent and already hard cases were separately verified. This filter is not a proof of any unresolved candidate, nor a model/eligibility claim.'}
Path(W/'common-filter.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'per_case':{r['rank']:{x:r[x] for x in ('shared_candidates','up_refuted','up_unresolved','cpu_seconds')} for k,r in reports.items()},
                  'up_unresolved_both':len(both),'excerpt':richly[:8]},indent=2))
