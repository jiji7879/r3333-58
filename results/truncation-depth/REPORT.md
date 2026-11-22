status: certified — four decided instances (three with DRAT replayed by drat-trim against the regenerated CNF, one SAT with an explicit verified object), exact enumeration theorems about all nine known witnesses, and one ERRATA-class encoder hazard reproduced. The two strengthened search objects remain UNKNOWN and are reported as measurements, not results. No case is closed, no bound moves.

# Member m10, direction d11 (minimal-violation analysis of the known objects), swarm `smwrmwgf7`

Everything below was computed by the code in this directory. No repository file
and no other member's directory was modified. The working tree was not touched.
`../../../` below is the repository root when a command is issued from
`.ultramath/smwrmwgf7/m10/`.

The question this direction asks is not "is the branch satisfiable" but "where do
the known objects actually die, how small is the piece that kills them, and is the
killing constraint a theorem about genuine objects or an encoder artefact". Three
of the answers turned out to be decidable; two did not.

## 1. Claims

### C1 (certified numbers) The record's "gap located" numbers are right

`python3 score.py ../../../.ultramath/smwr8io45/m6/wit/pair58_Tminus.wit`
reproduces, from the witness file alone and an independently written checker
(`k58lib.py`, written from the branch definition, not from any encoder):

| quantity | my value | record |
|---|---|---|
| monochromatic triangles inside the 42 slots | **2,562** (243 / 255 / 2,064) | 2,562 |
| colour-split overlap masses (ordinary colours) | **319 / 314 / 732**, total 1,365 | 319 / 314 / 732 |
| blocked-set cliques per arm (bound 5) | **9, 9, 10** | 9, 9, 10 |
| coverage of the arm points | 14 for every point | — |
| five zeros per word, part independence, pair rule, arm-colour ban | all hold | — |

The other 42-slot witness `smwrfgma5/m4/wit/p58.wit` gives 2,001 triangles,
484 / 377 / 504 (total 1,365) and cliques 9, 9, 8. So the diagnosis is not a
property of one file: every pair-level witness is far from the 455-per-colour
split and violates the sixth lemma with a clique of nine or ten.

### C2 (decided SAT, explicit object) The colour-0 side of the sixth lemma is satisfiable and sharp

`cnf/design.cnf` (`p cnf 16863 45024`) is SAT (kissat, < 1 s). Its model, decoded
by `extract_design.py`, is an explicit object

    log/design.blocks:  42 five-sets on 15 points,
                        every point in exactly 14 of them,
                        intersection graph inside each of the three arms has clique number exactly 5.

5 is the kernel-checked bound of the sixth arm lemma at colour 0, so the design
level of the lemma is satisfiable **and attained**. Consequence: no argument that
uses only the colour-0 supports and their intersections can close the branch; the
first colour-0-side constraint that can is the sixth lemma at its sharp value,
and that value is reachable.

### C3 (decided, DRAT) The design of C2 admits no pair colouring

```
python3 enc.py --out cnf/design_plain.cnf --template ../../../artifacts/k15_link_Tminus_m5.col \
        --pin-design log/design.blocks --drop S,S2
../../../.scratch/satcheck/bin/kissat cnf/design_plain.cnf log/design_plain.drat   # s UNSATISFIABLE
../../../.scratch/satcheck/bin/drat-trim cnf/design_plain.cnf log/design_plain.drat # s VERIFIED
```
kissat **7,839 conflicts**, DRAT 1,114,294 bytes, drat-trim `s VERIFIED` in 0.6 s
with a core of **3,153 of the 99,330 clauses and 4,644 lemmas over 141,769
resolution steps (82 RAT lemmas)**. This is a real search with a real core, not
unit propagation, so the UNSAT is not the ERRATA "empty clause" class. Meaning:
the sharp design of C2 does not lift from the support level to the pair level —
the pair rule kills it.
*Exactness*: families W1, W2, C1, P1, P2, P3, D1 are consequences of the branch
(§3 below); the design pin is **not**, so this is a statement about that design,
not about the branch.

### C4 (certified numbers, two more DRAT instances) The known witnesses are word-level dead under the sixth lemma

```
python3 enc.py --out cnf/sixth_pin.cnf --template ../../../artifacts/k15_link_Tminus_m5.col \
        --pin ../../../.ultramath/smwr8io45/m6/wit/pair58_Tminus.wit
kissat cnf/sixth_pin.cnf log/sixth_pin.drat       # s UNSATISFIABLE, 0 conflicts
drat-trim cnf/sixth_pin.cnf log/sixth_pin.drat    # s VERIFIED
```
"The 42 words of `pair58_Tminus.wit` cannot be completed to a pair colouring that
satisfies the sixth arm lemma" is therefore a certificate, not a measurement
(the record's §25 had it as a measurement: cliques of 9, 9, 10).

The same for the depth-3 word assignment of C6: `cnf/t3v2_pin.cnf`, UNSAT, 0
conflicts, DRAT `s VERIFIED` — its 211 dead pairs (below) refute it at depth 2.

### C5 (theorem, exhaustive) Truncation depth 3, with the exact obstruction characterisation

For a set `S` of slots of a witness, the *local object* is the witness's words on
`S` plus a colouring of the pairs inside `S` subject to (P1) the arm colour is
never used inside its own arm, (P2) colour `f` on a pair needs disjoint `f`-parts,
(X) no monochromatic triangle. Every genuine object restricts to a local object
on every subset of its slots, so a subset with no local object is a set of slots
that **no genuine object can carry with those words**.

`python3 depth.py <witness>` enumerates all subsets in increasing size.
Exhaustive result (`--kmax 3`, every subset checked, no sampling):

| witness | slots | infeasible pairs (of 861/378/…) | infeasible triples (of 11,480/3,276/…) |
|---|---|---|---|
| `pair58_Tminus.wit` (T⁻, `k15_link`) | 42 | **0** | **514** |
| `p58.wit` (= `.scratch/pkg/witnesses/p58.wit`) | 42 | 0 | 524 |
| `p58_cc.wit` | 42 | 0 | 459 |
| my own plain model `wit/plain.solver.wit` | 42 | 0 | 456 |
| `a_14_14.wit` | 28 | 0 | 50 |
| `a_14_13.wit` | 28 | 0 | 44 |
| `a_14_13_cap.wit` | 28 | 0 | 55 |
| `a_14_12.wit` | 26 | 0 | 40 |
| `a_14_12_cap.wit` | 26 | 0 | 52 |
| design-extension words `wit/dw.s1.wit` | 42 | **129** | (stops at depth 2) |

So the truncation depth is exactly **3** for every pair-level and two-arm witness
in the campaign's record, including the two-arm witnesses the record calls SAT
witnesses. And the mechanism is uniform (Lemma 1 of `PROOF.md`): a triple of
slots fails iff all three admissible-colour lists are *the same singleton* `{c}`.
I verified this on every obstruction: 514/514 and 524/524 have all three domains
singletons of the same value (`nogoods_pair58.json`, `nogoods_p58.json`,
`python3 analyse.py … --out …`). This is strictly stronger than the record's §29
sentence ("the smallest local obstruction is three words with one singleton pair
colour"): it is *every* depth-3 obstruction, not the exhibited one.

Consequence worth feeding into the search: a genuine object's 42 words must
contain **no** dead pair and **no** triple whose three lists are the same
singleton. That is a word-level condition; C6 below is the attempt to decide it.

### C6 (measurements, NOT results) The two strengthened objects are UNKNOWN

Both were built here from scratch, instrument-tested, and run under one solver
process at a time with hard caps:

| object | CNF | kissat 4.0.4 | CaDiCaL 2.1.2 |
|---|---|---|---|
| pair level + sixth lemma (A-part form) | `cnf/sixth.cnf` 22,743 v / 138,012 c | UNKNOWN 300 s | — |
| pair level + sixth lemma (both forms, incl. the true `N_a(x) ∩ N_a(r)`) | `cnf/sixth2.cnf` 23,577 v / 176,778 c | UNKNOWN 300 s, 3.92 M conflicts | — |
| pair level + sixth lemma, design of C2 pinned | `cnf/design_pin.cnf` | **UNSAT < 1 s** (DRAT not emitted) | — |
| word-only depth-3 relaxation (T2 no dead pair + T3 no dead triple) | `cnf/t3v2.cnf` 73,206 v / 326,564 c | UNKNOWN 330 s, 2.13 M conflicts | UNKNOWN 620 s |
| plain pair level (control) | `cnf/plain.cnf` 21,924 v / 98,700 c | **SAT 12 s** | pysat 6.4 s, 143,283 conflicts |

The plain-pair-level SAT is the falsification control: my encoder is not
over-constrained, because it reproduces the campaign's own finding on an instance
I built independently. Local search for a depth-3 model (`repair.py`) started from
`wit/plain.solver.wit` (0 dead pairs, 456 dead triples) and stalls at 439–580
dead triples with 30–40 dead pairs; no depth-3 model was found and no proof of
UNSAT exists. **I am not claiming anything about the satisfiability of either
object.**

### C7 (theorem, exhaustive) Every 14-slot arm needs a generic word — and the record's sentence is only true in the strong form

`extremal.py`, `extremal2.py`, run against `artifacts/k15_link_Tminus_m5.col`:

* the word census reproduces the record exactly: **254,628** words, part sizes
  `(4,3,3) 162,306`, `(4,4,2) 63,504`, `(5,3,2) 25,020`, `(5,4,1) 3,780`,
  `(5,5,0) 18` (18 extremal);
* with multiplicity `<= 2` per word and *pairwise admissibility only*, there are
  **2,244,026** all-extremal size-14 arms (for each of the three arm colours) — so
  the record's sentence "an all-extremal arm cannot fill 14 slots" is **false at
  the pair level**;
* adding the branch-necessary depth-3 condition of Lemma 1 (no triple whose three
  lists are the same singleton), the count is **0 for every arm colour**
  (search trees of 3,093–3,843 nodes).

So the mechanism the record uses to explain the ladder's shape is right, but the
correct statement is: **every 14-slot arm of a genuine object contains a
non-extremal word**, and the proof needs the depth-3 condition, not merely
pairwise admissibility. (Three copies of one extremal word already violate the
depth-3 condition, so the multiplicity bound `<= 2` is a consequence.)

### C8 (hazard, ERRATA class, reproduced) Mixing the two T⁻ template artefacts makes a 1-conflict "refutation"

`artifacts/k15_link_Tminus_m5.col` and `artifacts/k15_template_Tminus_aut2_m4.col`
are the same template under different labelings (each colour class is a connected
35-edge graph in both). Pinning a witness written against one of them into an
encoder built on the other gives:

```
python3 enc.py --out cnf/hazard_badtemplate.cnf --map cnf/hazard_badtemplate.map.json \
        --drop S,S2 --pin ../../../.ultramath/smwr8io45/m6/wit/pair58_Tminus.wit
python3 checkmodel.py cnf/hazard_badtemplate.cnf cnf/hazard_badtemplate.map.json \
        ../../../.ultramath/smwr8io45/m6/wit/pair58_Tminus.wit   # 72 violated clauses
kissat cnf/hazard_badtemplate.cnf                                # s UNSATISFIABLE, 1 conflict, 0 decisions
```

A 0.05 s UNSAT with **1 conflict and 0 decisions** is the signature of an
over-constrained formula, exactly the failure mode of `ERRATA.md`. Anyone pinning
a witness must take the template path from that witness's own header line. I hit
this myself: my first `t3` instrument test was void for this reason.

### C9 (own error, corrected, documented) An inverted cardinality sign in my own encoder

My first version of family (T2) ("every pair has an admissible colour") asserted
`⋁_{c blocked} N_c` instead of `⋁_{c} ¬N_c`, i.e. "every pair is blocked in some
colour" — an over-constraint that is *not* a branch consequence. It was caught by
the independent check `python3`-side (the model found had 211 dead pairs although
the CNF contained T2). Fixed; the corrected instance is `cnf/t3v2.cnf`. This is
recorded because it is the same class as the campaign's four void artefacts and
because the instrument that caught it (an independent semantic check of every
model before it is believed) is cheap and should be standard.

## 2. Rerun

```
cd .ultramath/smwrmwgf7/m10
bash make_all.sh                                  # rebuilds every CNF (deterministic)
python3 score.py ../../../.ultramath/smwr8io45/m6/wit/pair58_Tminus.wit
python3 depth.py <any .wit> --kmax 3
python3 analyse.py <any .wit> --out nogoods.json
bash verify_drat.sh                               # the three DRAT replays
python3 extremal.py ; python3 extremal2.py --arm 1   # C7 (49 s and 13 s)
```
Wall clock: `make_all.sh` 6 s, `score.py` < 0.1 s, `depth.py --kmax 3` < 1 s per
42-slot witness, DRAT replays 0.3–0.7 s each, the three SAT/UNSAT runs 1–12 s.

## 3. What the encoder families are, and why each is a branch consequence

| family | clause | why it follows from the branch |
|---|---|---|
| C1 | one colour per cell `(x,a)` | an edge has one colour |
| W1 | exactly five 0s per slot | `m(x) = |N_0(x) ∩ A| = 5` is the branch hypothesis |
| W2 | `M_f(x)` independent in template colour `f`, `f = 1,2,3` | else `a–x–a'` is a monochromatic triangle |
| P1 | one colour per slot pair | ditto |
| P2 | `colour(x,y) != b` inside arm `b` | else `x–y–r` is monochromatic in colour `b` |
| P3 | `colour(x,y) = c ⇒ M_c(x) ∩ M_c(y) = ∅` | else `x–y–a` is monochromatic in `c` |
| D1 | each arm point in exactly 14 colour-0 supports | `d_0(a) = 15` and `r` is one of them |
| S | inside one arm no six slots are pairwise `a`-blocked, `a != b`, using `A` as the common-neighbour set | `K58.part_family_le_five` (`Blocked.lean`, kernel-checked, axiom-clean); an `A`-witness of blocking is a witness of `ABlocked` |
| S2 | the same with the stated `a`-part `N_a(x) ∩ N_a(r)` | `K58.part_family_le_five` verbatim |
| T2 | every pair has an admissible colour | its own colour in the genuine object |
| T3 | no triple has all three lists equal to one singleton | Lemma 1 of `PROOF.md`, applied to the restriction of the genuine colouring |
| pin | fixed words / fixed colour-0 supports | **NOT** implied — every use of a pin is labelled as such |

The one thing I do **not** claim: that these families exhaust the branch. They are
a relaxation, which is the direction needed for a closure (UNSAT of a relaxation
refutes the branch) and the reason `SAT` in C6 tells us nothing.

## 4. What I did not verify, and what could still be wrong

* **The classification.** I use `Classified 15` nowhere except through the
  template edge counts (35 per colour), which I checked **directly** on both
  artefacts (`score.py` prints `edge counts {1: 35, 2: 35, 3: 35}`). The identity
  that produces the record's 455-per-colour split needs that 35 (or, more
  precisely, that each `N_0(a)` is a template); see `PROOF.md` Lemma 3. If the
  classification is wrong, Lemma 3's constant changes and C1's "target 455"
  reading changes with it — the *measurements* do not.
* **The DRAT certificates are relative to my encodings.** Each is replayed
  against the CNF that `make_all.sh` regenerates, so the certificate and the
  clause set are tied together; `checkmodel.py` is the independent instrument
  that says the clause set is what I claim it is (0 violated clauses for a model
  of the unpinned instance).
* **C3's significance is bounded by the pin.** It refutes one design, not the
  branch.
* **No closure.** The two objects of C6 are UNKNOWN; the local search of C6 found
  nothing. Anyone reading this should not treat 330 s or 620 s of UNKNOWN as
  evidence either way.
* **The two-arm witnesses' depth counts** are computed on their own slot sets
  (26 and 28), not on a 42-slot restriction, because the files do not contain the
  remaining arms.

## 5. Files

* `k58lib.py`, `score.py` — independent branch checker (words, pair rule,
  triangles, coverage, overlap masses, blocked cliques, armFar).
* `depth.py`, `analyse.py` — truncation depth, obstruction structure, nogood lists.
* `extremal.py`, `extremal2.py` — the extremal-word search of C7 (pairwise
  admissibility; with the depth-3 condition).
* `enc.py`, `enc_triple.py`, `enc_design.py` — the three encoders (pair level +
  sixth lemma; word-only depth-3 relaxation; colour-0 design level).
* `checkmodel.py`, `decode.py`, `extract_design.py`, `extend.py`, `repair.py` —
  instruments: clause-level model check, model decode, design extraction, word
  extension, local search.
* `make_all.sh`, `verify_drat.sh` — deterministic rebuild and the three replays.
* `cnf/`, `log/` — every CNF, every solver log, the three DRAT proofs and their
  drat-trim logs, the design, the depth-3 word file.
* `wit/` — my own pair-level model (`plain.solver.wit`), the design extension
  (`dw.s1.wit`), the depth-3 model found before the T2 fix (`t3_words.wit`).
* `nogoods_pair58.json`, `nogoods_p58.json`, `nogoods_plain.json` — the complete
  list of depth-3 obstructions of three witnesses (slot triple, arm pattern,
  domain sizes, which pair is the forced one). These are directly usable as
  ternary nogoods in any of the live XT instances.
* `PROOF.md` — the written arguments (Lemma 1 list-colouring, Lemma 2 coverage,
  Lemma 3 the 455 identity, Lemma 4 the depth counting, the design theorem).
