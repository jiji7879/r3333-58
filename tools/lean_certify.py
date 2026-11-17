#!/usr/bin/env python3
"""Produce kernel-checkable certificates one case at a time, then discard the rest.

Per case: regenerate the CNF from the frozen ledger row, solve with the pinned
Kissat, convert the DRAT proof to **binary LRAT** with `drat-trim -L -C`,
compress it, optionally replay it with a verified checker, and delete the CNF,
the DRAT and the uncompressed LRAT.  What survives is one compressed binary LRAT
per case plus a JSON record binding it to the CNF hash and the recipe.

This is the pipeline chosen for end-to-end checking: `cake_lpr` (or any LRAT
checker) consumes the binary LRAT, so the SAT side no longer needs a second
permanent proof archive; the DRAT certificates stay as they are and are not
duplicated.

    python3 lean_certify.py --bundle K58 --ids ids.txt --out certs --work tmp
    python3 lean_certify.py --bundle K58 --ids ids.txt --out certs --lpr-check /path/to/cake_lpr
"""
import argparse
import hashlib
import json
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
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode not in ok:
        raise RuntimeError(f"{' '.join(map(str, cmd))}\n{r.stdout[-600:]}\n{r.stderr[-600:]}")
    return r


def certify(case_id, bundle, work, out, checker, kissat, binary, lpr_check):
    cnf, drat, lrat = (work / f"{case_id}{s}" for s in (".cnf", ".drat", ".lrat"))
    run([sys.executable, bundle / "cover_evidence.py",
         "--ledger", bundle / "case-ledger.jsonl.gz",
         "--root", bundle, "export-input", case_id, cnf])
    run([kissat, "--quiet", cnf, drat], ok=(20,))
    cmd = [checker, cnf, drat, "-L", lrat] + (["-C"] if binary else [])
    r = run(cmd)
    if "s VERIFIED" not in r.stdout:
        raise RuntimeError(f"{case_id}: DRAT did not verify")
    packed = out / f"{case_id}.{'lpr' if binary else 'lrat'}.xz"
    with open(packed, "wb") as fh:
        subprocess.run(["xz", "-9e", "-q", "-c", str(lrat)], stdout=fh, check=True)
    record = dict(id=case_id, format="binary-lrat" if binary else "text-lrat",
                  cnf_sha256=sha256(cnf), lrat_sha256=sha256(packed),
                  cnf_bytes=cnf.stat().st_size, drat_bytes=drat.stat().st_size,
                  lrat_bytes=lrat.stat().st_size, lrat_xz_bytes=packed.stat().st_size)
    if lpr_check:
        r = run([lpr_check, str(cnf), str(lrat)])
        out_text = (r.stdout + r.stderr).lower()
        record["lpr_accepted"] = ("verified" in out_text or "s VERIFIED" in r.stdout
                                  or "accept" in out_text)
        if not record["lpr_accepted"]:
            raise RuntimeError(f"{case_id}: LRAT checker rejected the certificate\n"
                               f"{r.stdout[-500:]}\n{r.stderr[-500:]}")
    for f in (cnf, drat, lrat):
        f.unlink(missing_ok=True)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bundle", required=True, help="unpacked K58 bundle")
    p.add_argument("--ids", required=True, help="file with one case id per line")
    p.add_argument("--out", required=True, help="directory for the compressed LRAT")
    p.add_argument("--work", default="work/certify", help="scratch (purged per case)")
    p.add_argument("--kissat", default=None)
    p.add_argument("--checker", default=None, help="drat-trim")
    p.add_argument("--lpr-check", default=None, help="cake_lpr or similar, optional")
    p.add_argument("--text", action="store_true", help="text LRAT instead of binary")
    p.add_argument("--resume", action="store_true", help="skip cases already recorded")
    a = p.parse_args()
    bundle = Path(a.bundle).resolve()
    out, work = Path(a.out).resolve(), Path(a.work).resolve()
    out.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    kissat = a.kissat or str(bundle.parent / "tools/kissat/build/kissat")
    checker = a.checker or str(bundle.parent / "tools/drat-trim/drat-trim")
    ids = [l.strip() for l in Path(a.ids).read_text().splitlines() if l.strip()]
    done = set()
    rec_path = out / "records.jsonl"
    if a.resume and rec_path.exists():
        done = {json.loads(l)["id"] for l in rec_path.read_text().splitlines() if l.strip()}
    for cid in ids:
        if cid in done:
            print(json.dumps(dict(id=cid, skipped=True)))
            continue
        rec = certify(cid, bundle, work, out, checker, kissat, not a.text, a.lpr_check)
        with rec_path.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(json.dumps(rec))
    recs = [json.loads(l) for l in rec_path.read_text().splitlines() if l.strip()]
    tot = sum(r["lrat_xz_bytes"] for r in recs)
    dr = sum(r["drat_bytes"] for r in recs)
    print(f"{len(recs)} cases: LRAT-xz {tot/1e6:.2f} MB total, "
          f"{tot/max(1,len(recs))/1e6:.2f} MB/case, ratio to raw DRAT {tot/dr:.3f}")


if __name__ == "__main__":
    main()
