"""Perfect balance on K58: the wall rows of profile (15,14,14,14).

A good colouring of K58 has d_0+d_1+d_2+d_3 = 57 at every vertex.  "Perfect
balance" is d_c(v) in {14,15} for every v and c, which by 14+14+14+15 = 57 means
exactly one colour has degree 15 at each vertex.

In the campaign's frozen cover a row pins the profile of one root, so perfect
balance is compatible only with the 381 rows of `family.profile == [15,14,14,14]`
(any row with a part <= 13 has a vertex whose degree is <= 13 already).

    python3 tools/pb/balance.py ROW_ID OUT.cnf [--balance] [--stats]

The CNF is the frozen row (`gluing.host` + `gluing.units`) plus, with
`--balance`, the constraints d_c(v) >= 14 for all 58 vertices and 4 colours.
With d_c(v) <= 57 - 3*14 = 15 for free, both directions of {14,15} follow.

Needs PYTHONPATH=/workspace/nucleus/work/home/.local/lib/python3.12/site-packages
for pysat.
"""
import sys, os, json, gzip, itertools
sys.path.insert(0, '.scratch/k58')
from gluing import Family, host, units, representatives, data, counts
from pysat.card import CardEnc, EncType
from pysat.formula import CNF

ORDER = 58
LEDGER = '.scratch/k58/case-ledger.jsonl.gz'


def row_by_id(rid):
    for line in gzip.open(LEDGER, 'rt'):
        d = json.loads(line)
        if d['id'] == rid:
            return d
    raise SystemExit('row %s not found' % rid)


def family_of(d):
    f = d['family']
    return Family(tuple(f['profile']), tuple(f['root_kinds']), f['arm'],
                  f['mark_position'], f['marked_size'], f['marked_kind'],
                  f['root_position'])


def edge_lit(u, v, c):
    if u > v:
        u, v = v, u
    i = u * (2 * ORDER - u - 1) // 2 + (v - u - 1)
    return 4 * i + 1 + c


def build(rid, balance=True, stats=False):
    d = row_by_id(rid)
    f = family_of(d)
    _, clauses = host(ORDER)
    fixed = units(f, tuple(d['placement']))
    clauses = [list(c) for c in clauses] + [list(c) for c in fixed]
    nv = 4 * (ORDER * (ORDER - 1) // 2)
    nbal = 0
    if balance:
        top = nv
        for v in range(ORDER):
            for c in range(4):
                lits = [edge_lit(v, w, c) for w in range(ORDER) if w != v]
                assert len(lits) == 57
                enc = CardEnc.atleast(lits=lits, bound=14, top_id=top,
                                      encoding=EncType.seqcounter)
                clauses.extend([list(x) for x in enc.clauses])
                top = enc.nv
                nbal += 1
        nv = top
    if stats:
        print('row %s  profile %s  units %d  base %d  balance constraints %d  vars %d clauses %d'
              % (rid[:12], f.profile, len(fixed), len(host(ORDER)[1]), nbal, nv, len(clauses)),
              flush=True)
    if balance:
        assert nv > 4 * (ORDER * (ORDER - 1) // 2), 'auxiliary variables must start above the edge literals'
    cnf = CNF()
    cnf.nv = nv
    cnf.clauses = clauses
    return cnf, d


if __name__ == '__main__':
    rid, out = sys.argv[1], sys.argv[2]
    bal = '--balance' in sys.argv
    cnf, d = build(rid, balance=bal, stats=True)
    cnf.to_file(out)
    print('wrote', out, 'balance' if bal else 'no-balance control')
