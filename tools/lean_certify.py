#!/usr/bin/env python3
"""Produce the only artifact a Lean-side check needs, then discard the rest.

For each case: regenerate the CNF from the frozen ledger row, solve with the
pinned Kissat, turn the DRAT proof into LRAT with the pinned drat-trim, compress
the LRAT, and delete the CNF, the DRAT and the uncompressed LRAT.  What remains
is one compressed LRAT per case plus a JSON record binding it to the CNF hash.

This is the "Lean end to end" pipeline: the LRAT is the checkable object, and
everything regenerable is thrown away.  It is *not* a space saving — LRAT is
several times the trimmed DRAT — so the numbers it prints are the honest price
of kernel-checkable evidence.

    python3 tools/lean_certify.py --bundle K58 --ids ids.txt --out certs --work tmp
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, ok=(0,)):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in ok:
        raise RuntimeError(f"{' '.join(map(str, cmd))}\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
    return r


def certify(case_id, bundle, work, out, checker, kissat):
    cnfs = work / f"{case_id}.cnf"
    drat = work / f"{case_id}.drat"
    lrat = work / f"{case_id}.lrat"
    run([sys.executable, str(bundle / "cover_evidence.py"),
         "--ledger", str(bundle / "case-ledger.jsonl.gz"), "--root", str(out),
         "export-input", case_id, str(cnfs)])
    run([kissat, "--quiet", str(cnfs), str(drat)], ok=(20,))
    r = run([checker, str(cnfs), str(drat), "-L", str(lrat)])
    if "s VERIFIED" not in r.stdout:
        raise RuntimeError(f"{case_id}: DRAT did not verify")
    packed = out / f"{case_id}.lrat.xz"
    with open(packed, "wb") as fh:
        subprocess.run(["xz", "-9e", "-q", "-c", str(lrat)], stdout=fh, check=True)
    record = dict(id=case_id, cnf_sha256=sha256(cnfs), lrat_sha256=sha256(packed),
                  cnf_bytes=cnfs.stat().st_size, drat_bytes=drat.stat().st_size,
                  lrat_bytes=lrat.stat().st_size, lrat_xz_bytes=packed.stat().st_size)
    for f in (cnfs, drat, lrat):
        f.unlink(missing_ok=True)
    return record


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", required=True)
    p.add_argument("--ids", required=True, help="file with one case id per line")
    p.add_argument("--out", required=True, help="directory for the compressed LRAT")
    p.add_argument("--work", default="work/certify")
    p.add_argument("--kissat", default=None)
    p.add_argument("--checker", default=None)
    args = p.parse_args()
    bundle = Path(args.bundle).resolve()
    out, work = Path(args.out).resolve(), Path(args.work).resolve()
    out.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    kissat = args.kissat or str(bundle.parent / "tools/kissat/build/kissat")
    checker = args.checker or str(bundle.parent / "tools/drat-trim/drat-trim")
    ids = [l.strip() for l in Path(args.ids).read_text().splitlines() if l.strip()]
    records = []
    for cid in ids:
        rec = certify(cid, bundle, work, out, checker, kissat)
        records.append(rec)
        print(json.dumps(rec))
    with (out / "records.jsonl").open("a") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    tot = sum(r["lrat_xz_bytes"] for r in records)
    dr = sum(r["drat_bytes"] for r in records)
    print(f"{len(records)} cases: LRAT-xz {tot/1e6:.1f} MB, raw DRAT {dr/1e6:.1f} MB, "
          f"ratio {tot/dr:.2f}")


if __name__ == "__main__":
    main()
