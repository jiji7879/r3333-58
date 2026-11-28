#!/usr/bin/env python3
"""Build the compact receipt from the independently regenerated check files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text())


def sha(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main():
    prefix = load("checks/prefix-identity.json")
    rup = load("checks/independent-rup.json")
    reaudit = load("checks/run-reaudit.json")
    receipts = load("run/kissat-frontier/receipts.json")
    controls = load("checks/controls/summary.json")
    derivation = load("checks/derivation-replay.json")
    leaves = [{
        "index": x["index"], "cube": x["cube"], "status": x["status"],
        "query_original_parent_plus_cube_sha256": x["query_sha256"],
        "query_working_plus_cube_sha256": x["working_query_sha256"],
        "discarded_unfinished_proof_sha256": x["discarded_noncertificate_proof_sha256"],
        "discarded_unfinished_proof_bytes": x["discarded_noncertificate_proof_bytes"],
        "solver_conflicts": x["solver_conflicts_last"],
        "elapsed_s": x["elapsed_s"], "cpu_s": x["cpu_s"],
        "solver_status_lines": x["solver_status_lines"],
    } for x in receipts]
    summary = {
        "schema": "k58-independent-certificate-audit/v1",
        "row": "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06",
        "profile": [16, 16, 14, 11], "charge": 7,
        "identity": {
            "parent_sha256": prefix["parent_sha256"],
            "working_sha256": prefix["working_sha256"],
            "cas_sha256": prefix["cas_sha256"],
            "frontier_sha256": reaudit["frontier_sha256"],
            "solver_kissat_4_0_4_sha256": sha("bin/kissat-massive"),
            "checker_primary_sha256": sha("bin/drat-trim-own"),
            "checker_second_sha256": sha("bin/drat-trim-massive"),
            "checker_primary_source_sha256": sha("bin/drat-trim.c"),
        },
        "certified_derivation": {
            "parent_working_logical_equivalence": True,
            "reason": "Every one of 5445 additions is independently RUP with deletions ignored; applying all additions/deletions to parent yields exactly the working clause multiset, which contains parent and has 315 additional distinct clauses.",
            "proof_bytes": prefix["proof_bytes"], "proof_records": prefix["proof_records"],
            "proof_additions": prefix["proof_additions"],
            "proof_deletions": prefix["proof_deletions"],
            "empty_additions": prefix["proof_empty_additions"],
            "active_formula_equals_working": prefix["final_active_multiset_equals_working"],
            "independent_rup_passed": rup["all_additions_rup"],
            "native_derivation_replays": len(derivation["results"]),
            "native_derivation_all_passed": derivation["passed"],
            "native_empty_clause_or_unsat_claim": False,
        },
        "exact_cover": reaudit["cover"],
        "fresh_kissat": {
            "engine": "Kissat 4.0.4 from dist/k58-massive-solver.zip", "seed": 0,
            "seconds_per_leaf": 120, "conflict_cap_per_leaf": 4000000,
            "total_solver_conflicts": reaudit["total_solver_conflicts"],
            "total_elapsed_s": reaudit["total_solver_elapsed_s"],
            "total_cpu_s": reaudit["total_solver_cpu_s"],
            "checked_unsat_leaves": 0, "open_leaves": 5, "leaves": leaves,
        },
        "acceptance_controls": {
            "valid_k6_two_checkers_pass": controls["positive_passes"],
            "wrong_query_and_truncation_rejected": controls["negative_controls_reject"],
            "truncation_printed_verified_but_whole_byte_gate_rejected": controls["truncation_false_verified_status_rejected"],
            "cas_alone_rejected_as_refutation": True,
        },
        "status": {
            "ordinary_cnf_parent": "OPEN", "exact_five_leaf_frontier": "all OPEN",
            "cnf_unsat_cover": False, "physical_colouring_row": "NOT PROVED",
            "semantic_assembly": "not attempted by this direction",
        },
        "structural_blocker": "The exact cover and RUP prefix are certificate-ready; the unresolved objects are five ordinary original-parent+cube refutations. No complete leaf proof was emitted.",
    }
    (ROOT / "results/summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("summary regenerated")


if __name__ == "__main__":
    main()
