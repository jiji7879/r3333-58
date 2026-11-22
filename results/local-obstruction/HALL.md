# The Hall inequality for colour-0 independent 15-sets, decided

## Statement (as the pentagon package states it)

For colour-0 independent sets `I`, `J` with `|I| = 15` and `S ⊆ J \ I`,

    |N_0(S) ∩ I| ≥ |S| − 1.

## It is a theorem, and it is exactly the single-colour independence bound

`(I \ N_0(S)) ∪ S` is colour-0 independent: `S` is (it lies in `J`), `I` is, and no
element of `S` is 0-adjacent to a surviving element of `I`. So its size
`15 − |N_0(S) ∩ I| + |S|` is at most `α(G_0)`. In a triangle-free 4-colouring of
`K_n` with `n ≥ 17`, `α(G_0) ≤ 16`: a 17-set with no colour-0 edge would be a
triangle-free 3-colouring of `K_17` in colours 1,2,3, and `R(3,3,3) = 17`.

Conversely, if `α(G_0) ≥ 17` and `W` is a colour-0 independent set of size `α_0`,
take `I` = any 15 vertices of `W` and `S` = two others. Then `S ⊆ W \ I`,
`S` is colour-0 independent, and `N_0(S) ∩ I` is empty because `W` is independent.
So

    Hall  ⟺  α(G_0) ≤ 16.

The inequality is therefore a consequence of `R(3,3,3) = 17` alone. It carries no
information beyond `α(G_0) ≤ 16`, hence none beyond "the colour-0 graph is
17-clique-free in the complement", which full triangle-freeness already gives.

## Exact margin, and the size cap

`J` has 15 vertices, so always `|S| ≤ 15`. Put

    margin(I,S) = |S| − 1 − |N_0(S) ∩ I| = |(I \ N_0(S)) ∪ S| − 16.

Since the exchange set is colour-0 independent and `|I \ N_0(S)| ≤ 15`,

    margin ≤ min(α_0, 30) − 16,

and the bound is attained: split a colour-0 independent `W` with
`|W| = min(α_0, 30)` into `I` (15 vertices) and `S` (the rest). So the **exhaustive
answer over all `(I, S)` in one closed form** is `min(α_0, 30) − 16`.

## Verdict on the five witnesses

| witness | `α(G_0)` | max margin | verdict |
| --- | ---: | ---: | --- |
| `smwr8io45/m6/wit/pair58_Tminus.wit` (= `L_58.wit`, byte-identical) | 34 | 14 | violated |
| `smwr8io45/m4/pair58_Tminus_recoloured.wit` | 41 | 14 | violated |
| `smwr8io45/m4/wit_big.wit` | 36 | 14 | violated |
| `smwrfgma5/m4/wit/p58.wit` | 30 | 14 | violated |
| `smwrfgma5/m4/wit/p58_cc.wit` | 30 | 14 | violated |

and with `I = A` alone (the case the wall tested by sampling) the exact maximum is
**2** for all five: there is `T ⊂ A` with `|T| = 12` and 15–18 words whose colour-0
support lies inside `T`, so `|N_0(S) ∩ A| ≤ 12 < 14 = |S| − 1`. Beware the tempting
shorter route: dropping the hypothesis that `S` is colour-0 independent (which it is,
being a subset of `J`) gives the weaker bound `max_{|T| ≤ 13} (c(T) − |T| − 1)` =
7..10. The exact answer with that hypothesis enforced is 2.

The two witnesses the record *describes* but never stores are decidable on the
`I = A` half from their words alone, and both fail with margin **8**: WALL §13's
five-line construction and WALL §16's extremal-word witness
`002102211112020 / 332032200002323 / 330130011110303` have the same three
colour-0 supports `{0,1,4,12,14}`, `{3,7,8,9,10}`, `{2,5,6,11,13}` at 14 copies
each.

## Calibration

`α(G_c)` computed exactly on all fifteen `artifacts/*.col` colourings:
every genuine 4-colouring has `max_c α(G_c) = 16` exactly, attained in every colour
at `n = 49, 50, 51`; the `n = 48` Family-A colouring gives `(15,16,16,16)`, whose
15 is the 0-arm of the profile `(15,11,11,10)`. So `α ≤ 16` is true on real objects
and the bound is sharp.

## Method and validation

`scripts/mis.py` — bitset maximum-independent-set (colouring bound on the
complement), validated against brute force on 400 random graphs and against
enumeration of all maximum independent sets.
`scripts/crosscheck_mis.py` — every `α` re-decided by a SAT call with a sequential
cardinality encoding at `α` (SAT) and `α+1` (UNSAT); 16 of 16 agree.
`scripts/verify_hall.py` — re-checks each shipped certificate from the `.wit` file
alone. **All certificates verify.**

## Correction to the record

`review/PROFILE_15141414_STATE.md` §10 says "one witness survives it", and
`review/WALL_15141414_SWARM.md` §27 reports "no violation occurs" for `p58.wit`
with `I = A` over 300 random `J`. Both are sampling artefacts: the random-`J`
sample never meets a `J` lying inside a 12-point `T`. No witness survives, with
`I = A` or without.
