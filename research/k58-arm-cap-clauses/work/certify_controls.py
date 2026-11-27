#!/usr/bin/env python3
"""Original-parent DRAT certificate and independent controls for one exclusion."""
import argparse,hashlib,itertools,json,subprocess,time
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Cadical195
import pysolvers

def sha(b):return hashlib.sha256(b).hexdigest()
def append_units(raw,units):
 h,b=raw.split(b'\n',1);f=h.split();return f'p cnf {int(f[2])} {int(f[3])+len(units)}\n'.encode()+b+b''.join(f'{l} 0\n'.encode() for l in units)
def serialize(nv,cls):return f'p cnf {nv} {len(cls)}\n'.encode()+b''.join(' '.join(map(str,c)).encode()+b' 0\n' for c in cls)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',required=True,type=Path);ap.add_argument('--checker',required=True,type=Path);ap.add_argument('--refinement',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();run=a.run.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);assert Path.cwd().resolve() in out.parents
 import sys
 sys.path.insert(0,str(a.refinement.resolve()));from compare import without_deletions
 s=json.loads((run/'summary.json').read_text());records=json.loads((run/'exclusions.json').read_text());rec=records[0];raw=(run/'stock.cnf').read_bytes();assert sha(raw)==s['input_sha256'];stock=CNF(from_string=raw.decode());edges=list(itertools.combinations(range(58),2));profile=list(map(int,s['profile'].split(',')));starts=[1]
 for n in profile:starts.append(starts[-1]+n)
 x,c,ba,bb=rec['sender'],rec['color'],rec['arm_a'],rec['arm_b'];A=list(range(starts[ba],starts[ba+1]));B=list(range(starts[bb],starts[bb+1]));V={0,x,*A,*B};ie=set(itertools.combinations(sorted(V),2));base=[cl for cl in stock.clauses if all(abs(l)<=4*len(edges) and edges[(abs(l)-1)//4] in ie for l in cl)];units=rec['positive_spokes'];nv=stock.nv
 local_data=serialize(nv,base+[[l] for l in units]);full_data=append_units(raw,units);(out/'local.cnf').write_bytes(local_data);(out/'original-query.cnf').write_bytes(full_data)
 t=time.perf_counter()
 with Cadical195(bootstrap_with=base+[[l] for l in units],with_proof=True) as sat:
  sat.configure({'seed':0});sat.conf_budget(200000);answer=sat.solve_limited();search_stats=sat.accum_stats();assert answer is False,(answer,search_stats);pysolvers.flushpr(sat.prfp);sat.prfile.seek(0);proof=sat.prfile.read()
 clean,norm=without_deletions(proof);(out/'local-clean.drat').write_bytes(clean)
 def check(name,formula,proof_data):
  log=subprocess.run([str(a.checker.resolve()),str(formula),str(out/'local-clean.drat'),'-i','-U','-W','-t','300'],capture_output=True);(out/(name+'.log')).write_bytes(log.stdout+log.stderr);status=[z for z in log.stdout.splitlines() if z.startswith(b's ')];assert log.returncode==0 and status==[b's VERIFIED'] and b'WARNING' not in log.stdout.upper() and b'ERROR' not in log.stdout.upper(),(name,log.returncode,log.stdout[-1000:]);return {'exit':log.returncode,'status':['s VERIFIED'],'warnings':0,'proof_sha256':sha(proof_data),'query_sha256':sha(formula.read_bytes())}
 cert={'rank':s['rank'],'row_id':s['row_id'],'parent_sha256':s['input_sha256'],'record':rec,'local_clauses':len(base)+len(units),'original_query_clauses':len(stock.clauses)+len(units),'solver_answer':'UNSAT','solver_stats':search_stats,'search_wall_seconds':time.perf_counter()-t,'raw_proof_sha256':sha(proof),'normalization':norm,'clean_proof_bytes':len(clean),'clean_proof_sha256':sha(clean),'local_replay':check('local-replay',out/'local.cnf',clean),'original_parent_replay':check('original-replay',out/'original-query.cnf',clean),'flags':['-i','-U','-W','-t','300']}
 # A satisfiable local compatible pair, not a model of the UNSAT original parent.
 sys.path.insert(0,s['package']);sys.path.insert(0,s['package']+'/encoder');import probe
 optsA=list(probe.catalog(len(A),s['kinds'][ba],ba,c));optsB=list(probe.catalog(len(B),s['kinds'][bb],bb,c));bad={(r['support_a'],r['support_b']) for r in records if (r['sender'],r['color'],r['arm_a'],r['arm_b'])==(x,c,ba,bb)}
 def edge(u,v,col):
  ee=(min(u,v),max(u,v));return 4*edges.index(ee)+col+1
 pair=next((i,j) for i in range(len(optsA)) for j in range(len(optsB)) if (i,j) not in bad);sat_units=[edge(x,A[k],c) for k in optsA[pair[0]]]+[edge(x,B[k],c) for k in optsB[pair[1]]];sat_data=serialize(nv,base+[[l] for l in sat_units]);(out/'local-sat-control.cnf').write_bytes(sat_data)
 with Cadical195(bootstrap_with=base+[[l] for l in sat_units]) as sat:
  sat_answer=sat.solve();assert sat_answer is True;model=set(sat.get_model());assert all(any(l in model for l in cl) for cl in base+[[l] for l in sat_units]);stats_sat=sat.accum_stats()
 (out/'local-sat-model.txt').write_text(' '.join(map(str,sorted(model)))+' 0\n');sat_control={'pair':pair,'units':sat_units,'query_sha256':sha(sat_data),'answer':'SAT_LOCAL_ONLY','stats':stats_sat,'model_sha256':sha((out/'local-sat-model.txt').read_bytes()),'model_satisfies_query':True,'excluded_pairs_in_this_relation':len(bad),'support_pair_counts':[len(optsA),len(optsB)]}
 # Remove all row placement pins. Keep only root+named-template semantics.
 generic=[[edge(u,v,col) for col in range(4)] for u,v in ie]
 generic += [[-edge(u,v,c1),-edge(u,v,c2)] for u,v in ie for c1 in range(4) for c2 in range(c1+1,4)]
 for u,v,w in itertools.combinations(sorted(V),3):
  for col in range(4):generic.append([-edge(u,v,col),-edge(u,w,col),-edge(v,w,col)])
 generic.append([edge(0,x,c)])
 for arm,b in ((A,ba),(B,bb)):
  mat=probe.named_template(len(arm),s['kinds'][b],b)
  for y in arm:generic.append([edge(0,y,b)])
  for i,u in enumerate(arm):
   for j,v in enumerate(arm):
    if j>i:generic.append([edge(u,v,mat[i][j])])
 generic += [[l] for l in units];generic_data=serialize(max(nv,4*len(edges)),generic);(out/'template-only-control.cnf').write_bytes(generic_data)
 with Cadical195(bootstrap_with=generic) as sat:
  sat.conf_budget(200000);template_answer=sat.solve_limited();assert template_answer is True,(template_answer,sat.accum_stats());model2=set(sat.get_model());assert all(any(l in model2 for l in cl) for cl in generic);template_stats=sat.accum_stats()
 (out/'template-only-model.txt').write_text(' '.join(map(str,sorted(model2)))+' 0\n');template_control={'query_sha256':sha(generic_data),'answer':'SAT','stats':template_stats,'model_sha256':sha((out/'template-only-model.txt').read_bytes()),'model_satisfies_query':True,'tested_UNSAT_units':units,'conclusion':'The accepted physical exclusion fails when row placement pins are dropped; those pins are essential scope.'}
 # Exhaustive cap basis and a constructive sharpness example.
 triangles=list(itertools.combinations(range(6),3));pairs=list(itertools.combinations(range(6),2));colourings=0;bad_k6=0
 for bits in range(1<<len(pairs)):
  colourings+=1;colour={e:(bits>>i)&1 for i,e in enumerate(pairs)}
  if any(colour[min(u,v),max(u,v)]==colour[min(u,w),max(u,w)]==colour[min(v,w),max(v,w)] for u,v,w in triangles):continue
  bad_k6+=1
 assert bad_k6==0 and colourings==32768
 pairs5=list(itertools.combinations(range(5),2));colour5={e:int((e[1]-e[0]) in (1,4)) for e in pairs5};assert not any(colour5[min(u,v),max(u,v)]==colour5[min(u,w),max(u,w)]==colour5[min(v,w),max(v,w)] for u,v,w in itertools.combinations(range(5),3))
 cap_control={'binary_K6_colourings':colourings,'two_colour_triangle_free_K6':bad_k6,'K5_sharpness_coloring':[[u,v,k] for (u,v),k in sorted(colour5.items())]}
 result={'schema':'original-certificate-and-controls/v1','certificate':cert,'satisfiable_local_control':sat_control,'template_only_negative_control':template_control,'cap_finite_control':cap_control,'historical_proofs_used':False}
 (out/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'certificate':{'stats':search_stats,'proof_bytes':len(clean),'original':cert['original_parent_replay']},'sat_control':sat_control,'template_control':template_control,'cap':{'K6':colourings,'bad':bad_k6}},indent=2))
if __name__=='__main__':main()
