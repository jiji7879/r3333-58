#!/usr/bin/env python3
"""Prepare and run one matched direct/depth-one probe with entailed rules.

The current target is the independently checked square/six fixture for row
4a71.... The 384-clause implication is replayed RUP-only before any solving.
The augmented DIMACS is a derived parent, never the original row formula.
Only wallcc's original-parent exporter could later license an original-row
closure; this module returns measured attempt evidence, not an original proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from case_queue import VerificationError, parse_dimacs, sha256
from split_policy import compare_pair

EXPECTED_ORIGINAL = "33b7898ed58bd1a3a2e088f57d4bc9d01b5397e7b72f1f5f1449a7bf16f4a02a"
EXPECTED_QUERY = "810f073981467885bca1604f9bdf46e7f00f3729736378663e4c4008af2317b7"
EXPECTED_PROOF = "bbfe14c5a30eaa7879718da67c83866700f2b486e8121accb8e06b62bfb543fa"


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def append(original: bytes, extra) -> bytes:
    header, body = original.split(b"\n", 1)
    fields = header.split()
    if fields[:2] != [b"p", b"cnf"]:
        raise ValueError("invalid original header")
    nv, nc = map(int, fields[2:4])
    rows = ((" ".join(map(str, clause)) + " " if clause else "") + "0\n" for clause in extra)
    return f"p cnf {nv} {nc + len(extra)}\n".encode() + body + "".join(rows).encode()


def load_fixture(square: Path):
    import gzip
    original = gzip.decompress((square / "evidence/parent.cnf.gz").read_bytes())
    study = json.loads((square / "evidence/study.json").read_text())
    if sha256(original) != EXPECTED_ORIGINAL or study["parent_sha256"] != EXPECTED_ORIGINAL:
        raise ValueError("unexpected original parent")
    additions = [tuple(map(int, row["goal"])) for row in study["cuts"]]
    if len(additions) != 384 or len(set(additions)) != 384:
        raise ValueError("expected 384 distinct strengthening clauses")
    nv, clauses = parse_dimacs(original)
    originals = set(clauses)
    if any(not clause or set(additions) & originals for clause in additions):
        raise ValueError("empty or already-present strengthening clause")
    for clause in additions:
        if any(abs(lit) > nv for lit in clause):
            raise ValueError("strengthening literal outside original variables")
    return original, study, additions


def checker_run(checker: Path, formula: Path, proof: Path, output: Path, rup_only=True):
    # Keep warnings enabled: -w can continue after an invalid binary prefix.
    command = [str(checker), str(formula), str(proof), "-i"]
    if rup_only:
        command.append("-U")
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = run.stdout.decode(errors="replace")
    result = {"command": command, "returncode": run.returncode,
              "verified": run.returncode == 0 and "s VERIFIED" in text.splitlines(),
              "checker_tail": text[-1200:]}
    output.write_text(text)
    return result


def prepare(square: Path, checker: Path, out: Path) -> dict:
    if out.exists():
        raise ValueError(f"refusing to overwrite existing probe directory: {out}")
    out.mkdir(parents=True)
    original, study, additions = load_fixture(square)
    nv, _ = parse_dimacs(original)
    original_path = out / "original-parent.cnf"
    strengthened_path = out / "strengthened-parent.cnf"
    original_path.write_bytes(original)
    strengthened = append(original, additions)
    strengthened_path.write_bytes(strengthened)
    if sha256(strengthened) != sha256(strengthened_path.read_bytes()):
        raise ValueError("strengthened-parent write/read mismatch")

    selectors = list(range(nv + 1, nv + len(additions) + 1))
    selector_clauses = [selectors] + [[-q, -v] for q, goal in zip(selectors, additions) for v in goal]
    header, body = original.split(b"\n", 1)
    query = f"p cnf {selectors[-1]} {len(parse_dimacs(original)[1]) + len(selector_clauses)}\n".encode() + body
    query += b"".join((" ".join(map(str, clause)) + " 0\n").encode() for clause in selector_clauses)
    query_path = out / "rule-implication-query.cnf"
    query_path.write_bytes(query)
    proof = (square / "evidence/implication.drat").read_bytes()
    proof_path = out / "rule-implication.drat"
    proof_path.write_bytes(proof)
    empty_path = out / "empty.drat"
    empty_path.write_bytes(b"")
    if sha256(query) != EXPECTED_QUERY or sha256(proof) != EXPECTED_PROOF:
        raise ValueError("rule implication hash differs from the audited fixture")
    positive = checker_run(checker, query_path, proof_path, out / "rule-verify.log")
    negative = checker_run(checker, query_path, empty_path, out / "rule-empty-control.log")
    if not positive["verified"] or negative["verified"]:
        raise VerificationError("entailed-parent implication or empty-proof control failed")
    receipt = {
        "scope": "RUP-only verification of all 384 rule consequences; not a parent refutation",
        "row_id": study["row"]["id"], "original_sha256": sha256(original),
        "strengthened_sha256": sha256(strengthened), "added_clauses": len(additions),
        "query_sha256": sha256(query), "proof_sha256": sha256(proof),
        "checker_sha256": sha256(checker.read_bytes()),
        "positive_verified": positive["verified"],
        "empty_proof_rejected": not negative["verified"],
        "original_root_status": "OPEN",
    }
    write_json(out / "rule-receipt.json", receipt)
    return receipt


def command_record(command, output: Path, result: subprocess.CompletedProcess, elapsed: float) -> dict:
    output.write_bytes(result.stdout)
    text = result.stdout.decode(errors="replace")
    try:
        parsed = json.loads(text.strip().splitlines()[-1])
    except Exception:
        parsed = {"unparsed_output_tail": text[-1600:]}
    return {"command": command, "returncode": result.returncode,
            "wall_seconds": elapsed, "result": parsed}


def run_wallcc(python: Path, wallcc: Path, checker: Path, parent: Path,
               out: Path, depth: int, seconds: int, conflicts: int) -> dict:
    if out.exists():
        raise ValueError(f"refusing to overwrite run directory: {out}")
    out.mkdir(parents=True)
    command = [str(python), str(wallcc), "run", "--cnf", str(parent), "--out", str(out),
               "--depth", str(depth), "--jobs", "1", "--seconds", str(seconds),
               "--conflicts", str(conflicts), "--proof", "eager", "--checker", str(checker)]
    started = time.monotonic()
    result = subprocess.run(command, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    record = {"run": command_record(command, out / "run-output.json", result,
                                    time.monotonic() - started)}
    if result.returncode != 0:
        raise RuntimeError(f"wallcc run failed: {(out / 'run-output.json').read_text(errors='replace')[-1800:]}")
    started = time.monotonic()
    command = [str(python), str(wallcc), "verify", str(out), "--jobs", "1", "--checker", str(checker)]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    record["verify"] = command_record(command, out / "verify-output.json", result,
                                      time.monotonic() - started)
    if result.returncode not in (0, 2):
        raise RuntimeError(f"wallcc verify failed: {(out / 'verify-output.json').read_text(errors='replace')[-1800:]}")
    record["plan"] = json.loads((out / "plan.json").read_text())
    receipts = []
    for node in (out / "leaves").iterdir():
        receipt_path = node / "receipt.json"
        if receipt_path.is_file():
            receipts.append(json.loads(receipt_path.read_text()))
    record["receipts"] = sorted(receipts, key=lambda r: r["node"])
    return record


def plan_hash(plan) -> str:
    raw = (json.dumps(plan, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return hashlib.sha256(raw).hexdigest()


def analyze_runs(direct: dict, split: dict, total_conflicts: int) -> dict:
    dp, sp = direct["plan"], split["plan"]
    if dp["parent_sha256"] != sp["parent_sha256"]:
        raise ValueError("direct/split parent hashes differ")
    if dp["depth"] != 0 or dp["leaf_count"] != 1 or dp["splits"]:
        raise ValueError("direct is not an unsplit depth-0 plan")
    if sp["depth"] != 1 or sp["leaf_count"] != 2 or set(sp["splits"]) != {"r"}:
        raise ValueError("split is not one exact depth-1 probe")
    variable = sp["splits"]["r"]
    direct_receipts = direct["receipts"]
    split_receipts = split["receipts"]
    if len(direct_receipts) != 1 or len(split_receipts) != 2:
        raise ValueError("missing direct/split receipts")
    for plan, receipts in ((dp, direct_receipts), (sp, split_receipts)):
        expected_hash = plan_hash(plan)
        for receipt in receipts:
            if receipt.get("plan_sha256") != expected_hash:
                raise ValueError("receipt belongs to another plan")
            conflicts = receipt.get("conflicts_used")
            cap = receipt["budget"]["conflicts"]
            if type(conflicts) is not int or conflicts < 0:
                raise ValueError("invalid conflicts_used")
            if receipt.get("status") == "OPEN" and conflicts < cap:
                raise ValueError("premature OPEN receipt")
    if direct_receipts[0]["cube"] or direct_receipts[0]["node"] != "r":
        raise ValueError("direct parent unexpectedly has a cube")
    split_cubes = {r["node"]: r["cube"] for r in split_receipts}
    if split_cubes != {"r0": [-variable], "r1": [variable]}:
        raise ValueError("split children are not complementary")
    for receipt in split_receipts:
        if receipt["budget"]["conflicts"] * 2 != total_conflicts:
            raise ValueError("child caps do not sum to the direct allocation")
    if direct_receipts[0]["budget"]["conflicts"] != total_conflicts:
        raise ValueError("direct cap differs from the declared total allocation")
    actual_direct = direct_receipts[0]["conflicts_used"]
    actual_split = sum(r["conflicts_used"] for r in split_receipts)
    direct_closed = direct["verify"]["result"].get("status") == "VERIFIED_UNSAT"
    split_closed = split["verify"]["result"].get("status") == "VERIFIED_UNSAT"
    comparison = compare_pair({
        "case_id": "4a71c66153af2a1cb64fc609b92bdd3dc93714fb3983a687812849a19f1798b2",
        "scope": f"strengthened-parent:{dp['parent_sha256']}",
        "budget_relation": "EQUAL_TOTAL_CONFLICT_ALLOCATION",
        "direct": {"closed": direct_closed, "conflicts": actual_direct,
                   "budget_conflicts": total_conflicts},
        "split": {"closed": split_closed, "conflicts": actual_split,
                  "budget_conflicts": total_conflicts},
    })
    return {
        "parent_sha256": dp["parent_sha256"],
        "direct": {
            "status": direct["verify"]["result"], "conflicts_used": actual_direct,
            "budget_conflicts": total_conflicts,
            "run_wall_seconds": direct["run"]["wall_seconds"],
            "verify_wall_seconds": direct["verify"]["wall_seconds"],
            "leaf_receipts": direct_receipts,
        },
        "split": {
            "status": split["verify"]["result"], "conflicts_used": actual_split,
            "budget_conflicts": total_conflicts,
            "split_variable": variable,
            "run_wall_seconds": split["run"]["wall_seconds"],
            "verify_wall_seconds": split["verify"]["wall_seconds"],
            "leaf_receipts": split_receipts,
        },
        "policy": comparison,
        "observed_wall_seconds": {
            "direct_run": direct["run"]["wall_seconds"],
            "direct_verify": direct["verify"]["wall_seconds"],
            "split_run": split["run"]["wall_seconds"],
            "split_verify": split["verify"]["wall_seconds"],
            "note": "Separate process timings; not used to override the conflict-policy outcome. Split run includes both sequential attempts.",
        },
        "original_row_closure": "NOT_EVALUATED: requires a complete original-parent DRAT replay",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--square", required=True, type=Path)
    parser.add_argument("--wallcc", required=True, type=Path)
    parser.add_argument("--checker", required=True, type=Path)
    parser.add_argument("--python", required=True, type=Path,
                        help="checked python-sat 1.9.dev22 interpreter")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--conflicts", type=int, default=60000)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if args.conflicts <= 0 or args.conflicts % 2 or args.seconds <= 0:
        parser.error("conflicts must be positive and even, seconds positive")
    checker = args.checker.resolve()
    wallcc = args.wallcc.resolve()
    out = args.out.resolve()
    rule = prepare(args.square.resolve(), checker, out)
    write_json(out / "command-identity.json", {
        "conflict_allocation_total": args.conflicts,
        "seconds_per_leaf_cap": args.seconds, "jobs": 1,
        "proof_mode": "eager", "cas": "off (external DIMACS)",
        "wallcc": str(wallcc), "python": str(args.python.resolve()),
        "checker": str(checker),
        "conflicts_are_total_not_per_tree": True,
        "wall_time_not_conflict_time": True,
    })
    if args.prepare_only:
        print(json.dumps(rule, indent=2, sort_keys=True))
        return
    parent = out / "strengthened-parent.cnf"
    direct = run_wallcc(args.python, wallcc, checker, parent, out / "direct", 0,
                        args.seconds, args.conflicts)
    if direct["plan"]["parent_sha256"] != rule["strengthened_sha256"]:
        raise ValueError("wallcc parent differs from the certified strengthened formula")
    split = run_wallcc(args.python, wallcc, checker, parent, out / "split", 1,
                       args.seconds, args.conflicts // 2)
    analysis = analyze_runs(direct, split, args.conflicts)
    analysis["rule_receipt"] = rule
    analysis["comparison_scope"] = "one selected strengthened parent; no cohort or wall-speedup claim"
    write_json(out / "matched-report.json", analysis)
    print(json.dumps({"out": str(out), "parent_sha256": analysis["parent_sha256"],
                      "direct": analysis["direct"]["status"],
                      "split": analysis["split"]["status"],
                      "policy": analysis["policy"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
