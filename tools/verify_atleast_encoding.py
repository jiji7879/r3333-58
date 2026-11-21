#!/usr/bin/env python3
"""Check that PySAT's `CardEnc.atleast` is the K60 counter on the negations.

The Lean development proves encoding adequacy against `K58.SequentialCounter`,
which is the staggered at-*most* counter with a fixed variable allocation. That
only transfers to `dense.marked_threshold` if PySAT's default `atleast` emits
exactly that clause set on the negated literals. This checks it, clause for
clause, for every small `n` and every bound.

    python3 verify_atleast_encoding.py            # n = 2..9, all bounds
"""
import sys

from pysat.card import CardEnc, EncType


def index(k, d, j):
    """K58.SequentialCounter.index: first two rows interleaved."""
    if d == 0:
        return 2 * j
    if d == 1:
        return 2 * j + 1
    return d * k + j


def k60_counter(x, n, k, top):
    """Transcription of K58.SequentialCounter.counter (at most k of the atoms)."""
    def cell(d, j):
        return top + 1 + index(k, d, j)
    if n <= k:
        return [], 0
    if k == 0:
        return [[-x[i]] for i in range(n)], 0
    if k == n - 1:
        return [[-x[i] for i in range(n)]], 0
    out = []
    for d in range(n - k):
        for j in range(k):
            if j == 0:
                out.append([-x[d + j], cell(d, j)])
            else:
                out.append([-x[d + j], -cell(d, j - 1), cell(d, j)])
            if d + 1 < n - k:
                out.append([-cell(d, j), cell(d + 1, j)])
        out.append([-x[d + k], -cell(d, k - 1)])
    return out, (n - k) * k


def main():
    bad = 0
    for n in range(2, 10):
        for k in range(0, n):
            lits = list(range(1, n + 1))
            pysat = CardEnc.atleast(lits, bound=n - k, top_id=n, encoding=EncType.seqcounter)
            neg = [-l for l in lits]
            mine, used = k60_counter(neg, n, k, n)
            a = sorted(tuple(c) for c in pysat.clauses)
            b = sorted(tuple(c) for c in mine)
            if a != b or pysat.nv != n + used:
                bad += 1
                print(f"MISMATCH n={n} bound={n-k}: pysat {len(a)} clauses nv={pysat.nv}, "
                      f"counter {len(b)} clauses nv={n+used}")
    print(f"checked every bound for n = 2..9; mismatches: {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
