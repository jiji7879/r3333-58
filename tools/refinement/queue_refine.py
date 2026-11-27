#!/usr/bin/env python3
"""Verify proof-linked, single-survivor replacements in a bounded queue.

Only the guarded inner nodes in an assembler ledger are touched.  No solver
search runs here.  Every UNSAT status and every complete two-child cover is
re-derived from its exact files with strict drat-trim checks before use.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def append_unit(raw, literal):
    """Return the exact canonical CNF with one additional unit clause."""
    lines = raw.splitlines(keepends=True)
    positions = [i for i, line in enumerate(lines) if line.lstrip().startswith(b"p ")]
    assert len(positions) == 1
    i = positions[0]
    head = lines[i].split()
    assert len(head) == 4 and head[:2] == [b"p", b"cnf"]
    lines[i] = f"p cnf {int(head[2])} {int(head[3]) + 1}\n".encode()
    if not lines[-1].endswith(b"\n"):
        lines.append(b"\n")
    return b"".join(lines) + f"{literal} 0\n".encode()


def strict_check(checker, query, proof, timeout=300):
    command = [str(checker), str(query), str(proof), "-i", "-U", "-t", str(timeout)]
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         timeout=timeout + 10)
    output = run.stdout.decode(errors="replace")
    warnings = "WARNING" in output.upper()
    verified = (run.returncode == 0 and run.stdout.count(b"s VERIFIED") == 1
                and not warnings)
    return {"command": [str(query), str(proof), "-i", "-U", "-t", str(timeout)],
            "returncode": run.returncode, "verified": verified,
            "warnings": warnings, "output": output}


def decide(children, capacity, complete_cover):
    """Abstract queue policy; terminal evidence is never inferred from OPEN.

    `capacity` includes the queued parent's own slot.  An expansion is allowed
    only when every unresolved child has a queue slot.  Certified UNSAT leaves
    need proof-linked history, not queue space.
    """
    assert isinstance(complete_cover, bool) and capacity >= 1
    assert children
    assert all(c["status"] in ("VERIFIED_UNSAT", "OPEN_UNKNOWN") for c in children)
    unresolved = [c for c in children if c["status"] == "OPEN_UNKNOWN"]
    if not complete_cover:
        return {"action": "KEEP_PARENT_QUEUED", "unresolved": len(unresolved),
                "reason": "child coverage has not been certified"}
    if not unresolved:
        return {"action": "CLOSE_NODE_BY_COMPLETE_COVER", "unresolved": 0,
                "queue_delta": -1, "reason": "every child certified UNSAT"}
    if len(unresolved) == 1:
        return {"action": "REPLACE_WITH_ONE_OPEN_CHILD", "unresolved": 1,
                "queue_delta": 0, "reason": "every other child certified UNSAT"}
    free = capacity - 1
    if len(unresolved) <= free:
        return {"action": "EXPAND_ALL_OPEN_CHILDREN", "unresolved": len(unresolved),
                "queue_delta": len(unresolved) - 1,
                "reason": "all unresolved children fit; none pruned"}
    return {"action": "KEEP_PARENT_QUEUED", "unresolved": len(unresolved),
            "queue_delta": 0,
            "reason": f"need {len(unresolved)} free slots but only {free} available"}


def build_ledger(source, checker):
    source = source.resolve()
    document = json.loads((source / "ledger.json").read_text())
    assert document["schema"] == "verified-conditional-refinement/v1"
    assert document["count"] == len(document["conditional_refinements"])
    records = []
    for index, entry in enumerate(document["conditional_refinements"], 1):
        node = source / "nodes" / str(index)
        parent_path = node / "parent.cnf"
        refined_path = node / "refined.cnf"
        parent = parent_path.read_bytes()
        refined = refined_path.read_bytes()
        assert entry["status"] == "REFINED_NOT_CLOSED"
        assert entry["remaining_status"] == "OPEN_UNKNOWN"
        assert sha(parent) == entry["queries"]["parent_sha256"] == entry["source_parent"]
        assert sha(refined) == entry["queries"]["refined_sha256"] == entry["refined_query"]

        excluded = entry["excluded_sibling_replays"]
        assert len(excluded) == 1
        excluded_lit = excluded[0]["excluded_literal"]
        # Recover the literal from the exact body extension; the headers have
        # different clause counts and can have different byte lengths.
        parent_head, parent_body = parent.split(b"\n", 1)
        refined_head, refined_body = refined.split(b"\n", 1)
        assert parent_head.split()[:3] == refined_head.split()[:3]
        assert refined_body.startswith(parent_body)
        suffix = refined_body[len(parent_body):].splitlines()
        assert len(suffix) == 1 and len(suffix[0].split()) == 2
        positive, zero = map(int, suffix[0].split())
        assert zero == 0 and positive > 0
        assert append_unit(parent, positive) == refined
        # Distinct colours use distinct Boolean variables even on one edge.
        # The checked cover, not equal variable IDs, establishes the split.
        assert positive > 0 and excluded_lit > 0 and positive != excluded_lit
        assert excluded[0]["cube"][2][0] == entry["third_edge"]
        assert append_unit(parent, excluded_lit) == (source / "replays" / str(index) / "query.cnf").read_bytes()

        bad_query = source / "replays" / str(index) / "query.cnf"
        bad_proof = source / "replays" / str(index) / "proof.drat"
        cover_query = node / "cover.cnf"
        cover_proof = node / "cover.drat"
        assert sha(bad_query.read_bytes()) == excluded[0]["query"]
        assert sha(bad_proof.read_bytes()) == excluded[0]["proof"]
        assert len(bad_proof.read_bytes()) == excluded[0]["proof_bytes"]
        cover = entry["complete_child_cover"]
        assert cover["negative_literals"] == [-positive, -excluded_lit]
        assert append_unit(append_unit(parent, -positive), -excluded_lit) == cover_query.read_bytes()
        assert sha(cover_query.read_bytes()) == cover["query"]
        assert sha(cover_proof.read_bytes()) == cover["proof"]
        bad_check = strict_check(checker, bad_query, bad_proof)
        cover_check = strict_check(checker, cover_query, cover_proof)
        assert bad_check["verified"], bad_check
        assert cover_check["verified"], cover_check

        children = [
            {"value": "excluded", "signed_literal": excluded_lit,
             "status": "VERIFIED_UNSAT", "query_sha256": sha(bad_query.read_bytes()),
             "proof_sha256": sha(bad_proof.read_bytes()),
             "strict_check": bad_check},
            {"value": "survivor", "signed_literal": positive,
             "status": "OPEN_UNKNOWN", "query_sha256": sha(refined),
             "proof_sha256": None, "strict_check": None},
        ]
        policy = decide(children, 1, True)
        assert policy["action"] == "REPLACE_WITH_ONE_OPEN_CHILD"
        history = {
            "source_parent_query_sha256": sha(parent),
            "refined_query_sha256": sha(refined),
            "parent": entry["parent"], "guard": entry["guard"],
            "third_edge": entry["third_edge"], "branch_color": entry["branch_color"],
            "owner": entry["source_guard"]["owner"], "pivot": entry["source_guard"]["pivot"],
            "child_cover": {"query_sha256": cover["query"], "proof_sha256": cover["proof"],
                            "strict_check": cover_check},
            "children": children,
        }
        records.append({"node": index, "decision": policy, "before": [sha(parent)],
                        "after": [sha(refined)], "queue_slots_before": 1, "queue_slots_after": 1,
                        "history": history, "node_status": "REFINED_NOT_CLOSED",
                        "scope": "guarded inner node only; SAT-equivalent after checked cover+sibling proof"})
    return {"schema": "verified-refinement-queue/v1", "count": len(records),
            "replacements": records,
            "queue_slots_before": len(records), "queue_slots_after": len(records),
            "unresolved_nodes": len(records),
            "fresh_solver_searches": 0,
            "closure_boundary": "Nine guarded replacements, all survivors OPEN_UNKNOWN; no parent, wall-row or Ramsey closure."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("assembled", type=Path)
    ap.add_argument("--checker", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    args.out.mkdir(parents=True)
    result = build_ledger(args.assembled, args.checker.resolve())
    (args.out / "queue.json").write_bytes(json_bytes(result))
    logs = [(r["node"], kind, child["strict_check"])
            for r in result["replacements"] for kind, child in
            [("exclusion", r["history"]["children"][0])]]
    for node, kind, check in logs:
        (args.out / f"node-{node}-{kind}.log").write_text(check["output"])
    for record in result["replacements"]:
        (args.out / f"node-{record['node']}-cover.log").write_text(
            record["history"]["child_cover"]["strict_check"]["output"])
    print(json.dumps({k: result[k] for k in
                      ("count", "queue_slots_before", "queue_slots_after", "unresolved_nodes",
                       "fresh_solver_searches")}, indent=2))


if __name__ == "__main__":
    main()
