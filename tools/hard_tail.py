#!/usr/bin/env python3
"""Turn a zip of hard-case evidence into the small table a Lean binding needs.

A certificate archive is 1-7 MB per case: for 20,185 cases that is tens of GB,
and almost none of it is information.  What the Lean side actually needs is, per
case, the *encoding recipe* and the CNF hash, so that the Lean case list can be
tied to the exact formula a solver refuted.  The frozen ledger does not carry a
recipe (that is a known defect), so the certificates are the only place it lives.

This verifies every certificate against its regenerated CNF, then writes that
small table and nothing else.  The archive can be deleted afterwards; the
certificates remain reproducible from the recipe and the ledger row.

    python3 hard_tail.py --bundle K58 --source hard-evidence.zip \\
        --ids hard.txt --out tail-binding.jsonl.gz --workers 12
    python3 hard_tail.py ... --purge    # delete the extracted copy when done
"""
import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path

_W = {}


def _sha_file(p):
    h = sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _init(bundle, root, checker):
    sys.path.insert(0, bundle)
    import cover_evidence as ce
    _W.update(ce=ce, root=Path(root), checker=str(checker), rows=None)


def _one(args):
    cid, row = args
    ce, root, checker = _W["ce"], _W["root"], _W["checker"]
    case = root / cid[:2] / cid
    marker = case / "verified.json"
    if not marker.exists():
        return dict(id=cid, ok=False, error="no verified.json")
    ev = json.loads(marker.read_text())
    if ev.get("id") != cid:
        return dict(id=cid, ok=False, error="id mismatch in verified.json")
    try:
        chunks = ce.formula_chunks(row, ev["recipe"])
    except Exception as e:
        return dict(id=cid, ok=False, error=f"recipe failed: {e}")
    ident = ce.formula_id(chunks)
    if ident["sha256"] != ev["input"]["sha256"]:
        return dict(id=cid, ok=False,
                    error=f"regenerated CNF {ident['sha256'][:12]} != recorded "
                          f"{ev['input']['sha256'][:12]}")
    with tempfile.TemporaryDirectory() as td:
        cnf, proof = Path(td, "f.cnf"), Path(td, "p.drat")
        with open(cnf, "wb") as fh:
            for c in chunks:
                fh.write(c)
        with gzip.open(case / "certificate.drat.gz", "rb") as src, open(proof, "wb") as dst:
            shutil.copyfileobj(src, dst)
        if _sha_file(proof) != ev["drat"]["sha256"]:
            return dict(id=cid, ok=False, error="decompressed proof hash mismatch")
        r = subprocess.run([checker, str(cnf), str(proof)],
                           capture_output=True, text=True)
        if r.returncode != 0 or "s VERIFIED" not in r.stdout.splitlines():
            return dict(id=cid, ok=False, error="drat-trim rejected the certificate")
    return dict(id=cid, ok=True, recipe=ev["recipe"],
                cnf_sha256=ident["sha256"], cnf_bytes=ident["bytes"],
                proof_sha256=ev["drat"]["sha256"], proof_bytes=ev["drat"]["bytes"])


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bundle", required=True)
    p.add_argument("--source", required=True, help="zip or directory of evidence")
    p.add_argument("--ids", required=True)
    p.add_argument("--out", required=True, help="binding table to write (.jsonl.gz)")
    p.add_argument("--checker", required=True)
    p.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    p.add_argument("--purge", action="store_true", help="delete the extracted copy")
    a = p.parse_args()

    bundle = str(Path(a.bundle).resolve())
    ids = [l.strip() for l in Path(a.ids).read_text().splitlines() if l.strip()]
    print(f"{len(ids):,} ids", flush=True)

    tmp = None
    src = Path(a.source)
    if src.suffix == ".zip" or zipfile.is_zipfile(src):
        tmp = tempfile.mkdtemp(prefix="k58-tail-")
        print(f"extracting {src} ({src.stat().st_size/1e9:.1f} GB)", flush=True)
        with zipfile.ZipFile(src) as zf:
            zf.extractall(tmp)
        src = Path(tmp)
        # find the evidence root: the directory containing xx/<id>/verified.json
        for cand in [src] + [d for d in src.rglob("*") if d.is_dir()]:
            if any(cand.glob("[0-9a-f][0-9a-f]/*/verified.json")):
                src = cand
                break
    print(f"evidence root: {src}", flush=True)

    sys.path.insert(0, bundle)
    import cover_evidence as ce
    rows = {r["id"]: r for r in ce.records(Path(bundle) / "case-ledger.jsonl.gz")}
    work = [(i, rows[i]) for i in ids if i in rows]
    missing = [i for i in ids if i not in rows]
    print(f"{len(work):,} in the ledger, {len(missing)} not", flush=True)

    ok = bad = 0
    with ThreadPoolExecutor(max_workers=a.workers, initializer=_init,
                            initargs=(bundle, str(src), a.checker)) as pool, \
            gzip.open(a.out, "wt") as fh:
        for n, rec in enumerate(pool.map(_one, work, chunksize=8), 1):
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            if rec["ok"]:
                ok += 1
            else:
                bad += 1
                print(f"  {rec['id'][:12]} {rec['error']}", file=sys.stderr)
            if n % 1000 == 0:
                print(f"  {n:,}/{len(work):,}  ok={ok:,} bad={bad}", flush=True)

    print(json.dumps(dict(checked=len(work), verified=ok, failed=bad,
                          not_in_ledger=len(missing),
                          table=str(a.out),
                          table_bytes=Path(a.out).stat().st_size)))
    if tmp and a.purge:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"purged {tmp}")
    return 0 if bad == 0 and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
