#!/bin/sh
# One-command reproduction of every check reported in README.md.
# Run from this directory:  sh reproduce.sh
# Requires: python3, the repository's drat-trim, and an interpreter with
# python-sat 1.9.dev22 (set K58_PYSAT_PYTHON).  Nothing outside this directory
# is written.  Wall time about 60 s; solver CPU about 5 s.
set -eu
REPO=$(cd ../../.. && pwd)
HERE=$(pwd)
DT="$REPO/tools/color-resolved-wallcc/bin/drat-trim"
CAD="$REPO/tools/color-resolved-wallcc/bin/cadical-2.1.2"
PY=${K58_PYSAT_PYTHON:-$REPO/.scratch/k58/.venv/bin/python}
HOST="$REPO/.scratch/m7/stock-cube.cnf"          # retained parent+cube, hash-pinned below
HOST_SHA=8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8
H7="$REPO/.ultramath/smx06hpp8/m5/.scratch/runs/H7/input.cnf"
R11="$REPO/.ultramath/smx06hpp8/m5/.scratch/runs/R11/input.cnf"
mkdir -p work

echo "== 1. one-shot simplification of the retained parent+cube =="
python3 prep.py --cnf "$HOST" --expect-sha256 $HOST_SHA \
        --out work/host.red.cnf --proof work/host.prefix.drat \
        --proof-binary work/host.prefix.bdrat --receipt work/host.receipt.json || exit 1
sha256sum work/host.red.cnf work/host.prefix.drat work/host.prefix.bdrat

echo "== 2. prefix verified independently, both encodings =="
"$PY" check_prefix.py --cnf "$HOST" --prefix work/host.prefix.drat --format ascii \
        --reduced work/host.red.cnf --receipt work/host.check.ascii.json >/dev/null
"$PY" check_prefix.py --cnf "$HOST" --prefix work/host.prefix.bdrat --format binary \
        --reduced work/host.red.cnf --receipt work/host.check.binary.json >/dev/null
python3 -c "import json;d=json.load(open('work/host.check.binary.json'));print(d['verdict'],d['prefix'],d['engine_clause_checks'])"

echo "== 3. corruption controls must fail closed =="
python3 - <<'PY'
from pathlib import Path
import prep
lines = Path("work/host.prefix.drat").read_text().splitlines()
adds, dels = [], []
for line in lines:
    f = line.split()
    if f and f[0] == "d": dels.append(tuple(map(int, f[1:-1])))
    else: adds.append(tuple(map(int, f[:-1])))
bad = list(adds); bad[7] = (-bad[7][0],) + tuple(bad[7][1:])
Path("work/corrupt1.prefix.bdrat").write_bytes(prep.binary_drat(bad, dels))
bad2 = list(adds); k = next(i for i, a in enumerate(bad2) if len(a) > 1)
bad2[k] = tuple(bad2[k][:-1])
Path("work/corrupt2.prefix.bdrat").write_bytes(prep.binary_drat(bad2, dels))
PY
for c in 1 2; do
  if "$PY" check_prefix.py --cnf "$HOST" --prefix work/corrupt$c.prefix.bdrat --format binary \
        --reduced work/host.red.cnf >/dev/null 2>&1; then
    echo "CONTROL $c FAILED TO FAIL"; exit 1
  else
    echo "control $c rejected as required"
  fi
done

echo "== 4. R11: the existing closed leaf is refuted at root =="
python3 prep.py --cnf "$R11" --out work/r11.red.cnf --proof work/r11.prefix.drat \
        --proof-binary work/r11.prefix.bdrat --receipt work/r11.receipt.json || rc=$?
echo "prep exit ${rc:-0} (3 = root conflict, which is the point)"
"$DT" "$R11" work/r11.prefix.bdrat -i | tail -2
"$DT" "$R11" work/r11.prefix.drat -I | tail -2

echo "== 5. H7: solve host and reduced, then check the reduced proof on the host =="
python3 prep.py --cnf "$H7" --out work/h7.red.cnf --proof work/h7.prefix.drat \
        --proof-binary work/h7.prefix.bdrat --receipt work/h7.receipt.json || exit 1
sha256sum work/h7.red.cnf
"$CAD" --seed=0 --binary=true -q "$H7" work/h7.host.drat || test $? -eq 20
"$CAD" --seed=0 --binary=true -q work/h7.red.cnf work/h7.red.drat || test $? -eq 20
ls -l work/h7.host.drat work/h7.red.drat
cat work/h7.prefix.bdrat work/h7.red.drat > work/h7.composed.bdrat
echo "-- reduced-formula proof on the HOST:"
"$DT" "$H7" work/h7.red.drat -i | tail -2
echo "-- composed prefix+proof on the HOST:"
"$DT" "$H7" work/h7.composed.bdrat -i | tail -2
python3 - <<'PY'
from pathlib import Path
import prep
lines = Path("work/h7.prefix.drat").read_text().splitlines()
adds, dels = [], []
for line in lines:
    f = line.split()
    if f and f[0] == "d": dels.append(tuple(map(int, f[1:-1])))
    else: adds.append(tuple(map(int, f[:-1])))
bad = list(adds); bad[0] = (-bad[0][0],) + tuple(bad[0][1:])
Path("work/h7.corrupt.prefix.bdrat").write_bytes(prep.binary_drat(bad, dels))
PY
cat work/h7.corrupt.prefix.bdrat work/h7.red.drat > work/h7.corrupt.composed.bdrat
echo "-- control: one corrupted prefix unit must break the composed check:"
if "$DT" "$H7" work/h7.corrupt.composed.bdrat -i | grep -q "s VERIFIED"; then
  echo "CONTROL FAILED TO FAIL"; exit 1
else
  echo "corrupted composition rejected as required"
fi

echo "== 6. matched capped A/B on the retained parent+cube (4 seeds) =="
K58_PYSAT_PYTHON="$PY" python3 bench.py --out work/bench \
        --arm host="$HOST"@$HOST_SHA \
        --arm reduced=work/host.red.cnf@"$(sha256sum work/host.red.cnf | cut -d' ' -f1)" \
        --seeds 0,1,2,3 --caps 100000 | tail -8
echo "done"
