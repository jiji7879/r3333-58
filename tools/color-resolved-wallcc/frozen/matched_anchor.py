"""A matched benchmark of checker-certified C-anchor clauses on live K58 cases."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
from random import Random
from shutil import copyfileobj
import subprocess
from time import monotonic

from pysat.formula import CNF

from anchor_cuts import anchor_sets, binary_prefix, cuts_for
from dense import marked_threshold
from gluing import Family, host, units
from joint_plan import cases


PROFILE = (15,15,15,12)


def sample_sizes():
    random = Random(580113)
    sample = []
    for name, size in (("TTT-",12),("UUU-",6)):
        chosen = []
        count = 0
        for f, placement, index, charge in cases(PROFILE,tuple(name)):
            if len(anchor_sets(f,placement)[1])!=5:
                continue
            record = {"family":vars(f), "placement":placement, "branch":index,"charge":charge}
            count+=1
            if len(chosen) < size:
                chosen.append(record)
            else:
                next_slot=random.randrange(count)
                if next_slot<size:
                    chosen[next_slot]=record
        print(f"{name}: {count} live canonical cases with a five-vertex anchor",flush=True)
        sample.extend(sorted(chosen,key=lambda row:row["branch"]))
    return sample


def base_problem(row):
    fields=dict(row["family"])
    for key in ("profile","root_kinds"):
        fields[key]=tuple(fields[key])
    f=Family(**fields)
    fixed=units(f,row["placement"])
    _, base=host(58)
    extra=marked_threshold(f,fixed,row["charge"],tables=True,total_critical=True,full_root=row.get("full_root",False))
    return f, base+fixed+extra


def digest(path):
    h=sha256()
    with path.open("rb") as f:
        for piece in iter(lambda:f.read(1<<20),b""):
            h.update(piece)
    return h.hexdigest()


def run(row, variant, args):
    name="".join(row["family"]["root_kinds"])+str(row["branch"])
    out=Path(args.output,variant)
    out.mkdir(parents=True,exist_ok=True)
    root=out/name
    row = dict(row,full_root=getattr(args,"full_root",False))
    f,base=base_problem(row)
    extra=cuts_for(f,row["placement"]) if variant=="anchor" else []
    original=root.with_suffix(".cnf")
    CNF(from_clauses=base).to_file(str(original))
    solver_input=root.with_suffix(".aug.cnf") if extra else original
    if extra:
        CNF(from_clauses=base+extra).to_file(str(solver_input))
    raw=root.with_suffix(".raw")
    proof=root.with_suffix(".drat")
    log=root.with_suffix(".log")
    start=monotonic()
    with log.open("wb") as file:
        with subprocess.Popen([
            args.kissat,"--quiet",f"--time={args.seconds}",
            f"--conflicts={args.conflicts}",str(solver_input),str(raw)
        ],stdout=file,stderr=subprocess.STDOUT) as child:
            _,status,usage=os.wait4(child.pid,0)
            child.returncode=os.waitstatus_to_exitcode(status)
    outcome={20:"UNSAT",10:"SAT",0:"OPEN"}.get(child.returncode,"ERROR")
    record = dict(row, variant=variant, status=outcome, clauses=len(base),
                  cuts=len(extra), input_sha256=digest(original),
                  solver_input_sha256=digest(solver_input),
                  cpu=round(usage.ru_utime+usage.ru_stime,3),wall=round(monotonic()-start,3),
                  seconds=args.seconds,conflicts=args.conflicts)
    if outcome=="UNSAT":
        with proof.open("wb") as dest, raw.open("rb") as source:
            dest.write(binary_prefix(extra))
            copyfileobj(source,dest)
        record.update(proof_sha256=digest(proof),proof_bytes=proof.stat().st_size)
    if outcome=="OPEN":
        original.unlink()
    if solver_input!=original:
        solver_input.unlink()
    raw.unlink(missing_ok=True)
    root.with_suffix(".jsonl").write_text(json.dumps(record)+"\n")
    if outcome in ("SAT","ERROR"):
        raise RuntimeError(f"{outcome}: inspect {log}")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kissat",required=True)
    p.add_argument("--output",default="matched")
    p.add_argument("--seconds",type=int,default=16)
    p.add_argument("--conflicts",type=int,default=450000)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--cases",default="sample.json")
    p.add_argument("--variant",choices=("base","anchor"))
    p.add_argument("--full-root",action="store_true")
    args=p.parse_args()
    sample_path=Path(args.cases)
    if sample_path.exists():
        sample=json.loads(sample_path.read_text())
        if isinstance(sample,dict):
            sample=[sample]
    else:
        sample=sample_sizes()
        sample_path.write_text(json.dumps(sample,indent=2)+"\n")
    variants=(args.variant,) if args.variant else ("base","anchor")
    with ThreadPoolExecutor(max_workers=args.workers) as workers:
        for _ in workers.map(lambda pair:run(*pair,args),
                             ((r, variant) for r in sample for variant in variants)):
            pass


if __name__=="__main__":
    main()
