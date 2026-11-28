#!/usr/bin/env python3
import argparse, hashlib, json, platform, resource, time
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Solver

ap=argparse.ArgumentParser()
ap.add_argument('--conflicts',type=int,required=True)
ap.add_argument('--output',required=True)
ap.add_argument('items',nargs='+')
a=ap.parse_args()
out=Path(a.output)
with out.open('w') as stream:
 for item in a.items:
  label,path=item.split('=',1)
  data=Path(path).read_bytes()
  parse_start=time.monotonic(); parse_cpu=time.process_time()
  formula=CNF(from_file=path)
  parse_wall=time.monotonic()-parse_start
  parse_cpu=time.process_time()-parse_cpu
  with Solver(name='cadical195',bootstrap_with=formula.clauses) as solver:
   start=time.monotonic(); cpu=time.process_time(); before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
   solver.conf_budget(a.conflicts)
   answer=solver.solve_limited()
   result={'label':label,'path':path,'cnf_sha256':hashlib.sha256(data).hexdigest(),
    'nv':formula.nv,'clauses':len(formula.clauses),'conflict_cap':a.conflicts,
    'answer':answer,'status':'SAT' if answer is True else 'UNSAT_API_STATUS_UNCERTIFIED' if answer is False else 'OPEN',
    'conflicts_and_other_stats':solver.accum_stats(),
    'solve_wall_seconds':time.monotonic()-start,
    'solve_cpu_seconds':time.process_time()-cpu,
    'parse_wall_seconds':parse_wall,'parse_cpu_seconds':parse_cpu,
    'maxrss_kib_after':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    'note':'OPEN means cap reached. An API UNSAT status is not a certificate.'}
  print(json.dumps(result),flush=True); stream.write(json.dumps(result)+'\n'); stream.flush()
