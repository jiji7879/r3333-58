# Status: CERTIFIED (both targets closed; two record claims corrected)

Member m7, swarm `smwrmwgf7`, direction d2 (targets 5 and 4 of the round).
Everything below is mine and lives in this directory; the repo and other members'
directories were not modified and no solver process was shared with another member
(the heaviest run here is a 58-vertex maximum-independent-set computation, seconds).

**Target 5 — the Hall inequality: decided.** `|N_0(S) ∩ I| ≥ |S| − 1` for colour-0
independent `I` (`|I| = 15`) and `S ⊆ J \ I` is a theorem, and it is exactly
`α(G_0) ≤ 16`, the single-colour independence bound that follows from
`R(3,3,3) = 17`. Its exhaustive maximum over all `(I, S)` (with the cap `|S| ≤ 15`
that `|J| = 15` forces) has the closed form `min(α_0, 30) − 16`, and the value is
**14 for every one of the five order-58 pair-level witnesses** — all five violate
it. With `I = A` alone the exact maximum is **2**, so the wall §27 and the state
document §10 ("no violation occurs", "one witness survives it") are sampling
artefacts. Full statement and the sharpness calibration:
[out/HALL.md](out/HALL.md).

**Target 4 — the three-word gluing obstruction: certified.** The obstruction is
three words of one arm whose three admissible-colour sets `L(x,y)` are the same
singleton; then all three internal edges are forced to that colour and the arm
carries a monochromatic triangle. It is now a standalone certificate:
**661 mono-forced triples over the 15 arms of the five distinct order-58
pair-level witnesses, 0 dead pairs, 15 shipped certificates re-verified from the
witness files**, with the counts confirmed by an exact per-edge arm-module CSP and
shown not to over-fire (the two-arm witnesses' arms all pass). Full statement,
the certificate table, the minimal-size spectrum {3, 5, 6} and the non-completeness
counterexamples: [out/OBSTRUCTION.md](out/OBSTRUCTION.md).

## 1. Target 5, in detail

Statement tested, as the pentagon package states it (`.scratch/pent/README.md`):
`I` a colour-0 independent 15-set, `J` a colour-0 independent set, `S ⊆ J \ I`, then
`|N_0(S) ∩ I| ≥ |S| − 1`.

* **It is a theorem.** `(I \ N_0(S)) ∪ S` is colour-0 independent (no element of `S`
  is 0-adjacent to a survivor of `I`), and `α(G_0) ≤ 16` because a 17-set with no
  colour-0 edge would be a triangle-free 3-colouring of `K_17`. Hence
  `15 − |N_0(S) ∩ I| + |S| ≤ 16`.
* **Conversely** a colour-0 independent `W` with `|W| = α_0 ≥ 17` gives `I` = any 15
  of it and `S` = two more, with `N_0(S) ∩ I = ∅`: a violation. So the inequality is
  **equivalent** to `α(G_0) ≤ 16` and carries nothing beyond it.
* **Exhaustive maximum.** `margin = |S| − 1 − |N_0(S) ∩ I| = |exchange set| − 16`, and
  `|S| ≤ 15` always, so `margin ≤ min(α_0, 30) − 16`, attained. This is an exact
  answer over all `(I, S)`, not a sampled one.
* **The five witnesses.** `α(G_0) =` 34, 41, 36, 30, 30 for `pair58_Tminus`
  (= `L_58`, byte-identical), `pair58_Tminus_recoloured`, `wit_big`, `p58`,
  `p58_cc`. Margin 14 for all five.
* **Why the earlier test missed it.** With `I = A` fixed, every word has `|M_0| = 5`
  exactly, so `|S| ≤ 5` can never violate and a *random* 15-subset `J` covers nearly
  all of `A`. The violation needs a `J` whose 15 supports fit inside a 12-point
  `T ⊂ A`; the reduced exact test over all `T` (a 2^15 zeta transform, covering all
  2^42 subsets `S`) finds margin 2 for every witness.
* **The described-but-unstored witnesses** (WALL §13's five-line construction,
  WALL §16's extremal-word witness) are decidable on the `I = A` half from their
  words alone; both use the three supports `{0,1,4,12,14}`, `{3,7,8,9,10}`,
  `{2,5,6,11,13}` at 14 copies each and both fail with margin 8.
* **Calibration.** `α(G_c)` computed exactly on all fifteen `artifacts/*.col`:
  every genuine 4-colouring has `max_c α(G_c) = 16`, attained in every colour at
  `n = 49, 50, 51`; `n48_z4z4_f0` gives `(15,16,16,16)`, matching its
  `(15,11,11,10)` profile.

**Consequence for the campaign, stated plainly.** "Pair level + Hall" is strictly
stronger than the pair level (every witness violates it) but it is *not a new
rung*: it is implied by `R(3,3,3) = 17` plus `X`-internal triangle-freeness, which
the three-arm instance already contains. It cannot close anything the three-arm
instance does not.

## 2. Target 4, in detail

**Lemma.** Arm of root colour `k`, `L(x,y) = {f ≠ k : M_f(x) ∩ M_f(y) = ∅}`. If
`L(x,y) = L(x,z) = L(y,z) = {c}` on three words of one arm then every internal edge
of that triangle is forced to `c`, giving a monochromatic triangle: the arm is not
realisable, and the triple is inclusion-minimal. `k` is excluded because
`x, y ∈ N_k(r)`; `f` is excluded when the parts meet because `M_f(x) ∩ M_f(y) ∋ a`
puts `a` `f`-adjacent to both. Template-free.

* **Exhaustive.** All `C(14,3) = 364` triples of each of the 15 arms:
  661 mono-forced triples, **0 dead pairs**, per witness (arms 1/2/3)
  48/37/34, 56/47/57, 41/51/39, 44/60/45, 37/35/30. So every order-58 pair-level
  witness fails at least one arm module, proved by three words.
* **Certificates.** `out/three_word_certificates.json`, 15 entries;
  `scripts/verify_obstruction.py` re-derives each from the `.wit` file and shares no
  code with the search. All verify.
* **Exact cross-check.** `scripts/arm_sat.py` decides the arm module (variables per
  pair and colour, one colour per pair from `L`, one clause per triple and colour).
  It returns minimal infeasible sub-arm = 3 with the same counts for all 15 arms.
  `scripts/arm_validate.py` validates it in the dangerous direction: the 11 arms
  whose own pair colours are already legal all return SAT, 0 mismatches.
* **Does not over-fire.** The 10 arms of the five two-arm witnesses have 0 triples
  and the CSP is SAT, so `14+14` SAT (round five) is untouched.
* **Is not complete.** The ten `smwr8io45/m4/design_*.wit` arms 1 are infeasible
  with **no** infeasible subset of size ≤ 5 (`design_1` arm 1: minimum size 6, exactly
  14 such 6-sets), and `L_50` arm 3 has minimum size 5. So the spectrum of minimal
  local obstructions in the objects on disk is {3, 5, 6}; size 3 is the smallest that
  occurs, not the only one.
* **Robustness.** Banning colour 0 inside arms as well only increases every count
  (42–69 triples per arm, plus 0–4 dead pairs).

**What it settles.** The wall's §15/§29 question "which constraints kill the
extension — a column sum, a cross-arm pair condition, or a blocked set?" answers:
none of the three. The counting layer is SAT with the pins (round-five `m7`), the
pair level is SAT with the pins (`abs2_nomod.cnf`), and the failure is the second
arm's own list-colouring, with a three-word witness.

## 3. Referee check on the record's word-level numbers (independent recomputation)

`scripts/word_counts.py` recomputes the admissible-word census from the template
files alone (five 0s per word, each ordinary part independent in its template
colour, brute force over all `C(15,5)·3^10` assignments):

| template | `α` per colour / number of maximum independent 5-sets | admissible words | extremal words |
| --- | --- | ---: | ---: |
| `k15_link_Tminus_m5.col` | 5 / 11 | 254,628 | 18 |
| `k15_template_Tminus_aut2_m4.col` | 5 / 11 | 254,628 | 18 |
| `k15_link_Uminus_m5.col` | 5 / 11 | 254,088 | 18 |
| `k15_template_Uminus_aut10_m4.col` | 5 / 11 | 254,088 | 18 |

So WALL §24's "`alpha = 5` with exactly eleven maximum independent 5-sets ... only
**18** extremal words" and the state document's 254,628 / 254,088 both hold, in both
templates. New: the `U^-` template has the same profile (11 maximum independent
sets, 18 extremal words), so §24's "every 14-slot arm needs generic words" applies
to `U^-` unchanged.

## 4. Corrections to the record (for the coordinator)

1. **`PROFILE_15141414_STATE.md` §10, "One witness survives it"** — wrong. All five
   witnesses violate the Hall inequality; see §1.
2. **`WALL_15141414_SWARM.md` §27, "no violation occurs"** — true only for the
   sampled family (random `J`, `|S| ≤ 4`). The `I = A` case violates with margin 2.
3. **"Five pair-level witnesses"** — there are five *distinct* ones, but they sit in
   six files: `smwr8io45/m6/wit/L_58.wit` is byte-identical to
   `pair58_Tminus.wit` (md5 `de70189fdb0d16285467ea29fda76d15`). The one the
   record never lists by path is `smwr8io45/m4/wit_big.wit`
   (42 words, 861 pairs, coverage 14 — a full pair-level witness).
4. **No new rung from Hall** (§1, last paragraph), so the "pair level + Hall" hope
   is not a way past the three-arm instance.

## 5. Exact rerun commands

From the repo root, `bash .ultramath/smwrmwgf7/m7/rerun.sh` runs everything below
and prints every number quoted in this report. Individually, from this directory:

```sh
P=../../../.scratch/k58/.venv/bin/python      # python-sat 1.9.dev22, for the SAT checks

python3 scripts/mis.py --selftest             # MIS vs brute force, 400 random graphs
python3 scripts/alpha_col.py                  # alpha(G_c) on all 15 artefacts -> max 16
python3 scripts/hall_alpha.py                 # alpha(G_0) of the 5 witnesses
$P scripts/crosscheck_mis.py                  # every alpha re-decided by SAT at a and a+1
python3 scripts/hall_IA.py                    # the I = A reduction (2^15 zeta transform)
python3 scripts/hall_exact.py                 # exact max margin, min(alpha,30)-16
python3 scripts/hall_ship.py                  # -> out/hall_certificates.json
python3 scripts/verify_hall.py                # standalone re-check, exits 0
python3 scripts/hall_hand_witnesses.py        # WALL §13 and §16 constructions
python3 scripts/hall_all.py                   # Hall verdict for every witness on disk

python3 scripts/obstruction.py                # -> out/three_word_certificates.json
python3 scripts/verify_obstruction.py         # standalone re-check, exits 0
$P scripts/arm_sat.py                         # exact arm-module CSP, minimal sizes
$P scripts/arm_validate.py                    # CSP vs the witnesses' own colourings

# the word census of §3 (slow: ~600 s per template, not in rerun.sh)
python3 scripts/word_counts.py "k15_link_Tminus_m5.col"        # 254628 words, 18 extremal
python3 scripts/word_counts.py "k15_link_Uminus_m5.col"        # 254088 words, 18 extremal
```

Two long ones (not in `rerun.sh`): the `design_*` minimum-size search, reproduced by
the inline snippet recorded in `out/OBSTRUCTION.md`, and `scripts/obstruction_scan.py`
(every `.wit` on disk, ~1 min).

## 6. What I did not verify

* **No UNSAT claim is made anywhere**, so no DRAT is owed and none is offered. The
  SAT calls in `crosscheck_mis.py` and `arm_sat.py` are only used to certify
  numbers I also compute by a second, non-SAT route.
* **`α ≤ 16` is used as a known fact** (`R(3,3,3) = 17`), not formalised here. It is
  the campaign's own base fact (`d_c(v) ≤ 16`), and I checked it computationally on
  every colouring artefact.
* **The Hall inequality holds at every order** (with `α(G_0) ≤ min(n−1, 16)`) but it
  only bites when there are enough outside vertices to build a 17-set. The two-arm
  and one-arm models pass it with `α(G_0) = 15`, i.e. with slack, so their passing is
  not a discriminator and I draw no conclusion from it.
* **The three-word certificates are certificates about the five witnesses**, not a
  theorem that every pair-level model contains such a triple. I did **not** prove
  that the arm module is infeasible at the pair level in general, and the
  `design_*` arms show the three-word test alone would not prove it.
* **The witnesses are used as given.** I re-checked the structural conditions I need
  (word length 15, five 0s, 861 pair colours, `M_f` disjointness on the chosen pair
  colour, colour-0 coverage 14 per arm point) but did not re-verify each witness's
  provenance from its solver log.
* **`L(x,y)` is a necessary condition only.** It is exactly the set of colours a
  genuine colouring could use on that edge; I do not claim the arm module has no
  other constraints.
