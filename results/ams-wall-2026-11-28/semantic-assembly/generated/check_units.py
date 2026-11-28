#!/usr/bin/env python3
"""Whole-set binding of current Lean case units to the actual Python units."""
import hashlib,json,sys
from itertools import combinations
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools/selfcontained/wallcc/frozen'))
import audit_campaign,gluing,cover_evidence
row=json.loads((HERE/'inputs/row.json').read_text())
fields=dict(row['family']); fields['profile']=tuple(fields['profile']); fields['root_kinds']=tuple(fields['root_kinds'])
f=gluing.Family(**fields)
python_units=gluing.units(f,row['placement'])
lines=(HERE/'generated/lean-units.txt').read_text().splitlines()
assert lines[0]=='UNITS 458'
lean_units=[]
edges={e:4*i+1 for i,e in enumerate(combinations(range(58),2))}
for line in lines[1:]:
 u,v,c,pos=map(int,line.split())
 lit=edges[min(u,v),max(u,v)]+c
 lean_units.append([lit if pos else -lit])
lean_set={c[0] for c in lean_units}
python_set={c[0] for c in python_units}
assert len(lean_units)==458
assert len(lean_set)==len(python_units)==438
assert lean_set==python_set
assert [[x] for x in sorted(lean_set)]==python_units
serial=audit_campaign.lines(python_units)
result={
 'row_id':row['id'],'lean_key':{'planIndex':29,'arm':1,'markPosition':0,'secondSize':15,'secondTwisted':True,'rootPosition':7,'placement':[0,0,0]},
 'lean_caseUnitList_entries':len(lean_units),'unique_signed_literals':len(lean_set),
 'python_units':len(python_units),'ordered_python_units_equal_sorted_lean_set':True,
 'unit_dimacs_sha256':hashlib.sha256(serial).hexdigest(),'unit_dimacs_bytes':len(serial),
 'scope':'exact signed-unit set only; no full-parent or solver-status claim'
}
out=HERE/'generated/unit-binding.json';out.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
