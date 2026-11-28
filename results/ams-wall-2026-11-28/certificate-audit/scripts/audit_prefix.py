#!/usr/bin/env python3
"""Strict byte parser and parent/working/CAS-prefix identity audit.

This does not accept solver status. Proof validity is checked separately by
native drat-trim; here every proof byte and every DIMACS clause is accounted
for and the final active clause multiset is compared with working.cnf.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "inputs"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dimacs(path):
    data = path.read_bytes()
    text = data.decode("ascii")
    clauses = []
    current = []
    tokens = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("c"):
            continue
        tokens.extend(stripped.split())
    if len(tokens) < 4 or tokens[:2] != ["p", "cnf"]:
        raise ValueError(f"{path}: missing DIMACS header")
    nv, nc = int(tokens[2]), int(tokens[3])
    header = (nv, nc)
    for field in tokens[4:]:
        lit = int(field)
        if abs(lit) > nv:
            raise ValueError(f"{path}: literal outside header: {lit}")
        if lit == 0:
            clauses.append(tuple(current))
            current = []
        else:
            current.append(lit)
    if current or len(clauses) != nc:
        raise ValueError(f"{path}: truncated or wrong clause count")
    return header, clauses


def binary_proof(path):
    data = path.read_bytes()
    records = []
    pos = 0
    while pos < len(data):
        start = pos
        tag = data[pos]
        if tag not in (ord("a"), ord("d")):
            raise ValueError(f"invalid tag at byte {pos}: {tag}")
        pos += 1
        clause = []
        value = shift = 0
        while True:
            if pos == len(data):
                raise ValueError(f"truncated record beginning at byte {start}")
            byte = data[pos]
            pos += 1
            value |= (byte & 127) << shift
            if byte & 128:
                shift += 7
                if shift > 63:
                    raise ValueError(f"oversize literal at byte {start}")
                continue
            if value == 0:
                if byte != 0 or shift:
                    raise ValueError(f"noncanonical zero at byte {start}")
                break
            lit = value // 2 if value % 2 == 0 else -(value // 2)
            clause.append(lit)
            value = shift = 0
        records.append((chr(tag), tuple(clause)))
    return records


def main():
    ph, parent = dimacs(IN / "parent.cnf")
    wh, working = dimacs(IN / "working.cnf")
    proof = binary_proof(IN / "cas.drat")
    if ph[0] != wh[0]:
        raise ValueError("variable-header mismatch")
    active = Counter(parent)
    missing_deletions = 0
    empty_additions = 0
    additions = deletions = 0
    for tag, clause in proof:
        if any(abs(lit) > ph[0] for lit in clause):
            raise ValueError("proof literal outside parent header")
        if tag == "a":
            additions += 1
            if not clause:
                empty_additions += 1
            active[clause] += 1
        else:
            deletions += 1
            if active[clause] == 0:
                missing_deletions += 1
            else:
                active[clause] -= 1
                if active[clause] == 0:
                    del active[clause]
    delta = Counter(working) - Counter(parent)
    extra_working = Counter(working) - active
    extra_active = active - Counter(working)
    report = {
        "schema": "k58-cas-prefix-byte-and-multiset-audit/v1",
        "parent_sha256": sha(IN / "parent.cnf"),
        "working_sha256": sha(IN / "working.cnf"),
        "cas_sha256": sha(IN / "cas.drat"),
        "parent_header": ph,
        "working_header": wh,
        "parent_clauses_parsed": len(parent),
        "working_clauses_parsed": len(working),
        "working_minus_parent_distinct": sum(delta.values()),
        "working_minus_parent_unique": len(delta),
        "proof_bytes": (IN / "cas.drat").stat().st_size,
        "proof_records": len(proof),
        "proof_additions": additions,
        "proof_deletions": deletions,
        "proof_empty_additions": empty_additions,
        "missing_deletion_targets": missing_deletions,
        "final_active_clauses": sum(active.values()),
        "working_minus_final_active": sum(extra_working.values()),
        "final_active_minus_working": sum(extra_active.values()),
        "final_active_multiset_equals_working": active == Counter(working),
        "status_scope": "prefix identity only; DERIVATION, not a refutation",
    }
    out = ROOT / "checks" / "prefix-identity.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    assert report["final_active_multiset_equals_working"]
    assert not empty_additions and not missing_deletions
    assert sum(delta.values()) == 315


if __name__ == "__main__":
    main()
