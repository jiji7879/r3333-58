#!/usr/bin/env python3
"""Certified root-level redundancy elimination for a K58 pipeline CNF.

Given a CNF F (possibly with auxiliary/cardinality variables), compute the
unit-propagation closure of F at the root and emit

  * min.cnf      -- an equivalent formula: the derived units plus every
                    original clause restricted to its still-unassigned
                    literals (clauses satisfied at the root are dropped),
  * trace.json   -- a machine-checkable witness trace for every operation,
                    replayed independently by check_trace.py.

Equivalence argument (what check_trace.py verifies clause by clause):
  1. every entry of `derived` is RUP with respect to F and the earlier
     entries: its reason clause is a clause of F containing the literal,
     and every other literal of that clause is falsified by an earlier
     derived unit (an original unit clause has no other literal, so it is
     the base case);
  2. F = deleted + kept as a partition of the original clause indices;
  3. for c in deleted, the witness literal is a member of c and is a
     derived unit, hence every model of min.cnf satisfies c;
  4. for c in kept, min.cnf carries exactly the literals of c that are
     still unassigned, and every dropped literal is falsified by a
     derived unit.
Hence for every assignment to the original variables,
      M |= F  <=>  M |= min.cnf .
"""
import hashlib
import json
import sys
from array import array
from pathlib import Path

UNASSIGNED, TRUE, FALSE = 0, 1, 2


def parse_cnf(path):
    clauses = []
    with open(path, 'rb') as f:
        first = f.readline().split()
        if not first or first[0] != b'p' or first[1] != b'cnf':
            raise SystemExit('not a CNF header: %r' % (first[:8],))
        nv, nc = int(first[2]), int(first[3])
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[-1] != b'0':
                raise SystemExit('missing 0 terminator: %r' % (line[:60],))
            if len(parts) == 1:
                clauses.append(())
            else:
                clauses.append(tuple(int(t) for t in parts[:-1]))
    if len(clauses) != nc:
        raise SystemExit('header says %d clauses, read %d' % (nc, len(clauses)))
    for cl in clauses:
        for l in cl:
            if abs(l) > nv:
                raise SystemExit('literal %d exceeds header var count %d' % (l, nv))
    return nv, clauses


def value_of(value, lit):
    v = value[abs(lit)]
    if v == UNASSIGNED:
        return UNASSIGNED
    return TRUE if (v == TRUE) == (lit > 0) else FALSE


def root_reduce(nv, clauses, log=print):
    nclauses = len(clauses)
    value = bytearray(nv + 1)          # UNASSIGNED / TRUE / FALSE per variable
    sat = bytearray(nclauses)          # clause satisfied at the root
    satwit = array('i', [-1]) * nclauses
    unassigned = array('i', (len(cl) for cl in clauses))
    occ = {}
    for ci, cl in enumerate(clauses):
        for l in cl:
            occ.setdefault(l, []).append(ci)
    log('parsed: %d vars, %d clauses, %d literal occurrences'
        % (nv, nclauses, sum(len(c) for c in clauses)))

    trail = []                # literals derived true, in derivation order
    reason = array('i')        # original clause index justifying each trail entry
    qhead = 0
    conflict = None

    def enqueue(lit, why):
        nonlocal conflict
        v = abs(lit)
        want = TRUE if lit > 0 else FALSE
        if value[v] == UNASSIGNED:
            value[v] = want
            trail.append(lit)
            reason.append(why)
            return True
        if value[v] != want:
            conflict = ('unit clash on literal %d (reason clause %d)' % (lit, why))
            return False
        return True

    for ci, cl in enumerate(clauses):
        if not cl:
            conflict = 'empty clause (index %d)' % ci
            break
        if len(cl) == 1:
            if not enqueue(cl[0], ci):
                break
    if conflict is None:
        while qhead < len(trail):
            lit = trail[qhead]
            qhead += 1
            for ci in occ.get(lit, ()):          # clauses made satisfied
                if not sat[ci]:
                    sat[ci] = 1
                    satwit[ci] = lit
            for ci in occ.get(-lit, ()):         # clauses losing a literal
                if sat[ci]:
                    continue
                unassigned[ci] -= 1
                if unassigned[ci] == 1:
                    cl = clauses[ci]
                    for l2 in cl:
                        if value_of(value, l2) == UNASSIGNED:
                            if not enqueue(l2, ci):
                                break
                            break
                elif unassigned[ci] == 0:
                    conflict = ('root conflict: clause %d falsified' % ci)
                    break
            if conflict is not None:
                break
    log('root closure: %d true literals derived, conflict=%s'
        % (len(trail), conflict))
    return value, sat, satwit, unassigned, trail, reason, conflict, occ


def main(src, outdir, log=print):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    nv, clauses = parse_cnf(src)
    (value, sat, satwit, unassigned, trail, reason, conflict, occ) = \
        root_reduce(nv, clauses, log)

    deleted, kept, bad = [], [], []
    for ci, cl in enumerate(clauses):
        if sat[ci]:
            deleted.append({'ci': ci, 'lit': int(satwit[ci])})
            continue
        rest = [l for l in cl if value_of(value, l) == UNASSIGNED]
        dropped = [l for l in cl if value_of(value, l) != UNASSIGNED]
        if any(value_of(value, l) == TRUE for l in cl):
            bad.append(ci)              # should be impossible: sat flag is exact
            continue
        kept.append({'ci': ci, 'lits': rest, 'dropped': dropped})

    derived = [{'lit': int(l), 'reason': int(reason[k])}
               for k, l in enumerate(trail)]

    # min.cnf: derived units first, then the restricted clauses
    top = nv
    blob = [('p cnf %d %d\n' % (top, len(derived) + len(kept))).encode()]
    for d in derived:
        blob.append(('%d 0\n' % d['lit']).encode())
    for k in kept:
        blob.append((' '.join(map(str, k['lits'])) + ' 0\n').encode())
    blob = b''.join(blob)
    minpath = outdir / 'min.cnf'
    minpath.write_bytes(blob)

    trace = {
        'source': str(src),
        'source_sha256': hashlib.sha256(Path(src).read_bytes()).hexdigest(),
        'min_sha256': hashlib.sha256(blob).hexdigest(),
        'min_path': str(minpath),
        'variables': nv,
        'source_clauses': len(clauses),
        'conflict': conflict,
        'derived': derived,
        'deleted': deleted,
        'kept': kept,
    }
    tpath = outdir / 'trace.json'
    tpath.write_text(json.dumps(trace))

    lit_before = sum(len(c) for c in clauses)
    lit_after = sum(len(k['lits']) for k in kept) + len(derived)
    stats = {
        'source': str(src),
        'source_sha256': trace['source_sha256'],
        'min_sha256': trace['min_sha256'],
        'min_path': str(minpath),
        'variables': nv,
        'conflict': conflict,
        'derived_units': len(derived),
        'clauses_before': len(clauses),
        'clauses_after': len(kept) + len(derived),
        'deleted_satisfied': len(deleted),
        'kept_restricted': len(kept),
        'unsat_flag_inconsistency': bad,
        'literals_before': lit_before,
        'literals_after': lit_after,
        'brevity_saved_literals': lit_before - lit_after,
    }
    log(json.dumps(stats, indent=1))
    (outdir / 'stats.json').write_text(json.dumps(stats, indent=1))
    return stats


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
