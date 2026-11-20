#!/usr/bin/env python3
"""Build the release manifest with one process per core.

`cover_evidence.py manifest` does this on a single thread: for each certified
case it regenerates the CNF from the ledger row and hashes the retained
artefacts.  Measured 0.224 s per case, so ~5 hours for 79,000 cases — and
`--workers` does not touch it, only the replay phase.

Half of that cost is GIL-bound Python (the CNF generator), so threads cap out
near 2x.  This uses processes, and writes the identical `cases.jsonl.gz` and
`manifest.json`: the output is byte-for-byte the serial builder's, so the
manifest hash matches.

    python3 manifest_parallel.py --bundle K58 --root evidence --out release --workers 12
"""
import argparse
import gzip
import json
import os
import sys
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

_WORK = {}


def _init(bundle, root):
    sys.path.insert(0, bundle)
    import cover_evidence as ce
    _WORK["ce"] = ce
    _WORK["root"] = Path(root)


def _one(row):
    ce, root = _WORK["ce"], _WORK["root"]
    evidence = ce.inspect_case(root, row, None)
    if evidence is None:
        evidence = {"status": "OPEN" if row["status"] == "OPEN"
                    else "LEGACY_EVIDENCE_NEEDED"}
    return dict(id=row["id"], branch=row["branch"],
                prior_status=row["status"], **evidence)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bundle", required=True, help="unpacked K58 bundle (the generators)")
    p.add_argument("--root", required=True, help="evidence root")
    p.add_argument("--out", required=True, help="release directory to create")
    p.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    p.add_argument("--batch", type=int, default=4000)
    a = p.parse_args()

    bundle = str(Path(a.bundle).resolve())
    root = str(Path(a.root).resolve())
    out = Path(a.out)
    sys.path.insert(0, bundle)
    import cover_evidence as ce

    out.mkdir(parents=True, exist_ok=False)
    rows = list(ce.audit_cover(Path(bundle) / "case-ledger.jsonl.gz"))
    print(f"{len(rows):,} cover rows, {a.workers} processes", flush=True)

    counts = Counter()
    written = 0
    index = out / "cases.jsonl.gz"
    with index.open("xb") as handle, \
            gzip.GzipFile(fileobj=handle, mode="wb", mtime=0, filename="",
                          compresslevel=5) as stream, \
            ProcessPoolExecutor(max_workers=a.workers, initializer=_init,
                                initargs=(bundle, root)) as pool:
        for start in range(0, len(rows), a.batch):
            chunk = rows[start:start + a.batch]
            for entry in pool.map(_one, chunk, chunksize=16):
                stream.write(ce.json_bytes(entry))
                ce.add_counts(counts, entry)
                written += 1
            print(f"  {written:,}/{len(rows):,}", flush=True)

    manifest = out / "manifest.json"
    ce.atomic_json(manifest, dict(**ce.inputs(Path(bundle) / "case-ledger.jsonl.gz"),
                                  cases=ce.artifact(out, index),
                                  counts=dict(counts)))
    print(json.dumps(dict(manifest_sha256=ce.digest(manifest),
                          counts=dict(counts)), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
