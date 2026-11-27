#!/usr/bin/env python3
"""Read-only replay of joining3s preparation and any completed query receipts."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--prepared", type=Path, required=True)
    args = parser.parse_args()
    campaign, out = args.campaign.resolve(), args.prepared.resolve()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(campaign))
    from common import host, source
    from compile import append
    from problem import read_dimacs
    from representatives import full_query

    preparation = json.loads((out / "preparation.json").read_bytes())
    assert preparation["solver_calls"] == 0
    assert len(preparation["candidates"]) == preparation["candidate_pairs"]
    positive_checks = negative_checks = 0

    def check(query: Path, proof: Path, verified: bool, only_rup: bool) -> None:
        command = [str(campaign / "tools/drat-trim"), str(query), str(proof),
                   "-i", *(["-U"] if only_rup else []), "-t", "300"]
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        statuses = [line for line in run.stdout.splitlines() if line.startswith(b"s ")]
        expected = b"s VERIFIED" if verified else b"s NOT VERIFIED"
        assert statuses == [expected], (query, run.returncode, statuses, run.stdout[-500:])
        if verified:
            assert run.returncode == 0
        else:
            assert run.returncode != 0
        assert b"-w" not in command

    for candidate in preparation["candidates"]:
        rid, w, z = candidate["row_id"], candidate["w"], candidate["z"]
        parent, representative, cube = full_query(rid, w, z, "round50")
        assert sha(parent) == candidate["parent_sha256"]
        assert sha(representative) == candidate["representative_sha256"]
        assert (out / candidate["representative_file"]).read_bytes() == representative
        child_path = out / candidate["child_file"]
        child = append(representative, [[candidate["surviving_physical_literal"]]])[1]
        assert child_path.read_bytes() == child and sha(child) == candidate["child_sha256"]
        _, arm, _, outside = source(rid)
        edge, _ = host(58)
        all_four = sorted(edge(outside[0], outside[1], c) for c in range(4))
        assert all_four == candidate["all_four_physical_literals"]
        _, clauses = read_dimacs(representative)
        clause_set = {tuple(clause) for clause in clauses}
        assert tuple(all_four) in clause_set
        assert all((-a, -b) in clause_set for i, a in enumerate(all_four) for b in all_four[i + 1:])
        refuted = set()
        for branch in candidate["other_branches"]:
            query = out / branch["query_file"]
            proof = out / branch["proof_file"]
            expected_query = append(representative, [[branch["physical_literal"]]])[1]
            assert query.read_bytes() == expected_query
            assert sha(expected_query) == branch["query_sha256"]
            assert sha(proof.read_bytes()) == branch["proof_sha256"]
            check(query, proof, True, True)
            positive_checks += 1
            refuted.add(branch["physical_literal"])
        assert refuted | {candidate["surviving_physical_literal"]} == set(all_four)
        assert not refuted & {candidate["surviving_physical_literal"]}
        transported = next(branch for branch in candidate["other_branches"]
                           if branch["kind"] == "transported_arm_exclusion")
        check(out / transported["query_file"],
              out / f"splits/{candidate['pair_id']}/empty-proof-control.rup", False, True)
        negative_checks += 1

    result = {"prepared_representatives": len(preparation["candidates"]),
              "strict_complementary_proof_replays": positive_checks,
              "negative_controls_rejected": negative_checks,
              "fresh_query_replays": 0, "fresh_control_replays": 0,
              "closed_representatives_rechecked": 0}
    summary_path = out / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_bytes())
        expected_total = (2 * len(preparation["candidates"])
                          + preparation.get("positive_control_calls", 0))
        assert summary["scheduled_records"] == expected_total
        assert summary["records"] == len(summary["receipts"]) <= expected_total
        assert summary["cohort_complete"] == (summary["records"] == expected_total
            and not summary["aborted_after_control_failure"]
            and not any(r["status"].startswith("INFRASTRUCTURE") for r in summary["receipts"]))
        assert summary["whole_original_rows_closed"] == 0
        candidates = {c["pair_id"]: c for c in preparation["candidates"]}
        receipts = {r["run_index"]: r for r in summary["receipts"]}
        with (out / "design/execution-plan.tsv").open(newline="") as stream:
            frozen = {r["run_index"]: r for r in csv.DictReader(stream, delimiter="\t")}
        # Controls are not part of the candidate denominator, but their fresh
        # exact-query proofs must independently replay before accepting the run.
        for receipt in summary["receipts"]:
            expected_hash = frozen[receipt["run_index"]].get(
                "expected_sha256", frozen[receipt["run_index"]].get("query_sha256"))
            assert receipt["query_sha256"] == expected_hash
            if receipt.get("role") != "positive_control":
                continue
            query_path = out / f"runs/{receipt['run_index']}/query.cnf"
            assert sha(query_path.read_bytes()) == expected_hash
            assert receipt["status"] == "VERIFIED_UNSAT"
            proof_path = out / f"runs/{receipt['run_index']}/proof.drat"
            proof = proof_path.read_bytes()
            assert sha(proof) == receipt["proof_sha256"]
            assert len(proof) == receipt["proof_bytes"] and receipt["checker_verified"]
            check(query_path, proof_path, True, False)
            positive_checks += 1
            result["fresh_query_replays"] += 1
            result["fresh_control_replays"] += 1
        for closure in summary["closures"]:
            candidate = candidates[closure["pair_id"]]
            for key in ("parent_receipt", "child_receipt"):
                receipt = receipts[closure[key]]
                kind = "parent" if key == "parent_receipt" else "child"
                assert receipt["query_kind"] == kind
                expected_path = out / (candidate["representative_file"] if kind == "parent"
                                       else candidate["child_file"])
                expected = expected_path.read_bytes()
                assert sha(expected) == receipt["query_sha256"]
                query_path = out / f"runs/{receipt['run_index']}/query.cnf"
                if receipt["status"].startswith("INFRASTRUCTURE"):
                    continue
                assert query_path.read_bytes() == expected
                if receipt["status"] == "OPEN":
                    assert not receipt["checker_verified"] and receipt["proof_bytes"] == 0
                    continue
                if receipt["status"] == "VERIFIED_SAT":
                    model = gzip.decompress((out / f"runs/{receipt['run_index']}/model.gz").read_bytes())
                    assignment = {int(v) for v in model.split()}
                    _, clauses = read_dimacs(expected)
                    assert all(any(lit in assignment for lit in clause) for clause in clauses)
                    continue
                if receipt["status"] == "UNVERIFIED_SOLVER_UNSAT":
                    assert not receipt["checker_verified"]
                    assert closure["method"] == "OPEN" or kind == "child"
                    continue
                if receipt["status"] != "VERIFIED_UNSAT":
                    raise AssertionError(receipt["status"])
                proof_path = out / f"runs/{receipt['run_index']}/proof.drat"
                proof = proof_path.read_bytes() if proof_path.exists() else gzip.decompress(
                    (out / f"runs/{receipt['run_index']}/proof.drat.gz").read_bytes())
                assert sha(proof) == receipt["proof_sha256"]
                assert len(proof) == receipt["proof_bytes"] and receipt["checker_verified"]
                check(query_path, proof_path, True, False)
                positive_checks += 1
                result["fresh_query_replays"] += 1
            direct = receipts[closure["parent_receipt"]]["status"] == "VERIFIED_UNSAT"
            split = receipts[closure["child_receipt"]]["status"] == "VERIFIED_UNSAT"
            expected_method = ("DIRECT_REPRESENTATIVE_DRAT" if direct else
                               "COMPLETE_JOINING_COLOR_SPLIT" if split else "OPEN")
            assert closure["method"] == expected_method
            assert closure["representative_status"] == ("OPEN" if expected_method == "OPEN" else "CLOSED")
            result["closed_representatives_rechecked"] += expected_method != "OPEN"
        assert summary["closed_representatives"] == result["closed_representatives_rechecked"]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
