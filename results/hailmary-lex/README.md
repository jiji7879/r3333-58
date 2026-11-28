# Hail mary 1: symmetry breaking on the hard cases — sound, and worth 3 %

> **Withdrawn 2026-11-28 (Duggan method review, accepted `smwzxq4fl/m4`).**
> `hm.py::lex_leader` is existentially vacuous: setting every fresh auxiliary
> to true satisfies every added comparator clause for every physical colouring.
> Independently, all 120 non-lex pairs in the 256-pair control were accepted and
> all 7,404 case-7 additions have a positive fresh literal. Thus the formula did
> not enforce either strict or non-strict lex order. The 3%/4% numbers below are
> only solver-trajectory differences, and the conclusions about orbit redundancy
> and cubes are unsupported. The satisfiable `probe3.py` control tested only half
> of comparator correctness and cannot detect this defect. This differs from the
> separate historical strict-lex overconstraint.
>
> A corrected, bidirectional stabilizer-lex encoding passed all 256 row pairs,
> $3\times4096$ small-matrix controls and a strict DRAT control. On the same
> case-7 bare formula, the corrected 12-pair matching cost about 1.3× the wall
> time and the corrected 100-pair full rule 2.69×, with 4.75× the propagations;
> every call remained OPEN. Dynamic SMS was not tested. See
> `results/duggan-paper-2026-11-28/symmetry/` for the review and receipts.
> The text below is retained unedited as the historical, superseded report.

The cover's per-case CNF is bare `host(58)` plus pins (`gluing.host` + `units`),
so it contains every vertex permutation the pin does not destroy. The question was
whether a *sound* symmetry break could crack a hard case.

**The opportunity is real.** For the OPEN cases of `16,14,14,13` the pin leaves
**100-142 vertex pairs whose transposition preserves the pinned unit set
exactly**, i.e. 12-14 disjoint transpositions per case — a 2^12 to 2^14 factor in
the search space, and nothing in the runner exploits it.

**The method.** `lex_leader` in `hm.py` forbids `u`'s colour vector being
lexicographically greater than `v`'s for such a transposition. Auxiliaries carry
only forcing implications, so no model can be lost, and the scheme is applied
only to a *matching* of transpositions — disjoint supports commute, which is what
avoids the classic lex-leader pitfall of cutting every representative of an orbit.
Validated on a satisfiable instance with 45 twin pairs: SAT before and after
(`probe3.py`).

**The result: nothing moved.**

| case | twin pairs | matching | bare @120 s | lex @120 s |
| ---: | ---: | ---: | --- | --- |
| 7 | 100 | 12 | UNKNOWN | UNKNOWN |
| 8 | 100 | 12 | UNKNOWN | UNKNOWN |
| 12 | 142 | 14 | UNKNOWN | UNKNOWN |
| 20 | 142 | 14 | UNKNOWN | UNKNOWN |

And the cost/benefit on case 7 at a fixed 60 s (`conf.py`):

| arm | conflicts | propagations |
| --- | ---: | ---: |
| bare | 2,972,946 | 304,160,912 |
| lex (12 transpositions) | 2,884,915 | 290,835,042 |

So a 2^12 reduction in the nominal search space buys **3 % fewer conflicts and
4 % fewer propagations** in the same wall time — the solver is slightly slower per
conflict and no better overall.

**What that rules out.** The hardness of these cases is not orbit redundancy.
kissat is not spending its time re-exploring permutations of the pin's
automorphism group, so neither symmetry breaking nor a cube over those orbits is
worth pursuing. That is a useful negative: it was the cheapest sound hope
available, it is now measured, and the answer is no.

**Caveat.** This tests one case family (`16,14,14,13`), one solver (kissat 4.0.4),
one budget (120 s), and sound cuts only. It says nothing about `16,16,14,11` or
`15,15,14,13`, which were not run.
