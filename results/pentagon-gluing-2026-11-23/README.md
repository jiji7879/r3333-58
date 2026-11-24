# The pentagon-gluing bundle: fully verified here, with the certificates regenerated

Bundle: `K58_pentagon_solver_and_proof_notes.zip` (53.3 MiB), unpacked at `.scratch/pg2/`. The
410 MB DRAT archive was **not** used: every certificate was rebuilt from its recorded specification,
solved, and checked locally.

## What the bundle proves

On each of the two frozen rows, the marked pentagon in the colour-3 arm must satisfy one of two
cases, and this holds on the 51-vertex projection and hence on the full row:

1. **two-heavy**: at least two outside vertices send colour 1 to ≥ 3 pentagon sites; or
2. **one-heavy**: exactly one does, it hits all five, and the other eight hit eight *distinct pairs*,
   with exactly two of the ten pairs missing and exactly 21 colour-1 edges from the pentagon.

Underneath it sits a lemma for every 14-arm: in a triangle-free three-colouring of `K₁₄`, **any two
vertices have at most four common neighbours in any one colour** (five would give a two-coloured
pentagon and identical signatures). Equivalently the internal colour graphs are `K_{2,5}`-free. The
bound is attained; a `K₁₃` witness attains five, so it is sharp.

## Verified here

**Models and coverage** — `./k58.sh pentagon verify --models-only`:

```
Both parent pin lists match the frozen solver ledger.
Both row-specific K50s, the unmarked-vertex permutations and the omitted-pair involution check.
K13 boundary, 480 local heavy-pair witnesses, both arm premises and signature encoding checked.
All 810 local colorings and the row involution checked.
076e/4629  C 562, D 562 checked colorings;  K50 double pentagon and eight two-spoke signatures
076e  four 120/120; five 40/690; singleton 20/20; witnessed family 10/10
4629  four 120/120; five 40/690; singleton 20/20; witnessed family 10/10
```

**Certificates, regenerated** — each record's CNF was rebuilt from its spec and had to match the
recorded SHA-256 before solving, then solved with the bundle's Kissat and checked with `drat-trim`:

| set | count | time | result |
| --- | ---: | ---: | --- |
| `pentagon-gluing/proofs.json` | 110 | 21 min 33 s | **110/110, 0 failures** |
| `arm-gluing/proofs.json` (forced-triple, preceding) | 52 | 9 min 54 s | **52/52, 0 failures** |

Every CNF hash matched its manifest entry before any solving, so the objects verified are the ones
the bundle intends, and every regenerated proof was accepted by `drat-trim`.

## The capacity-six result

In each of the supplied `K₅₀` witnesses vertex 49 is the only heavy vertex and the eight others meet
exactly the pairs given by masks `3,5,6,9,10,17,18,20` (missing `{46,47}` and `{47,48}`). Exactly ten
local `D`-colourings have those signatures, **all ten are excluded with seven vertices in `B`**, even
with the colours from 49 to `C_*` free and the rest of the board recoloured. Six is attained. So for
that missing-pair family the maximum retained size of `B` is **exactly six**. The reflected family
obeys the same bound.

## What remains, and what it is worth

- `C(10,2) = 45` choices of two omitted pairs; the row involution gives **25 representatives**, the
  witnessed family and its reflection account for one, leaving **24 representative classes** in the
  one-heavy branch — the author's proposed next target, and a bounded one.
- The **two-heavy branch stays open** independently of that count.
- Both full rows remain **OPEN**. The pilot's ten runs, at 250,000 conflicts each with seed 0,
  all reached the limit and stayed OPEN (`pentagon-gluing/pilot.json`); the bundle states plainly
  that the pilot gives **no measured full-row speedup**.

## Judge's note on the common-neighbour lemma

Checked independently against the campaign's own catalogue of 332 arm types: the maximum number of
common neighbours in any one colour is 4, attained in 175 / 192 / 156 types for colours 0 / 1 / 2,
with **zero violations**. So the lemma holds on the whole alphabet, not only on the two rows.
