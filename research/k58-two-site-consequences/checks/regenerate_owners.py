#!/usr/bin/env python3
"""Rebuild all 47 owner formulas from the restored audited campaign source.

Usage: python3 -B checks/regenerate_owners.py AUDITED_K58 PACKAGE OUTPUT.json
No solver is called and nothing in either input tree is written.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

SOURCE, PACKAGE, OUTPUT = map(Path, sys.argv[1:])
SOURCE, PACKAGE = SOURCE.resolve(), PACKAGE.resolve()
sys.path.insert(0, str(SOURCE))
import revised


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


results = []
for i in range(47):
    transfer = json.loads((PACKAGE / f"transfer-{i:02d}.json").read_bytes())
    event = json.loads((PACKAGE / f"events/{i:07}.json").read_bytes())["event"]
    # JSON string-lists become Python lists; retained(n,g) stores word pairs as tuples.
    pair = tuple(transfer["pair"])
    raw, cube = revised.export(transfer["row"], pair)
    result = {
        "index": i,
        "row": transfer["row"],
        "pair": transfer["pair"],
        "parent": sha(raw),
        "owner_cube": cube,
        "parent_matches": sha(raw) == transfer["parent"] == event["parent"]["query"],
        "cube_matches": cube == event["guard"]["owner_cube"],
    }
    if not (result["parent_matches"] and result["cube_matches"]):
        raise RuntimeError(result)
    results.append(result)

report = {"regenerated": len(results), "parents_distinct": len({r["parent"] for r in results}),
          "all_parent_hashes_match": all(r["parent_matches"] for r in results),
          "all_owner_cubes_match": all(r["cube_matches"] for r in results),
          "solver_calls": 0, "records": results}
Path(OUTPUT).write_text(json.dumps(report, indent=1) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=1))
