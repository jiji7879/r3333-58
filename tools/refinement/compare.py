#!/usr/bin/env python3
"""Bounded fresh guard-parent versus proof-refined-child K58 comparison."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def without_deletions(data):
    """Drop binary DRAT `d` records, preserving every `a` record verbatim.

    Deletions only discard clauses; retaining all clauses can strengthen RUP
    premises without changing any addition.  The transformed proof is still
    independently checked, never trusted because of this transformation.
    """
    output = bytearray()
    additions = deletions = 0
    position = 0
    while position < len(data):
        kind = data[position]
        assert kind in (ord("a"), ord("d")), (position, kind)
        start = position
        position += 1
        while True:
            assert position < len(data), "truncated binary proof literal"
            byte = data[position]
            position += 1
            if byte == 0:
                break
        if kind == ord("a"):
            output.extend(data[start:position])
            additions += 1
        else:
            deletions += 1
    assert output.endswith(b"a\0"), "no final added empty clause"
    return bytes(output), {"additions_preserved": additions,
                           "deletions_removed": deletions}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("assembled", type=Path)
    ap.add_argument("--checker", type=Path, required=True)
    ap.add_argument("--python", type=Path, required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--leaf", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--budget", type=float, default=3.0)
    ap.add_argument("--cutoff", type=float, default=25.0)
    ap.add_argument("--resume", action="store_true",
                    help="reuse completed leaves in the existing output directory; rerun no terminated search")
    args = ap.parse_args()
    assert args.budget == 3.0 and args.cutoff > args.budget
    source = args.assembled.resolve()
    args.checker = args.checker.resolve()
    # Preserve the venv launcher: resolving its python symlink bypasses the
    # environment and hides the installed pysolvers extension.
    args.python = args.python.absolute()
    args.leaf = args.leaf.resolve()
    args.runtime = args.runtime.resolve()
    args.out = args.out.resolve()
    if args.out.exists():
        assert args.resume, "output exists; pass --resume only to replay its exact completed leaves"
    else:
        args.out.mkdir(parents=True)
    document = json.loads((source / "ledger.json").read_text())
    selected = []
    for entry in document["conditional_refinements"]:
        if entry["parent"]["n"] not in {r["parent"]["n"] for r in selected}:
            selected.append(entry)
    assert [r["parent"]["n"] for r in selected] == [11, 12, 13, 14]
    jobs = []
    for entry in selected:
        index = document["conditional_refinements"].index(entry) + 1
        parent = source / entry["queries"]["parent"]
        refined = source / entry["queries"]["refined"]
        assert sha(parent.read_bytes()) == entry["queries"]["parent_sha256"]
        assert sha(refined.read_bytes()) == entry["queries"]["refined_sha256"]
        for kind, query in (("guard_parent", parent), ("refined_child", refined)):
            jobs.append({"arm": entry["parent"]["n"], "node": index, "kind": kind,
                         "query": query, "parent_query": parent if kind == "refined_child" else None})
    assert len(jobs) == 8
    records = []
    started = time.perf_counter()
    for sequence, job in enumerate(jobs, 1):
        out = args.out / f"{sequence:02d}-{job['arm']}-{job['kind']}"
        raw_hash = sha(job["query"].read_bytes())
        old_receipt = out / "receipt.json"
        reused = args.resume and (old_receipt.is_file() or (out / "leaf" / "leaf.json").is_file())
        if reused:
            previous = json.loads(old_receipt.read_text()) if old_receipt.is_file() else {
                "query": str(job["query"]), "parent_query": str(job["parent_query"]) if job["parent_query"] else None,
                "query_sha256": raw_hash, "arm": job["arm"], "kind": job["kind"],
                "cut_off": False, "output": (out / "worker.log").read_text(),
                "process_wall_seconds": None, "worker_returncode": 0}
            assert previous["query_sha256"] == raw_hash
            assert previous["arm"] == job["arm"] and previous["kind"] == job["kind"]
            assert previous["query"] == str(job["query"])
            record = previous
            record.update({k: (str(v) if isinstance(v, Path) else v) for k, v in job.items()})
            record.update({"sequence": sequence, "query_sha256": raw_hash})
            if "node" in previous:
                assert previous["node"] == job["node"]
            record["reused_exact_leaf_without_solver"] = True
            record["status"] = "OPEN_UNKNOWN"
            if record["cut_off"]:
                records.append(record)
                print(job["arm"], job["kind"], "OPEN_UNKNOWN (reused cutoff)", flush=True)
                continue
            proc = None
            output = record["output"].encode()
            killed = False
        else:
            out.mkdir()
            argv = [str(args.python), str(args.leaf), str(job["query"]), str(out / "leaf"),
                    str(args.budget), str(args.runtime)]
            if job["parent_query"] is not None:
                argv.append(str(job["parent_query"]))
            t0 = time.perf_counter()
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            killed = False
            try:
                output, _ = proc.communicate(timeout=args.cutoff)
            except subprocess.TimeoutExpired:
                killed = True
                os.killpg(proc.pid, signal.SIGKILL)
                output, _ = proc.communicate()
            wall = time.perf_counter() - t0
            (out / "worker.log").write_bytes(output)
            record = {k: (str(v) if isinstance(v, Path) else v) for k, v in job.items()}
            record.update({"sequence": sequence, "query_sha256": raw_hash,
                           "reused_exact_leaf_without_solver": False,
                           "hard_cutoff_seconds": args.cutoff, "cut_off": killed,
                           "worker_returncode": proc.returncode, "process_wall_seconds": wall,
                           "status": "OPEN_UNKNOWN", "output": output.decode(errors="replace")})
        if killed:
            record["reason"] = "external hard cutoff; no terminal verdict inferred"
        else:
            leaf_file = out / "leaf" / "leaf.json"
            assert (reused or proc.returncode == 0) and leaf_file.is_file(), record
            leaf = json.loads(leaf_file.read_text())
            assert leaf["query_sha256"] == raw_hash
            record.update(leaf)
            if leaf["status"] == "UNKNOWN":
                assert leaf["decision_unknown_after_budget"]
                record["status"] = "OPEN_UNKNOWN"
                record["reason"] = "3-second search budget exhausted; UNKNOWN"
            elif leaf["status"] == "SAT":
                assert leaf["model_satisfies_query"]
                if job["kind"] == "refined_child":
                    assert leaf["model_satisfies_guard_parent"]
                record["status"] = "VERIFIED_SAT"
                record["reason"] = "checked complete model of exact query; scoped SAT only"
            elif leaf["status"] == "UNSAT":
                query = job["query"]
                proof = out / "leaf" / "proof.drat"
                original_proof = proof.read_bytes()
                normalized, trace_info = without_deletions(original_proof)
                strict_proof = out / "leaf" / "proof-nodeletions.drat"
                strict_proof.write_bytes(normalized)
                if trace_info["deletions_removed"]:
                    assert normalized != original_proof
                else:
                    assert normalized == original_proof
                record["proof_normalization"] = {
                    "original_query_sha256": raw_hash,
                    "original_proof_sha256": sha(original_proof),
                    "original_proof_bytes": len(original_proof),
                    "deletion_free_proof_sha256": sha(normalized),
                    "deletion_free_proof_bytes": len(normalized), **trace_info}
                tcheck = time.perf_counter()
                run = subprocess.run([str(args.checker), str(query), str(strict_proof), "-i", "-U", "-t", "300"],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
                check_seconds = time.perf_counter() - tcheck
                text = run.stdout.decode(errors="replace")
                good = (run.returncode == 0 and run.stdout.count(b"s VERIFIED") == 1
                        and b"WARNING" not in run.stdout.upper())
                record["proof_check"] = {"seconds": check_seconds, "returncode": run.returncode,
                    "verified": good, "warnings": b"WARNING" in run.stdout.upper(),
                    "flags": ["-i", "-U", "-t", "300"], "output": text,
                    "query_sha256": raw_hash, "proof_sha256": sha(normalized)}
                (out / "check.log").write_bytes(run.stdout)
                assert good, record
                record["status"] = "VERIFIED_UNSAT"
                record["reason"] = "exact guarded query refuted and strictly replayed; not an unguarded parent closure"
            else:
                raise AssertionError(leaf["status"])
        (out / "receipt.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        records.append(record)
        print(job["arm"], job["kind"], record["status"],
              f"search={record.get('search_seconds', 0):.3f}s", flush=True)
    assert len(records) == 8
    assert sum(r["search_budget_seconds"] for r in records if "search_budget_seconds" in r) <= 24.0
    result = {
        "schema": "bounded-refinement-comparison/v1",
        "completed_physical_solver_calls": len(records),
        "fresh_solver_calls_this_invocation": sum(not r["reused_exact_leaf_without_solver"] for r in records),
        "reused_completed_solver_calls": sum(r["reused_exact_leaf_without_solver"] for r in records),
        "max_calls": 8, "per_call_search_budget_seconds": args.budget,
        "declared_search_budget_total_seconds": 24.0,
        "invocation_wall_seconds": time.perf_counter() - started,
        "wall_time_scope": "this invocation only; reused leaves retain their per-record search and setup timings",
        "checker_sha256": sha(args.checker.read_bytes()), "leaf_sha256": sha(args.leaf.read_bytes()),
        "records": records,
        "interpretation": "Exploratory measurements on distinct guarded parent/strengthened child formulas; not a runtime-improvement theorem or generalization.",
        "closure_boundary": "Any result is conditional on its complete guard; no original parent, ordinary wall row or Ramsey bound is closed by this comparison alone.",
    }
    (args.out / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"represented_calls": len(records),
                      "fresh_calls_this_invocation": result["fresh_solver_calls_this_invocation"],
                      "statuses": {k: [r["status"] for r in records if r["kind"] == k]
                                   for k in ("guard_parent", "refined_child")}}, indent=2))


if __name__ == "__main__":
    main()
