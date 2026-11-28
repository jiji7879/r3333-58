#!/usr/bin/env python3
"""RUP-screen short new transversal clauses against the published rules."""
import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

from pysat.solvers import Cadical195, Minisat22
from counter_encoding import serialize


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True,
                    help="paired-arm-extension source root")
    ap.add_argument("--transversals", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ranks", default="1200,1300")
    ap.add_argument("--max-width", type=int, default=6)
    ap.add_argument("--propagation-solver", choices=("cadical", "minisat"), default="cadical")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str((args.source / "hard-more").resolve()),
                    str((args.source / "hard-study").resolve())]
    import probe
    from wider import wider
    reports = []
    for rank in map(int, args.ranks.split(",")):
        row = probe.rows[rank - 1]
        guards = {}
        raw, form, direct, _ = probe.build(row, guards)
        assert sha(raw) == row["input_sha256"]
        wide = [[-guards[x][1], *lits]
                for x, *lits in wider(probe.geometry[row["id"]])]
        published = sorted({tuple(x) for x in direct + wide})
        all_clauses = json.loads((args.transversals / str(rank) /
                                  "all-transversals.json").read_text())
        candidates = sorted({tuple(x) for x in all_clauses
                             if len(x) <= args.max_width and tuple(x) not in published},
                            key=lambda x: (len(x), x))
        begin = time.process_time()
        independent = []
        rup_over_published = []
        engine = Cadical195 if args.propagation_solver == "cadical" else Minisat22
        with engine(bootstrap_with=form.clauses) as solver:
            solver.append_formula(published)
            for clause in candidates:
                alive, _ = solver.propagate(assumptions=[-lit for lit in clause])
                if alive:
                    independent.append(clause)
                else:
                    rup_over_published.append(clause)
            selected = []
            for clause in independent:
                alive, _ = solver.propagate(assumptions=[-lit for lit in clause])
                if alive:
                    selected.append(clause)
                    solver.append_formula([clause])
        screen_cpu = time.process_time() - begin
        folder = args.out / str(rank)
        folder.mkdir()
        for name, extra in (("published", published),
                            ("new-independent", published + independent),
                            ("selected", published + selected)):
            data = serialize(raw, extra)
            (folder / (name + ".cnf")).write_bytes(data)
        (folder / "candidates.json").write_text(json.dumps(candidates) + "\n")
        (folder / "independent.json").write_text(json.dumps(independent) + "\n")
        (folder / "selected.json").write_text(json.dumps(selected) + "\n")
        rec = {"rank": rank, "id": row["id"], "input_sha256": row["input_sha256"],
               "published_clauses": len(published),
               "published_width_histogram": dict(collections.Counter(map(len, published))),
               "candidates": len(candidates),
               "candidate_width_histogram": dict(collections.Counter(map(len, candidates))),
               "independent_nonrup": len(independent),
               "independent_width_histogram": dict(collections.Counter(map(len, independent))),
               "selected_greedy_nonrup": len(selected),
               "selected_width_histogram": dict(collections.Counter(map(len, selected))),
               "screen_cpu_seconds": screen_cpu,
               "selection_order": "(len(clause), clause) after integer DIMACS conversion",
               "filter_semantics": f"{args.propagation_solver} propagate on negated clause; original parent + direct + all wider; selected clauses appended after surviving a second prefix-RUP test",
               "queries": {}}
        for name in ("published", "new-independent", "selected"):
            data = (folder / (name + ".cnf")).read_bytes()
            rec["queries"][name] = {"bytes": len(data), "sha256": sha(data)}
        (folder / "filter.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        reports.append(rec)
        print(json.dumps({k: rec[k] for k in ("rank", "published_clauses", "candidates",
                                             "candidate_width_histogram", "independent_nonrup",
                                             "selected_greedy_nonrup", "selected_width_histogram",
                                             "screen_cpu_seconds")}), flush=True)
    (args.out / "summary.json").write_text(json.dumps(reports, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
