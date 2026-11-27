#!/usr/bin/env python3
"""Hash-bound CaDiCaL phase experiments on original K58 hard-row parents.

No clauses are added, removed, reordered, or simplified: only initial phases differ.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
import sys
import time

if not __debug__:
    raise RuntimeError("Run with assertions enabled")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write_new(path, value):
    data = canonical(value)
    with path.open("xb") as stream:
        stream.write(data)


def generate(args):
    source = Path(args.source).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(source))
    import probe
    row = probe.rows[args.rank - 1]
    assert int(row["rank"]) == args.rank
    start_cpu = time.process_time()
    start_wall = time.perf_counter()
    guards = {}
    raw, formula, direct, selectors = probe.build(row, guards)
    generation_cpu = time.process_time() - start_cpu
    generation_wall = time.perf_counter() - start_wall
    assert sha(raw) == row["input_sha256"]
    cnf = out / "parent.cnf"
    cnf.write_bytes(raw)
    n = sum(probe.geometry[row["id"]]["family"]["profile"]) + 1
    physical_max = 4 * (n * (n - 1) // 2)
    assert max(max(map(abs, c)) for c in formula.clauses) == formula.nv
    metadata = {
        "rank": args.rank,
        "id": row["id"],
        "profile": row["profile"],
        "kinds": row["kinds"],
        "charge": row["charge"],
        "input_sha256": row["input_sha256"],
        "input_bytes": len(raw),
        "variables": formula.nv,
        "clauses": len(formula.clauses),
        "physical_max": physical_max,
        "guards": {str(x): list(gc) for x, gc in sorted(guards.items())},
        "generation_cpu_seconds": generation_cpu,
        "generation_wall_seconds": generation_wall,
        "source": str(source),
        "source_hashes": {name: sha((source / name).read_bytes())
                          for name in ("probe.py", "geometry.json", "hard1300.tsv",
                                       "encoder/cover_evidence.py", "encoder/gluing.py",
                                       "encoder/dense.py")},
        "historical_drat_sha256": row["proof_sha256"],
        "historical_drat_bytes": int(row["proof_bytes"]),
        "historical_proof_replayed": False,
        "baseline_direct_clause_count_for_metadata_only": len(direct),
        "baseline_selector_clause_count_for_metadata_only": len(selectors),
        "format_note": "Only parent.cnf is a solver query; direct/selectors were not appended."
    }
    write_new(out / "parent.json", metadata)
    print(json.dumps({k: metadata[k] for k in
                      ("rank", "id", "input_sha256", "variables", "clauses",
                       "physical_max", "generation_cpu_seconds")}, sort_keys=True))


def phase_literals(policy, variables, physical_max, guards):
    if policy in ("stock", "option-all-false", "lucky-off", "option-all-false-lucky-off"):
        return []
    if policy == "physical-false":
        return list(range(-1, -physical_max - 1, -1))
    if policy == "all-false":
        return list(range(-1, -variables - 1, -1))
    if policy == "physical-false-guards-false":
        return [-i for i in range(1, variables + 1)
                if i <= physical_max or i in guards]
    if policy == "aux-false":
        return [-i for i in range(physical_max + 1, variables + 1)]
    raise ValueError(policy)


def run(args):
    parent_dir = Path(args.parent).resolve()
    metadata = json.loads((parent_dir / "parent.json").read_text())
    raw = (parent_dir / "parent.cnf").read_bytes()
    assert sha(raw) == metadata["input_sha256"]
    if args.expected_sha and args.expected_sha != metadata["input_sha256"]:
        raise ValueError("expected parent hash mismatch")
    from pysat.formula import CNF
    from pysat.solvers import Cadical195
    import pysat
    import pysolvers
    start_cpu = time.process_time()
    start_wall = time.perf_counter()
    formula = CNF(from_string=raw.decode())
    parsed_cpu = time.process_time()
    parsed_wall = time.perf_counter()
    assert formula.nv == metadata["variables"]
    assert len(formula.clauses) == metadata["clauses"]
    guard_values = {int(value[1]) for value in metadata["guards"].values()}
    phases = phase_literals(args.policy, formula.nv, metadata["physical_max"], guard_values)
    phase_binary = b"" if not phases else canonical(phases)
    with Cadical195(bootstrap_with=formula.clauses, with_proof=args.proof) as solver:
        options = {"seed": args.seed}
        if args.policy in ("option-all-false", "option-all-false-lucky-off"):
            options["phase"] = 0
        if args.policy in ("lucky-off", "option-all-false-lucky-off"):
            options["lucky"] = 0
        solver.configure(options)
        if phases:
            solver.set_phases(phases)
        bootstrapped_cpu = time.process_time()
        bootstrapped_wall = time.perf_counter()
        solver.conf_budget(args.conflicts)
        answer = solver.solve_limited()
        finished_cpu = time.process_time()
        finished_wall = time.perf_counter()
        status = "OPEN" if answer is None else ("SAT" if answer else "UNSAT")
        stats = solver.accum_stats()
        proof_extract_seconds = None
        proof_path = None
        proof_bytes = None
        proof_sha256 = None
        if answer is False and args.proof:
            extract_wall = time.perf_counter()
            proof_path = Path(str(args.out) + ".drat").resolve()
            proof_path.parent.mkdir(parents=True, exist_ok=True)
            pysolvers.flushpr(solver.prfp)
            solver.prfile.seek(0)
            digest = hashlib.sha256()
            proof_bytes = 0
            with proof_path.open("xb") as output:
                while True:
                    block = solver.prfile.read(1 << 20)
                    if not block:
                        break
                    digest.update(block)
                    proof_bytes += len(block)
                    output.write(block)
            proof_sha256 = digest.hexdigest()
            proof_extract_seconds = time.perf_counter() - extract_wall
        model_checked = None
        if answer is True:
            model = set(solver.get_model())
            model_checked = all(any(lit in model for lit in clause)
                                for clause in formula.clauses)
            assert model_checked
        result = {
            "rank": metadata["rank"], "id": metadata["id"],
            "input_sha256": metadata["input_sha256"], "input_bytes": len(raw),
            "variables": formula.nv, "clauses": len(formula.clauses),
            "policy": args.policy, "seed": args.seed,
            "conflict_budget": args.conflicts, "cube": [],
            "phase_count": len(phases),
            "phase_positive_count": sum(x > 0 for x in phases),
            "phase_sha256": sha(phase_binary), "phase_bytes": len(phase_binary),
            "status": status, "answer_python": answer,
            "stats": stats,
            "parse_cpu_seconds": parsed_cpu - start_cpu,
            "parse_wall_seconds": parsed_wall - start_wall,
            "phase_bootstrap_cpu_seconds": bootstrapped_cpu - parsed_cpu,
            "phase_bootstrap_wall_seconds": bootstrapped_wall - parsed_wall,
            "search_cpu_seconds": finished_cpu - bootstrapped_cpu,
            "search_wall_seconds": finished_wall - bootstrapped_wall,
            "worker_cpu_seconds": finished_cpu - start_cpu,
            "worker_wall_seconds": finished_wall - start_wall,
            "model_checked_against_parent": model_checked,
            "engine": "Cadical195 via python-sat",
            "pysat_version": pysat.__version__,
            "pysolvers_path": str(Path(pysolvers.__file__).resolve()),
            "pysolvers_sha256": sha(Path(pysolvers.__file__).read_bytes()),
            "solver_options": options,
            "effective_documented_option_changes": dict(options, **({"lucky": 0} if phases else {})),
            "pysat_set_phases_also_disables_lucky": bool(phases),
            "proof_logging": args.proof,
            "proof_extract_wall_seconds": proof_extract_seconds,
            "proof_path": str(proof_path) if proof_path else None,
            "proof_bytes": proof_bytes,
            "proof_sha256": proof_sha256,
            "note": "OPEN means budget exhausted, never SAT or UNSAT"
        }
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    write_new(out, result)
    print(json.dumps({"policy": args.policy, "seed": args.seed,
                      "status": status, "stats": stats,
                      "search_cpu_seconds": result["search_cpu_seconds"],
                      "search_wall_seconds": result["search_wall_seconds"],
                      "out": str(out)}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--source", required=True)
    gen.add_argument("--rank", type=int, required=True)
    gen.add_argument("--out", required=True)
    gen.set_defaults(function=generate)
    runner = sub.add_parser("run")
    runner.add_argument("--parent", required=True)
    runner.add_argument("--out", required=True)
    runner.add_argument("--policy", required=True,
                        choices=("stock", "physical-false", "all-false", "option-all-false",
                                 "lucky-off", "option-all-false-lucky-off",
                                 "physical-false-guards-false", "aux-false"))
    runner.add_argument("--seed", type=int, default=0)
    runner.add_argument("--conflicts", type=int, required=True)
    runner.add_argument("--expected-sha", default="")
    runner.add_argument("--proof", action="store_true")
    runner.set_defaults(function=run)
    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
