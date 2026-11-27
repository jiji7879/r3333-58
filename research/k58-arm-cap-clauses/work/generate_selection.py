#!/usr/bin/env python3
"""Select short and genuinely additional paired-arm clauses, without long hits."""
import argparse
import json
from pathlib import Path
import sys
import time
import generate_panel as gp

POLICIES = ("short", "wide_delta", "four_only")


def generate(rank, out):
    start = time.process_time()
    record = gp.probe.rows[rank - 1]
    guards = {}
    raw, form, direct, extended = gp.probe.build(record, guards)
    assert gp.sha(raw) == record["input_sha256"]
    row = gp.probe.geometry[record["id"]]
    ternary = gp.one(row, guards)
    four = [[-guards[x][1], *lits] for x, *lits in gp.wider(row)]
    prior = {frozenset(c) for c in gp.unique([list(c) for c in direct] + ternary)}
    all_wide = gp.unique([list(c) for c in direct] + ternary + four)
    additions = {
        "short": [c for c in all_wide if len(c) <= 4],
        "wide_delta": [c for c in gp.unique(four) if frozenset(c) not in prior],
        "four_only": gp.unique(four),
    }
    rowdir = out / str(rank)
    rowdir.mkdir(parents=True, exist_ok=False)
    manifest = {"rank": rank, "id": record["id"], "input_sha256": record["input_sha256"],
                "base_clauses": len(form.clauses), "base_variables": form.nv,
                "generation_cpu_seconds_including_parent": time.process_time() - start,
                "files": {}}
    for policy in POLICIES:
        data = gp.augment(raw, additions[policy])
        path = rowdir / (policy + ".cnf")
        path.write_bytes(data)
        manifest["files"][policy] = {"path": str(path.relative_to(out)),
            "sha256": gp.sha(data), "added_clauses": len(additions[policy]),
            "bytes": len(data), "widths": {str(w): sum(len(c) == w for c in additions[policy])
                                           for w in sorted({len(c) for c in additions[policy]})}}
    (rowdir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True), flush=True)
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ranks", default="1300,1298,1288,1162")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    assert not a.out.exists()
    a.out.mkdir(parents=True)
    records = [generate(int(rank), a.out) for rank in a.ranks.split(",")]
    (a.out / "panel.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
