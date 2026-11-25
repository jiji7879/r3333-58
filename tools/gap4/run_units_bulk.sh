#!/bin/bash
# Refute the open rows of profile (15,15,15,12) from their FROZEN UNITS ALONE.
#
#   bash tools/gap4/run_units_bulk.sh ROWS.txt OUTDIR [WORKERS]
#
# ROWS.txt: one row id per line (the OPEN ids of profile 15,15,15,12 in
# results/ledger-2026-11-22.tsv.gz, or any list).  For each row:
#   1. build the certified row CNF        tools/pb/balance.py ID row.cnf --dense
#   2. keep only host(58)+units            every literal with |l| <= 6612
#   3. solve                               kissat, capped
#   4. verify                              drat-trim -c must print "s VERIFIED"
# and append "id verdict seconds units_sha drat_sha" to OUTDIR/verdicts.tsv.
# The units CNF is a clause subset of the row's certified CNF (verified on
# 0684ba38: all 135,498 clauses present, 0 missing), so UNSAT transfers to the row.
#
# Needs pysat for balance.py: PYTHONPATH=<site-packages> or the k58-solver venv.
set -u
ROWS=$1; OUT=$2; W=${3:-4}
HERE=$(cd "$(dirname "$0")/../.." && pwd)
K=${KISSAT:-$(command -v kissat)}
D=${DRATTRIM:-$(command -v drat-trim)}
mkdir -p "$OUT"
[ -f "$OUT/verdicts.tsv" ] || printf 'row\tverdict\tseconds\tunits_sha\tdrat_sha\n' > "$OUT/verdicts.tsv"
one(){
  id=$1; OUT=$2
  grep -q "^$id	" "$OUT/verdicts.tsv" && return 0
  row=$OUT/$id.row.cnf; units=$OUT/$id.units.cnf; drat=$OUT/$id.drat
  python3 "$HERE/tools/pb/balance.py" "$id" "$row" --dense > "$OUT/$id.build.log" 2>&1 || {
    printf '%s\tBUILDFAIL\t0\t-\t-\n' "$id" >> "$OUT/verdicts.tsv"; return 0; }
  python3 - "$row" "$units" <<'PY'
import sys
src,dst=sys.argv[1],sys.argv[2]
with open(src) as f:
    h=f.readline().split(); nv=int(h[2]); cls=[]
    for line in f:
        if not line.strip(): continue
        l=[int(x) for x in line.split()[:-1]]
        if all(abs(x)<=6612 for x in l): cls.append(l)
with open(dst,'w') as g:
    g.write('p cnf %d %d\n'%(nv,len(cls)))
    g.write(''.join(' '.join(map(str,c))+' 0\n' for c in cls))
PY
  sha=$(sha256sum "$units" | cut -d' ' -f1)
  t0=$(date +%s)
  timeout 900 nice -n 10 "$K" -q --time=840 "$units" "$drat" > "$OUT/$id.log" 2>&1
  rc=$?
  t1=$(date +%s)
  if [ $rc -eq 20 ]; then
    "$D" "$units" "$drat" -c > "$OUT/$id.drat.log" 2>&1
    if grep -q 's VERIFIED' "$OUT/$id.drat.log"; then v=UNSAT_VERIFIED; else v=UNSAT_UNCHECKED; fi
    dsha=$(sha256sum "$drat" | cut -d' ' -f1)
  else
    v=OTHER_$rc; dsha=-
  fi
  printf '%s\t%s\t%d\t%s\t%s\n' "$id" "$v" $((t1-t0)) "$sha" "$dsha" >> "$OUT/verdicts.tsv"
  rm -f "$row" "$units" "$drat"
}
export -f one
export K D HERE
cat "$ROWS" | xargs -r -P "$W" -I{} bash -c 'one "$@"' _ {} "$OUT"
