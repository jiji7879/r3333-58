# Status: DECIDED at the in-arm and pair level for BOTH templates; the full XT object is UNKNOWN (measured, with the exact counting boundary)

The judge's brief for this direction: build the `U^-` template's version of the
26-vertex object, which nobody had built, with the per-arm profile *recomputed*
rather than assumed. That is done, and the object is decided at the two levels
that are decidable here; the third (cross-arm triangle-freeness) is measured and
localised. **Headline: cross-arm triangle-freeness is the *whole* difficulty** —
the same object is SAT in 0.5 s without any triangle constraint, SAT for `T^-` in
140 s and for `U^-` in 342 s with in-arm triangle-freeness, and still UNKNOWN
after 200 s when *only* the cross-arm triangles are imposed.

## 1. The object, and the per-arm profile recomputed

26 vertices `X = B ⊔ C`, `|B| = 14` (root colour 1), `|C| = 12` (root colour 2),
`A` = 15 template positions.

* **W** every `x` carries a word `w_x : A → {0,1,2,3}` with `|M_0(x)| = 5` and
  `M_f(x)` `f`-independent in the template;
* **P** every pair has a colour `f` with `M_f(x) ∩ M_f(y) = ∅`, and `f ≠` root
  colour inside an arm;
* **T** no monochromatic triangle in `X` (in-arm and cross-arm);
* **C** coverage.

**The per-arm profile, recomputed (counting only).** In the genuine object every
`a ∈ A` has `d_0(a) = 15` and meets each other root class of `r` in 4 or 5 points
(kernel `K58.sender_split`), and every arm point has `m(x) = 5`. Restricting to
`B` (complete) and 12 of `C`'s 14 points gives, per `a`:

  `B-count ∈ {4,5}`, `C-count ∈ {2,...,5}`, `B-count + C-count ∈ [7,10]`,

because `Σ_a (B-count)` = `14·5` = 70 and `Σ_a (C-count)` = `12·5` = 60, so
`Σ_a (B+C)` = **130**, while the third arm of the genuine object contributes 4 or
5 of the 14. **Any encoder that demands `B+C ∈ {9,10}` (or `C ≥ 3` with `B ≤ 5`)
at every position is unsatisfiable by counting alone** — `130 < 15·9 = 135`. That
is exactly the ERRATA failure mode (an over-constrained cardinality cluster), and
it would void a `(14,12)+XT` instance silently: my own first build had it and read
UNKNOWN for 240 s. `m4`'s referee builder uses the sound form (`total ≤ 14`), so
nothing in the round is void on this count; the trap lives in the *phrase* "per-arm
coverage (ten 5s, five 4s)" once it is copied to a truncated arm.

## 2. What is decided (four explicit verified witnesses)

All four are checked from the definition by `work/arm26.verify` (words, parts
independent in the template, pair rule, coverage, triangle census), not from a
clause list.

| object | template | result | witness (sha256 prefix) |
| --- | --- | --- | --- |
| pair level (no triangle constraints) | `T^-` | **SAT 0.5 s** | `work/arm26_T_nox.wit` `92191b51…` |
| pair level | `U^-` | **SAT 0.5 s** | `work/arm26_U_nox.wit` `41f896d2…` |
| + in-arm triangle-freeness | `T^-` | **SAT 140 s** | `work/arm26_T_armtri.wit` `6db419c6…` |
| + in-arm triangle-freeness | `U^-` | **SAT 342 s** | `work/arm26_U_armtri.wit` `5fcedfd2…` |

The `U^-` rows are the ones nobody had built: the template is
`artifacts/k15_template_Uminus_aut10_m4.col` (15 vertices, 35 edges per colour,
every vertex a permutation of `(5,5,4)` in each colour — recomputed here), and the
words are searched, not imported. Monochromatic-triangle census of the four
witnesses (in-arm / cross-arm): `T^-` 121/224, `U^-` 165/236, `T^-`-arm 0/180,
`U^-`-arm 0/200.

## 3. The wall, localised

| instance | CNF | kissat |
| --- | --- | --- |
| `T^-`, both triangle families (XT) | `p cnf 25713 79152` | UNKNOWN 180 s |
| `U^-`, both (XT) | same size | UNKNOWN 180 s |
| `T^-`, **cross-arm only** | `p cnf 25713 77400` | UNKNOWN 200 s |
| `U^-`, **cross-arm only** | same size | UNKNOWN 200 s |
| `T^-`, in-arm only | `p cnf 25713 73104` | SAT 140 s |
| `U^-`, in-arm only | same size | SAT 342 s |

Removing *only* the cross-arm triangles makes both templates SAT; keeping *only*
them is UNKNOWN. The cross-arm condition is the binding one, and it is not a size
effect.

Three constructive routes were tried and are recorded as dead ends (all in
`work/`): min-conflicts on the pair colours with the words of a pair-level witness
fixed (stuck at ~200 mono triangles); the same with cross-arm edges only, started
from the in-arm witness (stuck at 108 of 1092); and the **adjacency-word ansatz**
(`M_f(x)` = the `f`-neighbourhood of a template vertex `v_x`, which makes part
independence automatic) — elegant, but its coverage is infeasible: no multiset of
14 template vertices of colour-0 degree 5 gives `B-count ∈ {4,5}` (best penalty 4
over 200 restarts, `work/adj26.py`). The extremal-word pool is real (18 words per
template, 6 with each empty colour) and admits the coverage, but leaves lists of
size 1 on pairs whose endpoints share an empty colour, which is where the
colouring search stalls (`work/ext26.py`).

## 4. Exact rerun commands

```bash
R=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo
cd $R/.ultramath/smwrmwgf7/m3/work
python3 run26.py T 60      # pair level, T^- (0.5 s)      -> arm26_T_nox.wit
python3 run26.py U 60      # pair level, U^- (0.5 s)      -> arm26_U_nox.wit
python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import run26
run26.run('k15_template_Tminus_aut2_m4.col','arm26_T_armtri',200,cross=True,arm_only=True)
run26.run('k15_template_Uminus_aut10_m4.col','arm26_U_armtri',400,cross=True,arm_only=True)
run26.run('k15_template_Uminus_aut10_m4.col','arm26_U_cross',200,cross=True,cross_only=True)
EOF
```
Every run writes `cnf/<tag>.cnf`; the witnesses are plain text (`word`, `pair`
lines) and are re-checked from the definition at save time.

## 5. What I did NOT verify

* The full `(14,12)+XT` object is **not decided** for either template. No DRAT is
  shipped and nothing here closes a case; UNKNOWN is not evidence.
* I did not check the campaign's own `p cnf 7574 46752` clause by clause; I only
  read `m4`'s builder, which states the sound per-arm coverage. The counting
  boundary of §1 is my own derivation and is not kernel-checked.
* The `U^-` rows use the template file as given. I recomputed its colour degrees
  (each vertex `(5,5,4)` in every colour, 35 edges per class) but did not re-derive
  the classification.
* The min-conflicts and adjacency-word experiments are heuristics: their failure
  says nothing about satisfiability.

## Coordinator's verification (2026-11-22)

Re-checked with this directory's own `arm26.verify`, from the definition:

| witness | template | W/P/C violations | in-arm mono triangles | cross-arm |
| --- | --- | ---: | ---: | ---: |
| `arm26_T_nox` | `k15_template_Tminus_aut2_m4.col` | 0 | 121 | 224 |
| `arm26_T_armtri` | `k15_template_Tminus_aut2_m4.col` | 0 | **0** | 180 |
| `arm26_U_nox` | `k15_template_Uminus_aut10_m4.col` | 0 | 165 | 236 |
| `arm26_U_armtri` | `k15_template_Uminus_aut10_m4.col` | 0 | **0** | 200 |

**The template pairing is load-bearing.** Against `k15_link_Tminus_m5.col` the two
`T^-` witnesses show 46 and 52 part-independence failures: it is the same template
under a different labelling (m10's hazard, `results/truncation-depth/`). A witness
must always be quoted with the template file it was built on.

The counting lemma, checked: `Sum_a B = 14*5 = 70`, `Sum_a C = 12*5 = 60`, so
`Sum_a (B+C) = 130` over 15 positions, and `B+C >= 9` everywhere would need 135.
Any encoder demanding `B+C in {9,10}` is UNSAT by counting — the `ERRATA` class.
`m4/build.py` carries only the optional `(3m) total coverage <= 14`, so the live
`(14,12)+XT` object is not void on this count.

Not verified by me: the UNKNOWN measurements (180 s with both triangle families,
200 s cross-arm only). The SAT side is verified by the witnesses existing.
