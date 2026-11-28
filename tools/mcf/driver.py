#!/usr/bin/env python3
"""Opt-in arm-MCF commands; never imported by stock run/finalise.

Main queries are exact ordinary parent+cube and raw maximal-colour parent+cube.
They are semantic-row relaxations. A verified augmented refutation is not a
physical-row closure and is never admitted to stock finalise by this program.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from normal_form import (McfError, assert_disjoint_and_allocated, augment_maximal,
                         configurable_variables, digest, file_digest, freeze_cube,
                         fresh_variables, parse_cube, read_dimacs, require)

SCHEMA = "k58-optin-configurable-mcf/v1"
TARGET_ROW = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
TARGET_PARENT = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
TARGET_CUBE = "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8"
TARGET_WORKING = "39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38"
TARGET_CAS = "dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3"
TARGET_ARM_CNF = "fface1b819e26261736cb516be9063e7be2b1be120253875947a4400d4ac912a"
TARGET_CUBE_LITERALS = [-1413, 1014]
STOCK_FILES = ("problem.py", "gluing.py", "dense.py")


def json_write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def public_receipt(value):
    return {key: item for key, item in value.items() if key not in ("rules",)}


def load_stock(package):
    package = Path(package).resolve()
    root = package / "color-resolved-wallcc"
    require(root.is_dir(), f"not an unpacked k58-massive-solver directory: {package}")
    sys.path.insert(0, str(root / "frozen"))
    sys.path.insert(0, str(root))
    import problem
    import gluing
    import dense
    row_resolved = root
    return package, row_resolved, problem, gluing, dense


def family_of(row, Family):
    fields = dict(row["family"])
    for key in ("profile", "root_kinds"):
        fields[key] = tuple(fields[key])
    return Family(**fields)


def inspect_baseline(run, package, row_id, tier):
    run = Path(run).resolve()
    package, stock, problem, gluing, dense = load_stock(package)
    for name in ("plan.json", "parent.cnf", "working.cnf", "cas.drat"):
        require((run / name).is_file(), f"baseline plan is missing {name}")
    plan = json.loads((run / "plan.json").read_text())
    require(plan.get("schema") == 1, "unknown ordinary plan schema")
    origin = plan.get("origin", {})
    require(origin.get("kind") == "wall" and origin.get("id") == row_id and
            origin.get("tier") == tier, "plan origin differs from exact retained row/tier")
    row = problem.lookup(row_id)
    require(row["id"] == row_id, "retained row identifier is not exact")
    parent = (run / "parent.cnf").read_bytes()
    working = (run / "working.cnf").read_bytes()
    cas = (run / "cas.drat").read_bytes()
    require(digest(parent) == plan.get("parent_sha256"), "baseline parent hash differs from plan")
    require(digest(working) == plan.get("working_sha256"), "baseline working hash differs from plan")
    require(digest(cas) == plan.get("cas_proof_sha256"), "baseline CAS prefix differs from plan")
    require(parent == problem.row_formula(row, tier),
            "baseline parent differs from regenerated frozen-tier row formula")
    if row_id == TARGET_ROW:
        require(tier == "first" and digest(parent) == TARGET_PARENT and
                digest(working) == TARGET_WORKING and digest(cas) == TARGET_CAS,
                "retained-row parent, working CNF, or CAS prefix does not match its pinned identity")
    nv, parent_clauses, _ = read_dimacs(parent)
    require(nv == plan.get("variables") and len(parent_clauses) == plan.get("clauses"),
            "plan dimensions differ from baseline parent")
    wnv, working_clauses, working_body = read_dimacs(working)
    require(wnv == nv and working_clauses[:len(parent_clauses)] == parent_clauses,
            "working CNF does not retain ordinary parent clause sequence")
    cuts = working_clauses[len(parent_clauses):]
    require(len(cuts) == plan.get("cuts"), "working cuts differ from plan")
    require(tuple(plan.get("arm_pair", ())) == (16, 16, 14, 11, 1) if row_id == TARGET_ROW else True,
            "target plan has a different arm/profile tuple")
    splits = plan.get("splits", {})
    require(splits.get("r") == 1413 and splits.get("r0") == 2206 and splits.get("r1") == 1426
            if row_id == TARGET_ROW else True, "target plan split roots differ")
    return {
        "run": run, "package": package, "stock": stock, "problem": problem,
        "gluing": gluing, "dense": dense, "plan": plan, "row": row,
        "parent": parent, "working": working, "cas": cas, "cuts": cuts,
    }


def build(baseline, arms, colour, cube):
    parent, row = baseline["parent"], baseline["row"]
    problem, gluing, dense = baseline["problem"], baseline["gluing"], baseline["dense"]
    family = family_of(row, gluing.Family)
    lit, host = gluing.host(58)
    fixed = gluing.units(family, row["placement"])
    extra = dense.marked_threshold(family, fixed, row["charge"], tables=True,
                                   total_critical=True, full_root=False)
    original = problem.row_formula(row, baseline["plan"]["origin"]["tier"])
    maximum = max(4 * 58 * 57 // 2,
                  max((abs(x) for c in fixed + extra for x in c), default=0))
    reconstructed = (f"p cnf {maximum} {len(host) + len(fixed) + len(extra)}\n".encode()
                     + problem.encode_clauses(host + fixed + extra))
    require(reconstructed == original == parent,
            "stock host/unit/threshold reconstruction differs from exact parent")
    fixed_edges = {(abs(c[0]) - 1) // 4 for c in fixed if len(c) == 1}
    groups, start = [], 1
    for size in family.profile:
        groups.append(tuple(range(start, start + size)))
        start += size
    configurable = []
    for arm in arms:
        require(arm != colour, "normalisation colour must differ from selected arm")
        for u, v in itertools.combinations(groups[arm], 2):
            edge = (lit(u, v, 0) - 1) // 4
            if edge not in fixed_edges:
                configurable.append((arm, u, v))
    require(configurable, "selected arms have no configurable edges")
    require(len({(u, v) for _, u, v in configurable}) == len(configurable),
            "duplicate configurable edge")
    augmented, rules, additions = augment_maximal(parent, configurable, colour)
    # Assert against the actual non-host clauses, not merely a nominal suffix.
    assert_disjoint_and_allocated(parent, rules, fixed + extra, cube, augmented)
    changing = configurable_variables(rules)
    require(not any(abs(x) in changing for clause in fixed + extra for x in clause),
            "configurable variables occur in non-host suffix")
    parent_cube = freeze_cube(parent, cube)
    augmented_cube = freeze_cube(augmented, cube)
    # The certification search adds the already-proved working cuts before MCF;
    # replay still targets the exact parent/arm3+cube objects above.
    # Use the same public DIMACS extension routine, avoiding hand-built output.
    from normal_form import extend_body
    working_augmented = extend_body(baseline["working"], additions,
                                    maximum + len(fresh_variables(rules)))
    working_cube = freeze_cube(baseline["working"], cube)
    working_augmented_cube = freeze_cube(working_augmented, cube)
    normal_form = {
        "schema": "k58-configurable-mcf-normal-form/v2",
        "row": row["id"], "tier": baseline["plan"]["origin"]["tier"],
        "profile": list(family.profile), "charge": row["charge"],
        "arms": list(arms), "colour": colour, "cube": list(cube),
        "ordinary_parent_sha256": digest(parent),
        "parent_cube_sha256": digest(parent_cube),
        "augmented_parent_sha256": digest(augmented),
        "augmented_cube_sha256": digest(augmented_cube),
        "original_variables": maximum, "augmented_variables": maximum + len(fresh_variables(rules)),
        "original_clauses": len(host) + len(fixed) + len(extra),
        "host_clauses": len(host), "nonhost_clauses": len(fixed) + len(extra),
        "working_cuts": len(baseline["cuts"]),
        "configurable_edges": len(rules), "added_clauses": len(additions),
        "fresh_witnesses": len(fresh_variables(rules)),
        "fresh_range": [maximum + 1, maximum + len(fresh_variables(rules))],
        "suffix_disjoint": True, "cube_disjoint": True,
        "parent_body_prefix_byte_exact": True,
        "reduction": ("existence-preserving sequential recolouring; NOT a DRAT implication; "
                      "each new witness is its defining conjunction"),
        "physical_closure": False,
        "remaining_bridge_obligations": [
            "physical realization itself; hbase/hvars are formalized in PhysicalBridge",
            "candidate criticality and adjusted/112-support guard-set totals",
            "whole-parent ChainReady and semantic assembly",
            "other leaves and exhaustive cover before any row-level conclusion",
        ],
        "rules": rules,
    }
    return {
        "parent_cube": parent_cube, "augmented": augmented,
        "augmented_cube": augmented_cube, "working_augmented": working_augmented,
        "working_cube": working_cube, "working_augmented_cube": working_augmented_cube,
        "normal_form": normal_form,
    }


def prepare(args):
    row_id = TARGET_ROW if args.row == "target" else args.row
    require(row_id == TARGET_ROW,
            "this opt-in variant deliberately supports only the retained hard row")
    require(len(row_id) == 64 and all(c in "0123456789abcdef" for c in row_id),
            "--row must be the exact full lowercase 64-hex row identifier or 'target'")
    arms = []
    for piece in args.arms.split(","):
        try:
            arm = int(piece)
        except ValueError as exc:
            raise McfError("arms must be comma-separated integers") from exc
        require(0 <= arm < 4 and arm not in arms, "arms must be unique values in 0..3")
        arms.append(arm)
    require(arms, "at least one arm is required")
    require(0 <= args.colour < 4, "colour must be in 0..3")
    baseline = inspect_baseline(args.baseline_run, args.package, row_id, args.tier)
    if args.expect_working_sha256:
        require(digest(baseline["working"]) == args.expect_working_sha256,
                "ordinary working CNF SHA does not match explicit expectation")
    if args.expect_cas_sha256:
        require(digest(baseline["cas"]) == args.expect_cas_sha256,
                "CAS prefix SHA does not match explicit expectation")
    require(arms == [3] and args.colour == 0,
            "this variant is exactly the checked arm 3, colour 0 normal form")
    cube = parse_cube(args.cube, baseline["plan"]["variables"])
    require(cube == TARGET_CUBE_LITERALS,
            "retained cube must be -1413,+1014 in this order")
    # Build the ordinary baseline first and pin every retained artifact before MCF.
    parent_cube = freeze_cube(baseline["parent"], cube)
    require(digest(baseline["parent"]) == TARGET_PARENT and
            digest(baseline["working"]) == TARGET_WORKING and
            digest(baseline["cas"]) == TARGET_CAS and
            digest(parent_cube) == TARGET_CUBE,
            "ordinary parent/working/CAS/parent+cube identity mismatch")
    if args.expect_parent_sha256:
        require(digest(baseline["parent"]) == args.expect_parent_sha256,
                "ordinary parent SHA does not match explicit expectation")
    if args.expect_parent_cube_sha256:
        require(digest(parent_cube) == args.expect_parent_cube_sha256,
                "ordinary parent+cube SHA does not match explicit expectation")
    built = build(baseline, arms, args.colour, cube)
    require(built["parent_cube"] == parent_cube, "builder changed ordinary baseline")
    require(digest(built["augmented_cube"]) == TARGET_ARM_CNF,
            "arm3+cube differs from the retained exact artifact")
    normal = built["normal_form"]
    if args.expect_augmented_parent_sha256:
        require(normal["augmented_parent_sha256"] == args.expect_augmented_parent_sha256,
                "augmented parent SHA does not match explicit expectation")
    if args.expect_augmented_cube_sha256:
        require(normal["augmented_cube_sha256"] == args.expect_augmented_cube_sha256,
                "augmented parent+cube SHA does not match explicit expectation")
    if args.expect_edges is not None:
        require(normal["configurable_edges"] == args.expect_edges,
                "configurable edge count differs from explicit expectation")
    queries = {
        "queries/parent-cube.cnf": built["parent_cube"],
        "queries/raw-arm-parent.cnf": built["augmented"],
        "queries/raw-arm-cube.cnf": built["augmented_cube"],
        "certification/working-cube.cnf": built["working_cube"],
        "certification/raw-arm-working.cnf": built["working_augmented"],
        "certification/raw-arm-working-cube.cnf": built["working_augmented_cube"],
        "baseline/plan.json": (baseline["run"] / "plan.json").read_bytes(),
        "baseline/cas.drat": baseline["cas"],
        "baseline/parent.cnf": baseline["parent"],
        "baseline/working.cnf": baseline["working"],
    }
    receipt = {
        "schema": SCHEMA, "feature": "explicit opt-in only; stock run/finalise unchanged",
        "row": row_id, "tier": args.tier, "cube": cube, "arms": arms, "colour": args.colour,
        "baseline_run": str(baseline["run"]), "package": str(baseline["package"]),
        "ordinary_parent_sha256": digest(baseline["parent"]),
        "ordinary_working_sha256": digest(baseline["working"]),
        "cas_prefix_sha256": digest(baseline["cas"]),
        "ordinary_parent_cube_sha256": digest(parent_cube),
        "normal_form_sha256_payload": digest(json.dumps(normal, sort_keys=True).encode()),
        "normal_form": public_receipt(normal),
        "main_comparison": {
            "parent": "queries/parent-cube.cnf", "raw-arm": "queries/raw-arm-cube.cnf",
            "body_and_cube_unchanged_except_mcf_suffix": True,
        },
        "certification_comparison": {
            "parent": "certification/working-cube.cnf",
            "raw-arm": "certification/raw-arm-working-cube.cnf",
            "proof_targets": {
                "parent": "queries/parent-cube.cnf", "raw-arm": "queries/raw-arm-cube.cnf"},
            "cas_prefix": "baseline/cas.drat",
        },
        "files": {name: {"sha256": digest(data), "bytes": len(data)}
                  for name, data in queries.items()},
        "physical_closure": False,
    }
    summary = public_receipt(receipt)
    if args.dry_run:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return summary
    out = Path(args.out)
    require(out != Path("") and not out.exists(), f"output already exists: {out}")
    temporary = out.with_name(out.name + ".building")
    require(not temporary.exists(), f"temporary output already exists: {temporary}")
    try:
        for name, data in queries.items():
            destination = temporary / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        json_write(temporary / "normal-form.json", normal)
        provenance = {
            "schema": "k58-mcf-source-provenance/v1",
            "builder_sources": {str(path.relative_to(HERE.parent)): file_digest(path)
                                for path in (HERE / "driver.py", HERE / "normal_form.py",
                                             HERE / "proof.py", HERE / "strict_rup.py",
                                             HERE / "cadical_worker.py")},
            "stock_sources": {
                "color-resolved-wallcc/problem.py": file_digest(baseline["stock"] / "problem.py"),
                "color-resolved-wallcc/frozen/gluing.py": file_digest(baseline["stock"] / "frozen/gluing.py"),
                "color-resolved-wallcc/frozen/dense.py": file_digest(baseline["stock"] / "frozen/dense.py"),
            },
            "baseline_run": str(baseline["run"]),
            "command": sys.argv,
        }
        json_write(temporary / "provenance.json", provenance)
        json_write(temporary / "receipt.json", receipt)
        temporary.rename(out)
    except BaseException:
        # Evidence is not silently replaced. Keep a failed build for diagnosis.
        raise
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def load_prepared(path):
    root = Path(path).resolve()
    receipt = json.loads((root / "receipt.json").read_text())
    require(receipt.get("schema") == SCHEMA, "unknown prepared MCF schema")
    normal = json.loads((root / "normal-form.json").read_text())
    require(digest(json.dumps(normal, sort_keys=True).encode()) == receipt["normal_form_sha256_payload"],
            "normal-form receipt payload changed")
    for name, record in receipt["files"].items():
        data = (root / name).read_bytes()
        require(len(data) == record["bytes"] and digest(data) == record["sha256"],
                f"prepared file hash/size mismatch: {name}")
    # Self-consistent receipt hashes are not a semantic certificate. Regenerate
    # the pinned parent and every auxiliary gadget from the shipped frozen stock
    # encoder, then compare all queries bytes. This rejects coordinated query,
    # rule, allocation, and receipt tampering before any search is launched.
    cube = receipt["cube"]
    require(receipt["row"] == TARGET_ROW and receipt["tier"] == "first" and
            cube == TARGET_CUBE_LITERALS,
            "prepared artifact is not the exact retained row/cube")
    require(normal["arms"] == [3] and normal["colour"] == 0,
            "prepared artifact is not the checked arm 3, colour 0 normal form")
    baseline = inspect_baseline(root / "baseline", HERE.parent,
                                receipt["row"], receipt["tier"])
    rebuilt = build(baseline, normal["arms"], normal["colour"], cube)
    require(normal == rebuilt["normal_form"],
            "normal-form rules/counts differ from pristine regenerated gadgets")
    expected = {
        "queries/parent-cube.cnf": rebuilt["parent_cube"],
        "queries/raw-arm-parent.cnf": rebuilt["augmented"],
        "queries/raw-arm-cube.cnf": rebuilt["augmented_cube"],
        "certification/working-cube.cnf": rebuilt["working_cube"],
        "certification/raw-arm-working.cnf": rebuilt["working_augmented"],
        "certification/raw-arm-working-cube.cnf": rebuilt["working_augmented_cube"],
    }
    for name, data in expected.items():
        require((root / name).read_bytes() == data,
                f"prepared artifact differs from pristine regeneration: {name}")
    require(receipt["main_comparison"] == {
        "parent": "queries/parent-cube.cnf", "raw-arm": "queries/raw-arm-cube.cnf",
        "body_and_cube_unchanged_except_mcf_suffix": True},
        "prepared main-comparison paths or identity declaration changed")
    require(receipt["certification_comparison"] == {
        "parent": "certification/working-cube.cnf",
        "raw-arm": "certification/raw-arm-working-cube.cnf",
        "proof_targets": {"parent": "queries/parent-cube.cnf",
                          "raw-arm": "queries/raw-arm-cube.cnf"},
        "cas_prefix": "baseline/cas.drat"},
        "prepared certification/proof targets changed")
    require(digest(rebuilt["augmented_cube"]) == TARGET_ARM_CNF,
            "regenerated arm3+cube differs from its pinned SHA-256")
    return root, receipt, normal


def invoke_worker(query, folder, conflicts):
    require(not folder.exists(), f"solver job output already exists: {folder}")
    command = [sys.executable, str(HERE / "cadical_worker.py"), str(query), str(folder), str(conflicts)]
    started = time.monotonic()
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if run.returncode:
        raise McfError("CaDiCaL worker failed without a result: " +
                       (run.stderr or run.stdout)[-1600:].decode(errors="replace"))
    receipt = json.loads((folder / "solver.json").read_text())
    receipt["process_wall_seconds"] = time.monotonic() - started
    receipt["query_sha256"] = file_digest(query)
    receipt["worker_command"] = command
    return receipt


def finish_solver_job(prepared, receipt, label, query, search_receipt, folder, checker, check_seconds,
                      conflicts):
    _, clauses, _ = read_dimacs(query.read_bytes())
    result = dict(search_receipt)
    status = search_receipt["status"]
    result.update({"label": label, "query": str(query), "physical_closure": False})
    if status == "OPEN":
        require(not (folder / "leaf.drat").exists() and not (folder / "model.json").exists(),
                "OPEN solver job retained an incomplete proof/model artifact")
        result["proof_artifact"] = None
        result["conclusion"] = "OPEN at exact conflict cap; no SAT/UNSAT claim"
    elif status == "SAT":
        model = json.loads((folder / "model.json").read_text())
        from proof import check_model
        projection = check_model(clauses, model)
        result["status"] = "CHECKED_SAT"
        result["model_sha256"] = file_digest(folder / "model.json")
        result["model_literals_checked"] = len(projection)
        result["conclusion"] = "CNF model only; not a physical-row model"
    elif status == "UNSAT":
        require((folder / "leaf.drat").is_file(), "UNSAT status has no retained proof")
        from strict_rup import strict_replay
        raw = folder / "leaf.drat"
        result["strict_replay"] = strict_replay(
            query, None, raw, folder / "strict-replay", file_digest(query),
            Path(checker), check_seconds)
        result["normalization"] = result["strict_replay"]["normalization"]
        result["status"] = "CNF_QUERY_UNSAT_VERIFIED" if result["strict_replay"]["strict_accepted"] else "CHECK_FAILED"
        result["conclusion"] = ("verified exact augmented CNF UNSAT only; normal-form and physical "
                                "bridge obligations remain" if label == "raw-arm" else
                                "verified exact ordinary parent+cube CNF UNSAT; physical bridge and cover remain")
    else:
        raise McfError(f"unknown worker status {status}")
    json_write(folder / "result.json", result)
    return result


def plan_certificate(prepared, receipt, label, checker, check_seconds, conflicts, parent_folder):
    """If exact query was UNSAT, also retain ordinary working+CAS proof route."""
    query = prepared / receipt["certification_comparison"][label]
    target = prepared / receipt["certification_comparison"]["proof_targets"][label]
    folder = parent_folder / "plan-certificate"
    search = invoke_worker(query, folder, conflicts)
    out = {"search_query": str(query), "search_query_sha256": file_digest(query),
           "proof_target_sha256": file_digest(target), "search": search}
    if search["status"] == "OPEN":
        require(not (folder / "leaf.drat").exists(), "plan OPEN retained proof")
        out["status"] = "PROOF_PENDING"
        out["conclusion"] = "exact query proof retained; working-plan replay not established"
    elif search["status"] == "UNSAT":
        from strict_rup import strict_replay
        joined = folder / "cas-plus-leaf.drat"
        with joined.open("wb") as stream:
            for name in (prepared / receipt["certification_comparison"]["cas_prefix"],
                         folder / "leaf.drat"):
                with name.open("rb") as source:
                    shutil.copyfileobj(source, stream, 1 << 20)
        require(digest(joined.read_bytes()) == digest(
            (prepared / receipt["certification_comparison"]["cas_prefix"]).read_bytes() +
            (folder / "leaf.drat").read_bytes()), "CAS+leaf concatenation differs")
        out["strict_replay"] = strict_replay(
            target, prepared / receipt["certification_comparison"]["cas_prefix"],
            folder / "leaf.drat", folder / "strict-replay", file_digest(target),
            Path(checker), check_seconds)
        out["normalization"] = out["strict_replay"]["normalization"]
        out["status"] = "PLAN_CNF_UNSAT_VERIFIED" if out["strict_replay"]["strict_accepted"] else "CHECK_FAILED"
        out["conclusion"] = "ordinary CAS+leaf proof replayed against exact CNF target; no physical closure"
    else:
        raise McfError("working-plan solver contradicted exact-query UNSAT with SAT")
    json_write(folder / "certificate.json", out)
    return out


def run_comparison(args):
    prepared, receipt, normal = load_prepared(args.prepared)
    require(type(args.conflicts) is int and args.conflicts > 0, "conflicts must be positive")
    require(type(args.check_seconds) is int and args.check_seconds > 0,
            "checker seconds must be positive")
    jobs = []
    for label in ("parent", "raw-arm"):
        query = prepared / receipt["main_comparison"][label]
        jobs.append({"label": label, "query": str(query), "query_sha256": file_digest(query),
                     "engine": "fresh CaDiCaL195", "with_proof": True,
                     "conflicts": args.conflicts, "wall_timeout_seconds": None,
                     "sat_check": "complete model re-evaluation" ,
                     "unsat_check": "independent complete CAS/leaf parse + final derived empty + valid deletion-only normalization + -i -U -W full-byte replay",
                     "on_unsat": "additional working-plan/CAS certification attempt at same conflicts"})
    plan = {"schema": "k58-mcf-balanced-comparison/v1", "prepared_sha256": file_digest(prepared / "receipt.json"),
            "jobs": jobs, "balanced_conflict_budget": True, "physical_closure": False}
    if args.dry_run:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return plan
    out = Path(args.out)
    require(not out.exists(), f"run output already exists: {out}")
    out.mkdir(parents=True)
    json_write(out / "plan.json", plan)
    results = []
    for job in jobs:
        label = job["label"]
        folder = out / label
        search = invoke_worker(Path(job["query"]), folder, args.conflicts)
        result = finish_solver_job(prepared, receipt, label, Path(job["query"]), search,
                                   folder, args.checker, args.check_seconds, args.conflicts)
        if search["status"] == "UNSAT":
            result["plan_certificate"] = plan_certificate(
                prepared, receipt, label, args.checker, args.check_seconds, args.conflicts, folder)
            json_write(folder / "result.json", result)
        results.append(result)
    counts = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    summary = {
        "schema": "k58-mcf-comparison-result/v1", "status_counts": counts,
        "results": [{key: value for key, value in result.items()
                     if key in ("label", "status", "query_sha256", "statistics", "solve_cpu_seconds",
                                "solve_wall_seconds", "conflict_cap", "conclusion")}
                    for result in results],
        "stock_finalise_admission": False, "physical_closure": False,
        "scope": ("CNF comparison only. Augmented UNSAT, if verified, reduces through the separate "
                  "existence-preserving normal form; all physical-row and cover bridges remain explicit."),
        "result_paths": {result["label"]: str(out / result["label"] / "result.json") for result in results},
    }
    json_write(out / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if counts.get("CHECK_FAILED"):
        raise McfError("at least one claimed UNSAT failed strict verification")
    return summary


def toy_proof(args):
    """Positive end-to-end UNSAT/replay control plus malformed proof rejection."""
    out = Path(args.out)
    require(not out.exists(), f"toy output already exists: {out}")
    out.mkdir(parents=True)
    query = out / "toy.cnf"
    # Three pigeons in two holes: genuine proof search, not checker's
    # complementary-input-units shortcut (which has no RAT-core footer).
    query.write_bytes(b"p cnf 6 9\n1 2 0\n3 4 0\n5 6 0\n"
                      b"-1 -3 0\n-1 -5 0\n-3 -5 0\n"
                      b"-2 -4 0\n-2 -6 0\n-4 -6 0\n")
    folder = out / "solve"
    search = invoke_worker(query, folder, 1000)
    require(search["status"] == "UNSAT", "toy contradictory units were not UNSAT")
    from proof import normalize_additions
    from strict_rup import ReplayError, strict_replay
    clean = folder / "leaf-nodeletions.drat"
    norm = normalize_additions(folder / "leaf.drat", clean)
    require(norm["complete_parse"] and norm["empty_additions"] == 1,
            "toy did not provide a completed proof with a derived empty clause")
    replay = strict_replay(query, None, folder / "leaf.drat", folder / "strict-replay",
                           file_digest(query), args.checker, args.check_seconds)
    require(replay["strict_accepted"], "toy strict proof replay failed")
    require(file_digest(clean) == replay["normalized_proof_sha256"],
            "independent addition normalizations disagree")
    truncated = folder / "without-final-empty.drat"
    truncated.write_bytes((folder / "leaf.drat").read_bytes()[:-2])
    try:
        strict_replay(query, None, truncated, folder / "must-not-replay-truncated",
                      file_digest(query), args.checker, args.check_seconds)
    except ReplayError:
        pass
    else:
        raise McfError("removing the final empty-clause addition was accepted")
    # Exercise the ordinary working-plan/CAS concatenation independently of
    # the exact-query proof above. The CAS addition repeats (1 or 2), which
    # is RUP from the toy parent; working adds that derived cut only.
    plan_root = out / "plan-input"
    plan_root.mkdir()
    (plan_root / "toy.cnf").write_bytes(query.read_bytes())
    nv, toy_clauses, toy_body = read_dimacs(query.read_bytes())
    working = (f"p cnf {nv} {len(toy_clauses) + 1}\n".encode() + toy_body + b"1 2 0\n")
    (plan_root / "working.cnf").write_bytes(working)
    (plan_root / "cas.drat").write_bytes(b"a\x02\x04\x00")  # binary addition (1, 2)
    toy_receipt = {"certification_comparison": {
        "raw-arm": "working.cnf", "proof_targets": {"raw-arm": "toy.cnf"},
        "cas_prefix": "cas.drat"}}
    plan_result = plan_certificate(plan_root, toy_receipt, "raw-arm", args.checker,
                                   args.check_seconds, 1000, out / "plan-run")
    require(plan_result["status"] == "PLAN_CNF_UNSAT_VERIFIED",
            "toy CAS+leaf strict replay failed")

    malformed = folder / "malformed.drat"
    malformed.write_bytes((folder / "leaf.drat").read_bytes() + b"x\x00")
    try:
        normalize_additions(malformed, folder / "must-not-exist.drat")
    except McfError:
        pass
    else:
        raise McfError("malformed binary DRAT was accepted")
    result = {"status": "PASS", "scope": "toy CNF proof interface only", "solver": search["status"],
              "normalization": norm, "strict_accepted": replay["strict_accepted"],
              "full_byte_read": replay["checks"]["full_normalized_file_read_exactly_once"],
              "final_empty_clause_required": replay["joined_additions_end_in_empty"],
              "deleted_final_empty_proof_rejected": True,
              "plan_cas_strict_accepted": True,
              "malformed_rejected": True, "stock_finalise_admission": False}
    json_write(out / "receipt.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def make_parser():
    parser = argparse.ArgumentParser(prog="k58-mcf.sh",
        description="Explicit opt-in configurable maximal-colour CNF generation and balanced CaDiCaL195 runs. Never a stock finalise path.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare", help="regenerate exact frozen parent+cube, then append raw MCF")
    p.add_argument("--package", type=Path, default=HERE.parent, help="unpacked k58-massive-solver root")
    p.add_argument("--baseline-run", type=Path, required=True)
    p.add_argument("--out", type=Path, help="new output directory (required unless --dry-run)")
    p.add_argument("--row", default="target", help="exact full row id; 'target' selects the retained hard row")
    p.add_argument("--tier", default="first", choices=["first"])
    p.add_argument("--cube", default="-1413,1014")
    p.add_argument("--arms", default="3")
    p.add_argument("--colour", type=int, default=0)
    p.add_argument("--expect-parent-sha256")
    p.add_argument("--expect-working-sha256")
    p.add_argument("--expect-cas-sha256")
    p.add_argument("--expect-parent-cube-sha256")
    p.add_argument("--expect-augmented-parent-sha256")
    p.add_argument("--expect-augmented-cube-sha256")
    p.add_argument("--expect-edges", type=int)
    p.add_argument("--dry-run", action="store_true", help="compute and verify everything; write no files")
    p.set_defaults(function=prepare)
    p = sub.add_parser("run", help="balanced exact parent/raw-arm conflict-capped comparison")
    p.add_argument("--prepared", type=Path, required=True)
    p.add_argument("--out", type=Path, help="new output directory (required unless --dry-run)")
    p.add_argument("--conflicts", type=int, required=True)
    p.add_argument("--checker", type=Path, default=HERE.parent / "bin/drat-trim")
    p.add_argument("--check-seconds", type=int, default=300, help="proof-checker limit, not a search timeout")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(function=run_comparison)
    p = sub.add_parser("toy-proof", help="positive toy UNSAT/replay and negative proof controls")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--checker", type=Path, default=HERE.parent / "bin/drat-trim")
    p.add_argument("--check-seconds", type=int, default=30)
    p.set_defaults(function=toy_proof)
    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare" and not args.dry_run:
            require(args.out is not None, "prepare requires --out unless --dry-run")
        if args.command == "run" and not args.dry_run:
            require(args.out is not None, "run requires --out unless --dry-run")
        args.function(args)
    except McfError as exc:
        parser.exit(2, f"error: {exc}\n")
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: invalid input/artifact: {exc}\n")


if __name__ == "__main__":
    main()
