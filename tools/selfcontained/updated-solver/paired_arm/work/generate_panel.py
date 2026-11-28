#!/usr/bin/env python3
"""Regenerate hash-bound hard-row parents and existing clause-family subsets.

All additions are selections of the already audited paired-arm rules.  The
only nontrivial selection policy is ``screened``: four-literal rules whose
false cube still propagates after the direct+ternary baseline.  No solver
status is used to generate a rule.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
HARD = HERE.parent / 'source'
sys.path.insert(0, str(HARD / "hard-study"))
sys.path.insert(0, str(HARD / "hard-more"))
import probe
from census import one
from wider import wider
from signed import signed
from pysat.solvers import Minisat22

POLICIES = ("stock", "ternary", "direct", "wide", "signed", "screened")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def augment(raw, additions):
    header, body = raw.split(b"\n", 1)
    p, cnf, nv, nc = header.split()
    assert (p, cnf) == (b"p", b"cnf")
    assert body.endswith(b"\n")
    extra = b"".join(" ".join(map(str, c)).encode() + b" 0\n" for c in additions)
    largest = max([int(nv.decode())] + [abs(lit) for c in additions for lit in c])
    return (f"p cnf {largest} {int(nc.decode()) + len(additions)}\n".encode()
            + body + extra)


def unique(clauses):
    return sorted({frozenset(c) for c in clauses}, key=lambda c: sorted(c))


def generate(rank, out):
    started = time.process_time()
    record = probe.rows[rank - 1]
    guards = {}
    raw, form, direct, extended = probe.build(record, guards)
    assert sha(raw) == record["input_sha256"]
    row = probe.geometry[record["id"]]
    ternary = one(row, guards)
    four = [[-guards[x][1], *lits] for x, *lits in wider(row)]
    sign = [[-guards[x][1], *lits] for x, *lits in signed(row)]
    direct = [list(c) for c in direct]
    prior = unique(direct + ternary)
    screened = []
    with Minisat22(bootstrap_with=form.clauses + prior) as solver:
        for clause in four:
            survives, _ = solver.propagate(assumptions=[-lit for lit in clause])
            if survives:
                screened.append(clause)
    additions = {
        "stock": [],
        "ternary": ternary,
        "direct": direct,
        # Match the prior wide policy: direct + ternary + all four-literal rules.
        "wide": unique(prior + four),
        # Match the prior signed policy: direct + ternary + all signed rules.
        "signed": unique(prior + sign),
        # Compact policy: prior + only four-literal rules not closed by UP.
        "screened": unique(prior + screened),
    }
    rowdir = out / str(rank)
    rowdir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "rank": rank,
        "id": record["id"],
        "profile": record["profile"],
        "kinds": record["kinds"],
        "charge": int(record["charge"]),
        "historical_proof_bytes": int(record["proof_bytes"]),
        "input_sha256": record["input_sha256"],
        "base_variables": form.nv,
        "base_clauses": len(form.clauses),
        "direct_raw": len(direct),
        "ternary_raw": len(ternary),
        "four_raw": len(four),
        "signed_raw": len(sign),
        "four_screened_survivors": len(screened),
        "generation_cpu_seconds_including_parent": time.process_time() - started,
        "files": {},
    }
    for policy in POLICIES:
        data = augment(raw, additions[policy])
        path = rowdir / f"{policy}.cnf"
        path.write_bytes(data)
        manifest["files"][policy] = {
            "path": str(path.relative_to(out)),
            "sha256": sha(data),
            "added_clauses": len(additions[policy]),
            "bytes": len(data),
        }
    (rowdir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True), flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", default="1300,1298,1288,1162")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists(), "refusing to overwrite an existing panel"
    args.out.mkdir(parents=True)
    records = [generate(int(rank), args.out) for rank in args.ranks.split(",")]
    (args.out / "panel.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
