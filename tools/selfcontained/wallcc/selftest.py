"""Run the SAT, proof, restart and coverage checks. Use --wall for a frozen-row check."""
import argparse
import itertools
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
from types import SimpleNamespace

from problem import ROOT, encode_clauses, extend_dimacs, file_hash, read_dimacs, require
from campaign import check_trace, probe, replay
from cubing import cover
from anchor_cuts import binary_prefix
from pysat.solvers import Minisat22


def cli(*args, expected=0):
    run = subprocess.run([sys.executable, str(ROOT / "wallcc.py"), *map(str, args)],
                         capture_output=True, text=True, timeout=180)
    require(run.returncode == expected, f"unexpected exit {run.returncode}: {run.stderr} {run.stdout}")
    return json.loads(run.stdout.splitlines()[-1]) if run.stdout.strip() else {}


def ramsey_cnf(n):
    edge = {uv: i for i, uv in enumerate(itertools.combinations(range(n), 2), 1)}
    clauses = []
    for u, v, w in itertools.combinations(range(n), 3):
        t = [edge[u, v], edge[v, w], edge[u, w]]
        clauses.extend((t, [-v for v in t]))
    return f"p cnf {len(edge)} {len(clauses)}\n".encode() + encode_clauses(clauses)


def controls(temp):
    src = temp / "test.cnf"
    for n, status in ((5, "VERIFIED_SAT"), (6, "VERIFIED_UNSAT")):
        run = temp / f"k{n}"
        src.write_bytes(ramsey_cnf(n))
        cli("run", "--cnf", src, "--out", run, "--depth", 2, "--jobs", 2,
            "--shards", 2, "--shard", 0)
        if n == 6:
            partial = cli("verify", run, expected=2)
            require(partial["counts"] == {"MISSING": 2, "VERIFIED_UNSAT": 2},
                    "missing sibling did not leave the root open")
            cli("export-drat", run, temp / "partial.drat", expected=1)
            require(not (temp / "partial.drat").exists(), "exported an incomplete tree")
        cli("resume", run, "--shards", 2, "--shard", 1, "--jobs", 2)
        result = cli("verify", run, "--jobs", 2)
        require(result["status"] == status and result["counts"] == {status: 4}, "wrong cube verdict")
        if n == 6:
            for method in ("compact", "isolated"):
                merged = cli("export-drat", run, temp / f"{method}.drat", "--method", method)
                require(merged["status"] == "VERIFIED_UNSAT", "merged proof failed")
        original = {p: p.stat().st_mtime_ns for p in run.glob("leaves/*/receipt.json")}
        cli("resume", run, "--jobs", 2)
        require(all(p.stat().st_mtime_ns == stamp for p, stamp in original.items()),
                "resume rewrote a completed leaf")
        plan = json.loads((run / "plan.json").read_bytes())
        assignments = itertools.product((False, True), repeat=len(set(plan["splits"].values())))
        variables = sorted(set(plan["splits"].values()))
        for assignment in assignments:
            signed = {v if bit else -v for v, bit in zip(variables, assignment)}
            require(sum(set(c).issubset(signed) for _, c in cover(plan["splits"], plan["variables"], 2)) == 1,
                    "a split assignment has the wrong coverage multiplicity")
        leaf = run / "leaves/r00"
        if n == 5:
            (leaf / "model.json").write_text("[]")
            receipt_path = leaf / "receipt.json"
            rec = json.loads(receipt_path.read_bytes())
            rec["artifact_sha256"] = file_hash(leaf / "model.json")
            receipt_path.write_text(json.dumps(rec))
        else:
            proof = leaf / "leaf.drat"
            proof.write_bytes(binary_prefix([[]]))
            receipt_path = leaf / "receipt.json"
            rec = json.loads(receipt_path.read_bytes())
            rec["artifact_sha256"] = file_hash(proof)
            receipt_path.write_text(json.dumps(rec))
        cli("verify", run, expected=1)
    src.write_bytes(ramsey_cnf(6))
    limited = temp / "capped"
    first = cli("run", "--cnf", src, "--out", limited, "--depth", 0, "--conflicts", 1)
    require(first["counts"] == {"OPEN": 1}, "a conflict-limited search must stay open")
    cli("verify", limited, expected=2)
    cli("resume", limited, "--conflicts", 10000)
    require(cli("verify", limited)["status"] == "VERIFIED_UNSAT", "larger-budget retry failed")
    # A declared but absent variable, multiline clauses and an empty clause.
    for i, (data, expected) in enumerate(((b"c empty\np cnf 12 0\n", "VERIFIED_SAT"),
        (b"p cnf 1 1\n0\n", "VERIFIED_UNSAT"),
        (b"p cnf 3 3\n1\nc between literals\n2 0 -1 0\n-2 0\n", "VERIFIED_UNSAT"))):
        src.write_bytes(data)
        run = temp / f"dimacs{i}"
        cli("run", "--cnf", src, "--out", run, "--depth", 0, "--proof", "eager")
        require(cli("verify", run)["status"] == expected, "DIMACS corner case failed")
    print("PASS  K5/K6, all split assignments, sharding, same-plan resume, missing sibling,"
          " damaged proof and model with updated hashes, capped retry, both DRAT exports,"
          " and DIMACS edge cases", flush=True)


def audit_wall(out):
    """Prove all exported CAS clauses simultaneously and replay a conditioned real cube."""
    plan = json.loads((out / "plan.json").read_bytes())
    nv, base = read_dimacs((out / "parent.cnf").read_bytes())
    _, working = read_dimacs((out / "working.cnf").read_bytes())
    cuts = working[len(base):]
    require(working[:len(base)] == base and len(cuts) == plan["cuts"], "parent is not the working prefix")
    if not cuts:
        return {"cuts": 0, "conditional_cube": None}
    checker = ROOT / "tools/drat-trim"
    with TemporaryDirectory(prefix="wallcc-cas-audit-") as name:
        tmp = Path(name)
        flags = [nv+i+1 for i in range(len(cuts))]
        # The extra CNF selects at least one goal and falsifies every literal in it.
        select = [flags] + [[-flag, -v] for flag, cut in zip(flags, cuts) for v in cut]
        _, body = (out / "parent.cnf").read_bytes().split(b"\n", 1)
        formula = tmp / "negated-conclusions.cnf"
        formula.write_bytes(f"p cnf {nv+len(cuts)} {len(base)+len(select)}\n".encode()
                            + body + encode_clauses(select))
        trace = tmp / "all.drat"
        trace.write_bytes((out / "cas.drat").read_bytes()
                          + binary_prefix([[-flag] for flag in flags] + [[]]))
        checked = subprocess.run([str(checker), str(formula), str(trace), "-f", "-U", "-i", "-t", "90"],
                                 capture_output=True, timeout=100)
        require(checked.returncode == 0 and b"s VERIFIED" in checked.stdout.splitlines(),
                "RUP replay of all CAS clauses failed: " + checked.stdout[-1200:].decode())
        with Minisat22(bootstrap_with=base) as solver:
            cube = next(([-v for v in c] for c in cuts if solver.propagate([-v for v in c])[0]), None)
        require(cube is not None, "no nontrivial cut for the conditioned control")
        outp = probe(out, tmp, cube, SimpleNamespace(seconds=30, conflicts=5000), True)
        require(outp["status"] == "UNSAT", "the conditioned CAS cut should refute its cube")
        passed, log = replay(out, tmp, cube, tmp / "leaf.drat", checker, 60)
        require(passed, "conditioned frozen-child replay failed: " + log)
        fixture = json.loads((ROOT / "smoke-results.json").read_bytes())["merged_control"]
        if plan["origin"]["id"] == fixture["row"] and plan["origin"]["tier"] == "first":
            formula = tmp / "restricted.cnf"
            extend_dimacs(out / "parent.cnf", formula, [[v] for v in fixture["cube"]])
            require(file_hash(formula) == fixture["cnf_sha256"], "wrong merged control input")
            passed, log = check_trace(formula, ROOT / "data/branch53-no-hit.drat", checker, 60)
            require(passed, "merged control replay failed: " + log)
    return {"cuts": len(cuts), "conditional_cube": cube, "all_cuts_rup": True,
            "conditional_drat": True}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wall", metavar="ROW", nargs="?", const="d11c492f44d3",
                    help="also check real-row CAS clauses and a conditioned cube")
    opts = ap.parse_args()
    with TemporaryDirectory(prefix="wallcc-test-") as d:
        tmp = Path(d)
        controls(tmp)
        if opts.wall:
            out = tmp / "row"
            cli("prepare", "--row", opts.wall, "--out", out, "--depth", 1)
            print(json.dumps(audit_wall(out), sort_keys=True))
