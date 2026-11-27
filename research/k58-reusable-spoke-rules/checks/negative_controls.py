#!/usr/bin/env python3
"""Two actual rejecting controls with an example physical refutation."""
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

P, DRAT, OUTPUT = map(Path, sys.argv[1:])
r = json.loads((P / "examples.json").read_bytes())[0]
parent = gzip.decompress((P / "parents" / f"{r['index']}.cnf.gz").read_bytes())
proof = gzip.decompress((P / "proofs" / r["proof"]).read_bytes())
pins = []
for u, v, c in ((r["x"],r["u"],r["alpha"]),(r["x"],r["v"],r["beta"])):
    edges = []
    for i,(a,b) in enumerate(__import__("itertools").combinations(range(58),2)):
        if {a,b} == {u,v}:
            pins.append(4*i+1+c)
            break


def append(raw, cs):
    h,b = raw.split(b"\n",1)
    n,m = map(int,h.split()[2:])
    return f"p cnf {n} {m+len(cs)}\n".encode() + b + b"".join(
        (" ".join(map(str,c)) + " 0\n").encode() for c in cs)

query = append(parent, [[lit] for lit in pins])
assert hashlib.sha256(query).hexdigest() == r["query"]
# Positive pin units alone are satisfiable by making all these literals true.
control = append(b"p cnf 19218 0\n", [[lit] for lit in pins])
assert all(lit > 0 for lit in pins)
records = []
for label,q,pf in [("satisfiable_pin_units_only",control,proof),
                   ("genuine_proof_half_truncated",query,proof[:len(proof)//2])]:
    identifier = Path(".scratch/reusable-spoke-rules-v1/negative-controls")
    identifier.mkdir(parents=True,exist_ok=True)
    qf,pf_file = identifier/(label+".cnf"),identifier/(label+".proof")
    qf.write_bytes(q); pf_file.write_bytes(pf)
    run = subprocess.run([DRAT,qf,pf_file,"-i","-U","-t","600"],capture_output=True)
    text = (run.stdout+run.stderr).decode("latin1").replace("\r\n","\n").replace("\r","\n")
    accepted = run.returncode == 0 and sum(l.strip()=="s VERIFIED" for l in text.splitlines())==1 and "WARNING" not in text.upper()
    records.append({"label":label,"rc":run.returncode,
                    "verified_lines":sum(l.strip()=="s VERIFIED" for l in text.splitlines()),
                    "warnings":text.upper().count("WARNING"),"errors":text.upper().count("ERROR"),
                    "strict_accept":accepted,"output":text})
    qf.unlink(); pf_file.unlink()
assert all(not x["strict_accept"] and x["rc"] != 0 and x["verified_lines"] == 0 for x in records)
OUTPUT.write_text(json.dumps({"controls":records,"all_rejected":True},indent=1)+"\n")
for x in records:print(x["label"],"rejected",x["rc"],"verified_lines",x["verified_lines"])
