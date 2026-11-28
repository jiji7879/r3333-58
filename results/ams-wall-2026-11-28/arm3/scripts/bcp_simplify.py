#!/usr/bin/env python3
"""Simplify an appended suffix using only parent-BCP assignments.

The parent DIMACS body is retained byte-for-byte. Every retained suffix clause
is its exact residual under the parent unit closure; satisfied suffix clauses
are omitted. Remaining fresh variables are renamed contiguously.
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path


def read_cnf(path):
    raw = Path(path).read_bytes()
    clauses = []
    header = None
    pending = []
    for line in raw.splitlines():
        if not line or line.startswith(b"c"):
            continue
        if line.startswith(b"p"):
            assert header is None
            fields = line.split()
            assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
            header = (int(fields[2]), int(fields[3]))
            continue
        for token in line.split():
            lit = int(token)
            if lit:
                pending.append(lit)
            else:
                assert pending
                clauses.append(tuple(pending))
                pending = []
    assert not pending and header is not None
    assert len(clauses) == header[1]
    return raw, header[0], clauses


class BCP:
    """Occurrence-counter unit propagation with a reason per assignment."""
    def __init__(self, clauses, nv):
        self.clauses = clauses
        self.assignment = bytearray(nv + 1)  # 0 unknown, 1 true, 2 false
        self.reason = [None] * (nv + 1)
        self.occ = [[] for _ in range(2 * nv + 1)]
        self.remaining = [len(c) for c in clauses]
        self.satisfied = bytearray(len(clauses))
        self.queue = deque()
        for i, clause in enumerate(clauses):
            assert clause, "empty parent clause"
            for lit in clause:
                self.occ[self.key(lit)].append(i)
            if len(clause) == 1:
                self.queue.append((clause[0], i))
        self.conflict = None

    @staticmethod
    def key(lit):
        return 2 * (abs(lit) - 1) + (lit < 0)

    def value(self, lit):
        a = self.assignment[abs(lit)]
        if not a:
            return None
        return (a == 1) if lit > 0 else (a == 2)

    def assign(self, lit, reason):
        var = abs(lit)
        wanted = 1 if lit > 0 else 2
        if self.assignment[var]:
            if self.assignment[var] != wanted:
                self.conflict = reason
            return
        self.assignment[var] = wanted
        self.reason[var] = reason
        self.propagate_literal(lit)

    def propagate_literal(self, lit):
        for ci in self.occ[self.key(lit)]:
            self.satisfied[ci] = 1
        for ci in self.occ[self.key(-lit)]:
            if self.satisfied[ci]:
                continue
            self.remaining[ci] -= 1
            assert self.remaining[ci] >= 0
            if self.remaining[ci] == 0:
                self.conflict = ci
            elif self.remaining[ci] == 1:
                for candidate in self.clauses[ci]:
                    if self.value(candidate) is None:
                        self.queue.append((candidate, ci))
                        break

    def run(self):
        while self.queue and self.conflict is None:
            lit, reason = self.queue.popleft()
            value = self.value(lit)
            if value is True:
                continue
            if value is False:
                self.conflict = reason
                break
            self.assign(lit, reason)
        assert self.conflict is None, f"parent BCP conflict in clause {self.conflict}"
        # After closure no clause is conflicting or unit without being satisfied.
        for ci, clause in enumerate(self.clauses):
            values = [self.value(lit) for lit in clause]
            assert any(v is True for v in values) or values.count(None) >= 2, (ci, clause, values)
        return self.assignment


def residual(clause, assignment):
    kept = []
    for lit in clause:
        a = assignment[abs(lit)] if abs(lit) < len(assignment) else 0
        if not a:
            kept.append(lit)
        elif (a == 1) == (lit > 0):
            return None
    return tuple(kept)


def write_cnf(path, parent_raw, suffix, old_nv, mapping):
    marker = parent_raw.find(b"\n")
    assert marker >= 0 and parent_raw.startswith(b"p cnf ")
    parent_body = parent_raw[marker + 1:]
    parent_fields = parent_raw[:marker].split()
    parent_clauses = int(parent_fields[3])
    new_nv = old_nv + len(mapping)
    out = bytearray(f"p cnf {new_nv} {parent_clauses + len(suffix)}\n".encode())
    out.extend(parent_body)
    for clause in suffix:
        out.extend((" ".join(str(mapping.get(abs(x), abs(x)) * (-1 if x < 0 else 1))
                            for x in clause) + " 0\n").encode())
    Path(path).write_bytes(out)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", required=True)
    ap.add_argument("--augmented", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--metadata", required=True)
    args = ap.parse_args()
    parent_raw, parent_nv, parent = read_cnf(args.parent)
    augmented_raw, augmented_nv, augmented = read_cnf(args.augmented)
    assert len(augmented) >= len(parent)
    assert augmented[:len(parent)] == parent
    suffix = augmented[len(parent):]
    bcp = BCP(parent, parent_nv)
    assignment = bcp.run()
    unit_literals = [i if a == 1 else -i for i, a in enumerate(assignment) if i and a]
    kept = []
    residuals = []
    satisfied = 0
    for clause in suffix:
        r = residual(clause, assignment)
        if r is None:
            satisfied += 1
            residuals.append(None)
        else:
            assert r, "nonempty clause has empty parent-BCP residual"
            kept.append(r)
            residuals.append(r)
    used = sorted({abs(x) for c in kept for x in c if abs(x) > parent_nv})
    mapping = {old: parent_nv + i for i, old in enumerate(used, 1)}
    output = write_cnf(args.output, parent_raw, kept, parent_nv, mapping)
    # Read-back and exact clause-sequence checks.
    out_raw, out_nv, out_clauses = read_cnf(args.output)
    assert out_clauses[:len(parent)] == parent
    assert out_raw.split(b"\n", 1)[1][:len(parent_raw.split(b"\n", 1)[1])] == parent_raw.split(b"\n", 1)[1]
    assert len(out_clauses) == len(parent) + len(kept)
    for j, r in enumerate(r for r in residuals if r is not None):
        expected = tuple(mapping.get(abs(x), abs(x)) * (-1 if x < 0 else 1) for x in r)
        assert out_clauses[len(parent) + j] == expected
    meta = {
        "schema": "k58-configurable-mcf-parent-bcp-simplification/v1",
        "parent_sha256": hashlib.sha256(parent_raw).hexdigest(),
        "augmented_sha256": hashlib.sha256(augmented_raw).hexdigest(),
        "output_sha256": hashlib.sha256(output).hexdigest(),
        "parent_variables": parent_nv,
        "parent_clauses": len(parent),
        "parent_bcp_units": len(unit_literals),
        "parent_bcp_units_sha256": hashlib.sha256((" ".join(map(str, unit_literals)) + " 0\n").encode()).hexdigest(),
        "original_suffix_clauses": len(suffix),
        "suffix_clauses_satisfied": satisfied,
        "residual_suffix_clauses": len(kept),
        "original_augmented_variables": augmented_nv,
        "used_fresh_variables": len(used),
        "output_variables": out_nv,
        "fresh_variable_map": [[old, mapping[old]] for old in used],
        "scope": "Exact clause-wise simplification modulo parent unit propagation; no DRAT or physical-colouring claim.",
    }
    Path(args.metadata).write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({k: v for k, v in meta.items() if k != "fresh_variable_map"}, indent=2))


if __name__ == "__main__":
    main()
