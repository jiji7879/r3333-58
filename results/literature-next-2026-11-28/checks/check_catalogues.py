import ast, json, pathlib, sys
REPO=pathlib.Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo')
OWN=REPO/'.ultramath/smx04thj8/m6'
sys.dont_write_bytecode=True
sys.path.insert(0,str(REPO/'tools/color-resolved-wallcc/frozen'))
from support_tables import allowed_supports

def block(path,start,end):
    return path.read_text().split(start,1)[1].split(end,1)[0].strip()

target=ast.literal_eval(block(REPO/'lean/K58/TargetSuffix.lean',
    'def targetSupports : List (List Nat) :=','\n\n/-- Exact linked allocation'))
mask_text=block(OWN/'.scratch/k60/upstream/formal/src/UniformK60/BalancedAnchorSupport.lean',
    'def supportMasks : Array (Array (Array Nat)) := #','\n\ndef minorIndex')
masks=ast.literal_eval(mask_text.replace('#[','['))
rows=[]
for minor,n in enumerate((16,15)):
    for twisted,kind in enumerate(('U','T')):
        expected=[[j for j in range(16) if (m>>j)&1] for m in masks[minor][twisted]]
        expected_set={tuple(x) for x in expected}
        exact_ordered=[]; exact_set=[]
        for arm in range(4):
            for marked in range(4):
                if arm==marked: continue
                actual=[sorted(s) for s in allowed_supports(n,kind,arm,marked)]
                (exact_ordered if actual==expected else exact_set).append((arm,marked)) \
                    if actual==expected or {tuple(x) for x in actual}==expected_set else None
        mismatches=[(arm,marked) for arm in range(4) for marked in range(4)
                    if arm!=marked and (arm,marked) not in exact_ordered and (arm,marked) not in exact_set]
        rows.append({'minor':bool(minor),'n':n,'kind':kind,'count':len(expected),
            'exact_ordered_palettes_arm_marked':exact_ordered,
            'same_set_different_order_palettes_arm_marked':exact_set,
            'different_set_palettes_arm_marked':mismatches})
actual_target=[sorted(s) for s in allowed_supports(16,'T',0,1)]
upstream_target=[[j for j in range(16) if (m>>j)&1] for m in masks[0][1]]
result={'checks':rows,
  'interpretation':"Four (arm,marked) palettes share K60's colour-2 ordered masks. The other eight differ as sets and need an explicit colour transport. The retained (0,1) palette matches.",
  'target_112_equals_allowed_supports_16_T_arm0_marked1_ordered':target==actual_target,
  'target_112_equals_upstream_full_T_ordered':target==upstream_target,
  'target_size_counts':{str(k):sum(len(s)==k for s in target) for k in (4,5)}}
assert all(not r['same_set_different_order_palettes_arm_marked'] for r in rows)
assert all(len(r['exact_ordered_palettes_arm_marked'])==4 for r in rows)
assert all(len(r['different_set_palettes_arm_marked'])==8 for r in rows)
assert result['target_112_equals_allowed_supports_16_T_arm0_marked1_ordered']
assert result['target_112_equals_upstream_full_T_ordered']
print(json.dumps(result,indent=2))
(OWN/'.scratch/k60/catalogue-check.json').write_text(json.dumps(result,indent=2)+'\n')
