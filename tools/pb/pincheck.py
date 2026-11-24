#!/usr/bin/env python3
"""Forced degree windows on the rows of profile (15,14,14,14).

Under PERFECT BALANCE every colour-degree lies in {14,15}.  The pinned units of a
frozen row already force some edges, so for each (vertex, colour) pair they give a
window

    forced_true(v,c)  <=  d_c(v)  <=  57 - forced_false(v,c) ,

and a pair whose window misses {14,15} kills the row under perfect balance with no
search.  This is the check behind Lemma 1 of `results/pb-balance-2026-11-24`.

    PYTHONPATH=<site-packages with pysat> python3 tools/pb/pincheck.py [--list] [--profile 15,14,14,14]

Reads the frozen ledger and the frozen encoder (`.scratch/k58/gluing.py`); writes
nothing.  Independent of `tools/pb/balance.py`: it never builds a CNF, it counts
the unit clauses of `units()` directly.
"""
import argparse
import gzip
import json
import sys

LEDGER = '.scratch/k58/case-ledger.jsonl.gz'
ORDER = 58

sys.path.insert(0, '.scratch/k58')


def vertex_colour(literal):
    """Edge literal -> (u, v, c).  Pairs are in lexicographic order, four colours each."""
    i, c = divmod(abs(literal) - 1, 4)
    u = 0
    while i >= ORDER - 1 - u:
        i -= ORDER - 1 - u
        u += 1
    return u, u + 1 + i, c


def family_of(row):
    sys.path.insert(0, '.scratch/k58')
    from gluing import Family
    f = row['family']
    return Family(tuple(f['profile']), tuple(f['root_kinds']), f['arm'],
                  f['mark_position'], f['marked_size'], f['marked_kind'],
                  f['root_position'])


def windows(row):
    """(true, false) counts per (vertex, colour) over the row's unit clauses."""
    from gluing import units
    forced = {}
    for clause in units(family_of(row), tuple(row['placement'])):
        assert len(clause) == 1, 'units() must return unit clauses'
        literal = clause[0]
        u, v, c = vertex_colour(literal)
        for x in (u, v):
            true, false = forced.get((x, c), (0, 0))
            forced[(x, c)] = (true + 1, false) if literal > 0 else (true, false + 1)
    return forced


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', default='15,14,14,14')
    parser.add_argument('--ledger', default=LEDGER)
    parser.add_argument('--list', action='store_true', help='print every dead row')
    options = parser.parse_args()
    profile = tuple(int(x) for x in options.profile.split(','))

    counts = {'dead_ge16': 0, 'dead_le13': 0, 'alive': 0}
    total = 0
    for line in gzip.open(options.ledger, 'rt'):
        row = json.loads(line)
        if tuple(row['family']['profile']) != profile:
            continue
        total += 1
        forced = windows(row)
        verdict = 'alive'
        witness = None
        for (v, c), (true, false) in sorted(forced.items()):
            low, high = true, ORDER - 1 - false
            if low > 15:
                verdict, witness = 'dead_ge16', (v, c, low, high)
                break
            if high < 14:
                verdict, witness = 'dead_le13', (v, c, low, high)
                break
        counts[verdict] += 1
        if verdict != 'alive' and options.list:
            print('%s  kinds=%s marked_size=%d  dead: v=%d c=%d  %d <= d_c(v) <= %d'
                  % (row['id'][:12], ''.join(row['family']['root_kinds']),
                     row['family']['marked_size'], witness[0], witness[1],
                     witness[2], witness[3]))
    print('profile %s: %d rows' % (','.join(map(str, profile)), total))
    print('  dead by a forced degree >= 16 : %d' % counts['dead_ge16'])
    print('  dead by a forced degree <= 13 : %d' % counts['dead_le13'])
    print('  alive (needs a solver)         : %d' % counts['alive'])
    return 0 if total else 1


if __name__ == '__main__':
    sys.exit(main())
