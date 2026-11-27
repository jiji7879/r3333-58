#!/usr/bin/env python3
"""Matched stock/hybrid CaDiCaL 1.9.5 completed attempt on original rank 1300."""
import hashlib,json,os,re,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[3]
cnf=R/'.scratch/arm-cap-research/rank1300-stock.cnf'
outdir=R/'research/k58-arm-cap-clauses/work/glucose-rank1300'
outdir.mkdir(exist_ok=True)
receipts=[]
for mode in ('stock','hybrid'):
 exe=R/'.scratch/glucose-reduction-v1/rebuild/bin'/('cadical-stock' if mode=='stock' else 'cadical')
 cmd=[str(exe),'--stats','--seed=0','-c','1200000','-t','300']
 if mode=='hybrid':cmd.append('--reduceglucose')
 proof=R/'.scratch/arm-cap-research'/f'rank1300-glucose-{mode}.drat';log=outdir/(mode+'.log')
 start=time.monotonic()
 with log.open('wb') as out:
  with subprocess.Popen(cmd+[str(cnf),str(proof)],stdout=out,stderr=subprocess.STDOUT) as child:
   _,status,usage=os.wait4(child.pid,0);child.returncode=os.waitstatus_to_exitcode(status)
 text=log.read_text(errors='replace')
 def metric(key):
  m=re.search(r'^c\s+'+key+r':\s+(\d+)',text,re.M)
  if not m:raise ValueError((mode,key))
  return int(m.group(1))
 rec=dict(mode=mode,command=cmd+[str(cnf),str(proof)],input_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),
  solver_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),exit_code=child.returncode,
  status={0:'OPEN',10:'SAT',20:'UNSAT'}.get(child.returncode,'ERROR'),wall_s=time.monotonic()-start,
  user_cpu_s=usage.ru_utime,system_cpu_s=usage.ru_stime,rss_kib=usage.ru_maxrss,
  **{k:metric(k) for k in ('conflicts','decisions','propagations','reduced','reductions')})
 if proof.exists():
  rec.update(proof_bytes=proof.stat().st_size,proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest())
 if rec['status']=='OPEN':proof.unlink(missing_ok=True)
 receipts.append(rec)
 print(json.dumps(rec,sort_keys=True),flush=True)
 tmp=(outdir/'receipts.json.tmp');tmp.write_text(json.dumps(receipts,indent=2,sort_keys=True)+'\n');tmp.replace(outdir/'receipts.json')
