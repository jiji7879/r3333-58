"""Bind proof checks to generated parent formulas and exact cover receipts."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import cache
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from pysat.formula import CNF

from anchor_cuts import cuts_for
from dense import marked_threshold
from gluing import Family,host,units
from joint_plan import cases
from matched_anchor import base_problem,digest


def formula_receipt(path):
    row=json.loads(path.read_text())
    fields=dict(row["family"])
    for field in ("profile","root_kinds"):
        fields[field]=tuple(fields[field])
    return Family(**fields),tuple(row["placement"]),row


def verify_matched(checker, root):
    counts = Counter()
    coverage = {}
    for path in sorted(Path(root).glob("*/*.jsonl")):
        f,p,row=formula_receipt(path)
        rebuilt,base=base_problem(row)
        assert rebuilt==f
        variant=row["variant"]
        assert variant in ("base","anchor")
        with TemporaryDirectory() as tmp:
            orig=Path(tmp,"parent.cnf")
            CNF(from_clauses=base).to_file(str(orig))
            assert digest(orig)==row["input_sha256"]
            augmented=orig
            if variant=="anchor":
                added=cuts_for(f,p)
                assert len(added)==row["cuts"]
                augmented=Path(tmp,"augmented.cnf")
                CNF(from_clauses=base+added).to_file(str(augmented))
            assert digest(augmented)==row["solver_input_sha256"]
            if row["status"]=="UNSAT":
                proof=path.with_suffix(".drat")
                assert digest(proof)==row["proof_sha256"]
                found=path.with_suffix(".cnf")
                assert CNF(from_file=str(found)).clauses==base
                run=subprocess.run([checker,str(orig),str(proof)],text=True,stdout=subprocess.PIPE)
                assert "s VERIFIED" in run.stdout.splitlines(),str(path)
                print(f"{proof} s VERIFIED",flush=True)
        counts[variant,row["status"]]+=1
        coverage.setdefault((f.root_kinds,row["branch"]),{})[variant]=row
    return counts,coverage


def lines(clauses):
    return b"".join((" ".join(map(str,cl))+" 0\n").encode() for cl in clauses)


@cache
def body():
    _,base=host(58)
    return lines(base), len(base), max(abs(lit) for cl in base for lit in cl)


def check_bytes(path, units_and_aux):
    payload, clauses, root_top=body()
    maximum=max(root_top,max((abs(x) for cl in units_and_aux for x in cl),default=0))
    prefix=f"p cnf {maximum} {clauses+len(units_and_aux)}\n".encode()
    suffix=lines(units_and_aux)
    with path.open("rb") as stream:
        assert stream.read(len(prefix))==prefix,path
        assert stream.read(len(payload))==payload,path
        assert stream.read()==suffix,path


def audit_receipt(task):
    path, checked = task
    f,p,row=formula_receipt(path)
    signature=(f,p,row["branch"],row["charge"])
    if row["status"]=="UNSAT":
        fixed=units(f,p)
        extra=marked_threshold(f,fixed,row["charge"],row["tables"],
                               row["total_critical"],row.get("full_root",False))
        cnf=path.with_suffix(".cnf")
        check_bytes(cnf,fixed+extra)
        if checked:
            proof=path.with_suffix(".drat")
            row=dict(row,formula_sha256=digest(cnf),proof_sha256=digest(proof),
                     formula=str(cnf),proof=str(proof),proof_bytes=proof.stat().st_size)
    return signature,row,checked


def verify_cover_type(folder,kind,verified,manifest,pool):
    profile=(16,16,15,10)
    expect={(f,p,b,charge) for f,p,b,charge in cases(profile,tuple(kind))}
    closed=set()
    validated=Counter()
    paths=[path for d in (Path(folder),Path(folder+"-retry")) for path in sorted(d.glob("*.jsonl"))]
    tasks=[(p,str(p.with_suffix(".drat")) in verified) for p in paths]
    for signature,row,checked in pool.map(audit_receipt,tasks,chunksize=4):
        assert signature in expect,signature
        if checked:
            assert row["status"]=="UNSAT"
            closed.add(signature)
            print(json.dumps(row),file=manifest)
        validated[row["status"]]+=1
    print(f"{kind} {len(closed)}/{len(expect)} checked exact cases {dict(validated)}",flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("checker")
    p.add_argument("--matched",action="store_true")
    p.add_argument("--root",default="matched")
    p.add_argument("--workers",type=int,default=4)
    args=p.parse_args()
    if args.matched:
        counts,cover=verify_matched(args.checker,args.root)
        print(dict(counts),flush=True)
        for variant in ("base","anchor"):
            rows=[value[variant] for value in cover.values() if variant in value]
            print(variant,"CPU seconds",round(sum(r["cpu"] for r in rows),3),flush=True)
        return
    checked={l.split()[0] for p in Path(".").glob("verified-B-*.txt")
             for l in p.read_text().splitlines() if l.endswith("s VERIFIED")}
    body()
    with Path("certified-inputs.jsonl").open("w") as manifest, ProcessPoolExecutor(max_workers=args.workers) as pool:
        for folder,kind in (("B-tut","TUT-"),("B-ttu","TTU-"),("B-ttt","TTT-")):
            if Path(folder).exists():
                verify_cover_type(folder,kind,checked,manifest,pool)


if __name__=="__main__":
    main()
