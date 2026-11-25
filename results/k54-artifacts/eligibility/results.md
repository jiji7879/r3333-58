# m3 — verified finite inputs of the k54cut handoff

Two directions, both finished: **d5** (the ledger of the 40.8 % case reduction)
and **d8** (the finite claims behind the eight-seed restriction).  Every number
below was recomputed from the archive's raw data by my own code; no module of
`k54cut/src` is imported anywhere.  All comparisons are exact; every script
exits 0 only if its check passes.

Archive: `/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut`
(read only).  `sha256sum -c SHA256SUMS` passes there.  Inputs used, with the
handoff's own hashes: `data/h42.json` eb9c7864…5136, `data/placements.json`
0499e473…9f4c, `data/rect_reps.json.gz` 0302e971…e3f6, `results/cover.json`
32e95d8a…1cf5, `results/omitted_orbit_ids.json.gz` 3cad454d…f672,
`data/r333_14.mc`, `data/r333_15.mc`, `data/core-cover.json`,
`results/global.json`.

---

## Part I (d5) — the case-reduction ledger

Claim audited: seed 12's dispatch falls from 59 925 marked rectangles to 35 031
and from 2 809 638 coloured cases to 1 662 749, "drop an orbit only when every
image misses the cut", over the 24 rooted H42 placements.

`audit_lib.py` re-derives the primitives: a placement is a pole and a palette
per template; its symmetry group is the set of 31-point permutations (image of
each template, image of the palette) preserving both colour twists, possibly
exchanging the templates; a marked rectangle is a pair of non-pole pairs, one on
each template; its weight is the number of inequivalent colourings of the four
crossing edges with the three ordinary colours, subject to the four template
triangles.

`audit_ledger.py` (8.5 s, `ledger_audit.json`) — **0 failures**:

* orbits: the stored representatives' orbits are pairwise disjoint and cover all
  78·78 = 6084 raw rectangles of each placement, and each stored orbit size
  equals the computed one (group orders, placements 1…24: 8,8,8,4,8,4,4,4,2,2,
  2,2,2,2,16,8,2,2,2,2,2,2,1,2);
* weights: every stored weight equals my recomputation (all 59 925 orbits);
* cuts: `omitted_orbit_ids.json.gz` is exactly the set of orbits some image of
  which crosses the stored partition (`cut_side`, `first_part`); the stored cut
  also removes at least as many coloured cases as *every* stored partition of
  either side, and `raw_permitted = 78·|cross|`;
* per-placement table and totals: 59 925 / 35 031 / 2 809 638 / 1 662 749, all
  equal to `results/cover.json`.

`audit_placements.py` (0.1 s, `placement_classes.json`): H42 has three vertex
classes under its eight colour-permuting automorphisms, {0,1,12,13}, {2,3} and
{4…11}, so {0,2,4} is a complete pole set; the 24 stored placements are exactly
the 24 equivalence classes of rooted placements (324 raw pole/palette states
modulo relabelling, global colour permutation and side exchange), each occurring
once, none missing.  So 59 925 is a complete mark count *given* the 104-row
catalogue assertion.

**Scoping (finding f1)**: the ledger consumes only **6 of the 161** stored
eligible partitions — mask 1776 (pole 0, parts 6|7, placements 1–8), 2032 and
5521 (pole 2, 7|6 and 6|7, placements 15 and 16), 3813, 5761, 6158 (pole 4,
8|5, the other 16 entries).  Their eligibility needs 36 + 72 + 3·94 = **390**
tightness tests for subsets of size ≥ 5, of which 3 are whole 8-parts (bound
against 9 outsiders) that the brief's "sizes 5, 6, 7" does not mention.  If an
*unused* stored partition failed eligibility the reduction would be unaffected.

---

## Part II (d8) — the eight-seed restriction's finite claims

Claim audited (README, "A restriction across eight full seed families"): the
restriction applies to 1 881 012 rooted pairs and rests on four finite
computations.  All four reproduce `results/global.json` exactly.

1. **K15 completeness** — `audit_k15.py` (11 s, `k15_extensions.json`).  Every
   ordinary one-vertex extension of every one of the 115 K14 catalogue rows is
   isomorphic, up to a permutation of the three colours, to one of the two K15
   catalogue rows.  There are exactly **6** extensions in all, from rows 23, 24
   and 40 (two each), splitting 2 / 4 between the two K15 classes = the stored
   `k15_extensions`.  Both catalogues are complete, triangle-free and pairwise
   non-isomorphic, and all **30** vertex deletions of the two K15 rows are
   catalogue rows (class 0 → row 24; class 1 → rows 40 and 23).
2. **Admissible deletions** — `audit_deletions.py` (11 s, `deletions.json`).
   For every row, the four-sets whose complementary K10 is isomorphic, up to a
   colour permutation, to a K10 inside one of the two K15 rows.  Per-row counts
   and union sizes match `global.json` with **0 mismatches**.  Only 16 rows have
   any admissible deletion: rows 17, 19, 20, 22, 23, 24, 25, 40, 69, 70, 77 with
   union 14 (= all vertices), and rows 1 (1 deletion, union 4), 4 (3, 6),
   26 (2, 5), 41 (7, 8), 114 (4, 8).  So the maximum union over the 104
   admissible rows is **8**, attained by rows 41 and 114, and row 42 (H42) has
   **none**.  The 11 rows the handoff excludes are exactly the rows whose
   deletion union is the whole vertex set.
3. **48 880 three-point bounds** — `audit_cap.py` (181 s, `cap_bounds.json`).
   For all 104 admissible rows and all 470 subsets P with |P| ≤ 3, no family of
   |P|+1 outsiders can have its c-support inside P (exact search: spoke words
   with the crossing colour allowed only on P, ordinary classes independent, a
   clause per monochromatic triangle, mutual edges coloured consistently).
   **0 violations, 0 undecided**, worst instance 6 763 search nodes.
   `crosscheck.py` (33 s, `crosscheck.json`) guards the search: the
   clique pre-filter against brute force on 300 random compatibility graphs
   (0 disagreements), four sharp unit tests of the mono-triangle logic, the
   unfiltered search on a seeded random sample of 1 500 of the 48 880 instances
   (0 violations, so the filter masks nothing), and `canon` against 150 random
   relabellings.  An earlier version of my pre-filter required *all four*
   colours to be unshared for a compatible pair instead of *some* colour; the
   unit tests caught it, it is fixed, and the full run above uses the corrected,
   sound condition.
4. **Rooted-pair tally** — `audit_scope.py` (0.3 s, `scope.json`).  With types =
   classes of (row, pole, palette) under colour-twisted automorphisms (4 749
   types over the 104 rows; automorphism orders 1:24, 2:45, 4:33, 8:1, 28:1) and
   Burnside over the six global colour permutations on unordered pairs, charged
   to the smaller seed, the per-seed counts are 278 654, 0, 52 188, 0, 736 362,
   440 328, 140 230, 13 198, 19 068, 200 844, 116, 24 for seeds 1…12 — identical
   to `global.json`, total **1 881 012**.  Seeds 2 and 4 give 0, matching the
   README's "all pairs assigned to seeds 5 through 12 and some of seeds 1 and 3".
   The seed-12 count, 24, equals the number of rooted H42 placements computed
   independently in Part I.

---

## What this does and does not establish

* The ledger arithmetic of the 40.8 % reduction is correct, and the reduction
  depends on exactly six of the stored partitions (f1).
* The four finite inputs of the eight-seed restriction are correct as stated.
* **Not** verified here: tightness of the six load-bearing partitions for
  subsets of size ≥ 5 (the crossing-cut theorem's one unverified input; d1 and
  m2 hold related directions, and after f1 the 390 tests above are all that is
  needed); the exhaustiveness of the 115-row K14 catalogue, which is an input
  assertion from an earlier handoff (I verified only that the two K15 rows'
  deletions live in it); the 4/4/3 four-point packing bounds (d7); and the hand
  counting argument of the restriction itself, whose finite inputs are what
  Part II checks.

## Replay

```sh
cd .ultramath/smwn8rsmo/m3
python3 audit_ledger.py        #  8.5 s, exit 0
python3 audit_placements.py    #  0.1 s, exit 0
python3 audit_k15.py           # 11   s, exit 0
python3 audit_deletions.py     # 11   s, exit 0
python3 audit_cap.py           #181   s, exit 0
python3 crosscheck.py          # 33   s, exit 0
python3 audit_scope.py         #  0.3 s, exit 0
```

Each script takes `--archive DIR` and writes its JSON verdict next to itself.
