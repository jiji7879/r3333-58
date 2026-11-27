#!/usr/bin/env python3
"""One fresh proof-logging CaDiCaL call on an exact physical query."""

if not __debug__:
    raise RuntimeError("Refinement verification requires Python assertions; do not use -O or PYTHONOPTIMIZE.")
import ctypes
import hashlib
import json
from pathlib import Path
import sys
import time
import pysolvers
from pysat.formula import CNF
from pysat.solvers import Cadical195

START = time.perf_counter()
CPU_START = time.process_time()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def model_ok(clauses, model):
    values = set(model)
    return all(any(lit in values for lit in clause) for clause in clauses)


def timed_solve(solver, runtime, budget):
    """Use the runtime's native CaDiCaL terminate deadline, not Python signals."""
    cap = ctypes.pythonapi.PyCapsule_GetPointer
    cap.argtypes = [ctypes.py_object, ctypes.c_char_p]
    cap.restype = ctypes.c_void_p
    native = ctypes.CDLL(pysolvers.__file__)
    terminate = getattr(native, "_ZN10CaDiCaL1956Solver9terminateEv")
    timer = ctypes.CDLL(str(runtime / "round50/deadline.so"))
    timer.arm_deadline.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double]
    timer.arm_deadline.restype = ctypes.c_void_p
    timer.disarm_deadline.argtypes = [ctypes.c_void_p]
    timer.disarm_deadline.restype = None
    handler = timer.arm_deadline(cap(solver.cadical, None), terminate, budget)
    try:
        return solver.solve_limited()
    finally:
        timer.disarm_deadline(handler)


def main():
    argv = sys.argv[1:]
    query, out = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    budget = float(argv[2])
    runtime = Path(argv[3]).resolve()
    parent_query = Path(argv[4]).resolve() if len(argv) > 4 else None
    raw = query.read_bytes()
    out.mkdir(parents=True, exist_ok=False)
    t = time.perf_counter()
    formula = CNF(from_file=str(query))
    parsed = time.perf_counter()
    with Cadical195(bootstrap_with=formula.clauses, with_proof=True) as solver:
        bootstrapped = time.perf_counter()
        (out / "search-start.json").write_text(json.dumps({
            "parse_seconds": parsed - t, "bootstrap_seconds": bootstrapped - parsed,
            "monotonic_offset_since_worker_start": bootstrapped - START}) + "\n")
        search_cpu = time.process_time()
        decision = timed_solve(solver, runtime, budget)
        searched = time.perf_counter()
        result = {
            "query_sha256": sha(raw), "query_bytes": len(raw),
            "variables": formula.nv, "clauses": len(formula.clauses),
            "parse_seconds": parsed - t, "bootstrap_seconds": bootstrapped - parsed,
            "search_seconds": searched - bootstrapped,
            "search_cpu_seconds": time.process_time() - search_cpu,
            "total_worker_seconds": searched - START,
            "total_worker_cpu_seconds": time.process_time() - CPU_START,
            "search_budget_seconds": budget,
            "native_deadline_seconds": budget,
            "native_deadline_library": str(runtime / "round50/deadline.so"),
            "native_deadline_sha256": sha((runtime / "round50/deadline.so").read_bytes()),
            "status": "UNKNOWN" if decision is None else ("SAT" if decision else "UNSAT"),
            "stats": solver.accum_stats(),
            "engine": "Cadical195 via python-sat",
            "pysolvers_library": str(Path(pysolvers.__file__).resolve()),
            "pysolvers_sha256": sha(Path(pysolvers.__file__).read_bytes()),
        }
        if decision is True:
            model = solver.get_model()
            assert model_ok(formula.clauses, model)
            result["model_satisfies_query"] = True
            if parent_query is not None:
                result["model_satisfies_guard_parent"] = model_ok(
                    CNF(from_file=str(parent_query)).clauses, model)
                assert result["model_satisfies_guard_parent"]
            data = (" ".join(map(str, model)) + "\n").encode()
            (out / "model.txt").write_bytes(data)
            result["model_sha256"] = sha(data)
            result["model_bytes"] = len(data)
        elif decision is False:
            tproof = time.perf_counter()
            pysolvers.flushpr(solver.prfp)
            solver.prfile.seek(0)
            proof = solver.prfile.read()
            (out / "proof.drat").write_bytes(proof)
            result["proof_extraction_seconds"] = time.perf_counter() - tproof
            result["proof_sha256"] = sha(proof)
            result["proof_bytes"] = len(proof)
        result["decision_unknown_after_budget"] = decision is None
        (out / "leaf.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "search_seconds": result["search_seconds"]}))


if __name__ == "__main__":
    main()
