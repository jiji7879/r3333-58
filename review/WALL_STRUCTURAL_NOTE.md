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

Two things follow.

1. The step that carries Section 6 is "every vertex has at least 31 critical
   neighbours, and 31 + 31 > 60, so any two critical sets intersect". At
   n = 58 the corresponding inequality is `w(u) + w(v) > 58`, which holds for
   every pair of two-critical wall vertices (`w = 30..32`) but fails for the
   one-critical ones (`w = 16, 15`). So a port covers 11,116 of the 11,585
   cases and leaves the 469 one-critical ones, which are the hardest (0 of 42
   at 60 s, 0 of 9 at 300 s).
2. At n = 60 the analogous statement — "no vertex has only two critical
   colours" — is true but was established by computation, not by structure.
   The honest reading is that at n = 58 the target is a **compression of 11,585
   cases**, not a hypothesis that can be assumed: if it has a proof it will be
   a global argument of the strength of Section 6, applied where Section 6's
   own counting fails.

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

The throughput pass (20,166 cases of `(15,15,15,12)`, ~390 CPU-h ≈ 33 h wall
on 12 cores, ~480 GB of DRAT deleted as it goes) takes the cover from 70.0% to
87.8% and leaves the wall and the 2,144 legacy rows untouched. It moves no
bound on its own: the reduction at n = 58 is still unformalised (no Lean
bridge, marking lemma unstarted). The wall is the binding constraint and, on
the measurements above, it is not a budget problem.
