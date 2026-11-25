"""Exactness (non-vacuity) controls for the capacity table.

capacity.py shows "k+1 outsiders inside P" is UNSAT for every P with |P| = k and,
for four-sets, "5 inside P" is UNSAT except the 12 exceptional ones.  An upper
bound alone leaves open that the encoding is simply too strong.  Here the same
CNFs with k (resp. 5) outsiders are required to be SAT with a checked model, so
every capacity value in the table is exact:

  |P| = 1, 2, 3:  capacity exactly |P|;
  |P| = 4:         capacity exactly 4, except the 12 exceptional masks (exactly 5).

Writes pack/exactness.json.
"""
import itertools
import json
from pathlib import Path

from pysat.solvers import Cadical153

import enc

ARCH = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut')
HERE = Path(__file__).resolve().parent


def main():
    H = enc.load_h42(ARCH / 'data/h42.json')
    exceptional = set(json.loads((ARCH / 'results/saturated4.json').read_text()))
    out = []
    for k in (1, 2, 3, 4):
        for P in itertools.combinations(range(14), k):
            allowed = sum(1 << i for i in P)
            r = k if k < 4 else 4
            nv, clauses = enc.build([allowed] * r, H, free=True)
            with Cadical153(bootstrap_with=clauses) as s:
                assert s.solve(), (k, allowed)
                model = set(s.get_model())
            assert all(any(v in model for v in cl) for cl in clauses)
            out.append(dict(size=k, allowed=allowed, outsiders=r, status='SAT',
                            nv=nv, nclauses=len(clauses),
                            cnf_sha256=enc.sha(enc.to_dimacs(nv, clauses))))
        n = sum(1 for e in out if e['size'] == k)
        print('size', k, ':', n, 'subsets admit exactly', k, 'outsiders inside them',
              flush=True)
    assert len(exceptional) == 12
    (HERE / 'exactness.json').write_text(json.dumps(out) + '\n')
    print('total exactness controls:', len(out),
          '; four-set capacities: 4 (989 sets) / 5 (12 sets)')


if __name__ == '__main__':
    main()
