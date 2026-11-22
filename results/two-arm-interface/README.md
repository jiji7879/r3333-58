status: partial (one rung decided SAT with a verified witness, one cube decided UNSAT with a DRAT replayed by drat-trim, one certified audit finding; the two-arm instance itself is measured, not decided)

# Member m8 (direction d5, Target 6): the two-arm instance at order 44

My direction was Target 6, the three-arm instance at order 58.  I worked on its
sharpest projection instead, because that is where a decision is reachable, and
I found that the projection is *stronger* than anything in the record:

> **Claim A (proved below).** In the uniform fully-sending child at profile
> `(15,14,14,14)`, for every arm point `a ∈ A`,
> `s_B(a) + s_C(a) ∈ {9,10}`, where `s_P(a) = |N_0(a) ∩ P|`.

So a genuine object restricts to a model of a *two-arm* instance whose coverage
is not `<= 5` or `<= 10` per column but exactly 9 or 10 — and that instance has
28 slots, the smallest that can carry the branch's interface.  `UNSAT` there
would close the uniform branch (every branch object restricts to a model of it);
`SAT` there proves that no two-arm argument can close the branch.

Answers obtained (details and commands below):

| # | statement | status |
|---|---|---|
| A | `s_B(a) + s_C(a) ∈ {9,10}` for every `a ∈ A` | **proved** (4 lines, from mixture + interface) |
| B | the instance `L3 = {words, pair rule, C1, C2, C3}` at `14+14` is **SAT** | **decided**, witness `wit/rung3.wit`, independent checker |
| C | `L6` (the full two-arm instance) with arm B pinned to one specific one-arm model is **UNSAT** | **certified**: `cnf/fixB_m1.cnf`, DRAT `log/fixB_m1.drat.gz`, `drat-trim` → `s VERIFIED`, 0 RAT steps |
| D | `L4 = L3 + arm module`, `L5 = L4 + C3`, `L6 = L5 + cross-arm module`, and `L6` without C1: **UNKNOWN** | measured, exact conflicts below |
| E | **audit**: the record's two-arm SAT witness `a_14_14.wit` violates the cross-arm module 258 times and Claim A once — the record's "14+14 is SAT" does **not** settle the rung with cross-arm triangle-freeness | **certified** (exact counts) |

---

## 1. Claim A: the coverage law survives at two arms

Fix the branch (uniform child): `A = N_0(r)`, `|A| = 15`, arms `B, C, D` of size
14, `d_0(a) = 15` for every `a ∈ A`, `m(x) = |N_0(x) ∩ A| = 5` for all 42 slots.
Then

1. no colour-0 edge lies inside `A` (with the two colour-0 edges to `r` it
   would be a monochromatic triangle), so `a`'s fourteen colour-0 partners lie
   in `B ⊔ C ⊔ D`: `s_B(a) + s_C(a) + s_D(a) = 14`;
2. mixture (`K58.mixture`, kernel-checked: `|N_f(x) ∩ N_g(u)| <= 5` for `f != g`,
   with `x = a`, `u = r`, `f = 0`, `g = c`) gives `s_P(a) <= 5` for each arm `P`;
3. hence each `s_P(a) >= 4`, each lies in `{4,5}`, and
   `s_B(a) + s_C(a) = 14 - s_D(a) ∈ {9,10}`.  ∎

The same computation at the slot level gives `|N_0(x) ∩ P| <= 5` for every slot
`x` and arm `P` (family `C2` below).  Both are new as *encoding* facts: the
record's two-arm encodings bounded the column sums only from above (`<= 10` in
the checker m4 used, `<= 14` in m6's encoder), never from below, which is why
they came out satisfiable at columns 8-10.

*Why two arms and not fewer.*  Truncating an arm to `k < 14` vertices only gives
`s_D' <= min(5,k)`, so the surviving lower bound is `s_B + s_C >= 14 - min(5,k)`,
which is vacuous for `k <= 4` and forces `=10` only at `k = 4`; a `(14,14,4)`
instance has 32 slots.  Dropping the third arm entirely is what makes the
instance minimal (28 slots).

## 2. The instance, its clause families, and why it is a relaxation

`tools/enc.py` writes the CNF; `python3 tools/enc.py --nB 14 --nC 14 --out X`
prints the clause census.  The template of `A` is Lean's `K58.template 15 true`
(the `T` template, campaign colours `1,2,3` for the file colours `0,1,2`);
fixing one labelled representative is WLOG by the kernel-checked classification
`K58.Classified 15` plus an isomorphism of the whole structure.

| family | clauses | why it is true of every branch object |
|---|---|---|
| `G1_onehot` | 2,940 | one colour per (slot, arm point) |
| `G2_Z` | 12,964 | `m(x) = 5` (branch) |
| `G3_I` | 2,940 | `a-f-a'-x` would be a monochromatic triangle |
| `G4_C1` | 37,665 | **Claim A** |
| `G5_pair`, `G5_pair_unique` | 22,050 | colour of `x y` admissible with disjoint `f`-parts; one colour per pair |
| `G6_C2` | 7,980 | `|N_0(x) ∩ P| <= 5`, mixture with `u = r` |
| `G7_armT` | 2,184 | no monochromatic triangle inside an arm |
| `G8_crossT` | 7,644 | no monochromatic 2+1 triangle across the two arms |
| `G9_C3_sixset` | 18,018 | a 6-set of an arm with no `f`-edge is 2-coloured with two colours, so `R(3,3)=6` gives a monochromatic triangle |

Total: `p cnf 34846 114385`.  Every family is implied by the branch, so the
instance is a relaxation and `UNSAT` closes the uniform branch; a model need not
extend to a colouring of `K_58` (the third arm's slots and the one-in-each-arm
triangles are projected out).

Guards against the `ERRATA.md` failure modes:

* `tools/enc.py` **refuses** to emit a formula if any cardinality bound has fewer
  guards than the bound (`*/empty` census key) — the `marked_threshold`
  empty-clause trap cannot fire.  It *did* fire during development (an empty arm
  received the full `4 <= s_C <= 5` bound) and was caught by this guard.
* the cardinality encoder is checked by brute force: `python3 tools/enc.py --selftest`
  (all assignments of the primary literals, all auxiliary assignments).
* every bound is stated *per arm*, never globally: the union `|N_0(a) ∩ (B∪C∪D)|`
  is 14, and the per-arm bound is 5.

## 3. Claim B: `L3` at 14+14 is SAT (decided, witness verified)

`L3 = {Z, I, pair, pairunique, C1, C2, C3}` — that is, the pair level *with the
exact coverage law*, the per-slot colour-0 caps and the six-point clauses.

```
python3 tools/enc.py --nB 14 --nC 14 --families Z,I,C1,C1sum,pair,pairuniq,C2,C3 --out cnf/rung3.cnf
kissat cnf/rung3.cnf          # SAT, 80,642 conflicts, ~40 s
python3 tools/decode.py --nB 14 --nC 14 --model log/rung3.txt --families Z,I,C1,C1sum,pair,pairuniq,C2,C3 --out wit/rung3.wit
python3 tools/verify.py witness wit/rung3.wit
```

`wit/rung3.wit`: 28 distinct words, `coverage s_B = [4,5,4,5,4,5,5,4,5,5,5,5,4,5,5]`,
`s_C = [5,4,5,5,5,4,5,5,4,4,5,5,5,4,5]`, sums in `{9,10}` everywhere.  The
independent checker (`tools/model.py::check_two_arm`, written from the definition
and sharing no code with the encoder) reports **failures only in the two
families left out of `L3`**: 107 monochromatic triangles inside an arm and 242
across the arms, and nothing else.

So the exact coverage law does **not** close the pair level at two arms.  The
ladder (each rung adds one implied family to the previous one) is:

| rung | families | verdict |
|---|---|---|
| L1 | `Z,I,C1,C1sum,pair,pairuniq` | **SAT** 2,556 conflicts (~0.5 s) |
| L2 | + `C2` | **SAT** 2,828 conflicts (~0.5 s) |
| L3 | + `C3` | **SAT** 80,642 conflicts (~40 s) |
| L4 | L3 − `C3` + `armT` | UNKNOWN: kissat 1,657,480 / 120 s; cadical 2,306,503 / 300 s |
| L5 | L4 + `C3` | UNKNOWN 1,344,564 / 120 s |
| L6 | L5 + `crossT` (the full instance) | UNKNOWN 1,999,507 / 120 s |
| — | L6 − `C1` − `C1sum` (no coverage law) | UNKNOWN 1,460,879 / 120 s |

**The arm module is the wall**, not the coverage law and not the cross-arm
module: everything up to and including the exact interface is decided SAT in 40
seconds, and adding `armT` alone loses the decision.

## 4. Claim C: a certified UNSAT cube

Fix arm B completely (its 14 words and its 91 internal pair colours) to a
one-arm model produced by `L1`-style search on that arm alone; the remaining
freedom is arm C's words, all 378 pair colours and the auxiliary variables.
This is a restriction of `L6`, so `UNSAT` says "this arm B does not extend".

```
python3 tools/fixB.py --pool 2 --cap 40        # writes nothing; see below for the recipe
cadical -t 240 cnf/fixB_m1.cnf log/fixB_m1.drat   # s UNSATISFIABLE, 234,769 conflicts, 12 s wall
drat-trim cnf/fixB_m1.cnf log/fixB_m1.drat     # s VERIFIED, 0 RAT lemmas, 4,403 of 114,686 clauses in core
python3 tools/verify.py cnf cnf/fixB_m1.cnf    # base clauses identical to the encoder, 301 pin units appended
python3 tools/verify.py drat cnf/fixB_m1.cnf log/fixB_m1.drat.gz
```

`cnf/fixB_m1.cnf` = the L6 encoder output (114,385 clauses) plus 301 unit
clauses (14×15 cell pins and 91 pair-colour pins); `cnf/fixB_m1.pin.json` holds
the pinned arm B model (words, internal pair colours, coverage vector; its
deficiency set is `{0,1,2,13,14}`).  The refutation is pure RUP.

Statistics over 19 arm-B models (`tools/fixB.py --pool 18 --cap 45`, plus one
300 s run): **10 UNSAT**, **9 UNKNOWN** (at 45 s), **0 SAT**.  The ten non-extending
deficiency sets are `{0,1,2,13,14}` (the certified one, 234,769 conflicts),
`{0,4,8,9,14}`*, `{0,6,8,12,13}`, `{3,8,11,13,14}`, `{8,10,11,12,14}`,
`{4,5,11,13,14}`, `{0,4,5,7,10}`, `{0,1,2,7,8}`, `{1,5,10,11,12}`, and
`{1,4,7,9,10}`* — the two starred ones only after the full budget (`*`: the last
one is `UNSAT` at 878,467 conflicts / 300 s; no proof retained for it).  So
**about half of all one-arm models do not extend to a two-arm model of `L6`** —
the two arms are tightly coupled — and the other half are open at 45 s.

## 5. Claim E: the record's two-arm witness does not settle the XT rung

`review/WALL_15141414_SWARM.md` §25 reports `14+14` SAT from
`smwrfgma5/m4/wit/a_14_14.wit` and lists the checks it passed: five zeros, parts
independent, coverage 8-10, pair colour not the shared arm colour, parts
disjoint, no monochromatic triangle *inside* an arm.  That list has no cross-arm
condition.  I transported the witness into the Lean template labelling
(`tools/rebase.py`, using an explicit coloured isomorphism, verified) and checked
it against the definition:

```
wit/a_14_14_lean.wit: 1 × "C1: s_B+s_C not in {9,10}" (point 1: 4+4)
                    258 × "T: monochromatic cross-arm triangle"
                     0 × anything else (words, parts, pair rule, arm module, C2, C3 all pass)
```

`tools/evalcheck.py` confirms the same thing clause by clause: the witness
falsifies **none** of my encoder's clauses in `I, pair, pairuniq, armT` (an
exactness control on the encoder), and its pair stage with `armT` only is SAT,
while adding `crossT` makes it UNSAT — the witness's *words* admit no
cross-arm-triangle-free pair colouring at all.  In particular:

* the record's "(14,14) is SAT" is a statement about the pair level + arm
  module + coverage `<= 10`, **not** about the object called
  "pair level plus arm and cross-arm triangle-freeness" in §24-§26, and
* the single-coverage-violation repair of that witness's design does not help:
  of the 9 legal single zero-swaps that make `C1` exact, every one leaves a
  formula whose pair stage is already UNSAT with `armT` alone, and of the 3
  tested as full cubes, all are UNSAT.

Two smaller confirmations while checking the set-up (both independent):

* the word census reproduces exactly: 254,628 words for the `T` template, part
  sizes `(4,3,3)×162306, (4,4,2)×63504, (5,3,2)×25020, (5,4,1)×3780, (5,5,0)×18`
  (`tools/vocab.py`, `tools/sepside.py`), matching `smwr8io45/m2`'s table;
* `artifacts/k15_template_Tminus_aut2_m4.col` and `k15_link_Tminus_m5.col` are
  both isomorphic to Lean's `template 15 true`, and
  `k15_template_Uminus_aut10_m4.col` to `template 15 false` — via an explicit
  coloured isomorphism with identity colour permutation (`tools/lean_template.py`).

## 6. Calibration on genuine colourings, and dead ends

**Calibration** (`tools/calibrate.py`): on all 15 triangle-free 4-colourings in
`artifacts/` (n = 15…50), the three caps my families use are never violated and
each has maximum exactly 5: mixture `|N_f(x) ∩ N_g(u)| <= 5` (max 5, on the
`k32/k40/k49/k50/n48` objects), the per-arm cap `|N_0(a) ∩ N_c(v)| <= 5` from
Claim A (max 5), and the slot cap `|N_0(x) ∩ N_d(v)| <= 5` from `C2` (max 5).
Zero violations.  So none of my families can cut a genuine object.

**Dead ends** (recorded so nobody repeats them):

* *local search at the word level* (`tools/anneal.py`, `tools/mc.py`):
  simulated annealing and min-conflicts both plateau — the best states reached
  are `dom 0, cov 0, tri ≈ 120` and never 0, from the record's witness or from
  random starts.  The landscape gives no gradient: the pair domains are decided
  by the words and the triangle count is essentially forced.
* *random designs*: 25 arbitrary designs plus 12 random C1-exact designs all
  died on the arm module in ≤ 0.2 s (0 SAT).  A design almost determines whether
  `armT` is feasible at all.
* *fixing both arm colourings* (a cube of `L4`/`L6`): 10 trials, all UNKNOWN at
  20 s — the cube removes the very freedom the solver needs (the arm colouring
  has to be chosen together with the words).
* *repairing the record's witness design to C1*: of the 9 legal single zero-swaps
  that make the coverage law exact, every one makes the pair stage UNSAT with
  `armT` alone; 3 tested as full cubes, all UNSAT.  The witness's neighbourhood
  does not contain a two-arm model.
* *gluing two independent one-arm models* (`tools/glue2.py`): of 16 pairs, 2 had
  disjoint deficiency sets and both had an empty cross pair domain — the
  cross-arm coupling is far too strong for independent arms.
* *structured part profiles* (`tools/profile.py`): putting each arm's
  internally-irrelevant colour large (`|M_1| = 5` for arm B, `|M_2| = 5` for arm
  C) makes the *internal* pair domains too thin: 18 of 91 same-arm pairs and 26
  of 196 cross pairs had **no** admissible colour, so the internal colouring is
  UNSAT at once.  Measured reason: a pair with random words fails colour 0 with
  probability ~0.92, so all 91 internal pairs admitting some colour is a strong
  code property — the record's witness has 0 empty domains out of 378, which is
  why it took CDCL 145 s to find.
* *fixing arm B completely* (`tools/fixB.py`): 10 of 19 one-arm models provably
  do not extend, 9 open at 45 s, 0 SAT; the same cube on `L4` (without the
  cross-arm module) is also UNKNOWN at 60 s for the three models tried.
  One-arm models found in isolation are systematically *bad* choices: they are
  optimal for their own constraints and pathological for the other arm.

## 7. What I did not verify, and what is still open

* **`L6` is not decided.**  No DRAT exists for it and no model exists.  The
  numbers above are budgets, not evidence of either verdict.
* **Claim C is a cube, not the branch.**  Pinning arm B is a restriction: its
  `UNSAT` refutes one arm-B model, nothing more.  It is a certified statement
  and a coupling statistic, not progress on W2.
* **`L3`'s witness is not a branch object.**  It has 107 + 242 monochromatic
  triangles in the two omitted families, so it is not close to a colouring; the
  record's own witnesses are equally far (§6 of the state file).
* **The third arm is projected out**, so `L6` drops the one-in-each-arm
  triangles and everything else involving `D`.  A `SAT` model of `L6` would not
  be a `K_58` colouring.
* I did **not** check `U^-` (73 of the 381 cases); my template is `T`.
* The six-point clauses `C3` are derivable from `armT` and `R(3,3)=6`; I kept
  them because they are cheap, but `L5` shows they change nothing measurable.

## 8. Exact rerun commands

```bash
R=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo
cd $R/.ultramath/smwrmwgf7/m8
K=$R/.scratch/satcheck/bin/kissat ; C=/opt/lean/bin/cadical

python3 tools/enc.py --selftest                       # cardinality encoder
python3 tools/lean_template.py                        # template isomorphism
python3 tools/enc.py --nB 14 --nC 14 --out cnf/L6.cnf # census + the full instance
$K --time=120 cnf/L6.cnf                              # UNKNOWN, 1,999,507 conflicts
python3 tools/enc.py --nB 14 --nC 14 --families Z,I,C1,C1sum,pair,pairuniq,C2,C3 --out cnf/rung3.cnf
$K cnf/rung3.cnf                                      # SAT
python3 tools/verify.py witness wit/rung3.wit          # only armT/crossT fail
python3 tools/verify.py cnf cnf/fixB_m1.cnf            # encoder exactness
python3 tools/verify.py drat cnf/fixB_m1.cnf log/fixB_m1.drat.gz
python3 tools/rebase.py ../../smwrfgma5/m4/wit/a_14_14.wit \
        $R/artifacts/k15_template_Tminus_aut2_m4.col wit/a_14_14_lean.wit
python3 tools/evalcheck.py wit/a_14_14_lean.wit --families I,pair,pairuniq,armT
python3 tools/designfix.py wit/a_14_14_lean.wit /tmp/design.txt   # the 9 legal C1 swaps
```

`cnf/fixB_m1.cnf` is pinned to the arm-B model stored in `cnf/fixB_m1.pin.json`;
`tools/verify.py cnf` regenerates the 114,385 base clauses from the encoder and
finds them identical, and the 301 appended units are that pin.  `cadical` was
invoked as `cadical -t 240 cnf/fixB_m1.cnf log/fixB_m1.drat`.

## 9. Files

* `REPORT.md` — this file.
* `cnf/fixB_m1.cnf`, `cnf/fixB_m1.pin.json` — the certified UNSAT cube.
* `log/fixB_m1.drat.gz` — its refutation (9.7 MB gzipped).
* `wit/rung3.wit` — the decided SAT witness (`L3`).
* `wit/a_14_14_lean.wit` — the record's witness, transported and re-checked.
* `cnf/rung3.cnf`, `cnf/rung4.cnf`, `cnf/rung5.cnf`, `cnf/fixB_m0.cnf` — the instances.
* `log/*.txt` — the solver outputs quoted above (conflict counts, verdicts).
* `tools/` — `enc.py` (encoder + census + selftest), `model.py` (definition and
  independent checker), `decode.py`, `verify.py`, `pairstage.py` (fixed-words
  pair stage), `anneal.py`/`mc.py` (local search, recorded as a dead end),
  `designloop.py`, `gammasweep.py`, `glue2.py`, `fixB.py`, `sepbuild.py`,
  `sample.py`, `vocab.py`, `sepside.py`, `lean_template.py`, `rebase.py`,
  `evalcheck.py`, `diag.py`, `scanprofile.py`, `designfix.py`.

## Coordinator's verification (2026-11-22)

* **Claim A** checked by hand: no 0-edge inside `A`, so `s_B + s_C + s_D = 14`;
  mixture with `x = a`, `u = r`, `f = 0`, `g = c` gives each `s_P <= 5`; hence each
  is 4 or 5 and `s_B + s_C in {9,10}`. Correct. It is the sharp form of the
  record's "ten 5s, five 4s", and it agrees with m3, which found the same law and
  the same caveat (on a truncated arm it is false, and demanding it there is UNSAT
  by counting, 130 < 135).
* **`wit/rung3.wit`** through this directory's `verify.py`: 28 words, coverage sums
  in {9,10}, **0 unexpected failures**; the only failures are the two omitted
  families, 107 in-arm and 242 cross-arm monochromatic triangles. So the exact
  coverage law does not close the two-arm level.
* **The cube**: `fixB_m1.cnf` (3.2 MB, committed) + its proof replayed here to
  `s VERIFIED`, 4,403 of 114,686 clauses in core, 479,324 resolution steps, **0 RAT
  lemmas**, 9.8 s. The proof is regenerable in 12 s (`cadical -t 240`), so only the
  CNF and its 301 pin units (`fixB_m1.pin.json`) are stored.
* **The audit**, checked against the record's witness with an independent checker:
  `a_14_14.wit` has **258** monochromatic cross-arm triangles and coverage
  `[8, 9, 10]` — one position at 8, violating the exact law. Its rebased copy is
  stored here as `a_14_14_lean.wit`.

**Consequence for the record.** `WALL` §25 ("the two-arm instance is SAT: that
route is dead") is withdrawn: the witness that established it is not a model of the
two-arm instance *with* cross-arm triangle-freeness, and its words admit no such
completion at all. What is SAT is the relaxation without `XT`; the rung that
heredity actually delivers — law + arm module + cross-arm module — is UNKNOWN, not
SAT. The route is hard, not closed.

Not verified by me: the ladder's UNKNOWN measurements, the 9 open cubes, and the
one UNSAT for which no proof was retained.
