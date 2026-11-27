#!/usr/bin/env python3
"""Strict RUP replay after removing only binary DRAT deletion records."""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode_additions(raw):
    pos = 0
    deletions = 0
    additions = 0
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
            additions += 1
            yield lits
        else:
            deletions += 1
        pos = end + 1
    assert pos == len(raw)


def encode_add(clause):
    data = bytearray(b"a")
    for lit in clause:
        value = 2 * abs(lit) + int(lit < 0)
        while value >= 128:
            data.append(128 | (value & 127))
            value >>= 7
        data.append(value)
    data.append(0)
    return bytes(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("certificate_dir", type=Path)
    ap.add_argument("--checker", required=True)
    args = ap.parse_args()
    folder = args.certificate_dir
    raw = (folder / "proof.drat").read_bytes()
    # consume generator fully before writing anything
    clauses = list(decode_additions(raw))
    normalized = b"".join(encode_add(clause) for clause in clauses)
    output = folder / "proof-nodeletions.drat"
    output.write_bytes(normalized)
    command = [args.checker, str(folder / "query.cnf"), str(output),
               "-i", "-U", "-W", "-t", "300"]
    begin = time.monotonic()
    run = subprocess.run(command, capture_output=True, timeout=300)
    wall = time.monotonic() - begin
    log = (run.stdout + run.stderr).decode("latin1").replace("\r\n", "\n").replace("\r", "\n")
    (folder / "checker-nodeletions.log").write_text(log)
    reads = [int(m.group(1)) for m in re.finditer(r"read (\d+) bytes from proof file", log)]
    status_lines = [line for line in log.splitlines() if line.startswith("s ")]
    accepted = (run.returncode == 0 and status_lines == ["s VERIFIED"] and
                "WARNING" not in log.upper() and "ERROR" not in log.upper() and
                "NOT VERIFIED" not in log and "UNKNOWN" not in log and
                "DERIVATION" not in log and reads == [len(normalized)])
    rec = {"query_sha256": sha((folder / "query.cnf").read_bytes()),
           "original_proof_bytes": len(raw), "original_proof_sha256": sha(raw),
           "normalized_proof_bytes": len(normalized), "normalized_proof_sha256": sha(normalized),
           "addition_records_retained": sum(1 for _ in clauses),
           "normalization": "parse full binary stream; retain every a addition/order, remove only d deletion records",
           "checker_command": command, "checker_returncode": run.returncode,
           "checker_wall_seconds": wall, "status_lines": status_lines,
           "proof_file_bytes_read": reads, "strict_accepted": accepted,
           "zero_RAT_in_core": "0 RAT lemmas in core" in log,
           "zero_warning_or_error_output": "WARNING" not in log.upper() and "ERROR" not in log.upper()}
    (folder / "strict-replay.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, sort_keys=True))
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
