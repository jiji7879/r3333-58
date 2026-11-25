"""Read the supports back out of a SAT model of the exactly-k CNF.

Guards the packing-bound certification against an encoding slip: the model of the
13-singleton + r-four-support instance must really have thirteen distinct
one-point supports and r supports of size exactly four, none containing the pole.
"""
from pathlib import Path

from pysat.solvers import Cadical153

import enc

ARCH = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut')


def spec_of(pole, r):
    nonpole = sum(1 << j for j in range(14) if j != pole)
    return [(1 << j, 1) for j in range(14) if j != pole] + [(nonpole, 4)] * r


def main():
    H = enc.load_h42(ARCH / 'data/h42.json')
    for pole, r in ((0, 4), (2, 4), (4, 3)):
        nv, clauses, var = enc.build_exact_k(spec_of(pole, r), H, want_map=True)
        with Cadical153(bootstrap_with=clauses) as s:
            assert s.solve()
            model = set(s.get_model())
        t = 14
        sup = []
        for i in range(13 + r):
            b = t + i
            sup.append([a for a in range(t) if (a, b) in var and var[a, b].get(3) in model])
        assert all(len(s) == 1 for s in sup[:13]), sup[:13]
        assert len({s[0] for s in sup[:13]}) == 13, sup[:13]
        assert all(len(s) == 4 for s in sup[13:]), sup[13:]
        assert all(pole not in s for s in sup), (pole, sup)
        print('pole %d: 13 singletons at %s; %d four-supports %s'
              % (pole, [s[0] for s in sup[:13]], r, sup[13:]))
    print('exactly-k encoding reads back as intended')


if __name__ == '__main__':
    main()
