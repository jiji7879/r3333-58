#!/usr/bin/env python3
"""Strict replay after stripping only DRAT deletion records.

The raw archive has warning-bearing (though rc=0/s VERIFIED) proofs. This does
not hide warnings: parses every a/d record, preserves every addition exactly,
and drops deletions only. If the original proof is valid RUP, adding redundant
clauses back can only preserve verification. No original file is edited.

Usage: repair_replay.py PACKAGE_ROOT DRAT_TRIM OUTPUT_DIR SUMMARY.json
PACKAGE_ROOT contains hard-more/ and hard-study/.
"""
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

P, DRAT, WORK, OUT = map(Path, sys.argv[1:])
P = P.resolve(); DRAT = DRAT.resolve(); WORK = WORK.resolve()
assert not WORK.is_relative_to(P), "Do not overwrite package inputs"
WORK.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(P / "hard-study"))
from probe import rows, build


def decode_records(raw):
    pos = 0
    while pos < len(raw):
        tag = raw[pos]
        end = raw.index(0, pos + 1)
        assert tag in (97, 100), f"invalid tag {tag} at {pos}"
        if tag == 97:
            values, shift, value, lits = [], 0, 0, []
            for byte in raw[pos + 1:end]:
                value |= (byte & 127) << shift
                if byte & 128:
                    shift += 7
                else:
                    lits.append(-(value // 2) if value & 1 else value // 2)
                    value = shift = 0
            assert shift == 0 and value == 0
            yield lits
        pos = end + 1


def encode_add(clause):
    data = bytearray(b"a")
    for lit in clause:
        value = 2 * abs(lit) + int(lit < 0)
        while value >= 128:
            data.append(128 | (value & 127)); value >>= 7
        data.append(value)
    data.append(0)
    return bytes(data)


def stripped(raw):
    return b"".join(encode_add(c) for c in decode_records(raw))


results = []
for file in sorted((P / "hard-more").glob("*.json")):
    rec = json.loads(file.read_bytes())
    if not isinstance(rec, dict) or not rec.get("verified"):
        continue
    rank, category, sender, first_literal = rec["rank"], rec["category"], rec["sender"], rec["spokes"][0]
    stem = f"{rank}-{category}-{sender}-{first_literal}"
    source = P / "hard-more" / (stem + ".drat.gz")
    raw_proof = gzip.decompress(source.read_bytes())
    assert hashlib.sha256(raw_proof).hexdigest() == rec["proof"], f"raw proof mismatch: {stem}"
    # Independent fake-query rejection would be expected only with actual
    # metadata, so rebuild the exact pinned parent as the original verifier does.
    g = {}
    raw, _, _, _ = build(rows[rank - 1], g)
    clause = [-g[sender][1], *rec["spokes"]]
    assert rec["clause"] == clause, f"guard mismatch: {stem}"
    pins = [-l for l in clause]
    head, body = raw.split(b"\n", 1)
    _, _, nv, nc = head.split()
    query = (f"p cnf {int(nv)} {int(nc) + len(pins)}\n".encode() + body +
             b"".join(b"%d 0\n" % l for l in pins))
    assert hashlib.sha256(query).hexdigest() == rec["query"], f"query mismatch: {stem}"
    proof = stripped(raw_proof)
    (WORK / (stem + ".rup")).write_bytes(proof)
    with tempfile.TemporaryDirectory(dir=WORK) as tmp:
        qf = Path(tmp, "q.cnf")
        pf = Path(tmp, "p.rup")
        qf.write_bytes(query)
        pf.write_bytes(proof)
        run = subprocess.run([DRAT, qf, pf, "-i", "-U", "-W", "-t", "600"], capture_output=True)
        normal = (run.stdout + run.stderr).decode("latin1").replace("\r\n", "\n").replace("\r", "\n")
    import re
    reads = [int(m.group(1)) for m in re.finditer(r"read (\d+) bytes from proof file", normal)]
    allowed = (run.returncode == 0 and
               [line for line in normal.splitlines() if line.startswith("s ")] == ["s VERIFIED"] and
               "WARNING" not in normal.upper() and "ERROR" not in normal.upper() and
               "NOT VERIFIED" not in normal and "UNKNOWN" not in normal and
               "DERIVATION" not in normal and reads == [len(proof)])
    log = WORK / (stem + ".out")
    log.write_text(normal)
    results.append({"rank": rank, "category": category, "clause": clause,
                    "parent_sha256": rec["parent"], "query_sha256": rec["query"],
                    "original_proof_sha256": rec["proof"],
                    "original_proof_bytes": len(raw_proof),
                    "normalised_proof_sha256": hashlib.sha256(proof).hexdigest(),
                    "normalised_proof_bytes": len(proof),
                    "raw_deletion_records_stripped": True,
                    "strict_rup_gate_accepted": allowed,
                    "checker_rc": run.returncode,
                    "bytes_fully_read": reads == [len(proof)],
                    "zero_warnings_or_errors": "WARNING" not in normal.upper() and "ERROR" not in normal.upper(),
                    "rat_zero_in_core": "0 RAT lemmas in core" in normal,
                    "log": str(log)})
    print(stem, "strict_accepted", allowed, "old_bytes", len(raw_proof), "new_bytes", len(proof))

assert len(results) == 16, len(results)
summary = {"original_batch_emitted_warnings": True,
           "original_batch_status": "strict unmodified batch aborted on warnings; not a clean 16/16 pass before deletion-only normalisation",
           "normalisation": "parse and remove ONLY deletion records, retain all addition records",
           "complete_examples": len(results),
           "strict_rup_accepted": sum(x["strict_rup_gate_accepted"] for x in results),
           "full_byte_reads": sum(x["bytes_fully_read"] for x in results),
           "zero_warning_or_error_outputs": sum(x["zero_warnings_or_errors"] for x in results),
           "zero_RAT_in_core": sum(x["rat_zero_in_core"] for x in results),
           "original_total_proof_bytes": sum(x["original_proof_bytes"] for x in results),
           "normalised_total_proof_bytes": sum(x["normalised_proof_bytes"] for x in results),
           "records": results}
OUT.write_text(json.dumps(summary, indent=1) + "\n")
print(json.dumps({k:v for k,v in summary.items() if k != 'records'}, indent=1))
assert summary["strict_rup_accepted"] == len(results) == summary["full_byte_reads"] == summary["zero_warning_or_error_outputs"]
assert summary["zero_RAT_in_core"] == len(results)
