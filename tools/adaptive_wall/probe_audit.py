#!/usr/bin/env python3
"""Offline identity, cube-geometry, and conflict-accounting audit for this probe.

This file never invokes a SAT solver or a proof checker. ``identity`` and
``write-cnf`` reconstruct formulas; ``run`` and ``compare`` only read run data.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WALLCC = REPO / "tools/selfcontained/wallcc"
K58 = Path(os.environ.get("K58_SQUARE_FIXTURE", REPO / ".ultramath/smwy2754s/m4/extracted/K58_square_six"))
ROW = "4a71c66153af2a1cb64fc609b92bdd3dc93714fb3983a687812849a19f1798b2"
ORIGINAL_SHA = "33b7898ed58bd1a3a2e088f57d4bc9d01b5397e7b72f1f5f1449a7bf16f4a02a"
STRENGTHENED_SHA = "17cd9b8bf8ee597782feb426145f7f926a076171e818635a270b4d662e0afe0b"
QUERY_SHA = "810f073981467885bca1604f9bdf46e7f00f3729736378663e4c4008af2317b7"
PROOF_SHA = "bbfe14c5a30eaa7879718da67c83866700f2b486e8121accb8e06b62bfb543fa"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
SOLVER = "CaDiCaL 1.9.5 / python-sat 1.9.dev22"
FINAL_STATUSES = {"OPEN", "PROOF_PENDING", "CHECK_FAILED", "CHECKED_SAT", "CHECKED_UNSAT"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_materials():
    """Return independently checked identity data and the exact 384-goal CNF."""
    sys.path.insert(0, str(WALLCC))
    import problem  # wallcc's frozen encoder; importing it does not solve.
    from gluing import host, units
    sys.path.insert(0, str(K58))
    from build import append

    row = problem.lookup(ROW)
    frozen = gzip.decompress((K58 / "evidence/parent.cnf.gz").read_bytes())
    regenerated = problem.row_formula(row, "first")
    require(regenerated == frozen, "regenerated first-tier row differs from frozen parent")
    require(digest(frozen) == ORIGINAL_SHA, "wrong original-parent hash")
    require(row["branch"] == 44 and row["family"]["profile"] == [16, 16, 14, 11],
            "wrong row branch/profile")
    require(row["family"]["root_kinds"] == ["T", "U", "-", "-"], "wrong root templates")
    require(row["charge"] == 7 and problem.identity(row) == ROW, "wrong row identity/charge")

    nv, clauses = problem.read_dimacs(frozen)
    family, pin_literals = problem.family_and_pins(row)
    pin_clauses = units(family, row["placement"])
    _, host_clauses = host(58)
    require(pin_literals == [clause[0] for clause in pin_clauses], "pin interface mismatch")
    require(clauses[:len(host_clauses)] == host_clauses, "host is not the exact initial block")
    start = len(host_clauses)
    require(clauses[start:start + len(pin_clauses)] == pin_clauses,
            "signed pins are not the exact block after the host")
    require(len(pin_clauses) == 434, "unexpected pin count")

    study = json.loads((K58 / "evidence/study.json").read_text())
    goals = [record["goal"] for record in study["cuts"]]
    require(study["row"]["id"] == ROW and study["parent_sha256"] == ORIGINAL_SHA,
            "study is bound to a different row/parent")
    require(len(goals) == 384 and len({tuple(goal) for goal in goals}) == 384,
            "goals are not 384 distinct clauses")
    require(not any(goal in clauses for goal in goals), "a goal was already an input clause")
    strengthened = append(frozen, goals)
    snv, strengthened_clauses = problem.read_dimacs(strengthened)
    require(snv == nv and strengthened_clauses[:-384] == clauses
            and strengthened_clauses[-384:] == goals, "strengthened prefix/suffix mismatch")
    require(digest(strengthened) == STRENGTHENED_SHA, "wrong strengthened-parent hash")

    proof = (K58 / "evidence/implication.drat").read_bytes()
    require(digest(proof) == PROOF_SHA, "implication proof hash mismatch")
    hashes = json.loads((K58 / "evidence/hashes.json").read_text())
    require(hashes == {"query_sha256": QUERY_SHA, "proof_sha256": PROOF_SHA},
            "recorded implication hashes differ")

    report = {
        "row": ROW, "branch": row["branch"], "profile": row["family"]["profile"],
        "root_kinds": row["family"]["root_kinds"], "arm": row["family"]["arm"],
        "marked_size": row["family"]["marked_size"],
        "marked_kind": row["family"]["marked_kind"], "charge": row["charge"],
        "placement": row["placement"], "row_identity_recomputed": True,
        "regenerated_first_tier_equals_frozen": True,
        "original": {
            "sha256": digest(frozen), "bytes": len(frozen), "variables": nv,
            "clauses": len(clauses), "header": frozen.split(b"\n", 1)[0].decode(),
        },
        "host": {"clauses": len(host_clauses), "exact_initial_block": True},
        "pins": {
            "unit_clauses": len(pin_clauses), "exact_block_after_host": True,
            "positive": sum(clause[0] > 0 for clause in pin_clauses),
            "negative": sum(clause[0] < 0 for clause in pin_clauses),
        },
        "post_pin_clauses": len(clauses) - len(host_clauses) - len(pin_clauses),
        "strengthened_384": {
            "sha256": digest(strengthened), "bytes": len(strengthened),
            "variables": snv, "clauses": len(strengthened_clauses),
            "header": strengthened.split(b"\n", 1)[0].decode(),
            "original_clause_sequence_is_exact_prefix": True, "new_unique_goals": 384,
        },
        "implication_artifact_hashes_only": hashes,
        "scope": "Identity only: implication proof replay is separate; parent remains OPEN.",
    }
    return report, strengthened


def expected_leaves(plan):
    """Apply depth-0/exact-depth-1 geometry without invoking cubing.py."""
    depth = plan.get("depth")
    splits = plan.get("splits")
    require(type(depth) is int and depth in (0, 1), "audit expects depth 0 or exact depth 1")
    require(type(splits) is dict, "missing split dictionary")
    require(plan["split_limit"] == plan["variables"],
            "external-CNF split limit must include all declared variables")
    if depth == 0:
        require(splits == {}, "depth-0 plan has splits")
        return [("r", [])], None
    require(set(splits) == {"r"}, "depth-1 comparison requires exactly one root split")
    variable = splits["r"]
    require(type(variable) is int and 1 <= variable <= plan["split_limit"],
            "invalid recorded root cube variable")
    # cubing.cover visits r0 before r1. Check signed cubes, not just cube lengths.
    return [("r0", [-variable]), ("r1", [variable])], variable


def inspect_run(run, expected_parent=STRENGTHENED_SHA, expected_depth=None,
                expected_cap=None, expected_source=STRENGTHENED_SHA,
                require_eager=True):
    """Read one run's plan/receipts; return allocation and actual work.

    Actual conflicts are null when a hard wall timeout discarded worker stats.
    No actual<=cap inequality is imposed: CaDiCaL statistics can overshoot it.
    """
    run = Path(run)
    plan = json.loads((run / "plan.json").read_text())
    parent = (run / "parent.cnf").read_bytes()
    require(plan["schema"] == 1, "unknown wallcc plan schema")
    require(digest(parent) == plan["parent_sha256"] == expected_parent,
            "changed or unexpected strengthened parent")
    require(plan["origin"]["kind"] == "dimacs", "probe must use --cnf, not --row")
    if expected_source is not None:
        require(plan["origin"].get("source_sha256") == expected_source,
                "input source hash differs; use the same raw CNF for both arms")
    if expected_depth is not None:
        require(plan["depth"] == expected_depth, "wrong run depth")
    require(plan["lookahead"] == 12, "probe requires the recorded lookahead setting 12")
    require(plan["cas"] == "off" and plan["cuts"] == 0 and plan["tables"] == 0,
            "external probe unexpectedly added CAS clauses/tables")
    require((run / "working.cnf").read_bytes() == parent
            and plan["working_sha256"] == digest(parent), "working CNF differs from parent")
    require((run / "cas.drat").read_bytes() == b""
            and plan["cas_proof_sha256"] == EMPTY_SHA, "external CAS prefix is nonempty")
    leaves, split_variable = expected_leaves(plan)
    require(plan["leaf_count"] == len(leaves), "wrong leaf count")
    plan_id = digest(json_bytes(plan))
    records, unknown = [], []
    for node, cube in leaves:
        receipt_path = run / "leaves" / node / "receipt.json"
        require(receipt_path.is_file(), f"missing receipt for {node}; allocated work is not optional")
        receipt = json.loads(receipt_path.read_text())
        require(receipt["plan_sha256"] == plan_id and receipt["node"] == node
                and receipt["cube"] == cube, f"receipt binding/cube mismatch at {node}")
        require(receipt["status"] in FINAL_STATUSES, f"nonfinal/invalid status at {node}")
        require(receipt["solver"] == SOLVER, "unexpected solver identity")
        budget = receipt["budget"]
        if expected_cap is not None:
            require(budget["conflicts"] == expected_cap, f"wrong conflict allocation at {node}")
        if require_eager:
            require(budget["proof"] == "eager" and "search_conflicts" not in receipt,
                    "use one eager proof-producing pass, not deferred search+trace")
        components = {}
        actual = 0
        for key in ("search_conflicts", "conflicts_used"):
            if key in receipt:
                value = receipt[key]
                require(type(value) is int and value >= 0, f"invalid {key} at {node}")
                components[key] = value
                actual += value
        if "conflicts_used" not in receipt:
            actual = None
            unknown.append(node)
        records.append({
            "node": node, "cube": cube, "status": receipt["status"],
            "reason": receipt.get("reason"), "allocated_conflicts": budget["conflicts"],
            "conflict_components": components, "actual_conflicts": actual,
            "budget": budget, "checker_sha256": receipt.get("checker_sha256"),
            "artifact_sha256": receipt.get("artifact_sha256"),
            "elapsed_s_including_leaf_check": receipt.get("elapsed_s"),
        })
    return {
        "run": str(run), "parent_sha256": plan["parent_sha256"],
        "source_sha256": plan["origin"].get("source_sha256"), "depth": plan["depth"],
        "split_variable": split_variable, "split_limit": plan["split_limit"],
        "leaf_count": len(leaves), "leaves": records,
        "status_counts": dict(Counter(record["status"] for record in records)),
        "allocated_conflicts_total": sum(r["allocated_conflicts"] for r in records),
        "actual_conflicts_total": None if unknown else sum(r["actual_conflicts"] for r in records),
        "unknown_actual_conflict_nodes": unknown,
        "accounting_note": "Caps are allocated, not actual work; actual may exceed cap. No UNSAT closure claim is made.",
    }


def compare_runs(direct, split, expected_parent=STRENGTHENED_SHA,
                 expected_source=STRENGTHENED_SHA, require_eager=True):
    lhs = inspect_run(direct, expected_parent, 0, 60000, expected_source, require_eager)
    rhs = inspect_run(split, expected_parent, 1, 30000, expected_source, require_eager)
    require(lhs["parent_sha256"] == rhs["parent_sha256"]
            and lhs["source_sha256"] == rhs["source_sha256"], "arms use different formulas")
    require(lhs["allocated_conflicts_total"] == rhs["allocated_conflicts_total"] == 60000,
            "total allocated conflict budgets differ")
    direct_budgets = [{k: v for k, v in leaf["budget"].items() if k != "conflicts"}
                      for leaf in lhs["leaves"]]
    split_budgets = [{k: v for k, v in leaf["budget"].items() if k != "conflicts"}
                     for leaf in rhs["leaves"]]
    require(all(budget == direct_budgets[0] for budget in direct_budgets + split_budgets),
            "seconds/proof/check-seconds settings differ across leaves")
    return {
        "direct": lhs, "split": rhs, "matched_parent_and_source": True,
        "matched_total_allocated_conflicts": 60000,
        "actual_conflicts": {
            "direct": lhs["actual_conflicts_total"], "split": rhs["actual_conflicts_total"],
            "complete": not lhs["unknown_actual_conflict_nodes"] and not rhs["unknown_actual_conflict_nodes"],
        },
        "scope": "Matched single-case accounting only; no speedup, root/export, or original-parent closure conclusion.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("identity", help="reconstruct and print checked row/formula identity")
    write = commands.add_parser("write-cnf", help="write exact original+384 direct goals CNF")
    write.add_argument("output", type=Path)
    run = commands.add_parser("run", help="audit one run's plan and receipts")
    run.add_argument("run", type=Path)
    compare = commands.add_parser("compare", help="compare 60000 direct vs 2x30000 split")
    compare.add_argument("direct", type=Path)
    compare.add_argument("split", type=Path)
    args = parser.parse_args()
    if args.command in ("identity", "write-cnf"):
        report, strengthened = load_materials()
        if args.command == "write-cnf":
            with args.output.open("xb") as stream:  # preserve every existing input/receipt
                stream.write(strengthened)
            report = {"output": str(args.output), **report["strengthened_384"]}
    elif args.command == "run":
        plan = json.loads((args.run / "plan.json").read_text())
        cap = 60000 if plan["depth"] == 0 else 30000
        report = inspect_run(args.run, expected_cap=cap)
    else:
        report = compare_runs(args.direct, args.split)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit(f"probe audit: {error}")
