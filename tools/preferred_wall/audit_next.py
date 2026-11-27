#!/usr/bin/env python3
"""Audit one completed preferred-cover batch without launching a SAT search."""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

CAP = 512


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--source", default="next-0-10000.tsv.gz")
    parser.add_argument("--probe", default="next-0-10000-cap512")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    out = args.out.resolve()
    if out.exists():
        parser.error("choose a new output path")
    sys.path.insert(0, str(campaign))
    from campaign_queue import batch
    from cheap import group_formula, key, per_row
    from common import OUT, canonical, physical, sha, tsv, wall
    from cover_proofs import rup
    from physical_order import sort_key
    from problem import check_model, read_dimacs
    from representatives import full_query, owner, preferred_extension

    expected = batch(0, 10000)
    source = tsv(OUT / args.source)
    records = tsv(OUT / (args.probe + ".tsv.gz"))
    if source != [{k: str(v) for k, v in row.items()} for row in expected]:
        raise ValueError("source batch does not reproduce campaign_queue.batch")
    if len(source) != 10000 or len(records) != 10000:
        raise ValueError("incomplete batch")
    by_rank = {(r["wave"], int(r["rank"])): r for r in records}
    if len(by_rank) != len(records):
        raise ValueError("duplicate probe rank")

    rows, _, _ = wall()
    formula, gates, row_lits = {}, {}, {}
    statuses, arms = collections.Counter(), collections.Counter()
    group_conflicts = actual_fallback_conflicts = 0
    proof_receipts = 0
    status_details = []
    for src in source:
        rid, w, z = src["row_id"], src["w"], src["z"]
        task = by_rank[src["wave"], int(src["rank"])]
        if (task["row_id"], task["w"], task["z"]) != (rid, w, z):
            raise ValueError("source/probe identity mismatch")
        if task["wave"] != src["wave"] or int(task["rank"]) != int(src["rank"]):
            raise ValueError("source/probe rank mismatch")
        row = rows[rid]
        k = key(row)
        if k not in formula:
            clauses, fixed, bypass = group_formula(row)
            formula[k] = clauses, fixed, bypass, max(abs(v) for c in clauses for v in c)
        clauses, fixed, bypass, top = formula[k]
        if rid not in row_lits:
            row_lits[rid] = per_row(row, fixed, bypass)
        group = (k, sort_key(rid))
        if task["group"] != sha(canonical(group)):
            raise ValueError("group formula identity mismatch")
        if group not in gates:
            gates[group] = preferred_extension(rid, top)[2]
        n = int(src["arm"])
        assumptions = row_lits[rid] + physical(rid, w, z) + owner(n, w, z, gates[group])
        if task["assumptions_sha256"] != sha(canonical(assumptions)):
            raise ValueError("physical/ownership assumption mismatch")
        if int(task["cap"]) != CAP:
            raise ValueError("unexpected conflict cap")
        conflicts = int(task["conflicts"])
        if conflicts < 0:
            raise ValueError("negative conflict count")
        group_conflicts += conflicts
        status = task["status"]
        statuses[status] += 1
        arms[(src["profile"], status)] += 1

        if status == "OPEN":
            if conflicts < CAP:
                raise ValueError("premature OPEN")
            continue
        if status not in ("PENDING_BASE", "UNSAT_PREFERRED_BASE", "VERIFIED_K58_MODEL"):
            raise ValueError(f"unexpected status {status}")
        parent, query, cube = full_query(rid, w, z, "preferred")
        stem = f"preferred-{rid}-{w}-{z}"
        if status == "VERIFIED_K58_MODEL":
            # A checked model is representative-class SAT, never whole-row UNSAT.
            modelpath = OUT / "native-models" / (stem + ".model.json.gz")
            modeldata = gzip.decompress(modelpath.read_bytes())
            modelreceipt = json.loads((OUT / "native-models" / (stem + ".json")).read_bytes())
            if (modelreceipt["query"] != sha(query) or modelreceipt["parent"] != sha(parent) or
                    modelreceipt["model_sha256"] != sha(modeldata)):
                raise ValueError("model receipt identity mismatch")
            nv, cls = read_dimacs(query)
            model = json.loads(modeldata)
            if type(model) is not list or len(model) != nv or {abs(v) for v in model} != set(range(1, nv + 1)):
                raise ValueError("incomplete full-parent model")
            check_model(cls, cube, model, nv)
            continue

        attempt_path = OUT / "raw-native-attempts" / (stem + ".json")
        attempt = json.loads(attempt_path.read_bytes())
        if attempt["query"] != sha(query) or int(attempt["fallback_cap"]) != CAP:
            raise ValueError("incorrect full-parent fallback identity")
        if attempt["full_solver_conflicts"] is not None:
            actual_fallback_conflicts += int(attempt["full_solver_conflicts"])
        if status == "PENDING_BASE":
            if attempt["status"] != "PENDING_BASE" or attempt["solver_returncode"] != 0:
                raise ValueError("pending fallback is not unresolved solver work")
            continue
        if attempt["status"] != "VERIFIED_UNSAT_BASE":
            raise ValueError("UNSAT status lacks a verified native receipt")
        compressed = (OUT / "raw-proofs" / (stem + ".drat.gz")).read_bytes()
        proof = gzip.decompress(compressed)
        if attempt["proof_sha256"] != sha(proof):
            raise ValueError("proof digest mismatch")
        with TemporaryDirectory(dir=OUT) as tmp:
            q, p = Path(tmp) / "query.cnf", Path(tmp) / "proof.drat"
            q.write_bytes(query)
            p.write_bytes(proof)
            if not rup(q, p):
                raise ValueError("strict original preferred-query refutation failed")
        proof_receipts += 1
        status_details.append({"row_id": rid, "w": w, "z": z, "query_sha256": sha(query),
                               "proof_sha256": sha(proof), "proof_bytes": len(proof),
                               "scope": "one preferred representative class; not a whole original row"})

    report = {
        "schema": "k58-preferred-next-batch-audit/v1",
        "verdict": "PASS",
        "records": len(records),
        "distinct_physical_identities": len({(r["row_id"], r["w"], r["z"]) for r in records}),
        "status_counts": dict(statuses),
        "status_by_profile": {f"{p}/{s}": n for (p, s), n in sorted(arms.items())},
        "group_conflicts_actual": group_conflicts,
        "full_parent_fallback_calls": statuses["PENDING_BASE"] + statuses["UNSAT_PREFERRED_BASE"],
        "full_parent_fallback_conflicts_actual": actual_fallback_conflicts,
        "strict_preferred_query_refutations": proof_receipts,
        "whole_original_rows_closed": 0,
        "cap_each_group_and_fallback_call": CAP,
        "scope_note": "OPEN/PENDING are unresolved. Refutations settle only exact representative classes, not complete original rows. Existing row-level cover remains OPEN.",
        "records_detail": status_details,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "records_detail"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
