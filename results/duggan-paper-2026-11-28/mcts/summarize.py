#!/usr/bin/env python3
import hashlib,json
from pathlib import Path

def load(path): return json.loads(Path(path).read_text())
def recs(path): return load(path+'/receipts.json') if Path(path).is_dir() else load(path)
def totals(rows):
 return {'leaves':len(rows),'conflicts':sum(r['conflicts_used'] for r in rows),
         'search_cpu_s':sum(r['cpu_s'] for r in rows),'search_elapsed_s':sum(r['elapsed_s'] for r in rows),
         'status_counts':{s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}}
def read_cubes(path):
 return [list(map(int,l.split()[1:-1])) for l in Path(path).read_text().splitlines()]
def cube_key(c):return tuple(sorted(c))
wall_mcts=recs('results/mcts-s10-leaves')
wall_greedy=[]
run=Path('../../../.scratch/shared-learning-pilot/K58_shared_learning/runs/06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06/first-depth2-arm-auto-both')
for node in ('r00','r01','r10','r11'):
 r=load(run/'leaves'/node/'receipt.json');r['cpu_s']=r['elapsed_s'];wall_greedy.append(r)
recube=recs('results/recube-leaves')
greedy=recs('results/control-greedy-leaves')
shallow=recs('results/control-mcts-leaves')
fullnew=recs('results/control-mcts-full20-new-leaves')
fullcubes=read_cubes('results/control-mcts-full20-s10.cubes')
positive_map={cube_key(r['cube']):r for r in shallow}
full=[]
for c in fullcubes:
 if c[0]==4141: full.append(positive_map[cube_key(c)])
 else:
  match=[r for r in fullnew if cube_key(r['cube'])==cube_key(c)];assert len(match)==1;full+=match
assert len(full)==4 and all(r['status']=='CHECKED_UNSAT' for r in full)
# All four distinct cover cubes must occur exactly once in each experiment.
assert {cube_key(c) for c in fullcubes}=={cube_key(r['cube']) for r in full}
summary={'schema':'duggan-alphamaplesat-k58-assessment/v1',
 'wall':{'row':load(run/'plan.json')['origin']['id'],'greedy':totals(wall_greedy),'shallow_mcts':totals(wall_mcts),'selective_recube':totals(recube)},
 'control':{'case':'0f9ba81047f417888a4c5291b6529e2ebca30f08d0412361e6e86b53b859580d',
            'greedy':totals(greedy),'shallow_mcts':totals(shallow),'full20_mcts':totals(full)},
 'cubing':{'wall_shallow_mcts_s':load('results/mcts-s10.json')['elapsed_s'],
           'wall_selective_recube_s':load('results/recube-s10.json')['elapsed_s'],
           'control_greedy_prepare_s':0.72,
           'control_shallow_mcts_s':load('results/control-mcts-s10.json')['elapsed_s'],
           'control_full20_mcts_s':load('results/control-mcts-full20-s10.json')['elapsed_s']}}
summary['control']['full20_vs_greedy']={'conflict_ratio':summary['control']['full20_mcts']['conflicts']/summary['control']['greedy']['conflicts'],
   'search_cpu_ratio':summary['control']['full20_mcts']['search_cpu_s']/summary['control']['greedy']['search_cpu_s']}
Path('results/summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
Path('results/control-full20-combined-receipts.json').write_text(json.dumps(full,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
