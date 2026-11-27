#!/usr/bin/env python3
"""Re-verify conditional refinements and emit exact queue-replacement ledgers.

No SAT search is run here. This program rebuilds and strictly checks each
proof obligation before recording a single-survivor replacement.
"""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()


def checker(binary, query, proof, timeout):
    command = [str(binary), str(query), str(proof), "-i", "-U", "-t", str(timeout)]
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout + 10)
    verified = run.returncode == 0 and run.stdout.count(b"s VERIFIED") == 1 and b"WARNING" not in run.stdout.upper()
    return {"returncode": run.returncode, "verified": verified, "output": run.stdout.decode(errors="replace"), "command": command}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--prototype", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    args.base = args.base.resolve()
    args.checker = args.checker.resolve()
    summary_path = args.summary.resolve()
    spec = importlib.util.spec_from_file_location("refinement_pilot", args.prototype.resolve())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary = json.loads(summary_path.read_text())
    prototype = module.Prototype(args.base, args.checker, out / "source", 0)
    from compile import append
    from representatives import preferred_extension
    from problem import row_formula

    def full_query_and_units(rule, include_target):
        pair = rule["parent"]["pair"]
        rid = rule["parent"]["rid"]
        n = rule["parent"]["n"]
        branch = rule["branch_color"]
        guard = [(tuple(e), c) for e,c in rule["guard"]]
        cube = (tuple(rule["third_edge"]), int(rule["target"])) if include_target else None
        units = prototype.get_units(rid, n, pair, branch, None, None,
                                   (*guard,) if cube is None else (*guard, cube))
        return append(prototype.full_base(rid, tuple(pair)), units)[1], units

    by_group = {}
    for test in summary["ternary_outcomes"]:
        by_group[test["n"], tuple(test["pair"]), test["rid"], test["branch_color"],
                 json.dumps(test["guard"], sort_keys=True)] = test
    entries = []
    all_steps = []
    for rule in summary["rules"]:
        key = (rule["parent"]["n"], tuple(rule["parent"]["pair"]), rule["parent"]["rid"],
               rule["branch_color"], json.dumps(rule["guard"], sort_keys=True))
        assert key in by_group, key
        rule = dict(rule, target=rule["forced_value"], third_edge=by_group[key]["third_edge"])
        cases = by_group[key]["tests"]
        n, pair, rid = key[0], key[1], key[2]
        prototype.current_n, prototype.current_pair, prototype.current_rid = n, pair, rid
        prototype.validate_stock(rid, n, pair)
        base = prototype.full_base(rid, pair)
        rec = prototype.rec(n, pair)
        assert sha(base) == rule["parent"]["representative"]
        assert rec["pivot"] and len(rec["branches"]) == 2
        guard_key = [list(x) for x in rule["guard"]]
        test_guard_key = [list(x) for x in by_group[key]["guard"]]
        assert guard_key == test_guard_key
        assert rule["target"] in [case["cube"][2][1] for case in by_group[key]["tests"]]
        target = rule["target"]
        raw_refined, target_units = full_query_and_units({"parent": rule["parent"],
            "guard": rule["guard"], "third_edge": rule["third_edge"], "target": target,
            "branch_color": rule["branch_color"]}, True)
        expected_refined = sha(raw_refined)
        assert expected_refined == rule["refined_query"], (expected_refined, rule["refined_query"])
        forbidden_checks = [c for c in cases if not c["sat"]]
        assert len(forbidden_checks) == 1
        sibling = [c for c in cases if c["sat"]]
        assert len(sibling) == 1
        parent_units = prototype.get_units(rid, n, pair, rule["branch_color"], None, None,
                                          extra_cube=[tuple(x) for x in rule["guard"]])
        raw_parent = append(base, parent_units)[1]
        parent_string = sha(raw_parent)
        node_dir = out / "nodes" / str(len(entries) + 1)
        node_dir.mkdir(parents=True, exist_ok=False)
        (node_dir / "parent.cnf").write_bytes(raw_parent)
        (node_dir / "refined.cnf").write_bytes(raw_refined)
        replacements = []
        for case in forbidden_checks:
            cube = case["cube"]
            assert cube[2][0] == rule["third_edge"] and cube[2][1] != rule["target"]
            units = prototype.get_units(rid, n, pair, rule["branch_color"], None, None,
                                        [(tuple(e), c) for e, c in cube])
            raw = append(base, units)[1]
            full = case["check"]
            source_dir = summary_path.parent / Path(full["log"]).parent
            source_query = source_dir / "query.cnf"
            source_proof = source_dir / "proof.drat"
            assert source_query.is_file() and source_proof.is_file(), source_dir
            assert source_query.read_bytes() == raw
            assert sha(raw) == full["query"]
            proof = source_proof.read_bytes()
            assert sha(proof) == full["proof"] and len(proof) == full["bytes"]
            assert full["flags"] == ["-i", "-U", "-t", "300"] and full["verified"]
            replay_dir = out / "replays" / str(len(entries) + 1)
            replay_dir.mkdir(parents=True, exist_ok=False)
            query_file = replay_dir / "query.cnf"
            proof_file = replay_dir / "proof.drat"
            query_file.write_bytes(raw)
            proof_file.write_bytes(proof)
            result = checker(args.checker, query_file, proof_file, 300)
            (replay_dir / "check.log").write_text(result["output"])
            assert result["verified"], result
            replacements.append({"cube": cube, "query": sha(raw), "proof": sha(proof),
                                 "proof_bytes": len(proof), "excluded_literal": units[-1][0],
                                 "source_query": str(source_query),
                                 "source_proof": str(source_proof), "checker_result": result})
        assert len(replacements) == 1
        # The sibling-exclusion proof alone does not show a complete binary
        # cover.  Certify P |= (target OR excluded) by refuting P with both
        # alternatives negated.  The two-byte binary proof adds the empty
        # clause; strict replay accepts it only when unit propagation suffices.
        cover_units = [[-target_units[-1][0]], [-replacements[0]["excluded_literal"]]]
        raw_cover = append(raw_parent, cover_units)[1]
        cover_proof = b"a\0"
        (node_dir / "cover.cnf").write_bytes(raw_cover)
        (node_dir / "cover.drat").write_bytes(cover_proof)
        cover_result = checker(args.checker, node_dir / "cover.cnf", node_dir / "cover.drat", 300)
        (node_dir / "cover-check.log").write_text(cover_result["output"])
        assert cover_result["verified"], cover_result
        entry = dict(rule)
        entry.update({
            "source_parent": parent_string,
            "refined_query_verified": expected_refined,
            "implication": "The only excluded alternative of the two-valued pivot is UNSAT on the exact full physical query, so the guard implies the remaining value.",
            "source_guard": {"arm": n, "pair": list(pair), "rid": rid, "owner": "revised",
                             "branch_color": rule["branch_color"],
                             "pivot": rec["pivot"], "root_forbidden": rec["root"]["forbidden"],
                             "child_forbidden": rec["branches"][str(rule["branch_color"])]["forbidden"]},
            "excluded_sibling_replays": replacements,
            "complete_child_cover": {"query": sha(raw_cover), "proof": sha(cover_proof),
                                     "proof_bytes": len(cover_proof), "negative_literals": [u[0] for u in cover_units],
                                     "files": ["cover.cnf", "cover.drat", "cover-check.log"],
                                     "checker_result": cover_result},
            "queries": {"parent": f"nodes/{len(entries) + 1}/parent.cnf",
                        "refined": f"nodes/{len(entries) + 1}/refined.cnf",
                        "parent_sha256": parent_string, "refined_sha256": expected_refined},
            "status": "REFINED_NOT_CLOSED",
            "progress_scope": "One queued inner node can be replaced by its unique locally surviving value after a checked complete two-child cover and checked sibling exclusion; no whole-parent or whole-row closure.",
        })
        entries.append(entry)
        all_steps.append(entry)

    malformed_controls = []
    for entry in entries[:1]:
        rejected = entry["excluded_sibling_replays"][0]
        query_file = out / "malformed-query.cnf"
        proof_file = out / "malformed-proof.drat"
        parent = entry["parent"]
        rejected = entry["excluded_sibling_replays"][0]
        cube = [tuple(x) for x in rejected["cube"]]
        units = prototype.get_units(parent["rid"], parent["n"], parent["pair"],
                                    entry["branch_color"], None, None, cube)
        raw = append(prototype.full_base(parent["rid"], tuple(parent["pair"])), units)[1]
        assert sha(raw) == rejected["query"]
        source_dir = summary_path.parent / Path(entry["excluded_checks"][0]["log"]).parent
        real_proof = (source_dir / "proof.drat").read_bytes()
        assert sha(real_proof) == rejected["proof"]
        bad = b"X\0" + real_proof
        assert bad != real_proof
        query_file.write_bytes(raw)
        proof_file.write_bytes(bad)
        # drat-trim itself exits zero for this input: after reporting the bad
        # binary prefix, unit propagation closes the formula and it prints
        # "s VERIFIED".  The accepted strict check nevertheless rejects the
        # warning; never substitute its return code for the strict verdict.
        control = checker(args.checker, query_file, proof_file, 300)
        assert not control["verified"]
        assert "WARNING: wrong binary prefix" in control["output"], control
        malformed_controls.append({"returncode": control["returncode"],
                                   "strictly_rejected": not control["verified"],
                                   "rejection_reason": "drat-trim warning (wrong binary prefix)",
                                   "output": control["output"]})

    assert len(entries) == len(summary["rules"])
    result = {
        "schema": "verified-conditional-refinement/v1",
        "prototype_sha256": sha(args.prototype.read_bytes()),
        "summary_sha256": sha(summary_path.read_bytes()),
        "solver_searches_in_assembler": 0,
        "conditional_refinements": entries,
        "count": len(entries),
        "malformed_control": malformed_controls,
        "no_w": True,
        "closure_boundary": "Conditional, guarded replacements only. No claim about other guards, parent closure, whole rows or Ramsey bounds.",
    }
    (out / "ledger.json").write_bytes(json_bytes(result))
    print(json.dumps({"conditional_refinements": len(entries), "malformed_controls_rejected": len(malformed_controls)}, indent=2))


if __name__ == "__main__":
    main()
