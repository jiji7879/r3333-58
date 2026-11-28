#!/bin/sh
# Run from .ultramath/smwzxq4fl/m8/. Small controls only; no production search.
set -eu
export PYTHONDONTWRITEBYTECODE=1
PY=python3
CADICAL=/opt/lean/bin/cadical
DRAT=../../../tools/color-resolved-wallcc/bin/drat-trim
VC="$PY ../../../tools/verify_coloring.py"
$PY mcf_pilot.py exhaustive --out exhaustive > exhaustive_console.txt
set +e
$CADICAL -q exhaustive/frozen_baseline.cnf -w exhaustive/solution_baseline_n5.sol > exhaustive/frozen_baseline_run.log 2>&1
rc=$?
set -e
[ "$rc" -eq 10 ]
set +e
$CADICAL -q exhaustive/frozen_mcf.cnf exhaustive/frozen_mcf.drat > exhaustive/frozen_mcf_run.log 2>&1
rc=$?
set -e
[ "$rc" -eq 20 ]
$DRAT exhaustive/frozen_mcf.cnf exhaustive/frozen_mcf.drat > exhaustive/frozen_mcf_drat.log 2>&1
# This first proof stream has a deletion warning; display and reject it.
grep 's VERIFIED' exhaustive/frozen_mcf_drat.log
if grep -Ei 'warning|error' exhaustive/frozen_mcf_drat.log; then
    echo 'REJECTED proof receipt: warning present'
else
    echo 'UNEXPECTED: warning reproduction missing' >&2
    exit 1
fi
: > exhaustive/frozen_mcf_empty.drat
$DRAT exhaustive/frozen_mcf.cnf exhaustive/frozen_mcf_empty.drat > exhaustive/frozen_mcf_empty_drat.log 2>&1
if grep -Ei 'warning|error' exhaustive/frozen_mcf_empty_drat.log; then
    echo 'STRICT PROOF FAILED' >&2
    exit 1
fi
grep 's VERIFIED' exhaustive/frozen_mcf_empty_drat.log
echo 'STRICT EMPTY-ADDITION CHECK=PASS'
$PY mcf_pilot.py verify-solution exhaustive/frozen_baseline.cnf exhaustive/solution_baseline_n5.sol

$PY mcf_pilot.py encode --n 10 --out unpinned > encoding_console.txt
set +e
$CADICAL -q unpinned/unpinned_baseline.cnf -w unpinned/solution_baseline_n10.sol > unpinned_baseline_run.log 2>&1
b=$?
$CADICAL -q unpinned/unpinned_mcf.cnf -w unpinned/solution_mcf_n10.sol > unpinned_mcf_run.log 2>&1
m=$?
set -e
[ "$b" -eq 10 ] && [ "$m" -eq 10 ]
$PY mcf_pilot.py verify-solution unpinned/unpinned_baseline.cnf unpinned/solution_baseline_n10.sol
$PY mcf_pilot.py verify-solution unpinned/unpinned_mcf.cnf unpinned/solution_mcf_n10.sol --maximal-colour 0

$PY mcf_pilot.py artifacts --out artifact_outputs \
  ../../../artifacts/k50_z4z4_m6.col \
  ../../../artifacts/k50_blockcayley_Z4xZ4_m4.col \
  ../../../artifacts/k50_sanity_f2.col \
  ../../../artifacts/k51_relax_m3_1defect_NOT_a_valid_colouring.col > artifact_console.txt
$PY k40_control.py --source ../../../artifacts/k40_two_16arms_UT_s7.col --out k40_outputs > k40_console.txt
: > independent_coloring_checks.log
for f in artifact_outputs/*.col k40_outputs/*.col; do
    $VC "$f" >> independent_coloring_checks.log
done
cat independent_coloring_checks.log
[ "$(wc -l < independent_coloring_checks.log)" -eq 14 ]
if grep -v '^VALID:' independent_coloring_checks.log; then
    echo 'INDEPENDENT COLOURING CHECK FAILED' >&2
    exit 1
fi

# Negative searches, expected exit 1 = no counterexample in stated finite scans.
set +e
$PY search_frozen.py --n 6 --out frozen6 > frozen6_scan_console.txt
r6=$?
$PY search_frozen.py --n 7 --require-four-root-colours --out frozen7 > frozen7_scan_console.txt
r7=$?
set -e
[ "$r6" -eq 1 ] && [ "$r7" -eq 1 ]

# Regenerate and bind the exact current parent without writing to the package.
../../../.scratch/k58/.venv/bin/python prepare_wall_parent.py \
  --tools ../../../tools/color-resolved-wallcc --row 06861a3df60c --tier first \
  --expect-sha256 90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae \
  --out wall_control/parent.cnf > wall_parent_console.txt
$PY augment_mcf_dimacs.py wall_control/parent.cnf wall_control/parent_mcf_c0.cnf \
  --n 58 --colour 0 > wall_mcf_c0_console.txt
$PY augment_mcf_dimacs.py wall_control/parent.cnf wall_control/parent_mcf_c0_pinned.cnf \
  --n 58 --colour 0 --pinned-only > wall_mcf_c0_pinned_console.txt

/usr/bin/time -f 'wall=%e user=%U sys=%S rss_kb=%M exit=%x' -o wall_control/baseline_10k.time \
  $CADICAL -c 10000 wall_control/parent.cnf > wall_control/baseline_10k.log 2>&1
/usr/bin/time -f 'wall=%e user=%U sys=%S rss_kb=%M exit=%x' -o wall_control/mcf_c0_10k.time \
  $CADICAL -c 10000 wall_control/parent_mcf_c0.cnf > wall_control/mcf_c0_10k.log 2>&1
/usr/bin/time -f 'wall=%e user=%U sys=%S rss_kb=%M exit=%x' -o wall_control/mcf_c0_pinned_10k.time \
  $CADICAL -c 10000 wall_control/parent_mcf_c0_pinned.cnf > wall_control/mcf_c0_pinned_10k.log 2>&1
for f in wall_control/baseline_10k.time wall_control/mcf_c0_10k.time wall_control/mcf_c0_pinned_10k.time; do
    cat "$f"
done
for f in wall_control/baseline_10k.log wall_control/mcf_c0_10k.log wall_control/mcf_c0_pinned_10k.log; do
    echo "$f"
    grep -E '^c (conflicts|decisions|propagations):' "$f"
done

$PY - <<'PY'
import json
from mcf_pilot import host_cnf, mcf_cnf
records=[]
for n in (51,58):
    top,base=host_cnf(n)
    top2,extra=mcf_cnf(n,0,top)
    records.append(dict(n=n,physical_variables=top,base_clauses=len(base),
        full_mcf_auxiliary_variables=top2-top,full_mcf_extra_clauses=len(extra),
        full_mcf_variables=top2,full_mcf_total_clauses=len(base)+len(extra),
        long_obligation_clauses=n*(n-1)//2,long_obligation_clause_length=n-1))
open('size_estimates.json','w').write(json.dumps(records,indent=2)+'\n')
assert records[0]['full_mcf_auxiliary_variables']==62475
assert records[1]['full_mcf_extra_clauses']==279357
ex=json.load(open('exhaustive/exhaustive.json'))
assert ex['good_colourings']==542952 and ex['maximal_incidence_vertices_checked']==117720
assert ex['maximal_incidence_violations']==0
ar=json.load(open('artifact_outputs/artifact_results.json'))
valid=[x for x in ar if 'incidence' in x]
assert len(valid)==12 and all(x['final_missing_paths']==0 for x in valid)
assert all(x['incidence']['global_min_degree_bound_valid'] for x in valid)
k=json.load(open('k40_outputs/k40_results.json'))
assert k[0]['root_star_and_arm_interiors_preserved'] and k[1]['root_star_and_arm_interiors_preserved']
assert not k[2]['root_star_and_arm_interiors_preserved']
w=json.load(open('wall_control/parent_mcf_c0_pinned.json'))
assert w['retained_obligations']==45 and w['fresh_auxiliary_variables']==2520
assert w['extra_clauses']==7605 and w['static_physical_only_not_a_verdict']['no_witness_possible']==0
print('JSON CONTROL ASSERTIONS=PASS')
PY
echo 'ALL REPRODUCTION CONTROLS COMPLETE; ALL WALL JOBS REMAIN OPEN AT CAP'
