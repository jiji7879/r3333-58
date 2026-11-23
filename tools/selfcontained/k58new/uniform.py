"""Search the seven fully sending uniform children of the twisted (15,14,14,14) family."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
from functools import cache, partial
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic
from zipfile import ZipFile

from pysat.solvers import Minisat22
import cover_evidence as ce
from matched_anchor import digest
from profile_fast import kissat
from run_cover import replay
from uniform_kernel import DATA, PHYSICAL, build, eligible, normalize, obstruction, write_cnf

ROOT=Path(__file__).resolve().parents[1]
PROOFS=ROOT/'k58/uniform_proofs/theorems.zip'
DEFAULT="split"


@cache
def proof_identity():
    actual=digest(PROOFS)
    with ZipFile(PROOFS) as z:
        ce.require(DATA.read_bytes()==z.read("armtypes14.txt"),"catalogue differs from theorem inputs")
    ce.require(actual=="b362f243e714a3f99544aca9bbf0f2006e8e08adea205ca88c95c195f14622ce","unexpected compatibility proof package")
    return actual


def cube_text(words,types):
    return {"zero_sets":{str(x):list(s) for x,s in words.items()},
            "arm_types":{"BCD"[c-1]:i for c,i in types.items()}}


def decode_cube(raw):
    def unique(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError("duplicate cube key: "+k)
            d[k]=v
        return d
    cube=json.loads(raw,object_pairs_hook=unique)
    if not isinstance(cube,dict) or any(not isinstance(cube.get(k,{}),dict) for k in ("zero_sets","arm_types")):
        raise ValueError("cube and its fields must be JSON objects")
    return normalize(cube)


def model_values(text):
    values={}
    for line in text.splitlines():
        if line.startswith("v "):
            for lit in map(int,line[2:].split()):
                if lit and abs(lit)<=PHYSICAL:
                    value=lit>0
                    ce.require(abs(lit) not in values or values[abs(lit)]==value,"contradictory model")
                    values[abs(lit)]=value
    ce.require(len(values)==PHYSICAL,"incomplete physical colouring")
    return [i if values[i] else -i for i in range(1,PHYSICAL+1)]


def check_model(row,words,types,model):
    reference=build(row,words,types,"frozen-reference")
    with Minisat22(bootstrap_with=reference.clauses) as s:
        ce.require(s.solve(assumptions=model),"colouring fails uniform child or cube")


def rows():
    ledger=ROOT/'k58/case-ledger.jsonl.gz'
    current=[r for r in ce.records(ledger) if eligible(r) and r["status"]=="OPEN"]
    ce.require(len(current)==7 and all(r["id"]==ce.identity(r) for r in current),"unexpected uniform ledger")
    return current


def serial_hash(obj):
    return hashlib.sha256(ce.json_bytes(obj)).hexdigest()


def binding():
    return {p.name:digest(p) for p in [DATA,Path(__file__),ROOT/'k58/uniform_kernel.py',
            ROOT/'k58/profile_kernel.py',ROOT/'k58/gluing.py',ROOT/'k58/dense.py',ROOT/'k58/support_tables.py']}


def verify_result(record,row,folder,checker,check_seconds):
    cfg=record["config"]
    ce.require(cfg["scope"]=="uniform-child" and cfg["row"]==row["id"]==ce.identity(row) and eligible(row),
               "wrong row or scope")
    ce.require(cfg["implementation"]==binding() and cfg["theorems"]==proof_identity(),"recipe changed")
    words,types=normalize(cfg["cube"])
    status=record["status"]
    if status=="EXCLUDED_CUBE":
        found=obstruction(words,types)
        ce.require(found is not None and ce.json_bytes(found)==ce.json_bytes(record["reason"]),"obstruction mismatch")
    elif status=="SAT_CHILD":
        model=folder/'physical.model'
        ce.require(digest(model)==record["model_sha256"],"model has changed")
        check_model(row,words,types,model_values(model.read_text()))
    elif status=="VERIFIED_CHILD_UNSAT":
        proof=folder/'reference.drat'
        ce.require(digest(proof)==record["proof_sha256"],"proof has changed")
        with TemporaryDirectory(dir=folder) as scratch:
            fresh=Path(scratch)/'reference.cnf'
            write_cnf(build(row,words,types,"frozen-reference"),fresh)
            ce.require(digest(fresh)==record["reference_sha256"],"reference input changed")
            replay(checker,fresh,proof,Path(scratch)/'check.log',("-t",str(check_seconds)))
    else:raise ValueError("receipt contains no certified result: "+status)
    return status


def solve(job, args, solver, identity):
    row,word_types=job
    words,types=word_types
    cfg=dict(scope="uniform-child", row=row["id"], cube=cube_text(words,types), variant=args.variant,
             seconds=args.seconds,conflicts=args.conflicts,proof_seconds=args.proof_seconds,
             proof_conflicts=args.proof_conflicts,check_seconds=args.check_seconds,
             solver_sha256=solver["sha256"],checker_sha256=digest(ROOT/'bin/drat-trim'),
             implementation=identity,theorems=proof_identity())
    folder=args.out/row["id"]/serial_hash(cfg)
    folder.mkdir(parents=True,exist_ok=True)
    receipt=folder/'child.json'
    with (folder/'lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if receipt.exists():
            saved=json.loads(receipt.read_text())
            ce.require(saved["config"]==cfg,"incompatible cached attempt")
            if saved["status"] in ("EXCLUDED_CUBE","SAT_CHILD","VERIFIED_CHILD_UNSAT"):
                verify_result(saved,row,folder,str(ROOT/'bin/drat-trim'),args.check_seconds)
            return saved["status"],receipt
        record=dict(config=cfg)
        started=monotonic()
        reason=obstruction(words,types) if args.variant!="reference" else None
        if reason:
            record.update(status="EXCLUDED_CUBE",reason=reason,solver_calls=0)
        else:
            work=folder/'working.cnf'
            F=build(row,words,types,args.variant)
            write_cnf(F,work)
            record.update(variables=F.top,clauses=len(F.clauses),working_sha256=digest(work),
                          setup_wall=monotonic()-started,solver_calls=1)
            log=folder/'search.log'
            search=kissat(solver,work,None,log,args.seconds,args.conflicts)
            record["search"]=search
            if search["status"]=="SAT":
                model=model_values(log.read_text())
                check_model(row,words,types,model)
                dest=folder/'physical.model'
                dest.write_text('v '+' '.join(map(str,model))+' 0\n')
                record.update(status="SAT_CHILD",model_sha256=digest(dest))
            elif search["status"]=="OPEN":record["status"]="OPEN"
            else:
                ref=folder/'reference.cnf'
                proof=folder/'reference.drat'
                write_cnf(build(row,words,types,"frozen-reference"),ref)
                second=kissat(solver,ref,proof,folder/'reference.log',args.proof_seconds,args.proof_conflicts)
                record.update(reference=second,reference_sha256=digest(ref),solver_calls=2,status="PROOF_PENDING")
                if second["status"]=="SAT":
                    raise ValueError("reference SAT after working UNSAT")
                if second["status"]=="UNSAT":
                    replay(str(ROOT/'bin/drat-trim'),ref,proof,folder/'reference.check.log',
                           ("-t",str(args.check_seconds)))
                    record.update(status="VERIFIED_CHILD_UNSAT",proof_sha256=digest(proof))
                else:proof.unlink(missing_ok=True)
                ref.unlink()
            work.unlink()
        record["elapsed"]=monotonic()-started
        ce.atomic_json(receipt,record)
        return record["status"],receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant",choices=("reference","split","ordered"),default=DEFAULT)
    parser.add_argument("--case-id",action="append",default=[])
    parser.add_argument("--cube",action="append",type=Path,help="one JSON cube per file; repeatable")
    parser.add_argument("--seconds",type=int,default=12)
    parser.add_argument("--conflicts",type=int,default=400000)
    parser.add_argument("--proof-seconds",type=int,default=120)
    parser.add_argument("--proof-conflicts",type=int,default=4000000)
    parser.add_argument("--check-seconds",type=int,default=300)
    parser.add_argument("--workers",type=int,default=1)
    parser.add_argument("--out",type=Path,default=ROOT/'uniform-runs')
    parser.add_argument("--replay",type=Path,help="verify one child.json receipt")
    parser.add_argument("--verify-theorems",action="store_true",help="rebuild the bundled mathematical exclusions")
    args=parser.parse_args()
    if min(args.seconds,args.conflicts,args.proof_seconds,args.proof_conflicts,args.check_seconds,args.workers)<1:
        parser.error("budgets and worker count must be positive")
    proof_identity()
    if args.verify_theorems:
        with TemporaryDirectory() as temp:
            with ZipFile(PROOFS) as z:z.extractall(temp)
            subprocess.run([sys.executable,'verify.py','--jobs',str(args.workers)],cwd=temp,check=True)
        return 0
    available={r["id"]:r for r in rows()}
    if args.replay:
        r=json.loads(args.replay.read_text())
        print(verify_result(r,available[r["config"]["row"]],args.replay.parent,str(ROOT/'bin/drat-trim'),args.check_seconds))
        return 0
    if set(args.case_id)-set(available):
        parser.error("case ID is outside the seven supported uniform children")
    try:
        cubes=[decode_cube(path.read_text()) for path in args.cube] if args.cube else [({},{})]
    except (ValueError,TypeError,OSError) as e:parser.error(str(e))
    selected=[r for i,r in available.items() if not args.case_id or i in args.case_id]
    jobs=[(r,cube) for r in selected for cube in cubes]
    solver=ce.tool_identity(ROOT/'bin/kissat',"Kissat")
    counts=Counter()
    worker=partial(solve,args=args,solver=solver,identity=binding())
    with ProcessPoolExecutor(args.workers) as pool:
        for status,receipt in pool.map(worker,jobs):
            counts[status]+=1
            print(status,receipt,flush=True)
    print(json.dumps(counts,sort_keys=True))
    return int(bool(counts["PROOF_PENDING"]))


if __name__=="__main__":raise SystemExit(main())
