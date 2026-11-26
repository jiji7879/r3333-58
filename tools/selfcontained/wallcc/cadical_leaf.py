"""Private subprocess entry point. A separate process gives native SAT a hard deadline."""
import json
from pathlib import Path
import shutil
import sys

import pysolvers
from pysat.formula import CNF
from pysat.solvers import Cadical195

from problem import json_bytes


def main(working, directory, conflicts, traced, cube):
    # These are unit clauses in the solver input, not solve() assumptions.
    with Cadical195(with_proof=traced) as solver:
        solver.append_formula(CNF(from_file=str(working)))
        for literal in cube:
            solver.add_clause([literal])
        solver.conf_budget(conflicts)
        decision = solver.solve_limited()
        stats = solver.accum_stats()
        if decision is True:
            (directory / "model.json").write_bytes(json_bytes(solver.get_model()))
        elif decision is False and traced:
            # PySAT 1.9.dev22 exposes binary DRAT here. Its text get_proof() first
            # materializes the entire trace. Copy directly to keep memory bounded.
            pysolvers.flushpr(solver.prfp)
            solver.prfile.seek(0)
            with (directory / "leaf.drat").open("wb") as out:
                shutil.copyfileobj(solver.prfile, out, 1 << 20)
        status = "OPEN" if decision is None else ("SAT" if decision else "UNSAT")
        print(json.dumps({"status": status, "conflicts_used": stats["conflicts"]}))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]),
         sys.argv[4] == "trace", list(map(int, sys.argv[5:])))
