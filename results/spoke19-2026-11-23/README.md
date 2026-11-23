# The twenty-spoke add-on: what it narrows, and what it does not decide

Bundle: `K58_spoke19_solver_addon.zip` (20.3 KiB), unpacked at `.scratch/sp19/`. Received
2026-11-23. Companion proof zips are **not** included, so the refutations themselves cannot be
replayed here.

## What it claims

On the two published rows, in addition to the known `U >= 7`, `V >= 8`, `U+V >= 19`:

- `U >= 8 or V >= 13`, and `U >= 12 or V >= 9`.

Together these cut the total-19 diagonal from six splits to **three**: `(8,11)`, `(9,10)`, `(10,9)`.
`U = 7` would force `U+V >= 20`; the two endpoints `(7,12)` and `(11,8)` are excluded on both rows.
Nothing is proved at 20: the three remaining splits at 19 are untouched.

## Verified here: all five splits are attained on small boards

The add-on ships 14 equality witnesses. The judge checked **all 14** from the definition — colours
decoded from each witness's upper triangle against its own vertex list, every triple tested, every
retained pin compared through the bundle's numbering, and the two spoke counts computed directly:

| witness | vertices | pins checked | U,V |
| --- | ---: | ---: | --- |
| `076e-7-12-K38` / `4629-7-12-K38` | 38 | 263 / 273 | 7,12 |
| `076e-8-11-K39` / `4629-8-11-K39` | 39 | 265 / 275 | 8,11 |
| `076e-9-10-K39` / `4629-9-10-K39` | 39 | 265 / 275 | 9,10 |
| `076e-10-9-K38` / `4629-10-9-K38` | 38 | 263 / 273 | 10,9 |
| `076e-11-8-K38` / `4629-11-8-K38` | 38 | 263 / 273 | 11,8 |
| four `model-*` boards | 36 | 269 | 8,11 and 9,10 |

All 14: **0 monochromatic triangles, 0 pin violations**, counts exactly as claimed.

Consequence, and it is a barrier rather than a step: **no board of 36–39 vertices can force
`U+V >= 20`**, because 19 is attained on them with the retained pins. If the bound is ever to be
pushed to 20, the boards must be larger than 39 vertices. It does **not** follow that those boards
admit 18 — the question the cheap route asks.

## The parents stay open

Eight runs on the frozen first-pass parents at the four splits `(8,11)`–`(11,8)`, 135,000 conflicts
each: all **OPEN**. Six strengthened-parent runs with the new cuts, 300,000 conflicts each: all
**OPEN** (actual conflicts 146,903 and up). Hashes and counts in `benchmarks/spoke-19/`.

## Not verified

The four local refutations behind `U >= 8 or V >= 13` and the five behind `U >= 12 or V >= 9`. They
are recorded as receipts against proof hashes; the proofs live in the two DRAT archives that were
never supplied. So the narrowing from six splits to three is **reported, not replayed** here.
