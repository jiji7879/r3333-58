"""Bounded standalone CaDiCaL with ordinary DIMACS cube units and binary DRAT."""
import json
import subprocess
from pathlib import Path
from time import monotonic

from problem import extend_dimacs, require

BINARY = Path(__file__).resolve().parent / "bin/cadical-2.1.2"
SEARCH_ONLY_FLAGS = (
    "--elim=false", "--probe=false", "--vivify=false",
    "--subsume=false", "--ternary=false", "--block=false", "--stabilize=false",
)


def solve(parent, temp, cube, args, traced):
    started = monotonic()
    query = parent
    if cube:
        query = temp / "native.cnf"
        extend_dimacs(parent, query, [(lit,) for lit in cube])
    policy = getattr(args, "native_policy", "default")
    require(policy in ("default", "search-only"), f"unknown native policy {policy}")
    options = SEARCH_ONLY_FLAGS if policy == "search-only" else ()
    command = [str(BINARY), "--seed=0", "--binary=true", "-c", str(args.conflicts),
               *options, str(query)]
    if traced:
        command.append(str(temp / "leaf.drat"))
    remaining = args.seconds - (monotonic() - started)
    if remaining <= 0:
        return {"status": "OPEN", "reason": "wall-time limit"}
    # Let CaDiCaL stop itself first so its final UNKNOWN marker and statistics
    # survive; the subprocess deadline remains the hard backstop.
    command[1:1] = ["-t", str(max(1, int(remaining) - 2))]
    try:
        run = subprocess.run(command, capture_output=True, text=True,
                             timeout=remaining)
    except subprocess.TimeoutExpired:
        return {"status": "OPEN", "reason": "wall-time limit"}
    statuses = {0: ("c UNKNOWN", "OPEN"), 10: ("s SATISFIABLE", "SAT"), 20: ("s UNSATISFIABLE", "UNSAT")}
    require(run.returncode in statuses, f"native CaDiCaL failed ({run.returncode}): {run.stderr[-400:]}")
    marker, status = statuses[run.returncode]
    lines = run.stdout.splitlines()
    require(marker in lines, "native CaDiCaL output and exit code disagree")
    result = {"status": status, "status_line": marker, "solver_exit": run.returncode,
              "conflicts_used": 0, "native_policy": policy,
              "solver_wall_s": monotonic() - started}
    for line in lines:
        if line.startswith("c conflicts:"):
            result["conflicts_used"] = int(line.split()[2])
        elif line.startswith("c total process time since initialization:"):
            require(line.split()[-1] == "seconds", "unexpected CaDiCaL time units")
            result["solver_cpu_s"] = float(line.split()[-2])
        elif line.startswith("c maximum resident set size of process:"):
            require(line.split()[-1] == "MB", "unexpected CaDiCaL memory units")
            result["solver_rss_mib"] = float(line.split()[-2])
    if status == "SAT":
        literals = [int(v) for line in lines if line.startswith("v ") for v in line.split()[1:] if v != "0"]
        (temp / "model.json").write_text(json.dumps(literals))
    elif status == "OPEN":
        result["reason"] = ("conflict limit" if result["conflicts_used"] >= args.conflicts
                            else "wall-time limit")
    return result
