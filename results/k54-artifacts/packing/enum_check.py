"""Re-derive the packing bound from the (now replayed) refuted mask sets.

1. `allowed` must be exactly the exceptional four-masks avoiding the pole.
2. Any configuration of outsiders with exact four-supports has distinct masks
   (multiplicity: at most one outsider per exceptional mask, certified
   separately by pack/multiplicity.py), all avoiding the pole, and containing no
   refuted subset.  So the number of such outsiders is at most
   overall = max{|S| : S subset of allowed, no refuted subset in S}.
   This script recomputes that maximum and the per-position limits.
3. The strengthened edge bound is 4*overall + 5*(13-overall).
4. The stored witness models must satisfy the CNF of the largest testable set
   and must have exactly `overall` masks.
"""
import gzip
import itertools
import json
from pathlib import Path

import enc

ARCH = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut')
HERE = Path(__file__).resolve().parent


def main():
    H = enc.load_h42(ARCH / 'data/h42.json')
    summary = json.loads((ARCH / 'results/packing/summary.json').read_text())
    exceptional = json.loads((ARCH / 'results/saturated4.json').read_text())
    report = {}
    bad_total = 0
    for pole in sorted(summary, key=int):
        p = int(pole)
        d = summary[pole]
        allowed = sorted(m for m in exceptional if not m >> p & 1)
        assert allowed == d['allowed'], (pole, allowed, d['allowed'])
        bad = [tuple(s) for s in d['bad']]
        bad_total += len(bad)
        # every refuted set is a set of distinct allowed masks of size >= 2
        for s in bad:
            assert len(set(s)) == len(s) >= 2 and set(s) <= set(allowed), (pole, s)
        # independent recomputation of the feasible mask sets
        possible = [s for k in range(len(allowed) + 1)
                    for s in itertools.combinations(allowed, k)
                    if not any(set(b) <= set(s) for b in bad)]
        overall = max(map(len, possible))
        limits = [max(sum(m >> i & 1 for m in s) for s in possible) for i in range(14)]
        assert overall == d['overall'], (overall, d['overall'])
        assert limits == d['limits'], (limits, d['limits'])
        # the refutation set is closed the right way: no refuted set inside another
        for s in bad:
            assert not any(set(b) < set(s) for b in bad), (pole, s)
        # every recorded status is one of the two, and every refuted set is recorded
        rec = {tuple(r[0]): r[1] for r in d['records']}
        for s in bad:
            assert rec.get(s) == 'UNSAT', (pole, s)
        largest = tuple(d['largest_witness_masks'])
        assert largest in set(possible) and len(largest) == overall, (pole, largest)
        assert rec.get(largest) == 'SAT', (pole, largest)
        # witness model satisfies its own CNF
        nv, clauses, raw = enc.cnf(p, list(largest), H)
        model_txt = gzip.decompress(
            (ARCH / 'results/packing' / ('pole-%d-largest.model.gz' % p)).read_bytes())
        model = {int(v) for v in model_txt.split()}
        assert all(any(v in model for v in cl) for cl in clauses), pole
        edge = 4 * overall + 5 * (13 - overall)
        report[pole] = dict(allowed=allowed, nbad=len(bad), overall=overall,
                            limits=limits, largest=list(largest),
                            edge_bound=edge, witness_model_ok=True,
                            npossible=len(possible),
                            cnf_sha256=enc.sha(raw))
        print('pole', p, ': allowed', len(allowed), 'refuted sets', len(bad),
              '-> at most', overall, 'four-support outsiders, edge bound', edge,
              '; witness model verified')
    pole_occ = [sum(m >> i & 1 for m in exceptional) for i in range(14)]
    print('exceptional masks:', len(exceptional))
    print('occurrences of each position in the 12 exceptional masks:', pole_occ)
    for p in (0, 2, 4):
        assert pole_occ[p] >= 3 and (12 - pole_occ[p]) == len([m for m in exceptional if not m >> p & 1])
    print('poles 0,2,4 occur', [pole_occ[p] for p in (0, 2, 4)],
          'times; available masks', [12 - pole_occ[p] for p in (0, 2, 4)])
    print('total refuted mask sets:', bad_total)
    (HERE / 'enum_check.json').write_text(json.dumps(report, indent=1) + '\n')


if __name__ == '__main__':
    main()
