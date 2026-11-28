#!/usr/bin/env python3
"""Private fresh-process CaDiCaL195 worker. No wall-clock search timeout."""
import json
import resource
import shutil
import sys
import time
from pathlib import Path

import pysat
import pysolvers
from pysat.formula import CNF
from pysat.solvers import Cadical195



def main(query, outdir, conflicts):
    if pysat.__version__ != "1.9.dev22":
        raise RuntimeError(f"this opt-in variant requires python-sat 1.9.dev22, got {pysat.__version__}")
    if type(conflicts) is not int or conflicts <= 0:
        raise ValueError("conflict cap must be a positive integer")
    outdir.mkdir(parents=True, exist_ok=False)
    parse_start, parse_cpu = time.monotonic(), time.process_time()
    formula = CNF(from_file=str(query))
    parse_wall = time.monotonic() - parse_start
    parse_cpu = time.process_time() - parse_cpu
    with Cadical195(with_proof=True, bootstrap_with=formula.clauses) as solver:
        start, cpu = time.monotonic(), time.process_time()
        solver.conf_budget(conflicts)
        answer = solver.solve_limited()
        stats = solver.accum_stats()
        receipt = {
            "engine": "CaDiCaL195 via python-sat Cadical195",
            "python_sat_version": pysat.__version__,
            "with_proof": True, "fresh_process": True,
            "conflict_cap": conflicts, "wall_timeout_seconds": None,
            "answer": answer,
            "status": "SAT" if answer is True else "UNSAT" if answer is False else "OPEN",
            "statistics": stats,
            "solve_wall_seconds": time.monotonic() - start,
            "solve_cpu_seconds": time.process_time() - cpu,
            "parse_wall_seconds": parse_wall, "parse_cpu_seconds": parse_cpu,
            "maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        }
        if answer is True:
            (outdir / "model.json").write_text(json.dumps(solver.get_model()) + "\n")
        elif answer is False:
            # PySAT 1.9.dev22 exposes binary DRAT through this file. Flush and
            # copy the complete stream; never call text get_proof().
            pysolvers.flushpr(solver.prfp)
            solver.prfile.seek(0)
            with (outdir / "leaf.drat").open("wb") as stream:
                shutil.copyfileobj(solver.prfile, stream, 1 << 20)
    (outdir / "solver.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]))
