#!/usr/bin/env python3
"""Find cases whose first-pass attempt returned UNSAT but which have no
published certificate (verified.json).

Such a case is closed by the solver but absent from any manifest: it would show
as OPEN in a release. Usually a few cases interrupted between writing the
receipt and writing the certificate; re-running the shard fixes them, because
the runner re-derives the certificate from the stored receipt.

    python3 find_unpublished.py --evidence evidence
"""
import json, os, sys
from pathlib import Path
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--evidence", required=True)
ev = Path(ap.parse_args().evidence)
unsat, no_marker = 0, []
for two in os.scandir(ev):
    if not two.is_dir() or len(two.name) != 2: continue
    for case in os.scandir(two.path):
        if not case.is_dir(): continue
        d = Path(case.path)
        receipts = list((d / "first").glob("*.jsonl"))
        if receipts and any(json.loads(r.read_text()).get("status") == "UNSAT" for r in receipts):
            if not (d / "verified.json").exists():
                no_marker.append(d.name)
print(f"UNSAT receipts without verified.json: {len(no_marker)}")
if no_marker:
    print("re-run the shard that owns them; the certificate is rebuilt from the receipt")
for c in no_marker[:10]: print("  ", c)
