"""Persistent plans, bounded conquer jobs and independent replay of leaf certificates."""
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from contextlib import contextmanager
import fcntl
import json
import os
from itertools import islice
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from cubing import cover, make_tree, propagator
from pentagons import compile_cas, marked_variables
from problem import (PHYSICAL, ROOT, check_model, digest, extend_dimacs, file_hash,
                     json_bytes, lookup, read_dimacs, require, row_formula)
from cover_evidence import atomic_json

SCHEMA = 1


@contextmanager
def lock(path):
    with path.open("a+b") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def store_plan(out, base, origin, row, cas, depth, lookahead):
    out.mkdir(parents=True, exist_ok=True)
    options = dict(schema=SCHEMA, origin=origin, parent_sha256=digest(base),
                   cas=cas, depth=depth, lookahead=lookahead)
    with lock(out / ".prepare.lock"):
        path = out / "plan.json"
        if path.exists():
            plan = json.loads(path.read_bytes())
            require(all(plan.get(k) == v for k, v in options.items()),
                    "existing plan has different inputs or split settings; use a new run directory")
            return plan
        require(not (out / "leaves").exists(), "missing plan beside existing receipts")
        pending = out / ".preparing.json"
        if pending.exists():
            require(json.loads(pending.read_bytes()) == options,
                    "an interrupted preparation used different inputs in this directory")
        else:
            require(not any((out / n).exists() for n in ("parent.cnf", "working.cnf", "cas.drat")),
                    "the output directory already contains a formula or proof")
            atomic_json(pending, options)
        nv, clauses = read_dimacs(base)
        limit = min(PHYSICAL, nv) if row else nv
        cuts, prefix, tables = [], b"", []
        lookahead_solver, fixed, feasible = propagator(clauses)
        with lookahead_solver as solver:
            if row and cas == "pentagon" and feasible:
                cuts, prefix, tables = compile_cas(row, fixed)
                for clause in cuts:
                    solver.add_clause(clause)
            special = marked_variables(row) if row else []
            splits = make_tree(clauses, limit, special, tables, depth, lookahead,
                               solver, fixed, feasible) if depth else {}
        leaves = cover(splits, limit, depth)
        work = out / "working.cnf"
        # Publish the plan last. An interrupted preparation can regenerate its inputs.
        (out / "parent.cnf").write_bytes(base)
        extend_dimacs(out / "parent.cnf", work, cuts)
        (out / "cas.drat").write_bytes(prefix)
        plan = dict(options, variables=nv, clauses=len(clauses), split_limit=limit,
                    tables=len(tables), cuts=len(cuts), cas_proof_sha256=digest(prefix),
                    working_sha256=file_hash(work), splits=splits, leaf_count=len(leaves))
        atomic_json(path, plan)
        pending.unlink(missing_ok=True)
        return plan


def inspect(out, for_search=False, expected=None):
    plan = json.loads((out / "plan.json").read_bytes())
    require(plan["schema"] == SCHEMA, "unknown plan format")
    parent = (out / "parent.cnf").read_bytes()
    require(digest(parent) == plan["parent_sha256"], "changed parent formula")
    if expected is not None:
        require(plan["parent_sha256"] == expected, "unexpected parent SHA-256")
    origin = plan["origin"]
    if origin["kind"] == "wall":
        row = lookup(origin["id"])
        require(row["id"] == origin["id"] and parent == row_formula(row, origin["tier"]),
                "stored CNF differs from the regenerated frozen row")
    elif origin["kind"] == "wall-color":
        from color_pivot import build, core_digest
        row = lookup(origin["id"])
        artifacts = build(row, origin["tier"])
        require(core_digest(artifacts) == origin["color_receipt_sha256"],
                "color receipt binding mismatch")
        require(digest(artifacts["formulas"]["original"]) == origin["original_parent_sha256"],
                "original-parent hash changed under a color run")
        require(origin["variant"] in ("counter", "escape", "color")
                and parent == artifacts["formulas"][origin["variant"]],
                "stored CNF differs from its regenerated color variant")
        require((out / "color-receipt.json").is_file()
                and digest((out / "color-receipt.json").read_bytes()) == origin["color_receipt_sha256"],
                "missing or changed color receipt")
        check = json.loads((out / "color-check.json").read_bytes())
        require(check.get("status") == "PASS_RUP_DERIVATION", "augmentation lacks a native derivation check")
    elif origin["kind"] in ("square", "wall-color-square"):
        from square_merge import apply as merge_square, verify_saved as verify_saved_square
        from color_pivot import build, core_digest
        row = lookup(origin["id"])
        verify_saved_square(out, origin["square_receipt_sha256"])
        require(origin["tier"] == "first", "square-spoke merging requires first tier")
        if origin["kind"] == "square":
            base = row_formula(row, "first")
            require(base == row_formula(row, origin["tier"]),
                    "square row changed the ordinary first-tier parent")
        else:
            require(origin["variant"] in ("counter", "escape", "color"), "unknown colour-square variant")
            artifacts = build(row, "first")
            base = artifacts["formulas"][origin["variant"]]
            require(artifacts["formulas"]["original"] == row_formula(row, "first"),
                    "colour-square merge changed the ordinary parent")
            require(digest(artifacts["formulas"]["original"]) == origin["original_parent_sha256"],
                    "colour-square merge lost its ordinary-parent hash")
            require(core_digest(artifacts) == origin["color_receipt_sha256"],
                    "saved colour-square receipt mismatch")
            require(digest((out / "color-receipt.json").read_bytes()) == origin["color_receipt_sha256"],
                    "missing or changed colour-square receipt")
            check = json.loads((out / "color-check.json").read_bytes())
            require(check.get("status") == "PASS_RUP_DERIVATION",
                    "colour-square augmentation lacks a native derivation check")
        expected, metadata = merge_square(base, row, "first")
        require(parent == expected, "stored CNF is not the exact validated colour-square composition")
        require(digest(json_bytes(metadata)) == origin["square_receipt_sha256"],
                "stored square reconstruction differs from its batch or original tier binding")
        require((out / "square-receipt.json").read_bytes() == json_bytes(metadata),
                "stored square receipt content differs from its checked reconstruction")
    else:
        require(origin["kind"] == "dimacs", "unknown formula origin")
    nv, clauses = read_dimacs(parent)
    require(plan["variables"] == nv and plan["clauses"] == len(clauses), "parent size mismatch")
    limit = min(PHYSICAL, nv) if origin["kind"] in ("wall", "wall-color", "square", "wall-color-square") else nv
    require(plan["split_limit"] == limit and type(plan["depth"]) is int and plan["depth"] >= 0,
            "invalid tree parameters")
    leaves = cover(plan["splits"], limit, plan["depth"])
    require(len(leaves) == plan["leaf_count"], "leaf count mismatch")
    require(file_hash(out / "cas.drat") == plan["cas_proof_sha256"], "changed CAS proof")
    if for_search:
        require(file_hash(out / "working.cnf") == plan["working_sha256"], "changed search CNF")
    return plan, digest(json_bytes(plan)), leaves, clauses


def replay(out, temp, cube, proof, checker, seconds):
    formula = temp / "check.cnf"
    extend_dimacs(out / "parent.cnf", formula, [(v,) for v in cube])
    trace = temp / "joined.drat"
    with trace.open("wb") as joined:
        for path in (out / "cas.drat", proof):
            with path.open("rb") as stream:
                shutil.copyfileobj(stream, joined, 1 << 20)
    return check_trace(formula, trace, checker, seconds)


def check_trace(formula, trace, checker, seconds, *options):
    cmd = [str(checker), str(formula), str(trace), "-i", "-t", str(seconds), *options]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=seconds + 2)
    except subprocess.TimeoutExpired:
        return False, "checker wall-time limit"
    log = (p.stdout + p.stderr).decode(errors="replace")
    messages = log.splitlines()
    passed = p.returncode == 0 and "s VERIFIED" in messages
    # The bundled drat-trim prints VERIFIED but exits 1 if it parses an
    # explicit empty input clause. Check that syntactic contradiction directly.
    if p.returncode == 1 and "c trivial UNSAT" in messages and "s VERIFIED" in messages:
        with formula.open("rb") as stream:
            passed = any(line.strip() == b"0" for line in stream)
    return passed, log[-1600:]


def probe(out, temp, cube, args, traced):
    command = [sys.executable, str(ROOT / "cadical_leaf.py"), str(out / "working.cnf"),
               str(temp), str(args.conflicts), "trace" if traced else "search", *map(str, cube)]
    try:
        run = subprocess.run(command, capture_output=True, timeout=args.seconds)
    except subprocess.TimeoutExpired:
        return {"status": "OPEN", "reason": "wall-time limit"}
    if run.returncode:
        raise RuntimeError(f"CaDiCaL worker exited {run.returncode}: "
                           + (run.stderr or run.stdout)[-1200:].decode(errors="replace"))
    result = json.loads(run.stdout)
    require(result["status"] in ("SAT", "UNSAT", "OPEN"), "invalid CaDiCaL result")
    if result["status"] == "OPEN":
        result["reason"] = "conflict limit"
    return result


def check_binding(receipt, plan_id, node, cube):
    require(receipt["plan_sha256"] == plan_id and receipt["node"] == node
            and receipt["cube"] == list(cube), f"receipt belongs to a different cube at {node}")


def validate_artifact(folder, receipt):
    status = receipt["status"]
    require(status in ("CHECKED_UNSAT", "CHECKED_SAT"), "unexpected evidence status")
    path = folder / ("leaf.drat" if status == "CHECKED_UNSAT" else "model.json")
    require(file_hash(path) == receipt["artifact_sha256"], f"damaged evidence at {folder.name}")
    return path


def conquer_one(out, item, plan_id, nv, clauses, checker, args):
    node, cube = item
    folder = out / "leaves" / node
    folder.mkdir(parents=True, exist_ok=True)
    budget = dict(seconds=args.seconds, conflicts=args.conflicts, proof=args.proof,
                  check_seconds=args.check_seconds)
    with lock(folder / ".lock"):
        receipt_path = folder / "receipt.json"
        if receipt_path.exists():
            rec = json.loads(receipt_path.read_bytes())
            check_binding(rec, plan_id, node, cube)
            if rec["status"] in ("CHECKED_UNSAT", "CHECKED_SAT"):
                validate_artifact(folder, rec)
                return rec["status"]
            if rec["status"] == "OPEN" and rec["budget"] == budget and not args.again:
                return "OPEN"
        started = monotonic()
        rec = dict(plan_sha256=plan_id, node=node, cube=list(cube), budget=budget,
                   solver="CaDiCaL 1.9.5 / python-sat 1.9.dev22")
        with TemporaryDirectory(prefix="attempt-", dir=folder) as name:
            temp = Path(name)
            result = probe(out, temp, cube, args, args.proof == "eager")
            if result["status"] == "UNSAT" and args.proof == "deferred":
                rec["search_conflicts"] = result["conflicts_used"]
                result = probe(out, temp, cube, args, True)
                if result["status"] == "OPEN":
                    result["status"] = "PROOF_PENDING"
                require(result["status"] != "SAT", "solver contradicted its UNSAT search")
            rec.update(result)
            if result["status"] == "SAT":
                artifact = temp / "model.json"
                check_model(clauses, cube, json.loads(artifact.read_bytes()), nv)
                rec["status"] = "CHECKED_SAT"
            elif result["status"] == "UNSAT":
                artifact = temp / "leaf.drat"
                passed, log = replay(out, temp, cube, artifact, checker, args.check_seconds)
                rec["status"] = "CHECKED_UNSAT" if passed else "CHECK_FAILED"
                rec["checker_log"] = log
                rec["checker_sha256"] = args.checker_sha256
            if rec["status"] in ("CHECKED_UNSAT", "CHECKED_SAT", "CHECK_FAILED"):
                rec["artifact_sha256"] = file_hash(artifact)
                artifact.replace(folder / artifact.name)
        rec["elapsed_s"] = round(monotonic() - started, 3)
        atomic_json(receipt_path, rec)
        return rec["status"]


def audit_one(out, item, plan_id, nv, clauses, checker, seconds):
    node, cube = item
    folder = out / "leaves" / node
    path = folder / "receipt.json"
    if not path.exists():
        return "MISSING"
    rec = json.loads(path.read_bytes())
    check_binding(rec, plan_id, node, cube)
    status = rec["status"]
    if status in ("OPEN", "PROOF_PENDING", "CHECK_FAILED"):
        return status
    artifact = validate_artifact(folder, rec)
    if status == "CHECKED_SAT":
        check_model(clauses, cube, json.loads(artifact.read_bytes()), nv)
        return "VERIFIED_SAT"
    with TemporaryDirectory(prefix="wallcc-replay-") as temp:
        passed, log = replay(out, Path(temp), cube, artifact, checker, seconds)
    require(passed, f"invalid proof at {node}: {log}")
    return "VERIFIED_UNSAT"


def execute(out, args, verify):
    plan, plan_id, leaves, clauses = inspect(out, not verify, getattr(args, "expect_sha256", None))
    checker = args.checker.resolve()
    require(checker.is_file() and os.access(checker, os.X_OK),
            f"missing executable checker {checker}; run setup.sh")
    args.checker_sha256 = file_hash(checker)
    color_check = None
    if verify and plan["origin"]["kind"] in ("wall-color", "wall-color-square"):
        from color_pivot import verify_saved
        color_check = verify_saved(out, checker, args.check_seconds)
    if verify:
        def task(item):
            return audit_one(out, item, plan_id, plan["variables"], clauses, checker, args.check_seconds)
    else:
        leaves = [item for i, item in enumerate(leaves) if i % args.shards == args.shard]
        def task(item):
            return conquer_one(out, item, plan_id, plan["variables"], clauses, checker, args)
    # Keep only one outstanding job per slot, including on interruption.
    stream, counts = iter(leaves), Counter()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        active = {pool.submit(task, item) for item in islice(stream, args.jobs)}
        while active:
            done, active = wait(active, return_when=FIRST_COMPLETED)
            counts.update(future.result() for future in done)
            active.update(pool.submit(task, item) for item in islice(stream, len(done)))
    if verify:
        if counts["VERIFIED_SAT"]:
            status = "VERIFIED_SAT"
        elif counts["VERIFIED_UNSAT"] == plan["leaf_count"]:
            status = "VERIFIED_UNSAT"
        else:
            status = "OPEN"
    else:
        if counts["CHECKED_SAT"]:
            status = "MODEL_READY"
        elif counts["CHECKED_UNSAT"] == plan["leaf_count"]:
            status = "COVER_READY"
        else:
            status = "OPEN"
    result = dict(status=status, origin=plan["origin"], parent_sha256=plan["parent_sha256"],
                  leaves=plan["leaf_count"], processed=len(leaves), counts=dict(counts))
    if color_check is not None:
        result["color_derivation"] = {key: color_check[key] for key in
                                      ("status", "checker_sha256", "original_parent_sha256",
                                       "selected_parent_sha256")}
        result["closure_scope"] = ("square_aux_extended_with_native_colour_derivation_and_local_K15_rules"
                                    if plan["origin"]["kind"] == "wall-color-square"
                                    else "aux_extended_parent_with_native_original_plus_counter_derivation")
    return result
