"""Consolidate every decided instance in out/ into one table (and a JSON dump).

For each tag:
  * the CNF header (vars/clauses) and its sha256 -> the CNF is regenerated from gy.py
  * the solver verdict from the kissat log
  * the drat-trim verdict from the verify log (UNSAT cases)
  * for SAT cases the model file and the checker verdict
"""
import glob
import hashlib
import json
import os
import re

OUT = "out"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    rows = []
    for log in sorted(glob.glob(os.path.join(OUT, "*.kissat.log"))):
        tag = os.path.basename(log)[:-len(".kissat.log")]
        status = None
        with open(log, errors="ignore") as fh:
            for line in fh:
                if line.startswith("s "):
                    status = line.split()[1]
        cnf = os.path.join(OUT, tag + ".cnf")
        head = open(cnf).readline().split()
        nv, nc = int(head[2]), int(head[3])
        row = dict(tag=tag, status=status or "INCOMPLETE", vars=nv, clauses=nc,
                   cnf_sha256=sha(cnf))
        if status == "UNSATISFIABLE":
            proof = os.path.join(OUT, tag + ".drat")
            vl = os.path.join(OUT, tag + ".verify.log")
            verified = None
            if os.path.exists(vl):
                verified = "s VERIFIED" in open(vl, errors="ignore").read()
            row["drat_replayed"] = verified
            if os.path.exists(proof):
                row["drat_sha256"] = sha(proof)
                row["drat_bytes"] = os.path.getsize(proof)
        else:
            model = os.path.join(OUT, tag + ".model.json")
            if os.path.exists(model):
                m = json.load(open(model))
                row["witness_verified"] = m.get("verified")
        rows.append(row)
    json.dump(rows, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print(f"{'instance':34s} {'verdict':10s} {'vars':>6s} {'clauses':>7s} "
          f"{'DRAT verified':>13s} {'proof bytes':>12s}")
    for r in rows:
        print(f"{r['tag']:34s} {r['status']:11s} {r['vars']:6d} {r['clauses']:7d} "
              f"{str(r.get('drat_replayed', r.get('witness_verified', '-'))):>13s} "
              f"{str(r.get('drat_bytes', '-')):>12s}")


if __name__ == "__main__":
    main()
