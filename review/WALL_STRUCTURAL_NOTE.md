# The wall in structural terms

Written 2026-11-21. Scope: the 11,585 open cases in the seven small degree
profiles — what they are, why the campaign's argument is weakest exactly
there, and what a proof would have to supply. Numbers come from
`tools/profile_table.py`, which recomputes the table from the definition, and
from `results/ledger-2026-11-22.tsv.gz` (rebuilt here byte-for-byte, 113,180
lines, summary identical).

## 1. The seven profiles are exactly the vertices with at most two critical colours

At a vertex `v` of a triangle-free 4-colouring, `d_c(v) = |N_c(v)| <= 16`
(`N_c(v)` has no colour-`c` edge, so it is 3-coloured by the other three
colours, and `R(3,3,3) = 17`), and the four degrees sum to 57. The sorted
profiles are therefore the partitions of 57 into four parts `<= 16`, and the
cover has all eleven of them.

Call colour `c` **critical at `v`** when `d_c(v) >= 15`, and let

    w(v) = sum of the critical degrees at v

(the number of neighbours joined to `v` in a colour that is critical at `v`).
Then (all columns recomputed by `python3 tools/profile_table.py`):

| profile | critical | w(v) | open | total | wall |
| --- | ---: | ---: | ---: | ---: | :---: |
| 16,16,16,9 | 3 | 48 | 0 | 214 | |
| 16,16,15,10 | 3 | 47 | 0 | 1,767 | |
| 16,15,15,11 | 3 | 46 | 0 | 16,173 | |
| 15,15,15,12 | 3 | 45 | 20,166 | 83,440 | |
| 16,16,14,11 | 2 | 32 | 140 | 140 | yes |
| 16,16,13,12 | 2 | 32 | 140 | 140 | yes |
| 16,15,14,12 | 2 | 31 | 2,058 | 2,058 | yes |
| 16,15,13,13 | 2 | 31 | 1,046 | 1,046 | yes |
| 15,15,14,13 | 2 | 30 | 7,732 | 7,732 | yes |
| 16,14,14,13 | 1 | 16 | 88 | 88 | yes |
| 15,14,14,14 | 1 | 15 | 381 | 381 | yes |

The split is clean: **the four profiles the campaign finds reachable have
three critical colours; the seven it is stuck on have two or one.** A proof
that every vertex of a triangle-free 4-colouring of `K_58` has at least three
critical colours — "no vertex has two colour-degrees `<= 14`" — would empty all
seven at once.

## 2. The campaign's engine, and why it is weakest there

The one global input is the ticket identity

    sum_v H(v) = sum_v w(v),

where `H(v)` counts the neighbours `u` of `v` whose edge to `v` is critical at
`u`. It is trivial (both sides count tickets sent) and it guarantees a root
`r` with `H(r) >= w(r)`. For such a root the cover fixes thresholds `t_c` with
`sum_c (t_c - 1) < w(r)` and refutes, for each arm, "arm `c` has at least `t_c`
senders". The whole budget the argument can spend is `w(r) - 1`.

At a wall vertex that budget is 14 to 31; at a reachable one it is 44 to 47.
That is the mechanical reason the two sets of profiles behave differently, and
it is a property of the *method*: the wall profiles are not "less constrained"
by geometry, they are the ones where the ticket argument has least to spend.

The cases are not vacuous, though, and it is worth being precise about what
the one-critical profile asserts. For `(15,14,14,14)` the plan takes
`t = 15` in the single 15-arm, so each case refutes: "there is a triangle-free
4-colouring of `K_58` in which `r` has a 15-class (a U- or T-minus template),
and a marked `q` of that class also sends to `r` along that colour" — i.e. `q`
has its own critical class of size `>= 15` through `r`. Two 15- or 16-classes
are pinned and 27 to 29 vertices are left free, and the case still does not
close: 0 of 42 at 60 s, 0 of 9 at 300 s.

## 3. L is not a local statement

Two facts rule out the obvious local approaches.

* **Pair bound.** For colours `i, j` and a vertex `v`, the colouring induced on
  `N_i(v) union N_j(v)` with `i` and `j` merged is a 3-colouring with no
  monochromatic triangle in the other two colours and no monochromatic `K_5`
  in the merged colour (a `K_5` there plus `v` is a 2-coloured `K_6`). So
  `d_i(v) + d_j(v) <= R(3,3,5) - 1`. But `45 <= R(3,3,5) <= 57` (DS1.18,
  claim (d)), so the bound is 44 or more and says nothing about 25..28.
  Iterating the same idea with more colours is what gives the known
  `R_4(3) <= 62`-style bounds, and it is why no grouping argument separates 58
  from the open range.
* **The verified `K_50` colourings already do this.** `artifacts/k50_z4z4_m6.col`
  has vertices of profile `(7,12,15,15)` and `(8,12,13,16)`;
  `k50_blockcayley_Z4xZ4_m4.col` has `(9,13,13,14)`;
  `k50_sanity_f2.col` has `(10,12,13,14)`. Two or three colour-degrees `<= 14`
  is realisable at 50. So no inequality that holds at every vertex of every
  such colouring can be sharpened from 50 to 58 by local reasoning alone —
  what changes is the sum, 49 versus 57, and that is a global fact.

Any proof of the target statement therefore has to be global.

## 4. The n = 60 precedent, which is the closest thing to a template

`.scratch/k60ref/proof.md` (the unrefereed `R_4(3) <= 60` argument) is the same
construction one level up. There the deficits sum to 5 and there are six
profiles; the two with exactly two critical colours are C1 `(13,14,16,16)`,
`w = 32`, and C2 `(14,14,15,16)`, `w = 31`. Section 2's ticket bounds refute
the other four, leaving "perfect balance"; Section 6 then uses reciprocity of
tickets, internal connectivity of the colour graphs inside a critical
template, and homogeneity to force **one common critical pair at every
vertex**, i.e. every vertex C1 or C2; Section 7 excludes that case with 8,532
exact formulas.

Three things follow.

1. The n = 60 proof met the same wall and crossed it by computation in two
   steps. Section 5 excludes an *entrance* -- a C1/C2 root `r` with a sender
   `p` in one of its non-critical neighbourhoods -- with 8,532 exact formulas
   (692 at C1, 7,840 at C2; `.scratch/k60ref/proof.md`, table at line 657).
   With no entrance, `H(v) <= w(v)` everywhere; since `sum H = sum w` and every
   difference is non-negative, `H(v) = w(v)` everywhere and only C1/C2 remain.
   Section 7 then excludes that balanced case, after deriving guards and
   visible neighbourhoods, by a second family of formulas. So "no vertex has
   only two critical colours" is not a structural truth at n = 60: it was the
   *output* of that computation. The n = 58 wall is the same kind of object --
   11,585 formulas in place of 8,532 -- not a different kind.
2. What differs is the per-case difficulty. At n = 60 the two-critical profiles
   have critical arms 16 and 15/16 with the small arms 13 and 14; at n = 58 the
   wall carries arms of 11 to 14 and a deficit spread of 7 instead of 5, which
   is why the same encoding closes 8,532 formulas at 60 and 0 of 68 at 58.
3. The step that carries Section 6 is "every vertex has at least 31 critical
   neighbours, and 31 + 31 > 60, so any two critical sets intersect". At n = 58
   the corresponding inequality is `w(u) + w(v) > 58`; it holds for every pair
   of two-critical wall vertices (`w = 30..32`) but fails for the one-critical
   ones (`w = 16, 15`). The numerical part of Section 6 is *more* comfortable
   at 58 -- the argument bounds `d_j(x) <= 5 + 5 = 10` against a critical
   requirement of 15 -- so the obstruction to porting it is the reciprocity
   step, and reciprocity at n = 60 is exactly what Section 5's computation
   supplied.

The transferable lead is therefore not "prove L" but "derive the n = 58
analogue of the guards and actual visible neighbourhoods of 7.1-7.2 and add
them to the encoding": at n = 60 that is what made the formulas small enough
to close, and it is the one thing the n = 58 cover does not yet do.

## 5. What would settle it, and what would not

Would: a global lemma that a vertex with one or two critical colours forces a
contradiction — e.g. by making the two critical arms' ticket exchange
reciprocal, which pins the two templates against each other and leaves too few
free vertices. The reduction to test first is whether `H(r) >= w(r)` at a
two-critical root forces the *other* end of each ticket to be critical as well
(the n = 60 reciprocity step). If that goes through at 58, the wall becomes a
finite but much smaller search over two-template configurations with a common
critical pair.

Would not: any further budget on the current case encodings (0 of 68 at 70 s,
0 of 42 at 60 s, 0 of 9 at 300 s, and a 644 MB DRAT from CaDiCaL in 120 s
without closing); any substitution, Cayley or group-partition construction
(Anabanti; primitivity at `n >= 51`); and any argument that ignores the
global degree sum.

## 6. Consequence for the open decision

The throughput pass (20,166 cases of `(15,15,15,12)`, ~390 CPU-h, about 33 h
wall on 12 cores, ~480 GB of DRAT deleted as it goes) takes the cover from
70.0% to 87.8% and leaves the wall and the 2,144 legacy rows untouched. It
moves no bound on its own: the reduction at n = 58 is unformalised (no Lean
bridge, marking lemma unstarted). The wall is the binding constraint, and on
the measurements above it is not a budget problem at the current encoding.

The one thing the n = 60 proof did that this campaign has not is derive
structure from the root hypothesis and add it to the encoding (guards,
visible neighbourhoods, exact membership) instead of giving the solver the
bare case. That is the cheapest next experiment on the wall and it is a
research step, not a purchase of CPU time: no wall case closed at 70 s or
300 s, while the n = 60 formulas of the same shape closed in bulk.
