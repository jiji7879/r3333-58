# Written arguments for the m10 report

Notation and the branch are as in `review/PROFILE_15141414_STATE.md`: a vertex
`r` of a triangle-free 4-colouring of `K_58` with profile `(15,14,14,14)`;
`A = N_0(r)` (15 points), arms `B = N_1(r)`, `C = N_2(r)`, `D = N_3(r)` (14 each),
`X = A ∪ B ∪ C ∪ D` complement (42 slots). For `x ∈ X` the *word* is the map
`a ↦ colour(x,a)` on `A`, and `M_f(x) = {a ∈ A : colour(x,a) = f}`.

Branch facts used below, each of them already in the record:

* **(F1)** `m(x) = |M_0(x)| = 5` for every `x ∈ X` (uniform fully-sending child).
* **(F2)** `d_0(a) = 15` for every `a ∈ A`, hence each `a` lies in exactly
  fourteen of the supports `M_0(x)` (the fifteenth colour-0 neighbour is `r`).
* **(F3)** every `N_0(a)` (`a ∈ A`) is a critical 15-point template, so its
  internal colouring has exactly 35 edges of each of the three ordinary colours
  (`Classified 15`; the number 35 is verifiable directly on both artefacts).
* **(F4)** kernel-checked: `K58.mixture` (L1), `K58.interface_count`,
  `K58.part_family_le_five` (the sixth arm lemma).

## Lemma 1 (list colouring of K_3)

Let `L_1, L_2, L_3 ⊆ C` be nonempty. The three edges of `K_3` can be coloured
from the lists with no monochromatic triangle **iff** it is not the case that
`L_1 = L_2 = L_3 = {c}` for a single `c ∈ C`.

*Proof.* If all three lists are `{c}`, every colouring is `(c,c,c)`, which is
monochromatic. Otherwise: if some `L_i` contains two distinct `a ≠ b`, then either
one of the other lists contains an element `≠ a` — colour `i` with `b` — or both
other lists are `{a}`, and colouring `i` with `b` again gives a non-monochromatic
triple. If all three lists are singletons `{c_i}` and not all `c_i` equal, the
only colouring is not monochromatic. ∎

Consequence for the enumeration in the report: the *local object* on a slot set
`S` is infeasible iff some pair in `S` has an empty admissible list, or some
triple in `S` has all three lists equal to one singleton. Only the second case
occurs for the campaign's witnesses, and it occurs at size three, which is why the
truncation depth is 3 and why every obstruction has three equal singleton
domains.

## Lemma 2 (coverage, counted twice)

`Σ_{x ∈ X} |M_0(x)| = Σ_{a ∈ A} #{x : a ∈ M_0(x)}`, and by (F1) and (F2) both
sides equal `42·5 = 210 = 15·14`. This is the record's interface identity at the
extremal child; it is what makes "five per outside vertex" and "fourteen per arm
point" simultaneously saturable, and it is why no per-vertex interface argument
can close the branch. Verified numerically: `score.py` prints coverage 14 for
every point on each 42-slot witness.

## Lemma 3 (the 455 identity, and why it is a *check* and not a constraint)

For a colour `f ∈ {1,2,3}` count the pairs `(a, {y,z})` with `a ∈ A`,
`colour(y,z) = f`, `y,z ∈ X`, `colour(a,y) = colour(a,z) = 0`:

* by pairs: `Σ_{{y,z} f-edge} |M_0(y) ∩ M_0(z)|`;
* by arm points: `Σ_{a∈A} e_f(X ∩ N_0(a))`.

Now `N_0(a) = {r} ∪ (X ∩ N_0(a))`, and the `f`-edges inside `N_0(a)` that touch
`r` are exactly `{r,z}` with `z ∈ N_f(r) ∩ N_0(a)`, i.e. `a ∈ M_0(z)`. Hence

  `Σ_{{y,z} f-edge in X} |M_0(y) ∩ M_0(z)| = Σ_{a∈A} e_f(N_0(a)) − Σ_{z∈N_f(r)} m_0(z)`.

The right side is `15·35 − 14·5 = 525 − 70 = 455` by (F1)–(F3). So in a genuine
object **each ordinary colour carries overlap mass exactly 455**, and since a
colour-0 pair has `M_0`-parts that intersect in nothing (the pair rule at `f = 0`),
the three masses sum to the total `Σ_{pairs}|M_0 ∩ M_0| = Σ_a C(14,2) = 1365`.

This is why the record's 319 / 314 / 732 (also 484 / 377 / 504, 493 / 388 / 484)
is a refutation of those words and not merely a curiosity: the *split* is forced,
and no re-colouring of the same words can move the *total* 1365, only its
distribution. The identity is an identity (it holds for every colouring), so it
cannot be used as an extra constraint on the pair colours; it constrains the
*words* jointly with the pair colours, which is why it is a check.

## Lemma 4 (exact obstruction counts)

For a witness `W` with 42 slots, `C(42,2) = 861` pairs and `C(42,3) = 11,480`
triples were each tested for a valid local object (`depth.py`; a backtracking
search over the pairs' admissible lists with the monochromatic-triangle clause,
which is exact by Lemma 1 and by construction). No pair fails; the triple counts
are those in the report's table, and every failing triple has three equal
singleton domains (checked by `analyse.py`, which prints the domain-size
histogram `{(1,1,1): n}` — it is `(1,1,1)` for all `n`).

For the two-arm witnesses the counts are over their own 26- and 28-slot sets:
40, 44, 50, 52, 55. The two-arm instance is SAT, and yet each of those SAT
witnesses already carries a three-slot word-level obstruction — i.e. the pair
level's satisfiability survives only because the pair level never asks a triple
to be *globally* consistent.

## Lemma 5 (every 14-slot arm needs a generic word)

A word is *extremal* if one of its three ordinary parts is empty. There are
exactly 18 of them (the full census of 254,628 words is reproduced here:
`(4,3,3) 162,306`, `(4,4,2) 63,504`, `(5,3,2) 25,020`, `(5,4,1) 3,780`,
`(5,5,0) 18`).

*Claim.* No 14-slot arm of a genuine object is built only from extremal words.

*Proof.* Two slots carrying the same extremal word `w` with empty part `f`:
every colour `g != f` has `M_g(x) = M_g(y) ≠ ∅`, and `f ∉ {arm colour}` when the
word is used in that arm, so the pair's admissible list is exactly `{f}` — a
singleton. Three such slots give three pairs with list `{f}`, which Lemma 1
forbids. Hence a word may occur at most twice in an arm.

The rest is finite: `extremal2.py` runs the exact search over all size-14
multisets of the 18 extremal words with multiplicity at most 2, keeping only the
multisets all of whose pairs are admissible, and testing the Lemma-1 condition on
every triple. For each of the three arm colours the search returns **0**
multisets (search trees of 3,093, 3,783 and 3,843 nodes).

For the record: with pairwise admissibility *alone* the search returns 2,244,026
multisets per arm colour, so the finite step is exactly where the depth-3
condition is needed; the record's sentence "an all-extremal arm cannot fill 14
slots" is true only in this strong form. (The multiplicity bound `<= 2` is not an
extra assumption: three copies are already forbidden by Lemma 1.) ∎

Consequence: every 14-slot arm of a genuine object carries a generic word, which
is the mechanism behind the record's remark that `14+14` is harder than one arm
and that cross-arm pairs are free exactly when a word is extremal.



`enc_design.py` builds the colour-0 side alone: cells `c(x,p)`, exactly five per
slot (F1), exactly fourteen per point (F2), and for each arm and each six-subset
of its fourteen slots the clause "not all fifteen pairs of that six-set are
`A`-intersecting", which is the colour-0 instance of the sixth arm lemma (a common
point of `A` is a common colour-0 neighbour, so `ABlocked` holds).

The instance is SAT (kissat, < 1 s) and the model decodes (`extract_design.py`)
to 42 five-sets with every point in exactly fourteen and intersection-graph
clique number exactly 5 in each arm. Since 5 is the bound of the lemma, the
colour-0 side of the branch is *sharp*: no counting argument on the supports and
their intersections can do better than 5, and 5 is attained. This is the precise
sense in which the record's "the cap bundle is thin" remark can be upgraded: at
the support level the constraint is not merely satisfiable, it is attained.

What does *not* follow: that the design extends. `cnf/design_plain.cnf` — the
design pinned into the pair level — is UNSAT (7,839 conflicts, DRAT verified), so
this particular sharp design has no pair colouring. That is a statement about the
design, not about the branch.

## Why no family in my encoders over-constrains (the exactness table)

See the table in `REPORT.md` §3. The two families worth stating in full:

* **(S), the sixth arm lemma in A-part form.** If six slots `x_1..x_6` of one arm
  `b` are pairwise `a`-blocked by common colour-`a` neighbours `z_ij ∈ A`, then
  (i) every mutual edge avoids `a` (else a monochromatic triangle with `z_ij`),
  (ii) every mutual edge avoids `b` (else a monochromatic triangle with `r`),
  so the six slots carry a triangle-free 2-colouring of `K_6`, which does not
  exist. This is `K58.blocked_set_le_five` with the `A`-witness of blocking.
* **(T2)/(T3).** In a genuine object every pair has its own colour admissible
  (P2/P3) and every triple's three lists are therefore nonempty and, by
  Lemma 1, not all the same singleton (the restriction of the genuine colouring
  is a valid colouring of that `K_3`).

## What remains open, stated exactly

1. Is the pair level + the sixth arm lemma (both forms) satisfiable? `cnf/sixth2.cnf`.
   UNKNOWN at the budgets tried; nothing here bears on the answer.
2. Is the word-only depth-3 relaxation (T2 + T3, `cnf/t3v2.cnf`) satisfiable?
   UNKNOWN at 330 s (kissat, 2.13 M conflicts) and 620 s (CaDiCaL).
   A SAT answer would be a strictly better object than every witness in the
   record (all of them have hundreds of dead triples); an UNSAT answer would
   close the uniform fully-sending branch, since T2 and T3 are consequences of it.
3. Does any sharp colour-0 design extend to a pair colouring? The one found here
   does not; the question is open for the other designs.
