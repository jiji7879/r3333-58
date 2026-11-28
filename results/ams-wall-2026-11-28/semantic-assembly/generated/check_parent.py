#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parents[1]
raw=(H/'generated/lean-parent.txt').read_bytes().splitlines(keepends=True)
starts=[i for i,l in enumerate(raw) if l.startswith(b'p cnf ')]
assert len(starts)==1
i=starts[0]
assert raw[i]==b'p cnf 19533 184335\n'
lean=b''.join(raw[i:])
retained=(H/'inputs/parent.cnf').read_bytes()
assert lean==retained,(len(lean),len(retained))
assert b'sorryAx' not in b''.join(raw[:i])
result={'row_id':'06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06',
 'parent_sha256':hashlib.sha256(retained).hexdigest(),'parent_bytes':len(retained),
 'parent_variables':19533,'parent_clauses':184335,'lean_targetParentCNF_length':len(raw)-i-1,
 'whole_parent_byte_identity':True,
 'working_sha256':'39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38',
 'rup_cas_prefix_sha256':'dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3',
 'conditional_theorem':'targetParent_satisfiable_of_ready',
 'axioms':['propext','Classical.choice','Quot.sound'],
 'remaining_hypotheses':['FormulaSat v (hostBaseCNF ++ targetUnitCNF)','VarsBelow (hostBaseCNF ++ targetUnitCNF) 6612','ChainReady 6612 v targetSuffixSteps'],
 'solver_called':False,'scope':'exact full-parent CNF binding and conditional semantic assembly; not a physical-row closure or solver verdict'}
out=H/'generated/parent-binding.json';out.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
