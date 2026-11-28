#!/usr/bin/env python3
"""Strict optional K15 square/matching preprocessing for 14 ordinary wall rows.

The 13 full-root historical rows are not silently accepted here.  Every row is
rebuilt as first-tier (tables=True,total_critical=True,full_root=False), and
its parent hash, physical guard blocks, original units, emitted clause set and
propagation count must agree with the audited batches.

`square run` deliberately returns STRENGTHENED_UNSAT, not a refutation of the
original parent.  This module does not insert its output into the production
cover release or finalise pipeline.  A local theorem/cube implication is not a
whole-original-parent DRAT proof.
"""
import argparse
import contextlib
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MODULE = Path(__file__).resolve().parent
ROOT = MODULE.parent
(ROOT / '.scratch').mkdir(exist_ok=True)
os.environ.setdefault('TMPDIR', str(ROOT / '.scratch'))
SOURCE = MODULE / "source"
NEXT = SOURCE / "next"
sys.path[:0] = [str(MODULE / "work"), str(NEXT), str(SOURCE / "hard-more"),
                str(SOURCE / "hard-study"), str(SOURCE / "hard-study" / "encoder")]
import stage2
from pysat.formula import CNF
from pysat.solvers import Cadical195


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rows():
    return json.loads((NEXT / "wall-rows.json").read_text())


def load_batch(index):
    packed = (NEXT / f"batch-{index}.json.gz").read_bytes()
    expected = {i: (h, n) for i, h, n in json.loads((NEXT / "batches.json").read_text())}
    assert index in expected and sha(packed) == expected[index][0], "batch compressed hash mismatch"
    data = json.loads(gzip.decompress(packed))
    assert sha(gzip.decompress((NEXT / "matching.drat.gz").read_bytes())) == data["local_proof"]
    assert data["tier"] == "first" and data["cube"] == [] and data["palette"] == [0, 1, 2, 3]
    return data


def run_external(script, *args):
    """Run a checked script with the package source and a disposable output path."""
    proc = subprocess.run([sys.executable, str(MODULE / script), *map(str, args)],
                          capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"{script} failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def verify(out, rows_to_check=None, deep=False, checker=None):
    """Independently rebuild rows, clauses and physical guard/cardinality blocks."""
    checker = Path(checker or ROOT / "bin" / "drat-trim").resolve()
    selected = set(rows_to_check or [i for i, _ in rows()])
    out.mkdir(parents=True, exist_ok=False)
    # normalization.py compares literal clause multisets under explicit vertex
    # and colour maps.  This is not just a graph-isomorphism assertion.
    (out / "normalization.out").write_text(run_external(
        "normalization.py", SOURCE, out / "normalization.json"))
    (out / "local-models.out").write_text(run_external(
        "local_models.py", SOURCE, out / "local-models.json"))
    strict = out / "strict"
    (out / "strict-replay.out").write_text(run_external(
        "strict_replay.py", SOURCE, checker, strict))
    native = json.loads((strict / "direct-receipts.json").read_text())
    assert native["matching"]["sha256"] == "9fb32091685b9e3adf1e7e670c3d4333f35b0d12ed6990e968a44b83fb180b01"
    assert native["strict_original"]["exit"] == 0
    assert native["strict_original"]["verified"] == 1
    assert native["strict_original"]["full_read"]
    assert native["strict_original"]["warnings"] == []
    assert native["strict_original"]["rat_zero"]
    assert native["negative_path"]["exit"] != 0
    if deep:
        (out / "rup-negative.out").write_text(run_external("rup_negative.py", SOURCE))
        assert "positive verified and both negatives rejected" in (out / "rup-negative.out").read_text()
    records = {}
    for i, row in rows():
        if i not in selected:
            continue
        rec = stage2.run(i, row)
        assert rec["parent"] == load_batch(i)["parent"]
        assert rec["missing_vs_shipped"] == rec["extra_vs_shipped"] == 0
        # stage2's witness tuples include extra recomputed fields; the following
        # full independent stage-3 test checks the supplied witness geometry and
        # the literal guard/order/palette and both cardinality directions.
        records[i] = rec
        (out / f"stage2-{i}.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    (out / "stage2.out").write_text(json.dumps(records, indent=1, sort_keys=True, default=list) + "\n")
    old_cwd = Path.cwd()
    try:
        os.chdir(out)
        prefix = sys.path[:]
        try:
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                import stage3
            (out / "stage3.out").write_text(stream.getvalue())
        finally:
            sys.path = prefix
            # The source modules are read-only; stage3 writes only its own receipt
            # in cwd, which is the caller's explicitly new output directory.
    finally:
        os.chdir(old_cwd)
    audited = json.loads((out / "stage3.json").read_text())
    for rec in audited:
        i = rec["index"]
        if i not in selected:
            continue
        assert rec["digest_ok"] and rec["parent_ok"] and rec["id_ok"] and rec["theorem_ok"]
        assert rec["tier"] == "first" and rec["cube"] == [] and rec["palette"] == [0, 1, 2, 3]
        assert not rec["bad"] and rec["unguarded_ok"] and rec["omitted_justified"]
        assert rec["nrules"] == records[i]["clauses"] and rec["novel"] == records[i]["novel"]
    result = {"status": "PASS", "checked_rows": sorted(selected),
              "total_clause_count_selected": sum(x["clauses"] for x in records.values()),
              "surviving_original_propagation_selected": sum(x["novel"] for x in records.values()),
              "K15_query_sha256": native["matching"]["sha256"],
              "raw_proof_sha256": native["proof"]["sha256"],
              "raw_proof_bytes": native["proof"]["bytes"],
              "native_original_strict_passed": True,
              "native_deletions_ignored_RUP_passed": native["strict_deletions_ignored"]["verified"] == 1,
              "negative_path_rejected": True,
              "deep_independent_RUP_controls": deep,
              "first_tier_recipe": {"tables": True, "total_critical": True, "full_root": False},
              "scope": "exact selected first-tier parents; no guard-activation, representative, wall-row or Ramsey conclusion"}
    (out / "verify-summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def one(index, output, checker=None):
    """Validate all 14 stored batches, then return one exact parent/clause set."""
    required = [i for i, _ in rows()]
    verify(output, required, False, checker)
    row = dict(rows())[index]
    batch = load_batch(index)
    raw, form = stage2.build(row)
    assert sha(raw) == batch["parent"]
    clauses = [list(cl) for cl, _ in batch["rules"]]
    assert len(clauses) == len({tuple(cl) for cl in clauses})
    return row, raw, form, clauses


def augment(raw, clauses):
    header, body = raw.split(b"\n", 1)
    fields = header.split()
    assert fields[:2] == [b"p", b"cnf"]
    largest = max([int(fields[2])] + [abs(l) for c in clauses for l in c])
    added = b"".join(" ".join(map(str, c)).encode() + b" 0\n" for c in clauses)
    return f"p cnf {largest} {int(fields[3]) + len(clauses)}\n".encode() + body + added


def call(form, conflicts, seed, original=False):
    with Cadical195(bootstrap_with=form.clauses, with_proof=True) as solver:
        solver.configure({"seed": seed})
        if conflicts:
            solver.conf_budget(conflicts)
        started, cpu = time.monotonic(), time.process_time()
        # A conflict budget is deliberate; this port does not start an unbounded
        # search hidden behind a local preprocessing check.
        result = solver.solve_limited()
        stats = solver.accum_stats()
        record = {"conflicts": stats["conflicts"], "decisions": stats["decisions"],
                  "propagations": stats["propagations"],
                  "cpu_seconds": time.process_time() - cpu,
                  "wall_seconds": time.monotonic() - started, "seed": seed}
        if result is True:
            record["status"] = "ORIGINAL_MODEL_CHECKED" if original else "STRENGTHENED_MODEL"
            model = set(solver.get_model())
            assert all(any((lit in model) if lit > 0 else (-lit not in model) for lit in c)
                       for c in form.clauses), "invalid model"
            record["model_checked_against_strengthened_formula"] = True
            record["model"] = sorted(model)
        elif result is False:
            record["status"] = ("ORIGINAL_UNSAT_SEARCH_ONLY_NO_RETAINED_PROOF"
                                  if original else "STRENGTHENED_UNSAT_NOT_ORIGINAL_CLOSURE")
        else:
            record["status"] = "OPEN_AT_CONFLICT_CAP"
        return record


def run_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checker", type=Path, default=ROOT / "bin/drat-trim")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("rows", help="list the 14 supported ordinary-wall rows")
    v = sub.add_parser("verify", help="strict local and original-parent batch audit")
    v.add_argument("--index", type=int)
    v.add_argument("--out", type=Path, required=True)
    v.add_argument("--deep", action="store_true", help="also run independent strict-RUP controls")
    e = sub.add_parser("export", help="append valid clauses after checking every batch")
    e.add_argument("--index", type=int, required=True)
    e.add_argument("--out", type=Path, required=True, help="new augmented CNF")
    e.add_argument("--receipt-dir", type=Path, required=True)
    r = sub.add_parser("run", help="bounded solving; never claim an original-parent closure")
    r.add_argument("--index", type=int, required=True)
    r.add_argument("--out", type=Path, required=True, help="new run directory")
    r.add_argument("--conflicts", type=int, default=40000)
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--baseline", action="store_true", help="also run the unchanged parent")
    return p


def main():
    args = run_parser().parse_args()
    if args.cmd == "rows":
        for i, row in rows():
            print(i, row["id"], "profile=" + ",".join(map(str, row["family"]["profile"])))
        return
    if args.cmd == "verify":
        selected = [args.index] if args.index is not None else None
        if selected and not any(i == selected[0] for i, _ in rows()):
            raise ValueError("square-spoke processing is restricted to the 14 checked ordinary rows")
        print(json.dumps(verify(args.out.resolve(), selected, args.deep, args.checker),
                         indent=2, sort_keys=True))
        print("All selected parent/emitting-guard clauses checked; no original-row closure claimed.")
        return
    index_row = dict(rows())
    if args.index not in index_row:
        raise ValueError("unsupported row index; use `square rows`")
    if args.cmd == "export":
        row, raw, form, extra = one(args.index, args.receipt_dir.resolve(), args.checker)
        data = augment(raw, extra)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("xb") as stream:
            stream.write(data)
        print(json.dumps({"index": args.index, "row_id": row["id"],
                          "original_parent_sha256": sha(raw),
                          "augmented_sha256": sha(data), "added_clauses": len(extra),
                          "scope": "strengthened formula; original parent/body retained, not an original DRAT closure"}, indent=2))
        return
    if not 0 < args.conflicts:
        raise ValueError("run requires a positive finite --conflicts cap")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    row, raw, form, extra = one(args.index, out / "validation", args.checker)
    augmented, original = out / "square.cnf", out / "original.cnf"
    augmented.write_bytes(augment(raw, extra))
    original.write_bytes(raw)
    f_square = CNF(from_string=augmented.read_text())
    result = {"index": args.index, "row_id": row["id"],
              "original_parent_sha256": sha(raw),
              "augmented_sha256": sha(augmented.read_bytes()),
              "added_clauses": len(extra),
              "policy": "validated K15 square/matching additions",
              "certificate_ceiling": "no original-parent UNSAT certificate is produced or inferred"}
    result["square"] = call(f_square, args.conflicts, args.seed)
    if args.baseline:
        result["original"] = call(form, args.conflicts, args.seed, original=True)
        # The comparison is local-clock data, not a speedup declaration.
        result["comparison_scope"] = "single seed and finite cap only"
        assert result["original"]["status"].startswith("ORIGINAL_") or result["original"]["status"].startswith("OPEN_")
    (out / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("square", "original")}, sort_keys=True))
    for name in (("original",) if args.baseline else ()) + ("square",):
        value = dict(result[name]); value.pop("model", None)
        print(name, json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
