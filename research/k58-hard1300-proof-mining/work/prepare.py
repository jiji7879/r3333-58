"""Regenerate exact full-root hard1300 parents and bind the cohort manifest."""
from pathlib import Path
import csv,hashlib,json,sys
ROOT=Path.cwd()
BASE=ROOT/'.scratch/massive-clean-install/k58-solver'
sys.path.insert(0,str(BASE/'k58'))
from cover_evidence import lookup, formula_chunks
OUT=ROOT/'.scratch/hard1300-proof-mining'
OUT.mkdir(exist_ok=True)
with (ROOT/'results/hard-tail-2026-11-27/hard1300.tsv').open() as stream:
    rows={int(x['rank']):x for x in csv.DictReader(stream,delimiter='\t')}
receipt={'schema':'k58-hard1300-exact-parent/v1','recipe':{'full_root':True,'tables':True,'total_critical':True},'cases':{}}
for rank in (1297,1300):
    m=rows[rank]
    row=lookup(BASE/'k58/case-ledger.jsonl.gz',m['id'])
    assert row['id']==m['id']
    raw=b''.join(formula_chunks(row,{'full_root':True,'tables':True,'total_critical':True}))
    assert hashlib.sha256(raw).hexdigest()==m['input_sha256'],(rank,'parent mismatch')
    path=OUT/f'rank{rank}-parent.cnf'
    path.write_bytes(raw)
    header=raw.split(b'\n',1)[0].decode()
    _,kind,nv,nc=header.split()
    assert kind=='cnf' and int(nc)==len(raw.splitlines())-1
    # Independently count host clauses and fixed-unit prefix boundaries, not
    # a suffix-specific assumption about cardinality variables.
    clauses=list(raw.splitlines()[1:])
    fixed_end=0
    while fixed_end+134995<len(clauses) and len(clauses[fixed_end+134995].split())==2:
        fixed_end+=1
    receipt['cases'][str(rank)]={'case_id':m['id'],'cohort_manifest':m,
        'path':str(path.relative_to(ROOT)),'parent_sha256':hashlib.sha256(raw).hexdigest(),
        'bytes':len(raw),'variables':int(nv),'clauses':int(nc),'fixed_unit_prefix':fixed_end,
        'family':row['family'],'placement':row['placement'],'branch':row['branch'],
        'historical_scope':'retry-tier full-root case, historically CERTIFIED; not an ordinary-wall completion'}
    if rank==1300:
        old=ROOT/'.scratch/k58-candidate-verification/proof/rank1300/rank1300.cnf'
        assert old.read_bytes()==raw
        receipt['cases'][str(rank)]['prior_parent_byte_identity']=str(old.relative_to(ROOT))
(OUT/'parents.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt['cases'],indent=2,sort_keys=True))
