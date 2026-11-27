#!/usr/bin/env python3
"""Replay this one case-0 joint experiment; never promote local SAT to K58 SAT.
Usage after extraction: python3 verify_archive.py [--all] [--runtime CAMPAIGN]
Build drat-trim first with: cc -std=c99 -D_GNU_SOURCE -O2 tools/drat-trim.c -o tools/drat-trim
--all rechecks all 400 local UNSAT proofs. Default replays eight full-parent
joint UNSAT proofs and validates every physical local model.
"""
import argparse
from collections import Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent

def require(ok, value):
    if not ok: raise AssertionError(value)

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def checker_output(query,proof):
    result=subprocess.run([str(ROOT/'tools/drat-trim'),str(query),str(proof),'-i','-U','-t','300'],capture_output=True)
    statuses=[x for x in result.stdout.splitlines() if x.startswith(b's ')]
    require(result.returncode==0 and statuses==[b's VERIFIED'] and b'WARNING' not in result.stdout.upper(),
            (str(query),result.returncode,result.stdout[-600:]));

def append_units(raw,units):
    header,body=raw.split(b'\n',1)
    p,c,nv,n=header.split(); require((p,c)==(b'p',b'cnf'),header)
    return f'p cnf {int(nv)} {int(n)+len(units)}\n'.encode()+body+b''.join(f'{x} 0\n'.encode() for x in units)

def strip_four(raw):
    header,body=raw.split(b'\n',1)
    _,_,nv,n=header.split(); lines=body.splitlines()
    require(int(n)>=4 and len(lines)>=4, 'cannot strip joined assumptions')
    return f'p cnf {int(nv)} {int(n)-4}\n'.encode()+b'\n'.join(lines[:-4])+b'\n'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--all',action='store_true')
    ap.add_argument('--runtime',type=Path,help='initialized campaign runtime for independent arm-owner validation')
    opt=ap.parse_args()
    manifest=json.loads((ROOT/'local-manifest.json').read_text())
    summary=json.loads((ROOT/'local-summary.json').read_text())
    ctl=json.loads((ROOT/'full-parent-controls.json').read_text())
    nodes=json.loads((ROOT/'case0-binding.json').read_text())
    records_by_tag={r['tag']:r for r in manifest['records']}
    require(manifest['counts']=={'SAT':112,'UNSAT':400,'UNKNOWN':0},manifest['counts'])
    require(len(records_by_tag)==514,'missing or duplicate records')
    parents={k:(ROOT/'base'/f'local-branch-{k}.cnf').read_bytes() for k in (1,2)}
    # Rebuild every local query from one base and its exact four unit hypotheses.
    for r in manifest['records']:
        if r['kind']=='base':
            require(digest(ROOT/'base'/f"local-branch-{r['local_color']}.cnf")==r['query_sha256'],r['tag'])
        else:
            raw=append_units(parents[r['local_color']],r['units'])
            require(hashlib.sha256(raw).hexdigest()==r['query_sha256'],r['tag'])
            if opt.all and r['status']=='UNSAT':
                q=ROOT/'scratch-query.cnf';q.write_bytes(raw)
                checker_output(q,ROOT/r['proof'])
    # Independently validate each explicit physical local assignment and its units.
    local0={r['tag']:r for r in summary['all_calls']}
    owner=None
    if opt.runtime:
        import sys
        sys.path.insert(0,str(opt.runtime.resolve()))
        from edge_domains import valid
        owner=lambda m:valid(14,('00000','01022'),'revised',m)
    vertices=tuple(sorted(nodes['root']+nodes['A']+nodes['B']))
    require(len(set(vertices))==30,'case 0 is root plus a 14-arm and a 15-arm')
    def edge(u,v,c):
        u,v=sorted((u,v));return 4*(u*(115-u)//2+v-u-1)+c+1
    models=0
    for r in manifest['records']:
        if r['kind']!='pair' or r['status']!='SAT':continue
        models+=1
        entries=json.loads((ROOT/r['model']).read_text())
        require(len(entries)==435,(r['tag'],'edge count'))
        colored={tuple(e[:2]):e[2] for e in entries}
        require(set(colored)==set(combinations(vertices,2)) and
                all(c in range(4) for c in colored.values()),
                (r['tag'],'not complete 4-coloring'))
        for u,v,w in combinations(vertices,3):
            es=[tuple(sorted(e)) for e in combinations((u,v,w),2)]
            require(len({colored[e] for e in es})>1,(r['tag'],'monochromatic triangle',u,v,w))
        for v in vertices:
            require(max(Counter(colored[tuple(sorted((v,w)))] for w in vertices if v!=w).values())<=16,
                        (r['tag'],'degree cap'))
        for literal in r['units']:
            # Decode the canonical host edge order.
            idx=(abs(literal)-1)//4;u,v=list(combinations(range(58),2))[idx];color=(abs(literal)-1)%4
            require((colored[u,v]==color)==(literal>0),(r['tag'],'assumption',literal))
        # Verify the arm_string against its physically mapped local edges and
        # independently recheck owner/order if runtime was supplied.
        arm_string=records_by_tag[r['tag']].get('arm_string') or local0[r['tag']]['arm_string']
        pairs=list(combinations(range(14),2));require(len(arm_string)==len(pairs),r['tag'])
        for (i,j),char in zip(pairs,arm_string):
            uv=tuple(sorted((nodes['A'][i],nodes['A'][j])))
            require(colored[uv]==nodes['palette'][int(char)],(r['tag'],'arm/model mismatch'))
        if owner:owner(arm_string)
    require(models==112,models)
    # Strictly replay all eight exact full-parent joint proofs.
    for group in ctl['sets']:
        if group['kind']=='joint':
            for r in group['records']:
                q=ROOT/'full'/r['case'];
                require(hashlib.sha256(q.read_bytes()).hexdigest()==r['query_sha256'],r['case'])
                physical=0 if r['case'][5]=='1' else 3
                expected=ctl['base_branch_queries']['physical_color_'+str(physical)]
                require(hashlib.sha256(strip_four(q.read_bytes())).hexdigest()==expected,
                        ('base branch formula mismatch',r['case']))
                checker_output(q,ROOT/'full'/r['case'].replace('.cnf','.drat'))
    # Each individual UNKNOWN is retained verbatim. Reconstruct the exact
    # individual queries and their hashes without pretending the raw result SAT.
    for group in ctl['sets']:
        if group['kind']=='single':
            for r in group['records']:
                case=r['case'];c=int(case[-5])
                joint='color'+case[5]+'-'+str(0 if 'alpha' in case else c)+'.cnf'
                base=strip_four((ROOT/'full'/joint).read_bytes())
                units=[347,390] if 'alpha' in case else [565+c,610]
                query=append_units(base,units)
                require(hashlib.sha256(query).hexdigest()==r['query_sha256'],case)
                require(r['status']=='OPEN_UNKNOWN',case)
    # Every earlier raw local model was owner-checked in the original engine;
    # physical checks here cover the full 30-vertex graph, its cube units and
    # degree cap. No pair-wise global closure is asserted.
    hashes=0
    for p in (ROOT/'tool-hashes.txt').read_text().splitlines():
        wanted,name=p.split()
        if name!='tool-hashes.txt':
            require(digest(ROOT/name)==wanted,name);hashes+=1
    print(json.dumps({'models_physically_checked':models,'strict_full_parent_joint_proofs':8,
                      'individual_open_unknown_controls':10,'all_400_local_proofs_reverified':bool(opt.all),
                      'owner_models_rechecked':models if opt.runtime else 0,'file_hashes_checked':hashes,
                      'scope':'Local realizations and conditional branch-specific joint UNSAT only; no K58, row or Ramsey bound claim.'},indent=2))

if __name__=='__main__':main()
