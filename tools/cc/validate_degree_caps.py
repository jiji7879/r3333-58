#!/usr/bin/env python3
"""Independently rederive the degree-cap formula suffix; reject bad parents."""
import json
import sys
from pathlib import Path
from pysat.card import CardEnc, EncType


def parts(path):
    first, body = Path(path).read_bytes().split(b'\n', 1)
    h = first.split()
    return int(h[2]), int(h[3]), body


def expected_suffix(nv, unit_aware=False, parent_body=b''):
    edges, i = {}, 0
    for x in range(58):
        for y in range(x + 1, 58):
            edges[x, y] = 4 * i + 1
            i += 1
    units = set()
    if unit_aware:
        for line in parent_body.splitlines():
            tokens = [int(tok) for tok in line.split()]
            assert tokens and tokens[-1] == 0
            if len(tokens) == 2:
                units.add(tokens[0])
    top, add = nv, []
    for v in range(58):
        for c in range(4):
            lits = sorted(edges[min(v, y), max(v, y)] + c for y in range(58) if y != v)
            if unit_aware:
                known_true = sum(lit in units for lit in lits)
                lits = [lit for lit in lits if lit not in units and -lit not in units]
                bound = 16 - known_true
                assert bound >= 0
            else:
                bound = 16
            if bound >= len(lits):
                continue
            top += 1
            enc = CardEnc.atmost(lits=lits, bound=bound, top_id=top, encoding=EncType.seqcounter)
            top = max(top, enc.nv)
            add.extend(enc.clauses)
    return top, b''.join((' '.join(map(str, c)) + ' 0\n').encode() for c in add)


def check(parent, out, unit_aware=False):
    nv, nc, body = parts(parent)
    on, oc, output = parts(out)
    top, suffix = expected_suffix(nv, unit_aware, body)
    assert output.startswith(body), 'base clause block changed'
    assert output[len(body):] == suffix, 'auxiliary suffix differs from recomputed caps'
    assert on == top
    print('PASS exact base and all 232 caps:', nc, '+', oc - nc, '=', oc,
          'clauses; top =', top, '; unit_aware =', unit_aware)


if __name__ == '__main__':
    check(sys.argv[1], sys.argv[2], '--unit-aware' in sys.argv[3:])
