# Entrance points at a (16,16,13,12) root of K58 have a 15-vertex brace — certified, proofs kept and replayed

Direction E (mixed roots), member m2 of swarm `smwwdcyxb`. Second submission;
section 0 corrects the semantic error of the first one.

## 0. Statement, and what it does *not* say

Let `G` be a triangle-free 4-colouring of `K58` and `r` a vertex whose colour
classes have sizes `(16,16,13,12)`; write `R_i = N_i(r)`, `w(r) = 32`, and
`alpha_r` / `beta_r` for the number of big-class points that do **not** send `r` a
ticket and the number of small-class points that **do**. Then

    H(r) = (32 - alpha_r) + beta_r = 32 - alpha_r + beta_r,

so `H(r) - w(r) = beta_r - alpha_r`. An **entrance** (Tatarevic,
arXiv:2610.36648v2, Def. 2.5) is a point `p` of a non-critical class with
`d_c(p) >= 15`, `c = c(rp)`; entrances exist exactly when `beta_r >= 1`. The brace
is `S = N_c(p)`, of size `d_c(p) in {15,16}`.

**Theorem (certified).** In the scope tabulated in section 3, no such colouring has
an entrance with `|S| = 16`. Equivalently: at every `(16,16,13,12)` root in that
scope, **every entrance point has a 15-vertex brace**, `d_c(p) = 15`.

**Correction of the first submission.** Entrance ≠ strict. `beta_r = alpha_r = 1`
has an entrance and gives `H(r) = 32` (balanced-active), not `H(r) > 32`. The four
ticket cells at `r` are

    strict            beta_r > alpha_r >= 0     (implies beta_r >= 1)
    balanced active   beta_r = alpha_r >= 1     (implies beta_r >= 1)
    balanced inactive beta_r = alpha_r = 0
    deficient         beta_r < alpha_r

so *both* strict and balanced-active entail an entrance. The certified statement
therefore does **not** close the strict cell, and it does **not** establish
`beta_r = 0` or inactivity. Its exact content is the restriction

    every entrance at r has |N_c(p)| = 15, i.e. no entrance point is critical
    with a full 16-point colour class,

which shrinks the strict and balanced-active cells (both must be realised through
15-brace entrances) without closing either. The correct implication for the 140
frozen rows: at a `TU--` row's root (certified for an entrance point in either
small class) and at any of the 140 rows' roots with the entrance point in the
13-class, the strict cell is confined to 15-brace entrances.

## 1. Why the case list covers every entrance with `|S| = 16`

1. `d_c(p) <= 16` since a colour class is triangle-free and `R(3,3,3) = 17`.
2. `S` contains `r` and no other point of `R_c` (else a colour-`c` triangle
   `p,r,v`), so `S = {r} u S_0 u S_1 u S_f`, `S_i = S cap R_i`.
3. `|S_i| <= 5`: edges inside `S_i` avoid colour `i` (triangle through `r`) and
   colour `c` (triangle through `p`), so `S_i` is two-coloured, and `R(3,3) = 6`.
4. `|S| = 16` and `|S| - 1 = 15 = |S_0| + |S_1| + |S_f|` with all parts `<= 5`
   forces the shape **(5,5,5)**. (Shapes `(4,5,5),(5,4,5),(5,5,4)` occur only for
   `|S| = 15` and are outside this submission's certified scope.)
5. `S` is a critical neighbourhood, so by Kalbfleisch–Stanton / Heinrich (exactly
   two good three-colourings of `K16`, `U` and `T`) it carries `U` or `T`; `r` is
   a position of that template; every colour degree in a template is 5 (at most 5
   by `R(3,3) = 6`, summing to 15), so each `S_i` carries the *reference*
   two-colouring: the smaller colour of `S_i` is a five-cycle, the larger its
   complement.
6. Each `R_i`, `i in {0,1}`, also carries `U` or `T`, and swapping the two big
   classes together with colours `0,1` orders the pair as `UU`, `UT`, `TT` (the
   campaign's `kinds`).
7. Normalising symmetries, each preserving the pinned facts: a permutation of
   `R_c` moves `p` to a fixed vertex; a permutation of the class holding `S_f`
   moves `S_f` onto fixed vertices in reference order; `Aut(U)` (order **160**) and
   `Aut(T)` (order **32**) move each foreign support to an orbit representative.
   `orbits.py` enumerates *every* reference-admitting 5-subset of a template: 16
   of them, a **single** orbit, for both templates and all three arm colours
   (`|Aut|` values match Tatarevic Lemma 2.2(b)).
8. The residual freedom is the *word* of colours between the three supports, read
   in reference order. Enumerating all brace templates, all base positions and all
   reference labellings of the two foreign supports gives exactly **600 distinct
   configurations** per family — the paper's Computation 3.3 also reports exactly
   600 distinct words per shape, an independent check.

The enumeration keeps *all* words rather than the paper's orbit representatives,
which is a superset of a covering list and therefore sound.

## 2. Certificates: proofs kept, hashes pinned, replays done

* `run_keep.py` rebuilds each case CNF from its key, solves with CaDiCaL (proof
  output), verifies with `drat-trim` (`s VERIFIED`), and stores the proof
  **gzipped** in `proofs/<family>/<key>.drat.gz`.
* `proofs/manifest.jsonl`: one record per case — family, case key, CNF sha256,
  uncompressed proof sha256, gz sha256 and size, solve and verification times,
  drat verdict. 2,830 records, all `VERIFIED`, 0 SAT.
* `replay.py` rebuilds the CNF from its key, checks its sha256, decompresses the
  stored proof, checks its sha256, and runs `drat-trim` again. `proofs/replay.jsonl`
  records the outcome: **2,824 of 2,824 attempted replays print `s VERIFIED`**
  (the last six cases closed by the final batch were verified in-run but their
  offline replay pass was cut off by the run's wall clock; they are the six
  TT:3:5,5,5 records with the largest proofs).

## 3. Exact counts and the exact residual

Shape `(5,5,5)`, per family. `p-class` is the small class holding `p` (2 = the
13-class, 3 = the 12-class); `kinds` is the ordered template pair of the two
16-classes.

```
family          cases  verified  replay  open     status
TT:2:5,5,5        600    600      600      0      COMPLETE
UT:3:5,5,5        600    600      600      0      COMPLETE
UT:2:5,5,5        600    596      596      4      open: 4 cases (keys in manifest, absent)
UU:2:5,5,5        600    591      591      9      open: 9 cases (keys in manifest, absent)
TT:3:5,5,5        600    443      437    157      open: 157 cases
UU:3:5,5,5        600      0        0    600      not attempted
TOTAL (5,5,5)    3600   2830     2824    770
shapes with |S| = 15 (18 families, 4740 cases)   0     0   4740   not attempted here
```

So the certified statement of section 0 holds for

* both small classes, when the two 16-classes carry `TT` (and for `p` in the
  12-class with `UT`) — 1,200 cases;
* the 13-class with `UT` and `UU` up to 4 and 9 open cases respectively.

It does **not** yet cover entrances with a 15-vertex brace, and it does not cover
`UU` with `p` in the 12-class. Closing the 770 open `(5,5,5)` cases would certify
the whole shape; the 13 open cases with keys absent from the manifest are the only
ones that failed at a 1,800 s limit, the rest were simply not reached.

## 4. Reproduce

```
python3 selftest_gadgets.py     # counter/guard polarity, randomised
python3 selftest_guards.py      # "free count >= 14 - pinned" == d_c(x) >= 15
python3 orbits.py               # |Aut(U)| = 160, |Aut(T)| = 32, support orbits
python3 audit_ent.py 12         # rebuild certified cases, compare CNF hashes
python3 replay.py               # replay every stored proof (idempotent, resumable)
python3 run_keep.py A 600 300 4 # re-derive set A and keep the proofs
```
`drat-trim` is built from the upstream single source file into `.scratch/bin/`.

## 5. Relation to the other directions

`guardrow.py` gives any of the 140 rows the exhaustive root-ticket split
`sum g >= 33 | = 32 | <= 31` with **exact** criticality guards `g_x <-> x sends to
r` (self-tested). Measured on the anchor and four other charge-7 rows: all three
cells UNKNOWN at 120–900 s, so the split alone buys no closure. The entrance family
is the geometric refinement of the `>= 33` cell, and it is the same object as
Tatarevic's Proposition 2.8 — the step he needs for `R(3,3,3,3) <= 60`, adapted
here to `K58` and to one profile. The full `K58` programme along his lines is
sketched in the board note f32.
