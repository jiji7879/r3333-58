#!/usr/bin/env python3
"""lrat_rup_check -- an independent, from-scratch RUP-only LRAT checker.

Purpose
-------
Cross-check a trimmed LRAT refutation against the *original* DIMACS CNF with a
second implementation, written here, so that acceptance does not rest on one
checker (lrat-trim).  This is deliberately a small, RUP-only checker: it does
not implement RAT, so it REJECTS any proof that needs a RAT step.  It is
unverified code, not a trusted checker; its only claim is that acceptance by
two independent implementations of the LRAT/RUP semantics is stronger evidence
than acceptance by one.

Semantics implemented (LRAT, ASCII)
----------------------------------
A proof is a sequence of operations.

  <id> <lit> ... 0 <hint> ... 0        addition of clause <id>
  <id> d <id> ... 0                    deletion of the listed clause ids

where the addition's hints are the clause ids of the unit-propagation
antecedents, in the order in which the propagation is performed: negate every
literal of the added clause, then for each hint clause in turn it must be unit
under the current assignment (propagate its literal) or falsified (the chain
found a conflict).  The addition is accepted iff the hint list ends in a
conflict.  A refutation must additionally contain an accepted empty clause.

Deliberate non-features: no RAT (negative hint ids are refused), no binary
input (the caller passes an ASCII proof), no proof trimming, no strict
resolution-chain (RAT-pivot) syntax, no clause minimisation.  Reading a
malformed or truncated file is an error, never a partial success.

Exit status: 20 = refutation verified, 1 = rejected/error.
"""
from __future__ import annotations

import argparse
import sys


class Reject(RuntimeError):
    pass


def read_cnf(path):
    """Return (nvars, {id: tuple-of-lits}) for a 'p cnf' DIMACS file."""
    nv = None
    db = {}
    nxt = 1
    clause = []
    with open(path, "r", encoding="ascii") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] == "c":
                continue
            if s[0] == "p":
                parts = s.split()
                if parts[:2] != ["p", "cnf"] or len(parts) != 4:
                    raise Reject("%s: bad header %r" % (path, s[:60]))
                nv = int(parts[2])
                continue
            for tok in s.split():
                x = int(tok)
                if x == 0:
                    db[nxt] = tuple(clause)
                    nxt += 1
                    clause = []
                else:
                    clause.append(x)
    if nv is None:
        raise Reject("%s: no 'p cnf' header" % path)
    if clause:
        raise Reject("%s: unterminated final clause" % path)
    return nv, db


def check(cnf_path, lrat_path, verbose=False):
    nv, db = read_cnf(cnf_path)
    val = [0] * (nv + 1)  # 0 unassigned, 1 true, -1 false

    n_added = n_deleted = 0
    n_steps = 0
    saw_empty = False
    empty_id = None

    with open(lrat_path, "r", encoding="ascii") as f:
        for lineno, line in enumerate(f, 1):
            toks = line.split()
            if not toks or toks[0] == "c":
                continue
            try:
                op_id = int(toks[0])
            except ValueError:
                raise Reject("line %d: first token %r is not an integer" % (lineno, toks[0]))

            if len(toks) > 1 and toks[1] == "d":
                ids = [int(t) for t in toks[2:]]
                if not ids or ids[-1] != 0:
                    raise Reject("line %d: unterminated deletion line" % lineno)
                for cid in ids[:-1]:
                    if cid not in db:
                        raise Reject("line %d: deletion of absent id %d" % (lineno, cid))
                    del db[cid]
                n_deleted += len(ids) - 1
                continue

            # addition: <id> lits 0 hints 0
            seq = [int(t) for t in toks[1:]]
            try:
                k = seq.index(0)
            except ValueError:
                raise Reject("line %d: no terminating 0 after literals" % lineno)
            lits = seq[:k]
            rest = seq[k + 1:]
            if not rest or rest[-1] != 0:
                raise Reject("line %d: no terminating 0 after hints" % lineno)
            hints = rest[:-1]
            if op_id in db:
                raise Reject("line %d: id %d already used" % (lineno, op_id))

            # assume the negation of the added clause
            trail = []
            ok = True
            for lit in lits:
                v = abs(lit)
                if v > nv:
                    raise Reject("line %d: literal %d exceeds %d variables" % (lineno, lit, nv))
                want = -1 if lit > 0 else 1
                if val[v] == -want:
                    ok = False  # clause is a tautology: negation is inconsistent
                    break
                if val[v] == 0:
                    val[v] = want
                    trail.append(v)
            if not ok:
                for v in trail:
                    val[v] = 0
                raise Reject("line %d: addition %d is tautological" % (lineno, op_id))

            conflict = False
            for h in hints:
                if h < 0:
                    for v in trail:
                        val[v] = 0
                    raise Reject("line %d: RAT hint %d; this checker is RUP-only" % (lineno, h))
                c = db.get(h)
                if c is None:
                    for v in trail:
                        val[v] = 0
                    raise Reject("line %d: antecedent %d is absent or deleted" % (lineno, h))
                unit = 0
                nunassigned = 0
                satisfied = False
                for lit in c:
                    x = val[abs(lit)]
                    if x == 0:
                        nunassigned += 1
                        if nunassigned > 1:
                            break
                        unit = lit
                    elif (x == 1) == (lit > 0):
                        satisfied = True
                        break
                n_steps += 1
                if satisfied or nunassigned > 1:
                    for v in trail:
                        val[v] = 0
                    raise Reject("line %d: antecedent %d is %s under the current assignment"
                                 % (lineno, h, "satisfied" if satisfied else "not unit"))
                if nunassigned == 1:
                    v = abs(unit)
                    val[v] = 1 if unit > 0 else -1
                    trail.append(v)
                else:
                    conflict = True  # falsified antecedent: chain closes
                    break
            for v in trail:
                val[v] = 0
            if not conflict:
                raise Reject("line %d: hints for %d do not yield a conflict (not RUP)"
                             % (lineno, op_id))

            db[op_id] = tuple(lits)
            n_added += 1
            if not lits:
                saw_empty = True
                empty_id = op_id

    if not saw_empty:
        raise Reject("no verified empty clause: the proof does not refute the formula")
    return {
        "status": "VERIFIED",
        "cnf": cnf_path,
        "proof": lrat_path,
        "nfixed_clauses": sum(1 for _ in db),
        "additions": n_added,
        "deletions": n_deleted,
        "resolution_steps": n_steps,
        "empty_clause_id": empty_id,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="independent RUP-only LRAT check")
    ap.add_argument("cnf")
    ap.add_argument("lrat")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args(argv)
    try:
        r = check(a.cnf, a.lrat)
    except Reject as e:
        print("REJECTED: %s" % e)
        return 1
    if not a.quiet:
        print("s VERIFIED (independent RUP-only replay)")
        print("c additions %(additions)d, deletions %(deletions)d, "
              "resolution steps %(resolution_steps)d, empty clause id %(empty_clause_id)d" % r)
    return 20


if __name__ == "__main__":
    sys.exit(main())
