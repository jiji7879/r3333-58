#!/usr/bin/env python3
import hashlib,json,time
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical195
p=Path('.scratch/arm-cap-research/m1-reproduced-r1300-two5.cnf')
raw=p.read_bytes();form=CNF(from_string=raw.decode())
rec={'cnf_sha256':hashlib.sha256(raw).hexdigest(),'variables':form.nv,'clauses':len(form.clauses),'policy':'two5+all-false','seed':0,'conflict_budget':1200000}
with Cadical195(bootstrap_with=form.clauses) as s:
 s.configure({'seed':0});s.set_phases(list(range(-1,-form.nv-1,-1)))
 t=time.process_time();w=time.perf_counter();s.conf_budget(1200000);a=s.solve_limited()
 rec.update(status={None:'OPEN',False:'UNSAT',True:'SAT'}[a],answer=a,stats=s.accum_stats(),search_cpu_seconds=time.process_time()-t,search_wall_seconds=time.perf_counter()-w)
Path('research/k58-arm-cap-clauses/work/m1m5-coordinator-r1300-two5-all-false.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
print(json.dumps(rec,sort_keys=True))
