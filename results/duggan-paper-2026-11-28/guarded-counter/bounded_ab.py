#!/usr/bin/env python3
"""One small matched CaDiCaL195 A/B control; OPEN has no UNSAT meaning."""
import hashlib
import json
import time
from pathlib import Path

import pysat
from pysat.formula import CNF
from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent / "actual"
CAP = 20000
records = []
for style in ("naive", "boundary"):
    path = HERE / f"r1300-{style}.cnf"
    raw = path.read_bytes()
    parsed = CNF(from_string=raw.decode())
    start = time.process_time()
    with Cadical195(bootstrap_with=parsed.clauses) as solver:
        solver.configure({"seed": 0})
        solver.conf_budget(CAP)
        answer = solver.solve_limited()
        elapsed = time.process_time() - start
        stats = solver.accum_stats()
    status = "OPEN" if answer is None else ("SAT" if answer else "UNSAT")
    record = {"style": style, "engine": "Cadical195 via python-sat",
              "pysat_version": pysat.__version__, "seed": 0,
              "conflict_budget": CAP, "status": status,
              "search_and_bootstrap_process_cpu_seconds": elapsed,
              "stats": stats, "sha256": hashlib.sha256(raw).hexdigest(),
              "proof_logging": False,
              "scope": "single historical full_root rank 1300; one capped seed; no speedup or closure claim"}
    records.append(record)
    print(json.dumps(record, sort_keys=True), flush=True)
(HERE / "bounded-ab.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
