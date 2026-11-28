#!/usr/bin/env python3
"""Independently recompute hashes/statuses of the completed five-leaf run."""
import hashlib
import itertools
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "inputs"
RUN = ROOT / "run/kissat-frontier"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def query_hash(base, cube):
    h = hashlib.sha256()
    with base.open("rb") as src:
        header = src.readline().split()
        nv, nc = int(header[2]), int(header[3])
        h.update(f"p cnf {nv} {nc + len(cube)}\n".encode())
        for block in iter(lambda: src.read(1 << 20), b""):
            h.update(block)
        for lit in cube:
            h.update(f"{lit} 0\n".encode())
    return h.hexdigest(), nv, nc + len(cube)


def exact_cover(cubes):
    variables = sorted({abs(lit) for cube in cubes for lit in cube})
    counts = []
    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        counts.append(sum(all(assignment[abs(lit)] == (lit > 0) for lit in cube)
                          for cube in cubes))
    return {"split_variables": variables, "assignments_checked": len(counts),
            "exactly_one_cube_per_assignment": all(x == 1 for x in counts),
            "coverage_multiplicities": sorted(set(counts))}


def read_cubes(path):
    result = []
    for line in path.read_text().splitlines():
        fields = line.split()
        assert fields[0] == "a" and fields[-1] == "0"
        result.append([int(x) for x in fields[1:-1]])
    return result


def main():
    cubes = read_cubes(IN / "frontier.cubes")
    cover = exact_cover(cubes)
    assert cover["exactly_one_cube_per_assignment"]
    receipts = json.loads((RUN / "receipts.json").read_text())
    assert len(receipts) == len(cubes) == 5
    audit = []
    for rec in receipts:
        index, cube = rec["index"], rec["cube"]
        assert cube == cubes[index]
        leaf = RUN / f"leaf-{index}"
        expected_query, nv, nc = query_hash(IN / "parent.cnf", cube)
        expected_working, wnv, wnc = query_hash(IN / "working.cnf", cube)
        actual_query = sha(leaf / "query.cnf")
        actual_working = sha(leaf / "working-query.cnf")
        log = (leaf / "solver.log").read_bytes().replace(b"\r", b"\n").decode(errors="replace")
        status_lines = [x for x in log.splitlines() if x in
                        ("s SATISFIABLE", "s UNSATISFIABLE", "s UNKNOWN")]
        conflicts = [int(x.replace(",", "")) for x in
                     re.findall(r"^c conflicts:\s+([0-9,]+)", log, re.M)]
        item = {
            "index": index, "cube": cube, "status": rec["status"],
            "query_sha256_recomputed": actual_query,
            "working_query_sha256_recomputed": actual_working,
            "query_reconstruction_matches": actual_query == expected_query == rec["query_sha256"],
            "working_query_reconstruction_matches": actual_working == expected_working == rec["working_query_sha256"],
            "original_query_header": [nv, nc], "working_query_header": [wnv, wnc],
            "solver_status_lines": status_lines,
            "open_protocol_ok": (rec["status"] == "OPEN" and status_lines == ["s UNKNOWN"]
                                 and rec["solver_returncode"] == 0 and rec["resource_stop"] is None),
            "conflicts_match_log": bool(conflicts) and conflicts[-1] == rec["solver_conflicts_last"],
            "unfinished_proof_removed": not (leaf / "leaf.drat").exists(),
            "no_normalized_proof_retained": not (leaf / "joined.additions-only.drat").exists(),
            "discarded_proof_below_1GB": 0 < rec["discarded_noncertificate_proof_bytes"] < 1000000000,
        }
        assert all(item[k] for k in ("query_reconstruction_matches", "working_query_reconstruction_matches",
                                     "open_protocol_ok", "conflicts_match_log", "unfinished_proof_removed",
                                     "no_normalized_proof_retained", "discarded_proof_below_1GB"))
        audit.append(item)
    result = {
        "schema": "k58-five-open-leaf-independent-reaudit/v1",
        "parent_sha256": sha(IN / "parent.cnf"), "working_sha256": sha(IN / "working.cnf"),
        "cas_sha256": sha(IN / "cas.drat"), "frontier_sha256": sha(IN / "frontier.cubes"),
        "cover": cover, "leaves": audit,
        "total_solver_conflicts": sum(x["solver_conflicts_last"] for x in receipts),
        "total_solver_elapsed_s": sum(x["elapsed_s"] for x in receipts),
        "total_solver_cpu_s": sum(x["cpu_s"] for x in receipts),
        "checked_unsat_leaves": sum(x["status"] == "CHECKED_UNSAT" for x in receipts),
        "cnf_parent_status": "OPEN",
        "physical_colouring_status": "NOT ADDRESSED; no semantic assembly claimed",
    }
    (ROOT / "checks/run-reaudit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("total_solver_conflicts", "total_solver_elapsed_s",
          "total_solver_cpu_s", "checked_unsat_leaves", "cnf_parent_status")}, sort_keys=True))


if __name__ == "__main__":
    main()
