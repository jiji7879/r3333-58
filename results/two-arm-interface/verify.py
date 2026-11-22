"""Verification of the two claims that carry member m8's report.

  python3 verify.py witness wit/rung3.wit
      rung3 must satisfy every family except the arm module and the cross-arm
      module, and must fail on nothing else.

  python3 verify.py cnf cnf/fixB_m1.cnf
      rebuild the same CNF from the encoder and compare clause for clause.

  python3 verify.py drat cnf/fixB_m1.cnf log/fixB_m1.drat.gz
      replay the refutation with drat-trim.
"""
import gzip
import itertools
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enc import build                      # noqa: E402
from model import (check_two_arm, read_witness,  # noqa: E402
                   template_colours)

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../")
DRATTRIM = os.path.join(R, ".scratch/satcheck/bin/drat-trim")
ALL_FAM = {"Z", "I", "C1", "C1sum", "pair", "pairuniq", "C2", "armT", "crossT", "C3"}
RUNG3 = set(ALL_FAM) - {"armT", "crossT"}


def verify_witness(path, expected_failures=("T: monochromatic triangle inside an arm",
                                           "T: monochromatic cross-arm triangle")):
    M = template_colours(15, twisted=True)
    tpl, arms, words, pairs = read_witness(path)
    bad = check_two_arm(M, arms, words, pairs)
    fams = {}
    for b in bad:
        fams[b[0]] = fams.get(b[0], 0) + 1
    print(f"{path}: {len(words)} words, {len(pairs)} pairs")
    print("   failures by family:", fams)
    unexpected = [b for b in bad if b[0] not in expected_failures]
    print("   unexpected failures:", len(unexpected), unexpected[:5])
    ok = not unexpected
    # the families that are absent from the instance must be exactly the
    # failures: nothing else may fail
    print("   VERDICT:", "OK" if ok else "FAIL")
    return ok


def verify_cnf(path):
    cnf, *_ = build(14, 14, ALL_FAM, None, None)
    rebuilt = [f"p cnf {cnf.nv} {len(cnf.clauses)}"]
    rebuilt += [" ".join(map(str, cl)) + " 0" for cl in cnf.clauses]
    with open(path) as fh:
        mine = [line.strip() for line in fh if line.strip()]
    header = mine[0].split()
    body = mine[1:]
    base = rebuilt[1:]
    n = min(len(base), len(body))
    same_prefix = all(base[i] == body[i] for i in range(n))
    print(f"{path}: header {mine[0]!r}, {len(body)} clauses; "
          f"base rebuild {len(base)} clauses, extra units {len(body) - len(base)}")
    print("   header count matches:", int(header[3]) == len(body),
          " vars match:", int(header[2]) == cnf.nv)
    print("   base identical:", same_prefix)
    if not same_prefix:
        for i in range(n):
            if base[i] != body[i]:
                print("   first difference at clause", i + 1, base[i][:80], "|", body[i][:80])
                break
    units = body[len(base):]
    print("   first units:", units[:3], "...", units[-2:])
    ok = (same_prefix and len(body) > len(base)
          and int(header[3]) == len(body) and int(header[2]) == cnf.nv)
    print("   VERDICT:", "OK" if ok else "FAIL")
    return ok


def verify_drat(cnfpath, proofpath):
    tmp = "drat_tmp"
    if proofpath.endswith(".gz"):
        with gzip.open(proofpath, "rb") as fh, open(tmp, "wb") as out:
            shutil.copyfileobj(fh, out)
        proof = tmp
    else:
        proof = proofpath
    p = subprocess.run([DRATTRIM, cnfpath, proof], capture_output=True, text=True)
    tail = [l for l in p.stdout.splitlines() if l.startswith(("s ", "c 0 RAT"))]
    print("drat-trim:", " | ".join(tail))
    if proof == tmp:
        os.remove(tmp)
    ok = any("s VERIFIED" in l for l in p.stdout.splitlines())
    print("   VERDICT:", "OK" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "witness":
        ok = verify_witness(sys.argv[2])
    elif what == "cnf":
        ok = verify_cnf(sys.argv[2])
    elif what == "drat":
        ok = verify_drat(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit("unknown mode")
    sys.exit(0 if ok else 1)
