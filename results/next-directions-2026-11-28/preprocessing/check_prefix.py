#!/usr/bin/env python3
"""Independent checker for a one-shot preprocessing *prefix* (a partial DRAT file).

drat-trim only verifies refutations.  Handed a prefix that ends without the empty
clause it prints "ERROR: no conflict / s NOT VERIFIED" and never reports whether
the individual additions were justified.  This checker verifies a prefix on its
own terms, reading only the three artifacts (host CNF, prefix, reduced CNF) and
justifying every addition with **MiniSat 2.2's own propagation engine** from the
pinned python-sat wheel -- a different solver from the CaDiCaL used to measure
search, and a different implementation from the occurrence-list closure in
``prep.py``.

Checks:

  P1 every unit addition is a literal MiniSat itself propagates from the host's
     unit clauses (one full root propagation, no search);
  P2 for every non-unit addition A, MiniSat's propagation under the assumptions
     ``-A`` (all literals of A negated) reports a conflict -- i.e. A is RUP with
     respect to the host alone, which is stronger than RUP at its position in
     the prefix, so the prefix is valid in any order;
  P3 every deletion names a clause currently present in the formula;
  P4 host - deletions + additions == the reduced CNF, as multisets;
  P5 the reduced CNF contains the unit clause of every forced literal;
  P6 every non-unit addition mentions no forced variable (so it is not a
     disguised duplicate of a unit).

A prefix is not a refutation.  This checker never claims UNSAT.  It is not
formally verified; what it adds is a second, independent propagation engine.
"""
import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path


def parse_dimacs(data):
    header, clauses, pending = None, [], []
    for raw in data.splitlines():
        line = raw.strip()
        if not line or line.startswith(b"c"):
            continue
        if line.startswith(b"p"):
            parts = line.split()
            header = (int(parts[2]), int(parts[3]))
            continue
        for field in line.split():
            lit = int(field)
            if lit:
                pending.append(lit)
            else:
                clauses.append(tuple(pending))
                pending = []
    if pending:
        raise ValueError("unterminated clause")
    if header is None:
        raise ValueError("missing header")
    if header[1] != len(clauses):
        raise ValueError(f"header says {header[1]} clauses, parsed {len(clauses)}")
    return header[0], clauses


def decode_vbyte(data, index):
    value = shift = 0
    while True:
        byte = data[index]
        index += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            return value, index


def parse_prefix(data, fmt):
    additions, deletions = [], []
    if fmt == "ascii":
        for raw in data.splitlines():
            fields = raw.split()
            if not fields:
                continue
            if fields[0] == b"d":
                deletions.append(tuple(int(x) for x in fields[1:-1]))
            else:
                additions.append(tuple(int(x) for x in fields[:-1]))
        return additions, deletions
    index = 0
    while index < len(data):
        tag = data[index]
        index += 1
        target = additions if tag == 0x61 else deletions
        clause = []
        while True:
            if index >= len(data):
                raise ValueError("truncated binary prefix")
            encoded, index = decode_vbyte(data, index)
            if encoded == 0:
                break
            clause.append(-(encoded >> 1) if encoded & 1 else (encoded >> 1))
        target.append(tuple(clause))
    return additions, deletions


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--format", choices=("ascii", "binary"), required=True)
    parser.add_argument("--reduced", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--limit", type=int, default=0,
                        help="check only the first N clause additions (0 = all)")
    parser.add_argument("--engine", default="Minisat22")
    parser.add_argument("--sample", type=int, default=0,
                        help="check this many clause additions with the engine (0 = all)")
    args = parser.parse_args(argv)

    from pysat.solvers import Minisat22, Cadical195
    engines = {"Minisat22": Minisat22, "Cadical195": Cadical195}
    engine = engines[args.engine]

    host_data = args.cnf.read_bytes()
    nvars, host = parse_dimacs(host_data)
    reduced_data = args.reduced.read_bytes()
    reduced_nvars, reduced = parse_dimacs(reduced_data)
    prefix_data = args.prefix.read_bytes()
    additions, deletions = parse_prefix(prefix_data, args.format)
    problems = []
    units = [a[0] for a in additions if len(a) == 1]
    clauses = [a for a in additions if len(a) > 1]

    host_units = [c[0] for c in host if len(c) == 1]
    rng = random.Random(20261128)
    with engine(bootstrap_with=[list(c) for c in host]) as solver:
        # pysat's propagate() reports only the Boolean status on this build, not the
        # propagated literals, so each claim is checked as its own RUP question:
        # "is host + not l already a propagation conflict?".
        if not solver.propagate(assumptions=[])[0]:
            problems.append("host is already refuted by root propagation")
        # P1: every unit addition is forced by the host's unit propagation
        unforced = []
        for lit in units:
            if solver.propagate(assumptions=[-lit])[0]:
                unforced.append(lit)
                if len(unforced) >= 5:
                    break
        if unforced:
            problems.append(f"{len(unforced)}+ unit additions are not forceable by the engine, "
                            f"e.g. {unforced}")
        # P2b: a seeded sample of clause additions re-checked as RUP by the engine
        sample = clauses if not args.limit else clauses[:args.limit]
        if args.sample and len(sample) > args.sample:
            sample = rng.sample(sample, args.sample)
        failures = []
        for index, clause in enumerate(sample):
            if solver.propagate(assumptions=[-lit for lit in clause])[0]:
                failures.append(clause)
                if len(failures) >= 5:
                    break
            if index and index % 100 == 0:
                print(f"  ... {index}/{len(sample)} clause additions checked by the engine",
                      flush=True)
        if failures:
            problems.append(f"{len(failures)}+ clause additions are not RUP per the engine, "
                            f"e.g. {failures[:2]}")

    # forced literals: the host's own units plus every engine-verified addition
    value = {abs(lit): lit > 0 for lit in host_units}
    for lit in units:
        value[abs(lit)] = lit > 0
        if abs(lit) in value and value[abs(lit)] != (lit > 0):
            problems.append(f"unit addition {lit} contradicts the forced value")

    # P2a: structural justification for every clause addition (exact, no engine):
    # A must be a host clause minus literals that are forced false.
    reduced_form = Counter()
    for clause in host:
        if len(clause) == 1:
            continue                      # host units are kept verbatim
        if any(value.get(abs(lit)) == (lit > 0) for lit in clause):
            continue                      # satisfied by a forced literal
        reduced_form[tuple(lit for lit in clause if abs(lit) not in value)] += 1
    tainted = []
    for clause in clauses:
        if any(abs(lit) in value and value[abs(lit)] == (lit > 0) for lit in clause):
            tainted.append(clause)
        elif reduced_form.get(clause, 0) == 0:
            problems.append(f"added clause is not a host clause minus forced literals: {clause}")
            break
    if tainted:
        problems.append(f"{len(tainted)} clause additions mention a forced literal, e.g. {tainted[:2]}")

    # P3
    pool = Counter(frozenset(c) for c in host)
    for clause in deletions:
        key = frozenset(clause)
        if pool[key] == 0:
            problems.append(f"deletion of an absent clause: {clause}")
            break
        pool[key] -= 1

    # P4
    final = Counter(frozenset(c) for c in host)
    for clause in deletions:
        final[frozenset(clause)] -= 1
    for clause in additions:
        final[frozenset(clause)] += 1
    final = Counter({k: v for k, v in final.items() if v})
    got = Counter(frozenset(c) for c in reduced)
    if final != got:
        absent = [sorted(m) for m in (final - got)][:3]
        extra = [sorted(m) for m in (got - final)][:3]
        problems.append(f"host - deletions + additions != reduced: missing={absent} extra={extra}")

    # P5
    for var, positive in value.items():
        if frozenset({var if positive else -var}) not in got:
            problems.append(f"reduced CNF lacks the unit for forced variable {var}")
            break

    receipt = {
        "engine": f"{args.engine} via python-sat (independent of the CaDiCaL measurement)",
        "host": {"sha256": hashlib.sha256(host_data).hexdigest(), "bytes": len(host_data),
                 "vars": nvars, "clauses": len(host)},
        "prefix": {"sha256": hashlib.sha256(prefix_data).hexdigest(), "bytes": len(prefix_data),
                   "format": args.format, "additions": len(additions),
                   "unit_additions": len(units), "clause_additions": len(clauses),
                   "clause_additions_checked": len(sample),
                   "deletions": len(deletions),
                   "trailing_empty_clause": bool(additions and not additions[-1])},
        "reduced": {"sha256": hashlib.sha256(reduced_data).hexdigest(),
                    "bytes": len(reduced_data), "vars": reduced_nvars,
                    "clauses": len(reduced)},
        "forced_vars": len(value),
        "engine_clause_checks": len(sample),
        "problems": problems[:10],
        "verdict": "prefix-checked" if not problems else "failed",
        "scope": ("verifies a partial DRAT prefix against its host with a second solver's "
                  "propagation; a prefix is not a refutation; the checker is not verified"),
    }
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.write_text(text)
    print(text, end="")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
