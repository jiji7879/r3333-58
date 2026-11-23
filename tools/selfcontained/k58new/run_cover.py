"""Run, verify, and resume a bounded or complete shard of the frozen K58 cover."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import fcntl
import gzip
from itertools import islice
import json
import os
from pathlib import Path
from random import Random
import subprocess
from time import monotonic

from audit_campaign import check_bytes
from cover_evidence import certificate_metadata, identity as case_id, tool_identity, validate_artifact
from dense import marked_threshold, solve_case
from gluing import Family, units
from matched_anchor import digest


CHECK_SECONDS = int(os.environ.get("K58_CHECK_SECONDS", "300"))


def open_rows(args):
    with gzip.open(args.ledger, "rt") as handle:
        for line in handle:
            row = json.loads(line)
            if row["status"] != "OPEN" and not getattr(args, "include_closed", False):
                continue
            assert row["id"] == case_id(row), row["id"]
            if ids := getattr(args, "case_ids", None):
                if row["id"] not in ids:
                    continue
            if int(row["id"], 16) % args.shards != args.shard:
                continue
            info = row["family"]
            if args.profile and ",".join(map(str,info["profile"])) != args.profile:
                continue
            if args.kinds and "".join(info["root_kinds"]) != args.kinds:
                continue
            yield row


def selected_rows(args):
    stream = open_rows(args)
    if args.sample_per_type:
        rng = Random(args.seed)
        samples = defaultdict(list)
        counts = Counter()
        for row in stream:
            f = row["family"]
            group = (tuple(f["profile"]), tuple(f["root_kinds"]), f["marked_size"])
            counts[group] += 1
            candidates = samples[group]
            if len(candidates) < args.sample_per_type:
                candidates.append(row)
            else:
                slot = rng.randrange(counts[group])
                if slot < args.sample_per_type:
                    candidates[slot] = row
        stream = (row for group in sorted(samples) for row in samples[group])
    yield from islice(stream, args.limit)


def write_json(path, data):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data,sort_keys=True)+"\n")
    temp.replace(path)


def replay(checker, formula, proof, log, extra=()):
    started = monotonic()
    with log.open("w") as stream:
        with subprocess.Popen([checker,str(formula),str(proof),*extra],
                              stdout=stream,stderr=subprocess.STDOUT) as child:
            _,status,usage=os.wait4(child.pid,0)
            child.returncode=os.waitstatus_to_exitcode(status)
    if child.returncode != 0 or "s VERIFIED" not in log.read_text().splitlines():
        raise RuntimeError(f"Proof replay did not pass: {log}")
    return monotonic()-started, usage.ru_utime+usage.ru_stime


def read_saved(path):
    return json.loads(path.read_text()) if path.exists() else None


def run_one(row, tier, args):
    case = args.output / row["id"][:2] / row["id"]
    case.mkdir(parents=True, exist_ok=True)
    fixed_mark = case/"verified.json"
    with (case/"lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        old = read_saved(fixed_mark)
        if old:
            assert old["id"] == row["id"]
            if old.get("schema") == 1:
                validate_artifact(case, old["certificate"])
                return "ALREADY_VERIFIED"
            if getattr(args, "publication", False):
                raise ValueError(f"Use import-legacy for {fixed_mark} or choose a new --output")
            for part in ("formula","proof"):
                assert digest(case/old[part]) == old[part+"_sha256"], old[part]
            return "ALREADY_VERIFIED"
        info = dict(row["family"])
        for key in ("profile","root_kinds"):
            info[key] = tuple(info[key])
        family = Family(**info)
        name = f"{''.join(family.root_kinds)}_{family.arm}_{row['branch']}"
        first = case/"first"/(name+".jsonl")
        if tier == "retry":
            result = read_saved(first)
            if result is None or result["status"] != "OPEN":
                return "NO_OPEN_FIRST_ATTEMPT"
        config = argparse.Namespace(
            kissat=args.kissat,tables=True,total_critical=True,full_root=tier=="retry",
            seconds=args.seconds if tier=="first" else args.retry_seconds,
            budget=args.conflicts if tier=="first" else args.retry_conflicts,
            solver_identity=getattr(args, "solver_identity", None),
        )
        dest = case/tier
        if tier=="retry":
            dest = dest/f"{config.seconds}s-{config.budget}"
        root = dest/name
        receipt = root.with_suffix(".jsonl")
        if not receipt.exists():
            solve_case(family,row["placement"],row["branch"],row["charge"],config,dest)
        result = json.loads(receipt.read_text())
        assert result["branch"]==row["branch"] and result["charge"]==row["charge"]
        assert result["family"]==row["family"] and result["placement"]==row["placement"]
        assert result["tables"] and result["total_critical"]
        assert result["full_root"]==config.full_root
        if result["status"] == "OPEN":
            return "OPEN"
        if result["status"] != "UNSAT":
            raise RuntimeError(f"Review {receipt}; solver status {result['status']}")
        formula = root.with_suffix(".cnf")
        proof = root.with_suffix(".drat")
        if not getattr(args, "publication", False):
            fixed = units(family,row["placement"])
            extra = marked_threshold(family,fixed,row["charge"],True,True,config.full_root)
            check_bytes(formula,fixed+extra)
        trim_args = ()
        if args.trim:
            trimmed = root.with_suffix(".compact")
            trim_args = ("-l",str(trimmed),"-C")
        limit = ("-t", str(CHECK_SECONDS))
        try:
            check_time,check_cpu = replay(args.checker,formula,proof,
                                          root.with_suffix(".check.log"),trim_args + limit)
            kept = proof
            if args.trim:
                trim_wall,trim_cpu = replay(args.checker,formula,trimmed,
                                            root.with_suffix(".compact.log"),limit)
                check_time += trim_wall
                check_cpu += trim_cpu
                kept = trimmed
        except RuntimeError as exc:
            # The checker rejected the proof or hit the time limit.  Write no
            # verified.json, so the case stays OPEN, and keep the shard running.
            sizes = {p.name + "_bytes": p.stat().st_size for p in (formula, proof) if p.exists()}
            (case/"CHECK_FAILED.json").write_text(
                __import__("json").dumps(dict(id=row["id"], stage=tier, limit_seconds=CHECK_SECONDS,
                                              reason=str(exc)[:400], **sizes), sort_keys=True) + "\n")
            return "CHECK_FAILED"
        if getattr(args, "publication", False):
            if "solver" not in result:
                raise ValueError(f"Use import-legacy for {receipt} or choose a new --output")
            evidence = certificate_metadata(
                row, case, formula, kept, result, args.checker_sha256,
                root.with_suffix(".compact.log"),
                artifacts=(receipt, root.with_suffix(".log"), root.with_suffix(".check.log")),
                metrics=dict(check_wall_seconds=round(check_time, 3),
                             check_cpu_seconds=round(check_cpu, 3),
                             solver_cpu_seconds=result["cpu_seconds"]),
            )
            write_json(fixed_mark, evidence)
            for path in (formula, proof, kept):
                path.unlink(missing_ok=True)
            return "VERIFIED"
        write_json(fixed_mark,dict(
            id=row["id"],tier=tier,formula=str(formula.relative_to(case)),
            proof=str(kept.relative_to(case)),formula_sha256=digest(formula),
            proof_sha256=digest(kept),proof_bytes=kept.stat().st_size,
            check_wall_seconds=round(check_time,3),check_cpu_seconds=round(check_cpu,3),
            solver_cpu_seconds=result["cpu_seconds"],checker_sha256=args.checker_sha256
        ))
        if args.trim:
            proof.unlink()
        return "VERIFIED"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger",type=Path,default=Path("case-ledger.jsonl.gz"))
    p.add_argument("--kissat",required=True)
    p.add_argument("--checker",required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--workers",type=int,default=6)
    p.add_argument("--tier",choices=("first","retry","both"),default="first")
    p.add_argument("--seconds",type=int,default=12)
    p.add_argument("--conflicts",type=int,default=400000)
    p.add_argument("--retry-seconds",type=int,default=70)
    p.add_argument("--retry-conflicts",type=int,default=2400000)
    p.add_argument("--shards",type=int,default=1)
    p.add_argument("--shard",type=int,default=0)
    p.add_argument("--profile")
    p.add_argument("--kinds")
    p.add_argument("--limit",type=int)
    p.add_argument("--sample-per-type",type=int)
    p.add_argument("--seed",type=int,default=581179)
    p.add_argument("--trim",action="store_true")
    p.add_argument("--publication", action="store_true",
                   help="Store replayable compressed certificates, exact recipes and execution evidence")
    p.add_argument("--include-closed", action="store_true",
                   help="Also solve selected historically closed rows, for direct certificates")
    p.add_argument("--case-id", action="append", dest="case_ids", metavar="SHA256",
                   help="Select a specific case ID, repeatable")
    args = p.parse_args()
    if args.workers < 1 or not 0 <= args.shard < args.shards:
        p.error("Use at least one worker and a shard index in [0, shards).")
    args.kissat = str(Path(args.kissat).resolve())
    args.checker = str(Path(args.checker).resolve())
    args.checker_sha256 = digest(Path(args.checker))
    if args.case_ids:
        requested = set(args.case_ids)
        args.case_ids = requested
        if requested != {row["id"] for row in open_rows(args)}:
            p.error("A requested case ID is missing or excluded by the current filters")
    if args.publication:
        args.trim = True
        args.solver_identity = tool_identity(args.kissat, "Kissat")
    totals = {}
    tiers = ("first","retry") if args.tier=="both" else (args.tier,)
    with ThreadPoolExecutor(max_workers=args.workers) as workers:
        for tier in tiers:
            source=iter(selected_rows(args))
            counts=Counter()
            processed=0
            while batch := tuple(islice(source,2*args.workers)):
                counts.update(workers.map(lambda row:run_one(row,tier,args),batch))
                processed+=len(batch)
                if processed//100 > (processed-len(batch))//100:
                    print(tier,processed,dict(counts),flush=True)
            totals[tier]=dict(counts)
    print(json.dumps(totals,sort_keys=True))


if __name__=="__main__":
    main()
