#!/usr/bin/env python3
"""Independent replay of the trace written by rootreduce.py.

Nothing here trusts rootreduce.py: the original CNF and min.cnf are re-parsed,
the derived-unit chain is replayed, and every operation type is checked.  Any
inconsistency is a hard failure (exit status 1), which is what the negative
controls rely on.

Checks
  1. header/hashes of the trace inputs agree with the files on disk;
  2. `derived` is a legal ordered RUP chain with respect to the ORIGINAL
     formula: each entry's reason clause contains the literal, every other
     literal of that reason clause is falsified by strictly earlier entries,
     and the same literal is never derived twice with opposite polarity;
  3. `deleted` and `kept` partition the original clause indices exactly;
  4. each deleted clause contains its witness literal, and that literal is
     true under the derived units;
  5. each kept clause is exactly the restriction of the original clause to
     literals unassigned under the derived units (no literal invented, none
     silently lost, none kept that is falsified);
  6. min.cnf is byte-identical to the clauses implied by the trace (units for
     `derived`, then the restricted clauses in order), and its header agrees.
"""
import hashlib
import json
import sys
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
                raise SystemExit('missing 0 terminator')
            clauses.append(tuple(int(t) for t in parts[:-1]))
    if len(clauses) != nc:
        raise SystemExit('header says %d clauses, read %d' % (nc, len(clauses)))
    return nv, clauses


def fail(msg):
    print('FAIL: ' + msg)
    raise SystemExit(1)


def main(tracepath):
    trace = json.loads(Path(tracepath).read_text())
    src = Path(trace['source'])
    if hashlib.sha256(src.read_bytes()).hexdigest() != trace['source_sha256']:
        fail('source CNF hash does not match the trace')
    nv, clauses = parse_cnf(src)
    if nv != trace['variables'] or len(clauses) != trace['source_clauses']:
        fail('source CNF shape does not match the trace')
    if trace['conflict'] is not None:
        fail('trace records a root conflict, %r; a refuted parent needs no reduction'
             % (trace['conflict'],))

    # ---- 2. replay the RUP chain over the original formula --------------
    value = bytearray(nv + 1)
    truth = []                       # literal of each derived unit, in order

    def val(lit):
        v = value[abs(lit)]
        if v == UNASSIGNED:
            return UNASSIGNED
        return TRUE if (v == TRUE) == (lit > 0) else FALSE

    for pos, entry in enumerate(trace['derived']):
        lit, why = int(entry['lit']), int(entry['reason'])
        if not (0 <= why < len(clauses)):
            fail('derived[%d]: reason clause index %d out of range' % (pos, why))
        cl = clauses[why]
        if lit not in cl:
            fail('derived[%d]: literal %d is not in reason clause %d'
                 % (pos, lit, why))
        for other in cl:
            if other == lit:
                continue
            if val(other) != FALSE:
                fail('derived[%d]: reason clause %d is not unit under the '
                     'earlier units (literal %d is not false)' % (pos, why, other))
        if val(lit) == TRUE:
            fail('derived[%d]: literal %d already derived' % (pos, lit))
        if val(lit) == FALSE:
            fail('derived[%d]: literal %d already falsified' % (pos, lit))
        value[abs(lit)] = TRUE if lit > 0 else FALSE
        truth.append(lit)

    # ---- 3. partition of the original clause indices -------------------
    seen = {}
    for entry in trace['deleted']:
        ci = int(entry['ci'])
        if ci in seen:
            fail('clause %d appears twice in the trace' % ci)
        seen[ci] = 'deleted'
    for entry in trace['kept']:
        ci = int(entry['ci'])
        if ci in seen:
            fail('clause %d appears twice in the trace' % ci)
        seen[ci] = 'kept'
    if len(seen) != len(clauses):
        missing = [i for i in range(len(clauses)) if i not in seen]
        fail('%d original clauses are not covered by the trace, e.g. %r'
             % (len(missing), missing[:5]))

    # ---- 4. deleted clauses -------------------------------------------
    for entry in trace['deleted']:
        ci, wit = int(entry['ci']), int(entry['lit'])
        if wit not in clauses[ci]:
            fail('deleted clause %d: witness literal %d is not in it' % (ci, wit))
        if val(wit) != TRUE:
            fail('deleted clause %d: witness literal %d is not a derived unit'
                 % (ci, wit))

    # ---- 5. kept clauses are exact restrictions -----------------------
    for entry in trace['kept']:
        ci = int(entry['ci'])
        rest = [int(x) for x in entry['lits']]
        dropped = [int(x) for x in entry['dropped']]
        if set(rest) & set(dropped):
            fail('kept clause %d: a literal is both kept and dropped' % ci)
        if sorted(rest + dropped) != sorted(clauses[ci]):
            fail('kept clause %d: kept+dropped literals are not the original clause'
                 % ci)
        for l in rest:
            if val(l) != UNASSIGNED:
                fail('kept clause %d: literal %d is assigned at the root' % (ci, l))
        for l in dropped:
            if val(l) != FALSE:
                fail('kept clause %d: dropped literal %d is not false' % (ci, l))

    # ---- 6. min.cnf is exactly what the trace implies ------------------
    expect = [('p cnf %d %d\n' % (nv, len(truth) + len(trace['kept']))).encode()]
    for l in truth:
        expect.append(('%d 0\n' % l).encode())
    for entry in trace['kept']:
        expect.append((' '.join(str(int(x)) for x in entry['lits']) + ' 0\n').encode())
    expect = b''.join(expect)
    if hashlib.sha256(expect).hexdigest() != trace['min_sha256']:
        fail('min.cnf does not match the clauses the trace claims')
    minpath = Path(trace['min_path']) if 'min_path' in trace else \
        Path(tracepath).parent / 'min.cnf'
    blob = minpath.read_bytes()
    if hashlib.sha256(blob).hexdigest() != trace['min_sha256']:
        fail('min.cnf on disk does not match the trace hash')
    if blob != expect:
        fail('min.cnf on disk differs from the trace reconstruction')

    print('s VERIFIED  %s' % tracepath)
    print('  derived units       %d' % len(truth))
    print('  deleted (satisfied) %d' % len(trace['deleted']))
    print('  kept (restricted)   %d' % len(trace['kept']))
    print('  clauses %d -> %d' % (len(clauses), len(truth) + len(trace['kept'])))


if __name__ == '__main__':
    main(sys.argv[1])
