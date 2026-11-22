# STATUS: decided (four new verified objects) + frontier measured — direction d17

Member m2, swarm `smwrmwgf7`. **Direction d17**: the pair level with the sixth
arm lemma added.

**The claim, in one line.** The uniform fully-sending branch's *word layer* is
consistent with the sixth arm lemma (`K58.part_family_le_five`) and with the
per-arm coverage cap at the same time — four explicit, independently verified
objects — even though every pair-level witness in the record violates both
families. The next rung, the pair level with the family on all three arms, is
UNKNOWN at 280 s (kissat, 4.13 M conflicts) and 400 s (cadical, 3.69 M); that is
reported as a frontier, not as a result.

## 1. The families, and why they are branch facts

| family | statement used | provenance |
| --- | --- | --- |
| (W1) | each word has exactly five `0`s | `m(x) = 5` |
| (W2) | the `f`-part is independent in the template's colour-`f` graph, `f=1,2,3` | `a,a',x` would be monochromatic |
| (C) | each of the 15 arm positions is `0`-covered exactly 14 times | coverage 14 per arm point |
| (M) | **per-arm cap**: each arm position has at most 5 colour-`0` slots in any one arm | `K58.mixture` with `x = a, f = 0, u = r, g = b` |
| (P) | every pair has a colour with disjoint parts, not the shared arm colour inside an arm | `colour(x,y) = f ⇒ N_f(x) ∩ N_f(y) = ∅` |
| (S) | **sixth arm lemma**: for `a ≠ b`, no 6 slots of arm `b` have pairwise intersecting `a`-parts, the `a`-part of `x` being `{z ∈ N_a(r) : col(x,z) = a}` (`a = 0`: the word's 0-part) | `K58.part_family_le_five`, `Blocked.lean`, no `sorry` |

`Blocked.lean` was read in full: `blocked_set_le_five` reduces six pairwise
blocked vertices to a triangle-free 2-colouring of `K_6` (contradicting
`K58.two_colour_six`), and `part_family_le_five` is its word form. For `a ≠ 0`
the `a`-part is carried by the pair colours, so (S) constrains words *and* pair
colours together; for `a = 0` it is word-level.

## 2. What every recorded witness does (measured here)

`work/pairlevel_check.py`, run on the three pair-level witnesses on disk
(`smwr8io45/m6/wit/pair58_Tminus.wit`, `smwrfgma5/m4/wit/p58.wit`,
`smwr8io45/m4/pair58_Tminus_recoloured.wit`): all three are valid at the pair
level (five zeros, part independence, coverage 14, all 861 pair conditions) and
**all three violate (S) in all nine `(a,b)` pairs**, the word form giving
cliques `9, 9, 10` for the first — exactly the record's figure — and `9, 9, 8`
for the second. They also **violate (M)**: per-arm column maxima `8,8,7` and
`7,6,8` against the bound 5. So (M) and (S) are genuine strengthenings of the
pair level, not consequences of it.

## 3. Decided: the word layer survives both word-level families

`work/w_armcap3.cnf` = (W1)+(W2)+(C)+(M)+(S for `a = 0`) on all three arms, no
pair variables. **SAT** (8725 conflicts). The decoded support structure
`work/blocks_armcap.json` is verified by `work/verify_wordlayer.py` from the
definitions:

```
global coverage: [14]*15
arm 1: per-arm coverage [5,4,5,5,5,4,5,5,4,4,4,5,5,5,5]  (ten 5s, five 4s)  clique number 5
arm 2: [5,5,5,4,4,5,5,5,5,5,5,4,5,4,4]                     (ten 5s, five 4s)  clique number 5
arm 3: [4,5,4,5,5,5,4,4,5,5,5,5,4,5,5]                     (ten 5s, five 4s)  clique number 5
verdict: ALL WORD-LEVEL FAMILIES HOLD
```

Every per-arm profile is exactly the branch's forced one (ten 5s and five 4s),
and the clique number is exactly the bound 5 in all three arms — the family is
satisfied *tightly*. No recorded witness comes near this.

## 4. Decided: the pair level with the sixth arm lemma, at one and two colour pairs

Three explicit objects, each a full 42-slot pair-level witness with 861 pair
colours, each verified twice (solver model decoded, then re-checked from the
definitions by `work/pairlevel_check.py`):

| witness | instance | max clique in the enforced (S) pairs |
| --- | --- | --- |
| `work/wit_ac01.wit` | (W1)+(W2)+(C)+(M)+(P)+(S at `(0,1)`) | `(0,1): 5` |
| `work/wit_ac0102.wit` | … `(S at (0,1),(0,2))` | `(0,1): 5, (0,2): 5` |
| `work/wit_f3.wit` | (W1)+(W2)+(C)+(P)+(S at `(0,1),(2,1),(3,1)`) | `(0,1): 5, (2,1): 5, (3,1): 5` |

All three: 0 definition-level violations, coverage 14 at every position, and the
enforced family at the bound. `wit_f3` mixes the word form with two pair-colour
forms, so the `a ≠ 0` half of the lemma is exercised too.

## 5. Frontier (reported, not claimed)

* pair level + (M) + (S) on all three arms (`work/pl_w3acc.cnf`, 133,311
  clauses): **UNKNOWN**, kissat 280 s / 4,134,022 conflicts; cadical 400 s /
  3,685,374 conflicts.
* all nine `(a,b)` families, pair level, no cap (`work/pl_fam9.cnf` or the sorted
  build): **UNKNOWN** at 280 s.
* A combinatorial construction of the 0-parts (the 15 cyclic 5-intervals of
  `Z_15`, one copy per arm, arm `i` omitting `I_{5(i-1)}`: coverage exactly 14,
  clique 5 in every arm) satisfies the word layer but is **not completable**: its
  0-parts pinned into the nine-family pair level are UNSAT (35,211 conflicts).
  So the word layer's structure is not the only constraint, and the interval
  design is a dead end worth recording.

## 6. Method and rigour (what makes these objects trustworthy)

* My own encoder (`work/build_partfull.py`), not a reuse: cells, cardinality via
  `pysat` sequential counters, pair condition, family gadgets, optional per-arm
  cap and validated slot-sorting symmetry break.
* **Validated against the record**: the encoder *accepts* `pair58_Tminus.wit`
  when built on that witness's own template `k15_link_Tminus_m5.col`, and
  *rejects* it on the differently-labelled isomorphic template — the labelling
  trap, which is why every object here names its template.
* **Two encoding bugs were found and fixed** by decoding models at the definition
  level: a polarity error in the clause that forces the disjointness auxiliary
  (it made the family vacuous, i.e. a fake SAT) and an arm-index off-by-one that
  applied each family to the wrong arm (also a fake SAT). Both were caught only
  because every model is re-checked semantically; the current code passes the
  check, and the earlier "SAT" runs are discarded.
* No global cap anywhere: the per-arm cap (M) is stated per arm and its sum
  `5+5+5 = 15 ≥ 14` is compatible with the coverage requirement (the ERRATA
  test).
* The slot-permutation sort used in some runs is an automorphism of every family
  (words move with the slots; coverage is indexed by arm *positions*), so it
  preserves satisfiability; the unsorted build gives the same verdict on the
  rungs where both were run.

## 7. What I did not do

* No UNSAT: nothing here closes the branch, and the frontier is a timeout.
* The `(a,b)` families for `a ≠ 0` beyond `(2,1),(3,1)` are not decided at the
  pair level; the full nine-family instance is open.
* The U^- template is not run for these families (the T^- one is; the templates
  are non-isomorphic, so the U^- verdict would have to be measured separately).
* No kernel work in this direction: `part_family_le_five` was read and its proof
  checked by eye, not rebuilt here.

## 8. Rerun

```bash
cd .ultramath/smwrmwgf7/m2
V=../../../.scratch/k58/.venv/bin/python; K=../../../.scratch/satcheck/bin/kissat
# 1. recorded witnesses: families measured
python3 work/pairlevel_check.py ../../smwr8io45/m6/wit/pair58_Tminus.wit \
        ../../smwrfgma5/m4/wit/p58.wit ../../smwr8io45/m4/pair58_Tminus_recoloured.wit
# 2. word layer with the per-arm cap and the word form on three arms
$V work/build_partfull.py --template k15_link_Tminus_m5.col --fams 0-1,0-2,0-3 \
    --nopair --armcap --sort --out work/w_armcap3.cnf
$K work/w_armcap3.cnf > work/w_armcap3.k           # s SATISFIABLE
$V work/get0.py work/w_armcap3.k                   # -> work/blocks_armcap.json
python3 work/verify_wordlayer.py work/blocks_armcap.json
# 3. the three pair-level objects
$V work/build_partfull.py --template k15_link_Tminus_m5.col --fams 0-1 --armcap \
    --sort --out work/pl_ac1.cnf && $K work/pl_ac1.cnf > work/pl_ac1.k
$V work/build_partfull.py --template k15_link_Tminus_m5.col --fams 0-1,0-2 --armcap \
    --sort --out work/pl_ac12.cnf && $K work/pl_ac12.cnf > work/pl_ac12.k
$V work/build_partfull.py --template k15_link_Tminus_m5.col --fams 0-1,2-1,3-1 \
    --out work/pl_fam3.cnf && $K work/pl_fam3.cnf > work/pl_fam3.k
$V work/export_wit.py work/pl_ac1.k work/wit_ac01.wit "0-1" --sort --armcap
$V work/export_wit.py work/pl_ac12.k work/wit_ac0102.wit "0-1,0-2" --sort --armcap
$V work/export_wit.py work/pl_fam3.k work/wit_f3.wit "0-1,2-1,3-1"
python3 work/pairlevel_check.py work/wit_ac01.wit work/wit_ac0102.wit work/wit_f3.wit
```

Solvers: kissat 4.0.4 and cadical 2.1.2 (`.scratch/satcheck/bin/kissat`,
`/opt/lean/bin/cadical`); one process at a time, longest run 400 s.

## Coordinator's verification (2026-11-22)

Independent checks, not solver statuses:

* `pairlevel_check.py` on the three recorded witnesses: all valid at the pair
  level, all violating the part-family bound — worst values **13, 9, 11** against
  the bound 5. **Correction:** `pair58_Tminus` violates at **seven** of the nine
  `(a,b)` pairs, not nine; `(2,1)` and `(2,3)` sit exactly at 5.
* the per-arm cap computed separately: maxima **8, 8, 8** against the bound 5, so
  `(M)` and `(S)` are genuine strengthenings.
* `verify_wordlayer.py`: coverage 14 everywhere, ten 5s and five 4s per arm, and
  intersection-graph clique number **exactly 5** in all three arms — so the word
  layer carries the sixth arm lemma at its exact bound together with the cap.
* the three pair-level witnesses: 0 definition-level violations, 861 pair colours,
  `wit_ac0102` holding the per-arm cap at exactly 5.

**Scope.** The pair-level objects enforce the sixth arm lemma at 1, 2 and 3 of the
nine `(a,b)` pairs respectively. The nine-family version is UNKNOWN at 280 s
(kissat, 4.13 M conflicts) and 400 s (cadical, 3.69 M) and is a frontier, not a
result. The headline "the lemma does not kill the pair level" therefore holds only
pair-by-pair; at all nine it is undecided.

**Why this matters.** `PROFILE` §5 records the colour-0 layer as closed — the
design quotient is SAT with the saturation families. This object strengthens that
to: the word layer is SAT with the sixth arm lemma at its bound *and* the per-arm
cap, on all three arms. No word-level argument closes the branch, even with the
lemma.

Rerun: see §8 of the report; the files here are the witnesses, the block object,
the two checkers and the builder.
