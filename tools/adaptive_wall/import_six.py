#!/usr/bin/env python3
"""Register and close the six supplied direct cases through CaseQueue.

This is a bounded import/replay integration check, not a wall-row search. The
caller supplies the already extracted results/proofs and a byte-identical
frozen encoder. Every original FIRST parent is regenerated and compared byte
for byte before its full proof is replayed by CaseQueue itself.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

from case_queue import CaseQueue, DratTrimVerifier, identity_matcher, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extracted", required=True, type=Path,
                        help="extracted K58_ranked_rows directory")
    parser.add_argument("--shared", required=True, type=Path,
                        help="checked K58_shared_learning encoder directory")
    parser.add_argument("--checker", required=True, type=Path)
    parser.add_argument("--queue", required=True, type=Path,
                        help="new SQLite path")
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--seconds", type=float, default=90)
    args = parser.parse_args()
    root = args.extracted.resolve()
    shared = args.shared.resolve()
    if args.queue.exists():
        parser.error("choose a new SQLite path")
    if args.out.exists():
        parser.error("choose a new summary path")
    args.queue.parent.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(shared))
    from problem import checked_case, row_formula  # type: ignore

    entries = json.loads((root / "results.json").read_text())
    if len(entries) != 6:
        raise ValueError(f"expected six direct cases, found {len(entries)}")

    def original_formula_validator(row, tier, data):
        regenerated = row_formula(row, tier)
        if regenerated != data:
            raise ValueError(f"frozen encoder parent differs for {row['id']} at {tier}")
        return {
            "validator": "K58_shared_learning.row_formula/byte-identical",
            "formula_sha256": sha256(data),
            "tier": tier,
        }

    verifier = DratTrimVerifier(args.checker, timeout_seconds=args.seconds)
    checker = {"name": "drat-trim", "sha256": sha256(args.checker.read_bytes())}
    queue = CaseQueue(args.queue, args.artifacts, verifier,
                      identity_matcher, "identity-v1")
    summaries = []
    try:
        for entry in entries:
            row = checked_case(entry["row"])
            if tuple(row["family"]["profile"]) != (15, 15, 15, 12):
                raise ValueError("unexpected profile in six-row package")
            parent_bytes = row_formula(row, "first")
            if sha256(parent_bytes) != entry["hashes"]["first.cnf"]:
                raise ValueError(f"published FIRST hash mismatch: {row['id']}")
            proof_bytes = gzip.decompress(
                (root / "proofs" / row["id"][:12] / "trim.drat.gz").read_bytes())
            if sha256(proof_bytes) != entry["hashes"]["trim.drat"]:
                raise ValueError(f"published proof hash mismatch: {row['id']}")
            case_id, parent_id = queue.register_k58_case(
                row, "first", parent_bytes, original_formula_validator)
            if queue.case_status(case_id) != "OPEN":
                raise ValueError("new original case is not OPEN before replay")
            queue.close_original(case_id, proof_bytes, checker)
            if queue.case_status(case_id) != "VERIFIED_UNSAT":
                raise ValueError(f"root replay did not close {row['id']}")
            summaries.append({
                "case_id": case_id,
                "root_parent_id": parent_id,
                "row_id": row["id"],
                "branch": entry["row"]["branch"],
                "status": queue.case_status(case_id),
                "original_first_sha256": sha256(parent_bytes),
                "proof_sha256": sha256(proof_bytes),
            })
        tasks = queue.open_tasks()
        if tasks:
            raise ValueError(f"direct import left unexpected open work: {tasks}")
        result = {
            "schema": "adaptive-wall-case-queue-six-import/v1",
            "scope": "six direct FIRST parents only; no cohort or wall closure",
            "validator": original_formula_validator.__name__,
            "verified_closed": len(summaries),
            "open_tasks_after_import": tasks,
            "queue": str(args.queue.resolve()),
            "cases": summaries,
        }
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"verified_closed": len(summaries),
                          "open_tasks_after_import": len(tasks),
                          "out": str(args.out)}, sort_keys=True))
    finally:
        queue.close()


if __name__ == "__main__":
    main()
