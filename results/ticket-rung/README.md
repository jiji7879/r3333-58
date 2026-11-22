# m5 — the ticket layer at 42 slots: decoupled, censused, and climbed to k = 4

**Status: partial.** Three exact new structural results, three decided instances
(verified witnesses) and two DRAT-certified exclusions on the record's live rung
"pair level + the ten-disjoint-partners condition"; the rung itself (k = 10) is **not**
decided — k = 4 is decided SAT, k = 5 is UNKNOWN at 620 s with a warm start. No bound
moved, nothing here closes the branch.

Direction held: **d15** — the ticket layer at 42 slots, i.e. the record's own
"next rung worth trying" (`review/WALL_15141414_SWARM.md` §14: "in the uniform branch
`d_0(x) = m(x) + #(colour-0 neighbours of x in X)`, so every one of the 42 words needs
**at least ten partners whose 0-part is disjoint from its own** … Pair level plus that
condition is open at 100–590 s").

## 0. The object, and why it is sound

42 slots = the three arms `N_1(r), N_2(r), N_3(r)` of 14; each slot `x` carries a word
`w_x : A → {0,1,2,3}` on the 15 template points (`A` = the arm's internal 3-colouring,
`artifacts/k15_link_Tminus_m5.col`; the `U^-` template is a second case). Families
encoded (`ticketenc.py`, written from the definitions, not from any existing builder):

| family | clauses | why sound |
| --- | --- | --- |
| `cell1/cell2`, `row5` | 630 / 3 780 / 19 446 | one colour per cell; `m(x) = 5` |
| `partindep` | 4 410 | `w_x^{-1}(f)` independent in the template's colour-`f` graph (no mono triangle `x,a,b`) |
| `colcap` 4 ≤ c ≤ 5 per (arm, point) | 19 395 | mixture `|N_0(a) ∩ N_f(r)| ≤ 5` plus `Σ_f = d_0(a) − 1 = 14` |
| `pair1`, `pairdisj` | 52 773 | one colour per pair; `q(x,y)=f ⇒ M_f(x) ∩ M_f(y) = ∅`; root colour banned inside an arm |
| `colsum` (optional) | 53 520 | every arm point has exactly 14 colour-0 partners in `X` |
| `ticketmin` ≥ k | ~107 000 | the ten-disjoint-partners condition, relaxed to `k` |

The last family is sound by two kernel-checked lemmas in
`.ultramath/smwr8io45/m1/lean/Ticket.lean`: `uniform_branch_zero_critical` (under
reciprocity `(R)` and the uniform-branch hypotheses, colour 0 is critical at *every*
vertex) and `ten_outside` (`d_0(x) ≥ 15` and `|N_0(x) ∩ A| ≤ 5` ⇒ at least 10 colour-0
neighbours outside `A`). So the rung at `k = 10` is exactly the branch, **conditional on
`(R)`** — as the record itself says. `k < 10` is a relaxation.

## 1. Exact census of words (new, exact)

`wordcount.c` enumerates the words directly. Per template:
* `T^-` (`k15_link_Tminus_m5.col`): **254 628** words; `U^-`: **254 088**.
  The record's "about 254 610" figure is confirmed.
* Part-size multisets (T^-): `(4,3,3)` 162 306, `(4,4,2)` 63 504, `(5,3,2)` 25 020,
  `(5,4,1)` 3 780, `(5,5)` **18**. So only **18 words in the whole census miss an
  ordinary colour** — the record's "at most 16 of the 42 have a missing ordinary colour"
  is nearly vacuous (there are only 18 such words to go round).
* Each colour class of the template has independence number exactly 5, and there are
  exactly 33 five-sets independent in some colour class (11 per colour, each independent
  in exactly one) — this is what caps the part sizes.

Cube-tree sizing for the `(14,12)+XT` route (the record asked for it): a slot has
254 628 words, the pair stage is sub-second only with *all* words fixed, so a leaf is a
multiset of 12 words out of 254 628: `C(W+11,12) = 1.55e56`; depth 1 is already 254 628
nodes. **Cube-and-conquer over words is dead by ~52 orders of magnitude** — not
"millions", and not worth running.

## 2. The compatibility cap (new, exact)

Two slots with the *same* zero-part `Z` can never take colour 0 (their 0-parts coincide
and are non-empty), so they need a colour `f ∈ {1,2,3}` with disjoint `f`-parts: the
slots sharing `Z` form a clique in the compatibility graph of the words of `Z`.
`designlayer.py` computes that clique number exactly (Bron–Kerbosch with pivoting) for
all 3 003 zero-parts:

* all three colours available: **6** for 2 985 zero-parts, **11** for the other 18
  (the 18 are exactly the zero-parts of the 18 `(5,5)` words);
* two colours available (`{1,2,3} \ {r}`, an arm with root colour `r`): 3 (822), 4 (1 446),
  5 (660), 6 (63), 11 (12) — data in `runs/caps.json`.

**Consequence (corollary of the census, quotable): at most 6 of the 42 slots can share a
zero-part** (at most 11 for the 18 exceptional parts). This bounds the twin structure of
the word system at 42 slots, complementary to the record's word-level copy bound.

## 3. The pair layer decouples (new, proved)

My instance carries **no triangle family** (that is the three-arm object, a different
instance). In that case the pair colours are *per-pair independent*: the only clauses
touching `q(x,y)` are "one colour per pair" and the disjointness clauses for the chosen
colour; nothing couples two different pairs. Hence:

> **Theorem.** A word assignment `W` extends to a full model of the 42-slot ticket
> instance iff (i) every (arm, point) column is 4 or 5 and every point is covered 14
> times, and (ii) every pair of slots whose zero-parts intersect is *compatible*: some
> `f ∈ {1,2,3}` (with `f ≠` the arm root inside an arm) has disjoint `f`-parts.
> In that extension the colour-0 degree of slot `x` may be any value between 0 and its
> number of disjoint partners (colour 0 is only ever *forbidden* by intersection), and
> conversely a slot with `j` disjoint partners can never exceed colour-0 degree `j`.

So the rung at `k` is **equivalent to**: *a column-profile-satisfying word assignment with
minimum disjoint-partner count ≥ k in which all intersecting pairs are compatible*. This
is why CDCL is slow on the rung — it searches 861 pair colours that are logically
determined, and it explains why the models it finds are *not* spread (see §5).

## 4. Every known pair-level witness dies at the design layer (new, certified)

`witcheck.py` + `wordlayer.py` decode every witness in the tree. Of the 12 that carry a
complete pair colouring (all 861 pairs), the **maximum** colour-0 degree of a slot is 0–5
and the **maximum** disjoint-partner count is 0–9:

```
pair58_Tminus.wit 4/9   L_58.wit 4/9   p58.wit 4/7   p58_cc.wit 4/8
plain.solver.wit 4/8    wit_ac01.wit 4/9   wit_ac0102.wit 5/8
t3.wit 5/7   wit_f3.wit 5/7   base58_witness.wit 0/8
wit_big.wit 3/8   pair58_Tminus_recoloured.wit 2/8
```
(the pair `colour-0 max / disjoint-partner max`). Since the rung needs **every** slot at
≥ 10 disjoint partners, **no known pair-level witness is even a candidate**: the exclusion
is by the design layer alone, with no word analysis. The record's "pair-level solutions have
minimum one" is sharpened: their *maximum* is 5.

## 5. Decided instances (verified witnesses)

`ticketenc.py --verify` is an independent checker (it re-derives every family from the
decoded model and knows nothing of the solver). All three models below verify
"MODEL OK: 42 slots, every family holds":

| instance | result | wall | model (sha256 prefix) |
| --- | --- | --- | --- |
| pair level + profile, k = 3 | **SAT** | 53 s (Kissat 4.0.4) | `runs/k3.out` `134daddc3e19a600` |
| + coverage 14, k = 3 | **SAT** | 360 s | `runs/k3_colsum.out` `43265856896401c7` |
| + coverage 14, k = 4 | **SAT** | 260 s, *warm start* | `runs/k4_model.txt` `e08bc96ccb092ec5` |

So the frontier moves from "minimum one" (the record) to **k = 4 decided SAT**. The
warm-started run is a real 2–3× gain: the same k = 4 instance is UNKNOWN at 600 s cold,
and the ladder is set up so that the decision variables precede all ticket auxiliaries, so
the k-model supplies phases for the (k+1)-instance directly (`warmstart.py`).

Not decided (reported as a wall, not as evidence): k = 5 UNKNOWN at 620 s warm-started
(6 M conflict budget); k = 3 with coverage 14 *and* the ordinary degree caps
`p_f + n_f + [f = root] ≤ 16` UNKNOWN at 300 s (495 k clauses).

## 5b. Two certified exclusions: a spread design admits no word assignment

The word layer of a *fixed* design is a finite CSP, and it can be decided with a proof.
`fixdesign2.py` regenerates the pair-level CNF with the zero-parts fixed by unit clauses
(a **restriction** of the ticket instance, so an UNSAT here is a statement about that
design only — never about the rung). Both designs below are UNSAT, Kissat 4.0.4, and the
proof replays against the regenerated CNF:

| design | instance | proof | replay |
| --- | --- | --- | --- |
| `runs/design_armed.json` (min disjoint degree **10**, ten 5s / five 4s per arm) | `cnf/grp_noticket.cnf` (24 591 v, 101 064 c, sha256 `9d39de8033bb30f6`) | `runs/grp_noticket.drat` | `s VERIFIED` |
| `runs/design_group_best.json` (min disjoint degree **9**, three arms that are partitions of A, `(5,5,4)` multiplicities) | `cnf/grp9_noticket.cnf` (sha256 `94a047aebdee265e`) | `runs/grp9.drat` (sha256 `5cf168e7f06c2c94`) | `s VERIFIED` (1 413-clause core) |

So "spread design + compatible words" is not automatic at either 9 or 10, and the two
certificates are the smallest decided facts this direction produced. `pairfilter.py`
shows the failure is not local: in the group design **0 of 563** intersecting zero-part
pairs is locally impossible (every pair at overlap 1–4 admits a compatible word pair,
checked exhaustively over the two word lists).

## 6. What the rung is really up against (measured)

The rung is a tension between two layers, both of which are individually satisfiable:

* **Design layer.** A 42-block design with per-arm column profile, coverage 14, every
  point in 14 blocks and min disjoint degree 10 **exists** — two explicit ones here:
  `runs/design_armed.json` (from `designsearch4.py`: translates of three base 5-sets,
  ten 5s / five 4s per arm, within-arm repair; min disjoint degree 10) and
  `runs/design_group_best.json` (`groupdesign.py`: three arms that are partitions of A
  into three 5-sets with multiplicities `(5,5,4)`; min disjoint degree 9, profile and
  per-arm caps satisfied, coverage 13–15). A design with multiplicities `(6,4,4)` is
  **impossible**: the per-arm column cap 5 forbids a multiplicity-6 group.
* **Word layer.** Fixing the design, the word problem is a binary CSP over 42 slots; on
  the two spread designs above it is **UNSAT** (Kissat, 1–2 s, e.g. `cnf/grp9_noticket.cnf`),
  yet no intersecting pair in the group design is locally impossible
  (`pairfilter.py`: 563 intersecting pairs, **0 dead** — every pair of zero-parts at
  overlap 1–4 admits a compatible word pair, checked exhaustively). So the obstruction on
  a spread design is *global*, not local; that is the precise sense in which the rung is
  hard. CDCL's own models duck it: the k = 4 model has min disjoint degree 4, which is
  exactly why k = 5 does not come easily.

## 7. Correction to my own board finding

My finding `f2` claimed the full-arm column profile is not hereditary. **That is wrong**,
and `f7` on the board carries the correction: for a *full* arm `B` the three arm counts
sum to `d_0(a) − 1 = 14` with each ≤ 5, so `col_B(a) ∈ {4,5}` and `Σ_a col_B(a) = 70`
forces ten 5s and five 4s — a conclusion about arm-`B` columns only, hence hereditary even
when the other arms are truncated. Only a *truncated* arm keeps nothing but the cap.

## 8. Exact rerun commands

```bash
R=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo
D=$R/.ultramath/smwrmwgf7/m5; K=$R/.scratch/satcheck/bin/kissat
PY=$R/.scratch/k58/.venv/bin/python          # python-sat 1.9.dev22 (cadical153)
cd $D
gcc -O2 -o wordcount wordcount.c && ./wordcount $R/artifacts/k15_link_Tminus_m5.col   # 254628
python3 designlayer.py caps                     # runs/caps.json  (~64 s)
python3 ticketenc.py --out cnf/t42_k3.cnf --degmin 3
python3 ticketenc.py --out cnf/k4_colsum.cnf  --degmin 4 --colsum
$K -q cnf/t42_k3.cnf > runs/k3.out; python3 ticketenc.py --verify cnf/t42_k3.cnf runs/k3.out --degmin 3
$PY warmstart.py cnf/k4_colsum.cnf runs/k3_colsum.out 3000000 cadical153   # 260 s
python3 ticketenc.py --verify cnf/k4_colsum.cnf runs/k4_model.txt --degmin 4 --colsum
python3 designsearch4.py 10 12                  # spread arm-balanced design
python3 groupdesign.py 3 10; python3 pairfilter.py runs/design_group_best.json
python3 witcheck.py $R/.ultramath/*/m*/**/*.wit  # witness survey
# the two certified exclusions (proof logging + replay)
python3 fixdesign2.py runs/design_armed.json cnf/grp_noticket.cnf
$K -q cnf/grp_noticket.cnf runs/grp_noticket.drat
$R/.scratch/satcheck/bin/drat-trim cnf/grp_noticket.cnf runs/grp_noticket.drat     # s VERIFIED
python3 fixdesign2.py runs/design_group_best.json cnf/grp9_noticket.cnf
$K -q cnf/grp9_noticket.cnf runs/grp9.drat
$R/.scratch/satcheck/bin/drat-trim cnf/grp9_noticket.cnf runs/grp9.drat           # s VERIFIED
```

## 9. What I did not verify

* The rung at k = 10 is **not** decided: k = 5 and beyond are UNKNOWN, and I have no
  argument either way.
* Soundness of the ticket family is **conditional on `(R)`** (all tickets returned).
  I cite `uniform_branch_zero_critical` and `ten_outside` from
  `.ultramath/smwr8io45/m1/lean/Ticket.lean` after reading their statements; I did not
  rebuild that file.
* Only the `T^-` template is instantiated. `U^-` (254 088 words) would need its own run
  for a closure of the 73 `U---` cases.
* The designs in `runs/design_armed.json` / `runs/design_group_best.json` are *words-free*
  objects; the report never claims they extend to models (they do not).
* `runs/caps.json` uses my Bron–Kerbosch implementation; it is exact but it is my code.
* The record's arithmetic (`d_0(a) = 15`, coverage 14, `|X| = 42`, `Σ m_x = 210`) is used
  as given; auditing it against the Lean tree is member m2's direction (d6), not mine.

## 10. Files (all under `.ultramath/smwrmwgf7/m5/`)

```
ticketenc.py      my encoder + independent verifier for the 42-slot ticket instance
wordcount.c       exact word census (254 628 / 254 088)
designlayer.py    per-zero-part compatibility cap (runs/caps.json)
designsearch.py   word-free design search, no arms
designsearch4.py  arm-balanced spread designs (runs/design_armed.json)
groupdesign.py    group-structured designs (runs/design_group_best.json)
design644.py build644.py   the (6,4,4) attempt, and why the per-arm cap kills it
armassign.py      exact SAT arm assignment for a design
fixdesign2.py     fix a design and emit the CNF (the restriction used for §5b)
pairfilter.py     local pair filter for a design (0 dead on the group design)
wordsearch.py     min-conflicts word search with the design fixed
overlapcompat.py  overlap t = 1..4 always admits a compatible word pair
warmstart.py      phase warm start (cadical153) — the k-ladder's engine
witcheck.py       witness survey (colour-0 and disjoint degrees)
wordlayer.py      word-layer / profile / coverage audit of a 42-word file
flipcheck.py      disjoint degrees of a model's design
REPORT.md         this file
cnf/, runs/       CNFs, models, DRATs, drat-trim logs, caps.json
```

Board findings under this direction: `f1` (cube tree dead), `f2`+`f7` (heredity, with
`f7` correcting `f2`).


## Coordinator's verification (2026-11-22)

* The decoupling checked by hand, not by claim: with no triangle family the pair
  colours are independent, so a word assignment extends iff every intersecting pair
  of zero-parts is compatible; each slot's 0-degree can then be raised to its
  disjoint-partner count, which makes "min disjoint degree >= 10" both necessary
  and sufficient for the rung.
* The exclusion of the existing witnesses verified independently on eleven of the
  twelve, in a stronger form than reported: the **minimum** disjoint-0-partner
  count is 0-2 and the maximum 7-9, so every pair-level witness in the tree misses
  the rung by a wide margin.
* The soundness chain is now in the kernel: `K58.uniform_branch_zero_critical` and
  `K58.ten_outside` were only in `.ultramath/smwr8io45/m1/lean/Ticket.lean`; they
  are now `lean/K58/Ticket.lean`, built by `build.sh`, axiom-clean.
* Not verified: the compatibility cap (<= 6 slots per zero-part, 11 for the 18
  exceptional), the two DRAT exclusions, and the k=3/k=4 witnesses. The U^- case is
  not instantiated.

**The gap, plainly.** k=4 is SAT, k=5 is UNKNOWN at 620 s with a warm start, and
the rung needs k=10. The relaxation at half strength already defeats CDCL, so the
ticket layer is not a route that is nearly there — the reduction is worth keeping,
the ladder as a route is not.
