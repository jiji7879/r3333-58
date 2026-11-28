#!/usr/bin/env python3
"""Direct Schur control for literal Toeplitz 4-colourings.

A Toeplitz colouring c(|i-j|) of K_(N+1) is good exactly when
{1,...,N} has no monochromatic a,b,a+b, including a=b.
This script only emits the small direct CNF; it does not build a Ramsey wall CNF.
"""
import argparse
from pathlib import Path


def clauses(n: int, k: int):
    def v(a: int, colour: int) -> int:
        return (a - 1) * k + colour + 1

    for a in range(1, n + 1):
        yield [v(a, c) for c in range(k)]
        for c in range(k):
            for d in range(c + 1, k):
                yield [-v(a, c), -v(a, d)]
    for a in range(1, n + 1):
        for b in range(a, n + 1 - a):
            total = a + b
            for c in range(k):
                # When a=b the Schur clause has a repeated literal.  Delete only
                # that syntactic duplicate so warning-fatal DRAT replay is clean.
                yield list(dict.fromkeys([-v(a, c), -v(b, c), -v(total, c)]))
    # Palette symmetry: colour 0 may be assigned to integer 1 without loss.
    yield [v(1, 0)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("k", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.n < 1 or args.k < 1:
        parser.error("n and k must be positive")
    body = list(clauses(args.n, args.k))
    text = "".join(f"{' '.join(map(str, clause))} 0\n" for clause in body)
    args.output.write_text(
        f"c direct Schur triples, including a=b; palette pin colour(1)=0\n"
        f"p cnf {args.n * args.k} {len(body)}\n{text}",
        encoding="ascii",
    )
    print(f"n={args.n} k={args.k} vars={args.n * args.k} clauses={len(body)}")


if __name__ == "__main__":
    main()
