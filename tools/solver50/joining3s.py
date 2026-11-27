#!/usr/bin/env python3
"""Prepare complete joining-colour splits, then run a frozen 3-second probe.

Every solver call gets a fresh process. A representative is closed only by a
strict proof of its exact full query, or by a strict surviving-child proof and
strict refutations of all three other physical joining-colour branches.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

SEARCH_SECONDS = 3.0
PROCESS_CUTOFF_SECONDS = 120.0
SOLVE_WATCHDOG_SECONDS = 6.0
WATCHDOG_POLL_SECONDS = 0.05
CHECKER_SECONDS = 300
MAX_PAIRS = 6
MAX_QUERIES = 12


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
    os.replace(temporary, path)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def checker(campaign: Path, query: Path, proof: Path, log: Path, expected: bool | None = None,
            only_rup: bool = False) -> dict:
    command = [str(campaign / "tools/drat-trim"), str(query), str(proof),
               "-i", *(["-U"] if only_rup else []), "-t", str(CHECKER_SECONDS)]
    started = time.monotonic()
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    elapsed = time.monotonic() - started
    verdicts = [line.decode(errors="replace") for line in run.stdout.splitlines()
                if line.startswith(b"s ")]
    verified = run.returncode == 0 and verdicts == ["s VERIFIED"]
    log.write_bytes(b"$ " + " ".join(command).encode() + b"\nreturncode: " +
                    str(run.returncode).encode() + b"\n" + run.stdout)
    if expected is True and not verified:
        raise RuntimeError(f"Required strict replay failed: {query}: {run.stdout[-1000:]!r}")
    if expected is False and (run.returncode == 0 or verdicts != ["s NOT VERIFIED"]):
        raise RuntimeError(f"Negative control did not fail closed: {query}")
    return {"command": command, "returncode": run.returncode, "verdicts": verdicts,
            "seconds": elapsed, "verified": verified, "warning_suppression": False}


def transport(campaign: Path, out: Path, folder: Path, job: dict, representative: bytes,
              parent: bytes, color: int) -> dict:
    """Lift one local excluded-colour proof to this exact full representative."""
    from arm_pairs import base
    from common import host, source
    from compile import append, binary
    from edge50 import local
    from edge_proofs50 import local_query
    from problem import read_dimacs

    n, w, z, rid = job["arm"], job["w"], job["z"], job["row_id"]
    stem = f"{n}-{w}-{z}-{color}"
    source_dir = campaign / "round50/edge-new/proofs"
    source_receipt = json.loads((source_dir / f"{stem}.json").read_bytes())
    assert source_receipt["scope"] == "round50"
    assert (source_receipt["n"], source_receipt["w"], source_receipt["z"],
            source_receipt["c"]) == (n, w, z, color)
    local_raw = local_query(n, w, z, color, "round50", "round50")
    local_proof = gzip.decompress((source_dir / f"{stem}.rup.gz").read_bytes())
    assert (sha(local_raw), sha(local_proof)) == (source_receipt["local_query"],
                                                  source_receipt["local_proof"])
    lq, lp = folder / f"excluded-{color}-local.cnf", folder / f"excluded-{color}-local.rup"
    lq.write_bytes(local_raw)
    lp.write_bytes(local_proof)
    local_check = checker(campaign, lq, lp, folder / f"excluded-{color}-local.log", True,
                          only_rup=True)

    _, arm, pentagon, outside = source(rid)
    edges, ids, _ = base(n)
    edge, _ = host(58)
    vertices = list(pentagon) + list(outside)
    image = [0] + [edge(vertices[i], vertices[j], k)
                   for i, j in edges for k in arm["palette"]]
    edge_variables = len(image) - 1
    old_top = int(parent.splitlines()[0].split()[2])
    image += list(range(old_top + 1, old_top + 1 + local(n, "round50")[0] - edge_variables))
    assert len(image[1:]) == len(set(image[1:]))
    literal = image[ids[5, 6] + color]
    assert literal == edge(outside[0], outside[1], arm["palette"][color])
    query = append(representative, [[literal]])[1]
    representative_top, full_clauses = read_dimacs(query)
    assert max(image[1:]) <= representative_top

    # The only mapped local clauses absent verbatim from the full query must be
    # the local three-colour at-least-one clauses supplied by the RUP prefix.
    _, local_clauses = read_dimacs(local_raw)
    full_set = {tuple(sorted(clause)) for clause in full_clauses}
    mapped = {tuple(sorted((-1 if v < 0 else 1) * image[abs(v)] for v in clause))
              for clause in local_clauses}
    missing = sorted(mapped - full_set)
    expected_missing = sorted({tuple(sorted(image[ids[e]:ids[e] + 3])) for e in edges})
    assert missing == expected_missing

    mapping = folder / f"excluded-{color}.map"
    local_copy = folder / f"excluded-{color}-copy.rup"
    lifted = folder / f"excluded-{color}-mapped.rup"
    mapping.write_text(str(len(image) - 1) + "\n" + " ".join(map(str, image[1:])) + "\n")
    local_copy.write_bytes(local_proof)
    subprocess.run([str(campaign / "tools/relabel"), str(mapping), str(local_copy), str(lifted)],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    prefix = b"".join(binary(image[i:i + 3]) for i in range(1, edge_variables + 1, 3))
    physical_proof = prefix + lifted.read_bytes()
    q, p = folder / f"excluded-{color}.cnf", folder / f"excluded-{color}.rup"
    q.write_bytes(query)
    p.write_bytes(physical_proof)
    check = checker(campaign, q, p, folder / f"excluded-{color}.log", True, only_rup=True)
    return {"kind": "transported_arm_exclusion", "normalized_color": color,
            "physical_literal": literal, "physical_color": arm["palette"][color],
            "source_receipt_row_id": source_receipt["row_id"],
            "source_receipt_scope": source_receipt["scope"],
            "local_query_sha256": sha(local_raw), "local_proof_sha256": sha(local_proof),
            "query_sha256": sha(query), "proof_sha256": sha(physical_proof),
            "query_file": str(q.relative_to(out)), "proof_file": str(p.relative_to(out)),
            "local_check": local_check, "full_check": check,
            "self_similarity": {"mapped_clauses": len(mapped),
                                "expected_prefix_clauses": len(missing),
                                "other_missing_clauses": 0}}


def prepare(campaign: Path, design: Path, out: Path) -> dict:
    from arm_pairs import between
    from common import host, source
    from compile import append, binary
    from edge_children50 import exclusions, export
    from problem import read_dimacs
    from representatives import full_query

    candidates = read_tsv(design / "candidates.tsv")
    plan = read_tsv(design / "execution-plan.tsv")
    primary = "query_path" in plan[0]
    work_plan = [entry for entry in plan if not primary or entry["role"] == "new_unprobed_pair"]
    assert 1 <= len(candidates) <= MAX_PAIRS and 1 <= len(plan) <= MAX_QUERIES
    assert len(work_plan) == 2 * len(candidates)
    (out / "design").mkdir()
    for name in ("candidates.tsv", "execution-plan.tsv", "selection-audit.json",
                 "verification.json", "audit.json", "checksums.json"):
        if (design / name).exists():
            shutil.copyfile(design / name, out / "design" / name)
    (out / "splits").mkdir()
    artifact_root = Path.cwd().resolve() if primary else design
    prepared = {}
    for row in candidates:
        pair = row.get("pair_id") or f"A{row['arm']}"
        rid, w, z, n = row["row_id"], row["w"], row["z"], int(row["arm"])
        triangle = sorted(between(w, z))
        extra = sorted(exclusions().get((n, w, z), ()))
        left = sorted(set(triangle) - set(extra))
        assert len(triangle) >= 2 and extra and len(left) == 1
        if not primary:
            assert triangle == [int(c) for c in row["triangle_colors"]]
            assert extra == [int(c) for c in row["proof_excluded_colors"]]
            assert left == [int(row["surviving_colors"])]
        job = {"pair_id": pair, "row_id": rid, "w": w, "z": z, "arm": n,
               "between": triangle, "excluded": extra, "surviving": left}
        from cover50 import make_batch
        batch = make_batch(int(row["offset"]), 1)[0]
        assert (batch["cover_index"], batch["row_id"], batch["arm"], batch["w"], batch["z"]) == \
               (int(row["cover_index"]), rid, n, w, z)
        surviving_literal = int(row.get("child_physical_literal") or row["surviving_physical_literal"])
        parent, representative, cube = full_query(rid, w, z, "round50")
        assert sha(parent) == row.get("source_parent_sha256", row.get("parent_sha256"))
        assert sha(representative) == row.get("representative_query_sha256", row.get("representative_sha256"))
        assert representative == (artifact_root / row["representative_path"]).read_bytes()
        if "owner_cube" in row:
            assert json.loads(row["owner_cube"]) == cube
        folder = out / "splits" / pair
        export(rid, w, z, folder)
        (folder / "parent.cnf").write_bytes(parent)
        (folder / "representative.cnf").write_bytes(representative)
        child = (folder / f"joining-{left[0]}.cnf").read_bytes()
        expected_child = append(representative, [[surviving_literal]])[1]
        assert child == expected_child == (artifact_root / row["child_path"]).read_bytes()
        assert sha(child) == row.get("child_query_sha256", row.get("child_sha256"))

        _, arm, _, outside = source(rid)
        edge, _ = host(58)
        all_four = sorted(edge(outside[0], outside[1], c) for c in range(4))
        _, representative_clauses = read_dimacs(representative)
        clause_set = {tuple(clause) for clause in representative_clauses}
        assert tuple(all_four) in clause_set
        assert all((-a, -b) in clause_set for i, a in enumerate(all_four) for b in all_four[i + 1:])

        branches = []
        for normalized in sorted(set(range(3)) - set(triangle)):
            literal = edge(outside[0], outside[1], arm["palette"][normalized])
            q, p = folder / f"triangle-{normalized}.cnf", folder / f"triangle-{normalized}.rup"
            query = append(representative, [[literal]])[1]
            proof = binary([])
            q.write_bytes(query)
            p.write_bytes(proof)
            check = checker(campaign, q, p, folder / f"triangle-{normalized}.log", True,
                            only_rup=True)
            branches.append({"kind": "monochromatic_triangle", "normalized_color": normalized,
                             "physical_literal": literal, "query_sha256": sha(query),
                             "proof_sha256": sha(proof), "query_file": str(q.relative_to(out)),
                             "proof_file": str(p.relative_to(out)), "full_check": check})
        missing = arm["missing_color"]
        literal = edge(outside[0], outside[1], missing)
        q, p = folder / "triangle-missing.cnf", folder / "triangle-missing.rup"
        query = append(representative, [[literal]])[1]
        proof = binary([])
        q.write_bytes(query)
        p.write_bytes(proof)
        check = checker(campaign, q, p, folder / "triangle-missing.log", True, only_rup=True)
        branches.append({"kind": "monochromatic_triangle", "normalized_color": "missing",
                         "physical_literal": literal, "physical_color": missing,
                         "query_sha256": sha(query), "proof_sha256": sha(proof),
                         "query_file": str(q.relative_to(out)),
                         "proof_file": str(p.relative_to(out)), "full_check": check})
        for color in extra:
            branches.append(transport(campaign, out, folder, job, representative, parent, color))

        refuted = {branch["physical_literal"] for branch in branches}
        assert refuted | {surviving_literal} == set(all_four)
        assert surviving_literal not in refuted
        # A transported nontrivial proof must not disappear into an empty-proof check.
        negative = branches[-1]
        empty = folder / "empty-proof-control.rup"
        empty.write_bytes(b"")
        checker(campaign, out / negative["query_file"], empty,
                folder / "empty-proof-control.log", False, only_rup=True)
        record = dict(job, profile=batch["profile"], offset=int(row["offset"]),
                      cover_index=int(row["cover_index"]), scope="round50",
                      parent_sha256=sha(parent), representative_sha256=sha(representative),
                      representative_cube=cube,
                      child_sha256=sha(child), surviving_physical_literal=surviving_literal,
                      representative_file=str((folder / "representative.cnf").relative_to(out)),
                      child_file=str((folder / f"joining-{left[0]}.cnf").relative_to(out)),
                      parent_file=str((folder / "parent.cnf").relative_to(out)),
                      all_four_physical_literals=all_four, other_branches=branches,
                      exhaustive_four_color_partition=True,
                      status="OPEN_UNTIL_SURVIVING_OR_REPRESENTATIVE_PROOF")
        write_json(folder / "job.json", record)
        prepared[pair] = record
        print(f"prepared {pair} arm={n}: {len(branches)} complementary branches strictly refuted",
              flush=True)

    for entry in work_plan:
        record = prepared[entry["pair_id"]]
        key = ("representative_sha256" if entry["query_kind"] == "parent" else "child_sha256")
        expected = entry.get("expected_sha256", entry.get("query_sha256"))
        assert expected == record[key]
    summary = {"schema": "k58-joining3s-preparation/v1", "candidates": list(prepared.values()),
               "candidate_pairs": len(prepared), "planned_queries": len(work_plan),
               "schedule_style": "primary" if primary else "reserve",
               "positive_control_calls": len(plan) - len(work_plan),
               "solver_calls": 0, "closure_boundary":
               "Only a direct representative proof or a complete four-colour split closes a representative; no row closure follows without its whole cover."}
    write_json(out / "preparation.json", summary)
    return summary


def solve_worker(campaign_text: str, job: dict, query_file: str, run_dir: str) -> None:
    """One isolated direct CaDiCaL process, including independent proof replay."""
    campaign = Path(campaign_text)
    destination = Path(run_dir)
    try:
        destination.mkdir()
        sys.path.insert(0, campaign_text)
        import timed50
        from common import sha as source_sha
        from pysat.formula import CNF
        from pysat.solvers import Cadical195
        import pysolvers

        raw = Path(query_file).read_bytes()
        assert sha(raw) == job["expected_sha256"] == source_sha(raw)
        (destination / "query.cnf").write_bytes(raw)
        setup_started = time.monotonic()
        clauses = CNF(from_string=raw.decode()).clauses
        with Cadical195(bootstrap_with=clauses, with_proof=True) as sat:
            setup = time.monotonic() - setup_started
            search_started = time.monotonic()
            (destination / "solve-started").write_text(str(search_started))
            cpu_started = time.process_time()
            try:
                result = timed50.timed_solve(sat, SEARCH_SECONDS)
            finally:
                (destination / "solve-finished").write_text(str(time.monotonic()))
            search = time.monotonic() - search_started
            cpu = time.process_time() - cpu_started
            stats = sat.accum_stats()
            receipt = dict(job, query_sha256=sha(raw), budget_s=SEARCH_SECONDS,
                           setup_s=setup, search_s=search, cpu_s=cpu, **stats,
                           status="OPEN", proof_sha256="", proof_bytes=0,
                           checker_verified=False, fresh_process=True)
            if result is False:
                pysolvers.flushpr(sat.prfp)
                sat.prfile.seek(0)
                proof = sat.prfile.read()
                proof_path = destination / "proof.drat"
                proof_path.write_bytes(proof)
                (destination / "proof.drat.gz").write_bytes(gzip.compress(proof, mtime=0))
                check = checker(campaign, destination / "query.cnf", proof_path,
                                destination / "proof-check.log")
                receipt.update(proof_sha256=sha(proof), proof_bytes=len(proof),
                               checker_verified=check["verified"], checker=check,
                               status="VERIFIED_UNSAT" if check["verified"]
                               else "UNVERIFIED_SOLVER_UNSAT")
            elif result:
                assignment = set(sat.get_model())
                if not all(any(lit in assignment for lit in clause) for clause in clauses):
                    raise ValueError("Solver returned an invalid model")
                model = " ".join(map(str, sorted(assignment, key=abs))).encode()
                (destination / "model.gz").write_bytes(gzip.compress(model, mtime=0))
                receipt["status"] = "VERIFIED_SAT"
        write_json(destination / "receipt.json", receipt)
    except BaseException:
        destination.mkdir(exist_ok=True)
        (destination / "failure.log").write_text(traceback.format_exc())
        raise


def execute(campaign: Path, out: Path, preparation: dict) -> dict:
    plan = read_tsv(out / "design/execution-plan.tsv")
    candidates = {row["pair_id"]: row for row in preparation["candidates"]}
    run_root = out / "runs"
    run_root.mkdir()
    receipts = []
    aborted_after_control_failure = False
    for entry in plan:
        role = entry.get("role", "new_unprobed_pair")
        expected_hash = entry.get("expected_sha256", entry.get("query_sha256"))
        if role == "positive_control":
            query_file = Path.cwd().resolve() / entry["query_path"]
            item = dict(entry, expected_sha256=expected_hash)
        else:
            pair = candidates[entry["pair_id"]]
            query_file = out / (pair["representative_file"] if entry["query_kind"] == "parent"
                                else pair["child_file"])
            item = dict(entry, row_id=pair["row_id"], w=pair["w"], z=pair["z"], arm=pair["arm"],
                        scope="round50", expected_sha256=expected_hash,
                        representative_sha256=pair["representative_sha256"],
                        child_sha256=pair["child_sha256"])
        destination = run_root / entry["run_index"]
        started = time.monotonic()
        process = mp.get_context("fork").Process(target=solve_worker,
            args=(str(campaign), item, str(query_file), str(destination)))
        process.start()
        solve_started = None
        failure_stage = None
        while process.is_alive():
            elapsed = time.monotonic() - started
            if elapsed >= PROCESS_CUTOFF_SECONDS:
                failure_stage = "whole_worker"
                break
            process.join(min(WATCHDOG_POLL_SECONDS,
                             max(0.001, PROCESS_CUTOFF_SECONDS - elapsed)))
            if not process.is_alive():
                break
            if solve_started is None and (destination / "solve-started").exists():
                try:
                    solve_started = float((destination / "solve-started").read_text())
                except (OSError, ValueError):
                    pass
            if (solve_started is not None and not (destination / "solve-finished").exists()
                    and time.monotonic() - solve_started > SOLVE_WATCHDOG_SECONDS):
                failure_stage = "solve_phase"
                break
        if process.is_alive():
            process.terminate()
            process.join(5)
            if process.is_alive():
                process.kill()
                process.join()
            destination.mkdir(exist_ok=True)
            write_json(destination / "receipt.json", dict(item,
                query_sha256=expected_hash, status="INFRASTRUCTURE_TIMEOUT",
                failure_stage=failure_stage or "whole_worker", checker_verified=False,
                fresh_process=True))
        elif process.exitcode:
            destination.mkdir(exist_ok=True)
            write_json(destination / "receipt.json", dict(item,
                query_sha256=expected_hash, status="INFRASTRUCTURE_FAILURE",
                failure_stage="worker_exception", checker_verified=False, fresh_process=True))
        receipt = json.loads((destination / "receipt.json").read_bytes())
        receipt["process_wall_s"] = time.monotonic() - started
        assert receipt["query_sha256"] == expected_hash
        assert receipt["row_id"] == entry["row_id"]
        write_json(destination / "receipt.json", receipt)
        receipts.append(receipt)
        print(entry["run_index"], entry.get("pair_id", ""), entry["query_kind"], receipt["status"],
              receipt.get("conflicts", ""), round(receipt.get("search_s", 0.0), 4), flush=True)
        if role == "positive_control" and receipt["status"] != "VERIFIED_UNSAT":
            aborted_after_control_failure = True
            print("stopping before candidate calls: positive control failed", flush=True)
            break

    candidate_receipts = [r for r in receipts if r.get("role", "new_unprobed_pair") != "positive_control"]
    closures = []
    if not aborted_after_control_failure:
        for pair_id, pair in candidates.items():
            own = [r for r in candidate_receipts if r["pair_id"] == pair_id]
            parent = next(r for r in own if r["query_kind"] == "parent")
            child = next(r for r in own if r["query_kind"] == "child")
            if parent["status"] == "VERIFIED_UNSAT":
                method = "DIRECT_REPRESENTATIVE_DRAT"
            elif child["status"] == "VERIFIED_UNSAT" and pair["exhaustive_four_color_partition"]:
                method = "COMPLETE_JOINING_COLOR_SPLIT"
            else:
                method = "OPEN"
            closures.append({"pair_id": pair_id, "row_id": pair["row_id"], "w": pair["w"],
                             "z": pair["z"], "arm": pair["arm"], "offset": pair["offset"],
                             "cover_index": pair["cover_index"], "method": method,
                             "representative_status": "CLOSED" if method != "OPEN" else "OPEN",
                             "parent_receipt": parent["run_index"], "child_receipt": child["run_index"],
                             "whole_original_row_closed": False})
    counts = {status: sum(r["status"] == status for r in receipts)
              for status in sorted({r["status"] for r in receipts})}
    complete = (not aborted_after_control_failure and len(receipts) == len(plan)
                and not any(r["status"].startswith("INFRASTRUCTURE") for r in receipts))
    controls = [r for r in receipts if r.get("role") == "positive_control"]
    summary = {"schema": "k58-joining3s-results/v1", "records": len(receipts),
               "scheduled_records": len(plan), "candidate_queries": len(candidate_receipts),
               "control_queries": len(controls), "status_counts": counts,
               "cohort_complete": complete, "aborted_after_control_failure": aborted_after_control_failure,
               "search_budget_seconds_per_query": SEARCH_SECONDS,
               "solve_watchdog_seconds": SOLVE_WATCHDOG_SECONDS,
               "watchdog_poll_seconds": WATCHDOG_POLL_SECONDS,
               "maximum_process_cutoff_seconds": PROCESS_CUTOFF_SECONDS,
               "sum_search_seconds": sum(r.get("search_s", 0.0) for r in receipts),
               "sum_candidate_search_seconds": sum(r.get("search_s", 0.0) for r in candidate_receipts),
               "sum_proof_bytes": sum(r.get("proof_bytes", 0) for r in receipts),
               "unique_representatives": len(candidates),
               "closed_representatives": sum(c["representative_status"] == "CLOSED" for c in closures),
               "whole_original_rows_closed": 0, "control_denominator_excluded": True,
               "no_speedup_claim": True, "receipts": receipts, "closures": closures,
               "closure_boundary": "Sample-level representative results only. No wall row or Ramsey bound change is implied."}
    write_json(out / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    campaign, design, out = args.campaign.resolve(), args.design.resolve(), args.out.resolve()
    if out.exists():
        parser.error("choose a new output path")
    if not (campaign / "tools/drat-trim").is_file() or not (design / "candidates.tsv").is_file():
        parser.error("invalid campaign or frozen design")
    out.mkdir(parents=True)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(campaign))
    import common  # Installs the campaign's engine and frozen-module paths.
    preparation = prepare(campaign, design, out)
    if args.prepare_only:
        print(json.dumps({"prepared": preparation["candidate_pairs"], "solver_calls": 0}, indent=2))
        return
    started = time.monotonic()
    summary = execute(campaign, out, preparation)
    summary["coordinator_seconds"] = time.monotonic() - started
    write_json(out / "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("records", "status_counts", "cohort_complete",
          "sum_search_seconds", "closed_representatives", "whole_original_rows_closed")}, indent=2))


if __name__ == "__main__":
    main()
