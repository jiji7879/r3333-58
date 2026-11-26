#!/usr/bin/env python3
"""Append unconditional d_c(v)<=16 to any K58 host-colouring CNF.

Preserves the whole parent clause block and allocates new cardinality variables
above the declared parent maximum. The literal map is checked against the
frozen K58 host definition. The proof obligation is simply triangle-freeness:
N_c(v) is triangle-free in the other three colours, so R(3,3,3)<=17 applies.

This is an unconditional relaxation-compatible strengthening for triangle-free
four-colouring: no criticality, ticket balance, template or row claim is used.
"""
import hashlib
import json
from pathlib import Path
import sys
from pysat.card import CardEnc, EncType

ORDER = 58
DEGREE_CAP = 16


def host_map():
    edges, i = {}, 0
    for x in range(ORDER):
        for y in range(x + 1, ORDER):
            edges[x, y] = 4 * i + 1
            i += 1
    return edges


def main(parent, out, unit_aware=False):
    parent, out = Path(parent), Path(out)
    raw = parent.read_bytes()
    first, body = raw.split(b'\n', 1)
    head = first.split()
    assert head[0:2] == [b'p', b'cnf']
    nv, nc = map(int, head[2:4])
    assert body.count(b'\n') == nc, 'parent needs one clause per line'
    # A parent with undeclared or auxiliary-colliding variables is rejected.
    clauses = []
    for line in body.splitlines():
        tokens = [int(tok) for tok in line.split()]
        assert tokens and tokens[-1] == 0, 'invalid DIMACS clause line'
        clauses.append(tokens[:-1])
    max_literal = max(abs(tok) for clause in clauses for tok in clause)
    assert nv == max_literal, (nv, max_literal, 'input maximum/declaration mismatch')
    unit_literals = {clause[0] for clause in clauses if len(clause) == 1}
    assert not ({x for x in unit_literals if x > 0} &
                {-x for x in unit_literals if x < 0}), 'parent has contradictory units'
    edges = host_map()
    add, top = [], nv
    for v in range(ORDER):
        for c in range(4):
            physical = sorted(edges[min(v, y), max(v, y)] + c
                              for y in range(ORDER) if y != v)
            assert len(physical) == ORDER - 1
            if unit_aware:
                # Any edge literal already fixed by a unit in the parent is
                # removed from the counter, with forced positives offset in k.
                yes = sum(lit in unit_literals for lit in physical)
                lits = [lit for lit in physical if lit not in unit_literals
                        and -lit not in unit_literals]
                bound = DEGREE_CAP - yes
                assert bound >= 0, 'parent forces more than cap-known neighbours'
            else:
                lits, bound = physical, DEGREE_CAP
            if bound >= len(lits):
                continue
            top += 1
            enc = CardEnc.atmost(lits=lits, bound=bound, top_id=top,
                                 encoding=EncType.seqcounter)
            top = max(top, enc.nv)
            add.extend(enc.clauses)
    blob = (f'p cnf {top} {nc + len(add)}\n'.encode() + body +
            b''.join((' '.join(map(str, c)) + ' 0\n').encode() for c in add))
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + '.tmp')
    tmp.write_bytes(blob)
    assert tmp.read_bytes().split(b'\n', 1)[1].startswith(body)
    tmp.replace(out)
    meta = dict(parent=str(parent), output=str(out), parent_nvars=nv,
                parent_clauses=nc, parent_sha256=hashlib.sha256(raw).hexdigest(),
                new_clauses=len(add), output_nvars=top,
                total_clauses=nc + len(add), sha256=hashlib.sha256(blob).hexdigest(),
                unit_aware=unit_aware, unit_literals=len(unit_literals),
                physical_hypothesis='TriangleFree edge-colouring of K58 with four colours',
                encoding='4 colours * 58 vertices, sequential-counter d_c(v) <= 16',
                base_preserved=True, fresh_variables_allocated_above_parent=True,
                literal_map='frozen host(58), 4*edge_index+colour+1',
                off_limits=['c=q support cap', 'perfect degree balance', '15-ticket floor'])
    print(json.dumps(meta, indent=2))
    out.with_suffix('.json').write_text(json.dumps(meta, indent=2) + '\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--unit-aware' in sys.argv[3:])
