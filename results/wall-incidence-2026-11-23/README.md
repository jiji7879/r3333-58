# The wall-incidence bundle: 381 certified cuts, and what they do and do not close

Bundles: `K58_wall_incidence_addon.zip` (119 KB) + `K58_wall_incidence_DRAT.zip` (19.0 MiB),
unpacked at `.scratch/wi/`. Received 2026-11-23.

## What it contains

For each of the 381 rows of the `(15,14,14,14)` profile, a **single-colour incidence cut**: fix a
root, a colour `h`, its arm `B`, and partition the remaining 43 vertices into cells of size ≤ 3.
Writing `D_i` for the arm vertices touching cell `P_i` and `I_i` for the common `h`-neighbours in
`Q`, the union `I_i ∪ D_i` omits colour `h`, so it has size ≤ 16, giving

> Σ|D_i| ≤ Σ(16 − |I_i|), and for a 14-arm at least `42 + 2t` incidences are needed (`t` senders).

Over the published 5-regular alignment this gives `42 + 2t ≤ 41 + 2d`, i.e. **at least `d = t + 1`
prescribed edges must differ from colour `h`**. Per row: `d = 1` for 36 rows, `d = 2` for 311,
`d = 3` for 34. The DRAT archive holds **one proof per row for the negation of its strongest
published cut**.

It also classifies the 381 rows: **64 have explicit K₅₀ witnesses** from a three-copy construction
(root degrees `(15,6,14,14)`, all three arms complete), 18 have the mark in the long 15-arm, 296
have a type-T mark in a 14-arm, 3 have a nonextendible four-set. 50 + 14 + 18 + 296 + 3 = 381.

## Verified here

```
python3 restricted.py replay --proofs ../proofs --checker .../drat-trim --jobs 4
Verified the strongest restricted-child proof for each of 381 rows.
real 1m44s
```

All 381 proofs replay against CNFs reconstructed from the physical rows, with `drat-trim`. This is
the cheapest full-archive replay of anything in this campaign so far — the 2,733-proof cross-arm
archive took 10 minutes on four workers, this one under two.

## What it closes

**Nothing.** The bundle is explicit, and its own measurements agree:

- all 381 unrestricted parents remain **OPEN**;
- the 34 full K₅₈ parents were run with the strongest cuts at 10 s / 50,000 conflicts, seed 0 — all
  34 reached the conflict limit and stayed OPEN (`full58-runs.json`);
- the 18-row K₅₁ projections were run at 8 s / 50,000 conflicts — all reached the limit, OPEN
  (`k51-runs.json`).

The cuts are a **screening layer**: a certified reason to reject a proposed partial join. That is
useful for pruning a queue, and the bundle is careful about its scope — the published alignments
"were deliberately selected to survive ordinary unit propagation" and "do not measure a frequency
in a production search".

## The barrier result, which is the more important half

64 rows admit explicit triangle-free **K₅₀** colourings satisfying their projected pins, with the
root of degrees `(15,6,14,14)` and the marked neighbourhood intact. Those 64 rows therefore **cannot
be closed by an argument that uses only the projected pins** — any such argument would have to
exclude a colouring that demonstrably exists. That is a real constraint on what a wall argument may
assume, and it is worth more than the cuts: it rules out a whole style of proof for 17 % of the
profile.

## What this does not answer

Whether "enough time" settles the wall. Nothing in this bundle bears on that: it adds certified
pruning, and every parent it was applied to stayed open.
