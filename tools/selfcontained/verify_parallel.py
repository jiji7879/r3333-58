#!/usr/bin/env python3
"""Replay every retained certificate in parallel, against its regenerated CNF.

The bundle's `cover_evidence.py verify` does this on one core: correct, but at
~3 CPU-seconds per certificate it takes ~90 hours for the full cover.  This does
the same check with one worker per core.

For each `<evidence>/<xx>/<case>/verified.json` it rebuilds the CNF from the
frozen ledger row and the recipe recorded in the certificate, checks the rebuilt
bytes against the recorded input hash, decompresses the certificate, and replays
it with an independent checker.

    python3 verify_parallel.py --bundle K58 --evidence evidence --checker bin/drat-trim
    python3 verify_parallel.py ... --workers 12 --limit 100     # a sample
"""
import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path


def sha256_file(path):
    h = sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_one(case, row, ce, checker, tmpdir):
    marker = case / "verified.json"
    ev = json.loads(marker.read_text())
    if ev.get("id") != case.name:
        return (case.name, "FAIL id mismatch")
    chunks = ce.formula_chunks(row, ev["recipe"])
    ident = ce.formula_id(chunks)
    if ident["sha256"] != ev["input"]["sha256"]:
        return (case.name, "FAIL regenerated CNF differs from the recorded input")
    base = Path(tmpdir) / case.name
    cnf = base.with_suffix(".cnf")
    proof = base.with_suffix(".drat")
    with open(cnf, "wb") as fh:
        for chunk in chunks:
            fh.write(chunk)
    with gzip.open(case / "certificate.drat.gz", "rb") as src, open(proof, "wb") as dst:
        shutil.copyfileobj(src, dst)
    r = subprocess.run([checker, str(cnf), str(proof)],
                       capture_output=True, text=True)
    ok = r.returncode == 0 and "s VERIFIED" in r.stdout.splitlines()
    cnf.unlink(missing_ok=True)
    proof.unlink(missing_ok=True)
    return (case.name, "ok" if ok else "FAIL drat-trim rejected the certificate")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bundle", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--checker", required=True)
    p.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    p.add_argument("--limit", type=int)
    p.add_argument("--only", type=Path, metavar="PATH",
                   help="verify only the case ids listed in PATH, one per line")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()
    bundle = Path(a.bundle).resolve()
    sys.path.insert(0, str(bundle))
    import cover_evidence as ce

    ledger = {r["id"]: r for r in ce.records(bundle / "case-ledger.jsonl.gz")}
    markers = sorted(Path(a.evidence).glob("[0-9a-f][0-9a-f]/*/verified.json"))
    if a.only:
        wanted = {line.strip() for line in a.only.read_text().splitlines()
                  if line.strip() and not line.lstrip().startswith("#")}
        markers = [m for m in markers if m.parent.name in wanted]
        missing = wanted - {m.parent.name for m in markers}
        if missing:
            print(f"  {len(missing)} requested id(s) have no verified.json", file=sys.stderr)
    if a.limit:
        markers = markers[:a.limit]
    cases = [(m.parent, ledger.get(m.parent.name)) for m in markers]
    known = [(c, r) for c, r in cases if r is not None]
    unknown = [c.name for c, r in cases if r is None]
    print(f"{len(known)} certificates, {len(unknown)} without a ledger row, "
          f"{a.workers} workers", flush=True)

    ok = bad = 0
    failures = []
    with tempfile.TemporaryDirectory(prefix="k58-verify-") as td, \
            ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(check_one, c, r, ce, a.checker, td) for c, r in known]
        for i, fut in enumerate(futures, 1):
            cid, status = fut.result()
            if status == "ok":
                ok += 1
            else:
                bad += 1
                failures.append((cid, status))
                print(f"  {cid[:12]} {status}", file=sys.stderr)
            if not a.quiet and i % 500 == 0:
                print(f"  {i}/{len(known)} checked", flush=True)
    print(json.dumps(dict(checked=len(known), replayed=ok, failed=bad,
                          unknown=len(unknown))))
    return 0 if bad == 0 and not unknown else 1


if __name__ == "__main__":
    sys.exit(main())
