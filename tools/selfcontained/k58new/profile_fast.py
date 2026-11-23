"""Proof-producing search for the frozen (15,14,14,14) rows."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import fcntl
from functools import partial
from hashlib import sha256
from itertools import islice
import json
import os
from pathlib import Path
import subprocess
from time import monotonic

import cover_evidence as ce
from gluing import units
from matched_anchor import digest
from profile_kernel import PROFILE, PHYSICAL, build, dispensable_counts, family_of, lift, physical_index
from run_cover import replay
from sender_kernel import build_senders, extend_retry, fully_sending

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("auto", "cached", "compact", "pentagon", "senders")


def working_formula(row, recipe, variant, path, proof_prefix=None):
    if variant == "senders":
        return build_senders(row, recipe, path, proof_prefix=proof_prefix)
    return build(row, recipe, path, hits=variant=="pentagon", proof_prefix=proof_prefix)


def checked_model(row, recipe, working_variant, log, destination):
    """Lift an actual SAT witness and check every frozen clause before retaining it."""
    values = {}
    for line in log.read_text().splitlines():
        if line.startswith("v "):
            for lit in map(int, line[2:].split()):
                if lit:
                    values[abs(lit)] = lit > 0
    if not values:
        raise ValueError("Kissat returned SAT without a model")
    if working_variant != "cached":
        family = family_of(row)
        pins = [cl[0] for cl in units(family, row["placement"])]
        ok, propagated = physical_index()[-1].propagate(assumptions=pins)
        ce.require(ok, "inconsistent frozen pins")
        for lit in pins + propagated:
            values[abs(lit)] = lit > 0
        if dispensable_counts(family, row, recipe):
            values = {var: val for var, val in values.items() if var <= PHYSICAL}
    if working_variant == "senders" and recipe["full_root"]:
        values = extend_retry(row, recipe, values)
    head, *parts = ce.formula_chunks(row, recipe)
    top = int(head.split()[2])
    for part in parts:
        for line in part.splitlines():
            literals = list(map(int, line.split()))[:-1]
            ce.require(any(values.get(abs(lit), False) == (lit > 0) for lit in literals),
                       "candidate fails a frozen clause")
    model = [v if values.get(v, False) else -v for v in range(1, top+1)]
    destination.write_text("v " + " ".join(map(str, model)) + " 0\n")


def kissat(solver, work, proof, log, seconds, conflicts):
    command = [solver["path"], "--quiet", f"--time={seconds}", f"--conflicts={conflicts}", str(work)]
    if proof is not None:
        proof.unlink(missing_ok=True)
        command.append(str(proof))
    start = monotonic()
    with log.open("wb") as out:
        with subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT) as child:
            _, status, usage = os.wait4(child.pid, 0)
            child.returncode = os.waitstatus_to_exitcode(status)
    if child.returncode not in (0, 10, 20):
        raise RuntimeError(f"Kissat exit {child.returncode}; see {log}")
    return dict(status={0:"OPEN", 10:"SAT", 20:"UNSAT"}[child.returncode], command=command,
                solver_wall=monotonic()-start, cpu_seconds=usage.ru_utime+usage.ru_stime)


def publish(row, recipe, variant, folder, run, receipt, args):
    original = run / "frozen.cnf"
    chunks = ce.formula_chunks(row, recipe)
    with original.open("wb") as out:
        out.writelines(chunks)
    raw = run / "raw.drat"
    ce.require(digest(raw) == receipt["raw_sha256"], "raw proof has changed")
    proof = raw
    if variant != "cached":
        rebuilt = run / "working.cnf"
        prefix = run / "prefix.drat"
        working_formula(row, recipe, variant, rebuilt, proof_prefix=prefix)
        ce.require(digest(rebuilt) == receipt["working_sha256"], "search input did not reproduce")
        proof = run / "lifted.drat"
        lift(prefix, raw, proof)
    else:
        ce.require(digest(original) == receipt["working_sha256"], "frozen input did not reproduce")
    checked = run / "checked.drat"
    check_log = run / "frozen.check.log"
    compact_log = run / "compact.check.log"
    limit = ("-t", str(args.check_seconds))
    try:
        t1, c1 = replay(args.checker, original, proof, check_log, ("-l", str(checked), "-C", *limit))
        t2, c2 = replay(args.checker, original, checked, compact_log, limit)
    except RuntimeError:
        return "CHECK_FAILED"
    metrics = dict(check_cpu_seconds=round(c1+c2, 4), check_wall_seconds=round(t1+t2, 4),
                   solver_cpu_seconds=receipt["cpu_seconds"] + receipt.get("proof_cpu_seconds", 0))
    # The frozen release format accepts an independently replayed external DRAT.
    # The separate search receipt identifies the actual input and solver command.
    metadata = ce.certificate_metadata(row, folder, original, checked, recipe,
                                       args.checker_sha256, compact_log, metrics=metrics)
    ce.atomic_json(folder / "verified.json", metadata)
    for name in ("frozen.cnf", "raw.drat", "prefix.drat", "lifted.drat", "checked.drat", "working.cnf"):
        (run / name).unlink(missing_ok=True)
    return "VERIFIED"


def run_one(row, args):
    recipe = dict(tables=True, total_critical=True, full_root=args.tier=="retry")
    family = family_of(row)
    variant = args.variant
    if variant == "auto":
        if recipe["full_root"] and fully_sending(row):
            variant = "senders"
        else:
            variant = "compact" if dispensable_counts(family, row, recipe) else "cached"
    kernel_hash = args.sender_sha256 if variant == "senders" else args.kernel_sha256
    folder = ce.case_dir(args.out, row["id"])
    folder.mkdir(parents=True, exist_ok=True)
    run = folder / "profile-fast-v1" / args.tier / variant / args.proof_mode / f"{args.seconds}s-{args.conflicts}"
    with (folder / "lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (folder / "verified.json").exists():
            ce.inspect_case(args.out, row)
            return "ALREADY_VERIFIED"
        run.mkdir(parents=True, exist_ok=True)
        record = run / "attempt.jsonl"
        work, raw, log = (run / n for n in ("working.cnf", "raw.drat", "kissat.log"))
        if record.exists():
            receipt = json.loads(record.read_text())
            ce.require(receipt["id"] == row["id"] and receipt["recipe"] == recipe
                       and receipt["variant"] == variant and receipt["solver"]["sha256"] == args.solver["sha256"]
                       and receipt["kernel_sha256"] == kernel_hash, "attempt configuration changed")
            if receipt["status"] == "SAT":
                ce.require(digest(run / "frozen.model") == receipt["model_sha256"], "saved model has changed")
            if receipt["status"] != "UNSAT":
                return receipt["status"]
        else:
            start = monotonic()
            if variant == "cached":
                chunks = ce.formula_chunks(row, recipe)
                with work.open("wb") as out:
                    out.writelines(chunks)
                stats = dict(clauses=int(chunks[0].split()[3]), bytes=work.stat().st_size)
            else:
                stats = working_formula(row, recipe, variant, work)
            working_sha = digest(work)
            setup_time = monotonic() - start
            search = kissat(args.solver, work, raw if args.proof_mode == "eager" else None,
                            log, args.seconds, args.conflicts)
            outcome = search["status"]
            receipt = dict(id=row["id"], branch=row["branch"], family=row["family"], recipe=recipe,
                           variant=variant, working_sha256=working_sha, proof_mode=args.proof_mode,
                           kernel_sha256=kernel_hash, solver=args.solver,
                           seconds=args.seconds, budget=args.conflicts, setup_wall=setup_time,
                           **search, **stats)
            if outcome == "SAT":
                checked_model(row, recipe, variant, log, run / "frozen.model")
                receipt["model_sha256"] = digest(run / "frozen.model")
            if outcome == "UNSAT" and args.proof_mode == "eager":
                receipt["raw_sha256"] = digest(raw)
            if outcome == "OPEN":
                raw.unlink(missing_ok=True)
                work.unlink()
            ce.atomic_json(record, receipt)
            if outcome != "UNSAT":
                return outcome
        if "raw_sha256" not in receipt:
            ce.require(digest(work) == receipt["working_sha256"], "pending search input has changed")
            tag = f"proof-{args.proof_seconds}s-{args.proof_conflicts}"
            saved = run / (tag + ".json")
            if saved.exists() and json.loads(saved.read_text())["status"] == "OPEN":
                return "PROOF_PENDING"
            search = kissat(args.solver, work, raw, run / (tag + ".log"),
                            args.proof_seconds, args.proof_conflicts)
            ce.atomic_json(saved, search)
            if search["status"] == "OPEN":
                raw.unlink(missing_ok=True)
                return "PROOF_PENDING"
            ce.require(search["status"] == "UNSAT", "solver outcomes disagree")
            receipt.update(raw_sha256=digest(raw), proof_attempt=saved.name,
                           proof_cpu_seconds=search["cpu_seconds"])
            ce.atomic_json(record, receipt)
        return publish(row, recipe, variant, folder, run, receipt, args)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", choices=("15,14,14,14",), default="15,14,14,14")
    p.add_argument("--out", type=Path, default=Path(os.environ.get("EV", ROOT / "evidence")))
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--shards", type=int, default=1)
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--tier", choices=("first", "retry"), default="first")
    p.add_argument("--variant", choices=VARIANTS, default="auto")
    p.add_argument("--limit", type=int)
    p.add_argument("--fully-sending", action="store_true", help="only the nine whole rows requiring all 15 senders")
    p.add_argument("--charge-one", action="store_true", help="the 299 rows with a single required sender")
    p.add_argument("--seconds", type=int)
    p.add_argument("--conflicts", type=int)
    p.add_argument("--proof-mode", choices=("deferred", "eager"), default="deferred")
    p.add_argument("--proof-seconds", type=int, help="time to reproduce a deferred UNSAT with proof")
    p.add_argument("--proof-conflicts", type=int, help="conflicts for that proof-producing rerun")
    p.add_argument("--check-seconds", type=int, default=int(os.environ.get("K58_CHECK_SECONDS", 300)))
    p.add_argument("--case-id", action="append", default=[])
    args = p.parse_args()
    if args.seconds is None:
        args.seconds = 12 if args.tier == "first" else 70
    if args.conflicts is None:
        args.conflicts = 400000 if args.tier == "first" else 2400000
    if args.proof_seconds is None:
        args.proof_seconds = max(60, 2*args.seconds)
    if args.proof_conflicts is None:
        args.proof_conflicts = 2*args.conflicts
    if (min(args.workers, args.check_seconds, args.seconds, args.conflicts,
            args.proof_seconds, args.proof_conflicts) < 1
            or not 0 <= args.shard < args.shards or (args.limit is not None and args.limit < 0)):
        p.error("invalid budget, worker count, limit or shard")
    args.out = args.out.resolve()
    args.solver = ce.tool_identity(ROOT / "bin/kissat", "Kissat")
    args.checker = str(ROOT / "bin/drat-trim")
    args.checker_sha256 = digest(Path(args.checker))
    args.kernel_sha256 = digest(Path(__file__).with_name("profile_kernel.py"))
    args.sender_sha256 = sha256((args.kernel_sha256 + digest(Path(__file__).with_name("sender_kernel.py"))).encode()).hexdigest()
    selected = set(args.case_id)
    rows = [r for r in ce.records(ROOT / "k58/case-ledger.jsonl.gz")
            if tuple(r["family"]["profile"]) == PROFILE and r["status"] == "OPEN"
            and int(r["id"], 16) % args.shards == args.shard
            and (not (args.fully_sending or args.variant=="senders") or fully_sending(r))
            and (not args.charge_one or r["charge"] == 1)
            and (not selected or r["id"] in selected)]
    if selected and selected != {r["id"] for r in rows}:
        p.error("a requested case is outside the profile or shard")
    rows = list(islice(rows, args.limit))
    for row in rows:
        ce.require(ce.identity(row) == row["id"], "ledger identity mismatch")
    counts = Counter()
    with ProcessPoolExecutor(max_workers=args.workers) as workers:
        for row, result in zip(rows, workers.map(partial(run_one, args=args), rows)):
            counts[result] += 1
            print(row["id"], result, flush=True)
    print(json.dumps(dict(counts), sort_keys=True))
    return 1 if counts["CHECK_FAILED"] or counts["PROOF_PENDING"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
