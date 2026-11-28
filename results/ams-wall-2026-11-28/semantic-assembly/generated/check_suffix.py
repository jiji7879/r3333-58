#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parents[1]
m=json.loads((H/'generated/parent-trace.json').read_text())
lean=(H/'generated/lean-suffix.txt').read_bytes().splitlines(keepends=True)
assert lean[0].startswith(b"'targetSuffix_satisfiable_of_ready' depends on axioms: [propext, Classical.choice, Quot.sound]")
assert lean[1]==b'COUNT 48902\n'
lean_bytes=b''.join(lean[2:])
parent=(H/'inputs/parent.cnf').read_bytes().splitlines(keepends=True)
skip=1+m['base']['count']+m['fixed_units']['count']
parent_extra=b''.join(parent[skip:])
assert len(lean)-2==m['extra']['count']==48902
assert lean_bytes==parent_extra
result={'row_id':m['row_id'],'parent_sha256':m['parent_sha256'],'extra_clauses':m['extra']['count'],
        'extra_start_parent_clause':m['base']['count']+m['fixed_units']['count']+1,
        'extra_end_parent_clause':m['base']['count']+m['fixed_units']['count']+m['extra']['count'],
        'extra_sha256':hashlib.sha256(lean_bytes).hexdigest(),'extra_bytes':len(lean_bytes),
        'lean_targetSuffixCNF_length':len(lean)-2,'whole_extra_byte_identity':True,
        'final_top':19533,'axioms_targetSuffix_satisfiable_of_ready':['propext','Classical.choice','Quot.sound'],
        'solver_called':False,'scope':'exact CNF suffix and conditional extension, no ChainReady physical premises discharged here'}
out=H/'generated/suffix-binding.json';out.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
