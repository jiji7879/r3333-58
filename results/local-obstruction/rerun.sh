#!/bin/sh
# Everything in REPORT.md, end to end.  Run from this directory.
set -e
P=../../../.scratch/k58/.venv/bin/python
echo "== 1. MIS machinery vs brute force"
python3 scripts/mis.py --selftest
echo "== 2. alpha(G_c) on every colouring artefact (expect max 16 everywhere at n>=49)"
python3 scripts/alpha_col.py
echo "== 3. alpha(G_0) of the five order-58 pair-level witnesses"
python3 scripts/hall_alpha.py
echo "== 4. every alpha re-decided by SAT at alpha (SAT) and alpha+1 (UNSAT)"
$P scripts/crosscheck_mis.py | tail -20
echo "== 5. the I = A reduction over all S (2^15 zeta transform)"
python3 scripts/hall_IA.py
echo "== 6. exact max margin = min(alpha_0,30) - 16"
python3 scripts/hall_exact.py
echo "== 7. Hall certificates, and their standalone re-check"
python3 scripts/hall_ship.py
python3 scripts/verify_hall.py
echo "== 8. the two witnesses the record describes but never stores"
python3 scripts/hall_hand_witnesses.py
echo "== 9. Hall verdict for every witness on disk"
python3 scripts/hall_all.py
echo "== 10. three-word obstruction: certificates + exhaustive counts"
python3 scripts/obstruction.py | tail -2
python3 scripts/verify_obstruction.py
echo "== 11. exact arm-module CSP: minimal infeasible sub-arm = 3, same counts"
$P scripts/arm_sat.py | tail -20
echo "== 12. CSP validated against the witnesses' own legal colourings"
$P scripts/arm_validate.py
echo
echo "DONE: all certificates verified."
