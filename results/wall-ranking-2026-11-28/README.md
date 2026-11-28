# Ranking the seven wall profiles by expected difficulty

This is a **prior**, not a measurement: every one of the 11,585 rows has resisted every
budget tried (0/98 at 12 s, 0/68 at 70 s, 0/51 at 60 s, 0/9 at 300 s, and 352 rows of
`(15,14,14,14)` at 700 s x4, 40 min, and 600 s on the two-sided encoding). Nothing has
observed one profile close, so the ordering below comes from structure and arithmetic, and a
calibration run could overturn it.

| rank | profile | rows | critical | w(v) | charge >= 4 | kinds |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `16,16,14,11` | 140 | 2 | **32** | 126 | 3 |
| 2 | `16,16,13,12` | 140 | 2 | **32** | 126 | 3 |
| 3 | `16,15,13,13` | 1,046 | 2 | 31 | 320 | 4 |
| 4 | `16,15,14,12` | 2,058 | 2 | 31 | 630 | 4 |
| 5 | `15,15,14,13` | 7,732 | 2 | 30 | 0 | 3 |
| 6 | `16,14,14,13` | 88 | **1** | 16 | 0 | 2 |
| 7 | `15,14,14,14` | 381 | **1** | 15 | 73 | 2 |

`w(v)` is the sum of the critical (>= 15) colour-degrees at the root - the campaign's own
measure of how much of the row the ticket budget can reach. Reachable profiles run 45-48;
the wall runs 15-32.

## Why this order

**The two `16,16,*` profiles are the best targets on every axis.** Highest critical mass
(w = 32), 90 % of their rows at charge >= 4 and 40 % at charge >= 6, the fewest rows of any
two-critical profile (140 each), and only three root-kind families each. If any wall row is
decidable at a large budget, it is one of these; and 280 rows is a finite set somebody could
actually exhaust rather than sample.

**Ranks 3-4 are the same structure one step weaker** (w = 31, a third of their rows at
charge 5) but with 7-15x the row count, so the same per-row cost buys far less.

**Rank 5 is the bulk of the wall and the least promising per row.** 7,732 rows - two thirds
of everything left - with no row above charge 3: every one of them is in the low-charge
regime where the campaign measured its hardest instances (charge 1-3, critical mass 3-5,
closing in 39-52 s but never at the wall). Closing this profile is a 7,732-row search.

**Ranks 6-7 have only one critical colour**, which puts them structurally below everything
else: w = 16 and 15 against 30-32. `15,14,14,14` is also the profile this repository spent
two sessions on with the perfect-balance work, and the result was negative in a specific
way: 29 of its 381 rows die on a ticket pin, the other 352 survive every pin-degree
argument, no isomorphism reduction exists (381 classes for 381 rows), and the two-sided
perfect-balance encoding left them UNKNOWN. `16,14,14,13` is the same shape with 88 rows and
w = 16, so it is the cheaper of the two but still one-critical.

## What would overturn this

A calibration run: 3 rows per profile at a fixed large budget (say 600 s / 15M conflicts),
recording conflicts reached and whether any row closes. If, say, `16,15,14,12` closes rows
at a rate the `16,16,*` pair does not, the ranking is wrong and cheap. That is 21 runs,
about 40 minutes on four cores, and it is the next thing I would do.

## The caveat that dominates all of it

Every profile here has one or two critical colours, so a single structural statement kills
all 11,585 at once: *no triangle-free 4-colouring of K_58 has a vertex with two
colour-degrees <= 14* (equivalently, every vertex has at least three critical colour-degrees
- "lemma L"). The ranking above is the order to try if that lemma is out of reach; it is
not an argument that any of these profiles must be attacked one row at a time.
