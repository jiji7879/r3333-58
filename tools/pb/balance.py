"""Perfect balance on K58: the wall rows of profile (15,14,14,14).

A good colouring of K58 has d_0+d_1+d_2+d_3 = 57 at every vertex.  "Perfect
balance" is d_c(v) in {14,15} for every v and c, which by 14+14+14+15 = 57 means
exactly one colour has degree 15 at each vertex.

In the campaign's frozen cover a row pins the profile of one root, so perfect
balance is compatible only with the 381 rows of `family.profile == [15,14,14,14]`
(any row with a part <= 13 has a vertex whose degree is <= 13 already).

    python3 tools/pb/balance.py ROW_ID OUT.cnf [--balance] [--dense] [--stats]

The CNF is the frozen row plus, with `--balance`, the constraints d_c(v) >= 14 for
all 58 vertices and 4 colours.  With d_c(v) <= 57 - 3*14 = 15 for free, both
directions of {14,15} follow.

A row has two CNFs, and the difference decides how a verdict reads:

* `gluing.host` + `gluing.units` alone is a RELAXATION of the row.  It drops the
  charge threshold that `dense.marked_threshold` adds - 74,555 clauses on row
  `325a259a...`, which is 135,304 clauses there against the certified 210,068.
* `--dense` adds that threshold back (`tables=True, total_critical=True,
  full_root=False`) and reproduces a certified row CNF clause for clause: checked
  on `325a259ab5fd...`, whose `verified.json` records 210,068 clauses and
  `formula_sha256 eb7413e5...`.

So UNSAT of the relaxation transfers to the row under perfect balance, while SAT
of the relaxation decides nothing.  Perfect balance only ever selected the 381 rows
of profile (15,14,14,14); 29 of those die on the ticket pin with no search (see
`results/pb-balance-2026-11-24`), and the other 352 are the instances to decide.

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


def build(rid, balance=True, stats=False, dense=False):
    d = row_by_id(rid)
    f = family_of(d)
    _, clauses = host(ORDER)
    fixed = units(f, tuple(d['placement']))
    clauses = [list(c) for c in clauses] + [list(c) for c in fixed]
    nv = 4 * (ORDER * (ORDER - 1) // 2)
    nxtra = 0
    if dense:
        from dense import marked_threshold
        extra = marked_threshold(f, fixed, d['charge'], tables=True,
                                 total_critical=True, full_root=False)
        if extra == [[]]:
            raise SystemExit('row %s: the threshold requirements contradict the pins' % rid[:12])
        clauses.extend([list(c) for c in extra])
        nxtra = len(extra)
        nv = max([nv] + [abs(l) for c in clauses for l in c])
    nbal = 0
    if balance:
        top = nv
        for v in range(ORDER):
            for c in range(4):
                lits = [edge_lit(v, w, c) for w in range(ORDER) if w != v]
                assert len(lits) == 57
                # Both directions.  The upper bound is implied - d_c(v) <= 57 - 3*14 = 15
                # once the other three colours are at least 14 - but that implication needs
                # the global count over all 57 edges at v, which CDCL does not get for free:
                # with the lower bounds alone the 29 ticket-pin rows stay UNKNOWN past 300 s
                # although they are refutable by 16 + 3*14 > 57.  Adding the upper bound is
                # sound (same formula, up to the implied clause) and unit-propagates it.
                enc = CardEnc.atleast(lits=lits, bound=14, top_id=top,
                                      encoding=EncType.seqcounter)
                clauses.extend([list(x) for x in enc.clauses])
                top = enc.nv
                enc = CardEnc.atmost(lits=lits, bound=15, top_id=top,
                                     encoding=EncType.seqcounter)
                clauses.extend([list(x) for x in enc.clauses])
                top = enc.nv
                nbal += 1
        nv = top
    if stats:
        print('row %s  profile %s  units %d  base %d  threshold %d  balance constraints %d  vars %d clauses %d'
              % (rid[:12], f.profile, len(fixed), len(host(ORDER)[1]), nxtra, nbal, nv, len(clauses)),
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
    dense = '--dense' in sys.argv
    cnf, d = build(rid, balance=bal, stats=True, dense=dense)
    cnf.to_file(out)
    print('wrote', out, 'balance' if bal else 'no-balance control',
          'with the row threshold' if dense else 'relaxation without the row threshold')
