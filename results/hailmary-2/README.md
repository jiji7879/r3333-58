# Hail mary 2: pinning one arm's words decides the 42-slot instance in 10 s

m4's method (`smwrmwgf7` d4) turned `(14,7)` from UNKNOWN-at-600-1500 s into
UNSAT-at-18-71 s by **fixing the arm's words** and restricting the short arm to
the pair-compatible domain. This tests whether the first half of it transfers to
the decisive 42-slot instance — the one that, by m1's exactness theorem, *is*
the uniform branch.

**It transfers.** `ladder.build(tpl, [14,14,14], xt=True)` is the 42-slot
instance (45,381 variables, 179,318 clauses). Pinning the 210 cells of one arm's
14 words and solving with kissat:

| words pinned | result | wall |
| ---: | --- | ---: |
| 0 | UNKNOWN | 60 s |
| 1 | UNKNOWN | 60 s |
| 2 | UNKNOWN | 60 s |
| 4 | UNKNOWN | 60 s |
| 8 | UNKNOWN | 60 s |
| **14** | **UNSAT** | **10.5 s** |

And it is certified: `drat-trim gp_14.cnf gp_14.drat` gives **`s VERIFIED`** —
7,271 of 179,528 clauses in core, 107,351 of 830,431 lemmas, 3.4 M resolution
steps, 2,009 RAT lemmas, 52 MB of proof, regenerable in 10.5 s.

The words pinned are arm 1 of `.ultramath/smwrfgma5/m4/wit/a_14_14.wit`, which
are admissible on their own: coverage per position 4-5, no repeated word, every
pair with an available colour, and no word with an empty ordinary colour — so
this is a genuine cube of the 42-slot space and not an inconsistent pin.

**A trap worth recording.** The first attempt used
`results/two-arm-interface/a_14_14_lean.wit` and returned UNSAT in **0.0 s** for
every number of pinned words down to 1. That is the template-labelling hazard
again: that witness lives in the Lean labelling, so its words violate part
independence against `k15_template_Tminus_aut2_m4.col` on contact, and the pin
contradicts the instance immediately. A 0.0 s UNSAT on a 179k-clause instance is
always a pin contradiction, never a discovery.

**What this does and does not give.** It gives a cheap, certified *cube*
refutation: no branch object carries those fourteen words in arm 1. It does not
close the 42-slot instance, because a complete cover would have to range over the
arm's word multisets — of size 14 from 254,628 words — and m4's own reach was
7-of-14 words pinned. What it does establish is that the *hardness is in the last
few words*: eight pinned words still leave the instance undecided at 60 s while
fourteen decide it in ten seconds.

**The next shape this suggests.** Cube on the arm's *coverage profile* rather than
its words: every arm has each position covered 4 or 5 times, summing to 70, so the
profile is one of C(15,5) = 3,003 count vectors — the same 3,003 that
`smwrmwgf7/m4` flagged as unused. If the residual is cheap for each profile, that
is a finite cover of the arm layer; if it is not, the words carry information the
profile does not.
