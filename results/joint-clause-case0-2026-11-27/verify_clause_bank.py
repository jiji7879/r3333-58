#!/usr/bin/env python3
"""Replay eight case-specific parent-entailed joint clauses (no global rule).
Extract ZIP, then: python3 verify_clause_bank.py. It does not use campaign code.
If needed, rebuild the checker:
  cc -std=c99 -D_GNU_SOURCE -O2 tools/drat-trim.c -o tools/drat-trim
"""
import hashlib
from itertools import combinations
import json
import re
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
EDGE_INDEX={e:i for i,e in enumerate(combinations(range(58),2))}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,label):
    if not ok:raise AssertionError(label)
def lit(u,v,col):return 4*EDGE_INDEX[tuple(sorted((u,v)))]+1+col

def serialize(nv,clauses):
    return f'p cnf {nv} {len(clauses)}\n'.encode()+b''.join(
        (' '.join(map(str,clause))+' 0\n').encode() for clause in clauses)

def cnf(raw):
    header,body=raw.split(b'\n',1)
    parts=header.split();require(parts[:2]==[b'p',b'cnf'],header)
    nv,nc=map(int,parts[2:]);lines=body.splitlines()
    assert len(lines)==nc,(nv,nc,len(lines))
    return nv,[list(map(int,line.split()[:-1])) for line in lines]

def strict(query,proof):
    call=subprocess.run([str(ROOT/'tools/drat-trim'),str(query),str(proof),'-i','-U','-t','300'],capture_output=True)
    status=[line for line in call.stdout.splitlines() if line.startswith(b's ')]
    require(call.returncode==0 and status==[b's VERIFIED'] and b'WARNING' not in call.stdout.upper(),
            (str(query),str(proof),call.returncode,call.stdout[-500:]))

def main():
    audit=json.loads((ROOT/'clause-audit.json').read_text())
    require(audit['count']==8 and len(audit['entailed_clauses'])==8,'not exactly eight scoped clauses')
    parents={i:(ROOT/'parents'/f'branch{i}.cnf').read_bytes() for i in (1,2)}
    hashes={r['branch_local_color'] if 'branch_local_color' in r else None for r in audit['entailed_clauses']}
    for r in audit['entailed_clauses']:
        tag=r['tag'];m=re.fullmatch(r'branch([12])-w1-1-w2-([0-9]+)',tag)
        require(m is not None,tag);branch=int(m.group(1));w=int(m.group(2))
        require(w in (2,9,11,13),w)
        expected=[-lit(31,1,2),-lit(42,1,1),-lit(42,w,1)]
        require(r['clause']==expected,(tag,r['clause'],expected))
        nv,parent_clauses=cnf(parents[branch]);qpath=ROOT/'clauses'/f'{tag}.cnf'
        nv2,query_clauses=cnf(qpath.read_bytes());require(nv==nv2,'nv mismatch')
        expected_query=serialize(nv,parent_clauses+[[-x] for x in expected])
        require(expected_query==qpath.read_bytes(),tag+' query does not match parent+negation')
        require(sha(qpath.read_bytes())==r['query_sha256'],tag+' query hash')
        p=ROOT/'clauses'/f'{tag}.drat'
        require(sha(p.read_bytes())==r['proof_sha256'],tag+' proof hash')
        strict(qpath,p)
        base_hash=sha(serialize(nv,parent_clauses))
        require(base_hash==r['parent_sha256'],tag+' stripped parent hash')
    for color in (1,2):
        parent=parents[color]
        nv,clauses=cnf(parent)
        goal_rows=[next(r['clause'] for r in audit['entailed_clauses'] if int(r['tag'].split('-')[0][-1])==color and
                     int(r['tag'].split('-w2-')[1])==w) for w in (2,9,11,13)]
        expected=serialize(nv,clauses+goal_rows)
        q=ROOT/'augmented'/f'color{color}-strengthened.cnf'
        require(q.read_bytes()==expected,'strengthened formula not exactly parent+4 proven clauses')
        receipt=json.loads((ROOT/'augmented'/f'color{color}-strengthened.json').read_text())
        require(receipt['query_sha256']==sha(expected) and receipt['status']=='UNKNOWN','strengthened status')
    hashes_done=0
    for raw_line in (ROOT/'tool-hashes.txt').read_text().splitlines():
        expected_hash,name=raw_line.split()
        if name!='tool-hashes.txt':
            require(sha((ROOT/name).read_bytes())==expected_hash,name);hashes_done+=1
    print(json.dumps({'proofs_replayed':8,'literal_goal_definitions_checked':8,
                      'parent_hashes_checked':8,'strengthened_formulas_and_OPEN_UNKNOWN_checked':2,
                      'whole_branch_closed':False,'file_hashes_checked':hashes_done,
                      'scope':'Only these exact case-0 branches entail the displayed clauses. No generic Wave A transfer, full branch/row closure or Ramsey result.'},indent=2))

if __name__=='__main__':main()
