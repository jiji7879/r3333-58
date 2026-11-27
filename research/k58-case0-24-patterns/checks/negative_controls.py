#!/usr/bin/env python3
"""Discriminating controls against one actual terminal arm proof; no solver."""
import gzip
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path

P, DRAT, WORK, OUTPUT = map(Path, sys.argv[1:])
WORK.mkdir(parents=True, exist_ok=True)
f = json.loads((P / "frontier.json").read_text())
parent = gzip.decompress((P / "signed-parent.cnf.gz").read_bytes())
OFF = {e: 4*i+1 for i, e in enumerate(itertools.combinations(range(58), 2))}
E = list(itertools.combinations(range(31, 45), 2))
edge = lambda a, b, h: OFF[tuple(sorted((a, b)))] + h
record = next(r for r in f["patterns"] if r["status"] == "REFINED")
h, word, model = record["color"], record["word"], record["arm_colorings"][0]
pins = ([edge(31, 42, h), *f["trigger"],
         *[edge(*e, int(k)) for e, k in zip(f["signature_edges"], word)],
         *[edge(*e, int(k)) for e, k in zip(E, model)]])
cell = record["arms"][0]
proof = (P / "proofs" / (cell["proof"] + ".rup")).read_bytes()


def append(raw, cs):
    h, b = raw.split(b"\n", 1)
    n, m = map(int, h.split()[2:])
    return f"p cnf {n} {m + len(cs)}\n".encode() + b + b"".join(
        (" ".join(map(str, c)) + (" " if c else "") + "0\n").encode() for c in cs)


query = append(parent, [[l] for l in pins])
assert hashlib.sha256(query).hexdigest() == cell["query"]
sat_query = append(b"p cnf 19218 0\n", [[l] for l in pins])
# Every literal is positive. Repeated pivot/word units already appear in
# the full 91-edge arm pin; duplicates are harmless units. The control CNF
# has no AMO clauses, so making these positive literals true satisfies it.
assert all(l > 0 for l in pins)

results = []
for label, q, pf in [("satisfiable_units_query", sat_query, proof),
                     ("genuine_proof_half_truncated", query, proof[:len(proof)//2])]:
    qf = WORK / (label + ".cnf")
    pf_path = WORK / (label + ".proof")
    qf.write_bytes(q)
    pf_path.write_bytes(pf)
    r = subprocess.run([DRAT, qf, pf_path, "-i", "-U", "-t", "600"], capture_output=True)
    text = (r.stdout + r.stderr).decode("latin-1")
    normal = text.replace("\r\n", "\n").replace("\r", "\n")
    accepted = (r.returncode == 0 and
                sum(l.strip() == "s VERIFIED" for l in normal.splitlines()) == 1 and
                "WARNING" not in normal.upper() and "ERROR" not in normal.upper())
    results.append({"label": label, "query_sha256": hashlib.sha256(q).hexdigest(),
                    "proof_sha256": hashlib.sha256(pf).hexdigest(), "returncode": r.returncode,
                    "exact_verified_lines": sum(l.strip() == "s VERIFIED" for l in normal.splitlines()),
                    "warning_count": normal.upper().count("WARNING"),
                    "error_count": normal.upper().count("ERROR"),
                    "strict_accept": accepted, "must_reject": True,
                    "query_bytes": len(q), "proof_bytes_read": len(pf), "output": normal})
    qf.unlink()
    pf_path.unlink()
assert all(x["strict_accept"] is False and x["returncode"] != 0 for x in results)
OUTPUT.write_text(json.dumps({"controls": results, "all_rejected": True}, indent=1) + "\n")
for r in results:
    print(r["label"], "rejected", "rc", r["returncode"], "verified_lines", r["exact_verified_lines"],
          "warnings", r["warning_count"], "errors", r["error_count"])
