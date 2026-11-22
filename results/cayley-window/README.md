STATUS: decided (a bounded, complete family) — every claim below carries a replayed DRAT
against a CNF regenerated from my own encoder, or an exactly checked witness. Two groups of
order 58: Z_58 decided, **D_29 not decided** (kissat 300 s, cadical 320 s, 330 s with the
kernel-checked rigidity family added: all unfinished).

# The Cayley (vertex-transitive-regular) family of `K_n`, n = 50..58

Member m9, swarm `smwrmwgf7`, direction d16 (“close the vertex-transitive loose end”).
Everything here is computed by code in this directory; no repository file and no other
member's directory was modified.

## 1. The claim

A *Cayley k-colouring of `K_n` over a group G of order n* is a colouring of the edges of
`K_n` (vertices = G) that is invariant under the regular action of G, i.e. the colour of
`{x,y}` depends only on `y - x`; equivalently a map `c : G \ {e} -> {1..k}` with
`c(d) = c(d^{-1})`. It is *good* when no triangle is monochromatic.

**Claim 1 (decided).** For every n in {50,...,58} and **every abelian group G of order n**
there is no good 4-colouring of `K_n` invariant under the regular action of G. Fifteen
groups; every instance UNSATISFIABLE with a DRAT proof replayed by `drat-trim` against the
regenerated CNF. Table in §5.

**Claim 2 (decided, complete at those orders).** The groups of order 51, 53, 55 and 57 are
exactly the cyclic ones (`51 = 3*17` with `3 ∤ 16`, `53` prime, `55 = 5*11` with `5 ∤ 10`,
`57 = 3*19` with `3 ∤ 18`). Hence **no Cayley 4-colouring of `K_51`, `K_53`, `K_55` or
`K_57` is good** — the family is decided *completely*, not just on a subsample. In
particular a Cayley object cannot witness `R_4(3) >= 52`.

**Claim 3 (decided).** At order 58 the groups are exactly `Z_58` and `D_29`
(a group of order `2p` with p an odd prime is cyclic or dihedral). `Z_58` is decided
UNSATISFIABLE, both without extra constraints and with the W2 profile imposed
(`|S_0|,|S_1|,|S_2|,|S_3| = 15,14,14,14`). This independently reproduces the record's
“no `Z_58`-circulant good colouring of `K_58`” (PROFILE §5) from a different encoder.
**`D_29` is not decided** (Claim 4 is therefore open at that one group).

**Claim 4 (open).** Whether a good 4-colouring of `K_58` invariant under `D_29` exists.
Measured: kissat 4.0.4 unfinished at 300 s on the unconstrained instance (172 vars /
2 205 clauses) and on the profile instance (13 168 vars / 28 417 clauses); CaDiCaL
unfinished at 320 s on the profile instance. No claim is made either way.

### What this does and does not say about W2

W2 forbids a vertex of profile `(15,14,14,14)` with `H(v) >= 15`. In a Cayley colouring the
colour degrees are the connection-set sizes, so the profile at the identity (hence, by
translation invariance, at **every** vertex) is `|S_c| = 15,14,14,14`, and the ticket
identity gives `H(v) = s_0(v) = 15 = w(v)` (colour 0 is the only critical colour), so
**any good Cayley colouring of `K_58` with that profile violates W2**. The profile is *not*
excluded by class parity: `57 = 15+14+14+14`. For `Z_58`, which is the group I could decide,
there is exactly one involution, so the 57 non-identity elements split into 29 classes and
the profile pins the counts exactly — colour 0 takes 8 classes including the involution
(`2*7+1 = 15`) and colours 1,2,3 take 7 classes each (`2*7 = 14`), 29 in all; that is the
instance of row `Z_58_58_k4_prof`. (For `D_29` the split is much freer: 29 involutions, so
43 classes; see the correction posted on the board.) Either way, Claim 3 is a genuine
(if special) case of W2 for `Z_58`: W2 holds for `Z_58`-invariant colourings. It says
nothing about non-Cayley colourings, which are where every live direction works, and nothing
about `D_29`.

## 2. The encoding, and why it is exact

Vertices are the group elements; `mul` is the full multiplication table. The colour of the
pair `{x,y}` is `c(y - x)` with `c(d) = c(d^{-1})`, so the free variables are the
**inverse classes** of `G \ {e}` (`{d, d^{-1}}`, a singleton at an involution). Every
triangle is a translate of `(e, a, a+b)` with `a, b, a+b != e`, whose three edge differences
are `a, b, -(a+b)`; the constraint “not monochromatic” therefore depends only on the
**multiset of inverse classes** `{cls a, cls b, cls a+b}`, which is what the encoder emits
(once per multiset and colour, with repeated literals deduplicated). `k` colours per class
are Boolean with an exactly-one encoding.

Four independent exactness checks (`selfcheck.py`, `python3 selfcheck.py`):

1. **Encoder vs exhaustive enumeration.** For n = 3..10, every group in the catalogue, k = 2
   and k = 3, with and without a profile constraint: the CNF verdict equals the verdict of
   enumerating *all* class colourings and checking each exhaustively on all `C(n,3)`
   triangles. 60 instances, all agree.
2. **No missing triangle.** For n in {6,8,16,51,58} and each of two groups: every one of the
   `C(n,3)` triangles (up to 30 856) has its class multiset in the emitted constraint list —
   0 missing. This is the failure mode that would make an UNSAT unjustified.
3. **Weighted cardinality encoder** (`card.py`, used only for the profile instance): 186 069
   pinned-assignment cases agree with integer arithmetic, 300 of them cross-checked with
   kissat. (A wrong cardinality encoder is the ERRATA failure mode that manufactures
   closures.)
4. **Classics.** `R(3,3) = 6` refused over `Z_6` and `D_3`; `R(3,3,3) = 17` refused over
   `Z_17`; a good 3-colouring of `K_16` found over `Z_2^4` and over `Z_4xZ_4` and verified
   exhaustively on all 560 triangles (so the SAT side is validated with a real object);
   `K_5` 2-colourable. The group tables themselves are checked for identity, Latin-square
   rows/columns, associativity and involution parity.

UNSAT certificates: kissat writes binary DRAT, `drat-trim` replays it against the CNF
regenerated in the same command. SAT certificates: the model is decoded to a colour per
inverse class and re-checked by `gy.check_colouring`, which never sees the clause set.

### 2b. One extra sound family, built and validated, but not decisive

`K58.model_pair_rigidity` (kernel-checked) says: if `|N_c(u)| >= 15`, `y in N_c(u)` and
`f != c` then `4 <= |N_f(y) cap N_c(u)| <= 5`. At a transitive vertex with the profile every
`|N_0(u)|` is 15, so with `u = e`, `c = 0` this becomes, for every `w` with `colour(w) = 0`
and every `f in {1,2,3}`,

    4 <= #{s : colour(s) = f and colour(w+s) = 0} <= 5.

(`rigid.py`.) That set identity is pure group theory and is verified computationally on random
colourings; the `4..5` bound is the kernel's. Validations actually run: the guarded
cardinality clause set reproduces the brute-force model set on `Z_10` and `D_5` for bounds
`(1,1),(2,2),(1,2),(2,3)` (discriminating: at `D_5`, `(1,2)` keeps 122 of 456 good colourings,
matching exactly), and the lemma itself holds on the three K_50 artefacts — 6 762 `(u,y,f)`
instances, 0 violations.

It does **not** help: in Cayley form the family costs 57 elements x 3 colours x 57 terms of
guarded cardinality, so the profile instance goes from 28 417 to 1 156 990 clauses and kissat
gets slower — `Z_58` profile + rigidity is still UNSAT with a verified DRAT (78.7 MB) but in
about 60 s against about 5 s plain, and `D_29` profile + rigidity is still UNKNOWN at 330 s.
Recorded as a dead end on the board so that nobody re-derives it.

## 3. Exact rerun commands

From `.ultramath/smwrmwgf7/m9/`:

```bash
python3 selfcheck.py                       # all four exactness checks (~10 s)
python3 run_cayley.py out 58 Z_58 4        # unconstrained, order 58, cyclic
python3 run_cayley.py out 58 Z_58 4 '[15,14,14,14]'   # with the W2 profile
python3 run_cayley.py out 50 - 4           # every group of order 50 in the catalogue
python3 summarize.py                       # the table of §5, plus out/results.json
```

`run_cayley.py <outdir> <n> <group|-> <k> [profile-json]` regenerates the CNF, runs kissat,
replays the DRAT, and prints one JSON line per instance. Each instance in §5 is reproduced
by exactly one such line; `summarize.py` recomputes the sha256 of every CNF and proof.

## 4. What I did not verify

* **`D_29`**, and therefore “no Cayley colouring of `K_58`”: open (Claim 4), despite adding the
  kernel-checked rigidity family (§2b). The dihedral groups `D_25`, `D_26`, `D_27`, `D_28` at
  orders 50, 52, 54, 56 are also undecided (`D_25` exceeded 340 s, `D_26`/`D_27`/`D_28` were
  not attempted once `D_25` and `D_29` showed the wall); only the abelian family is complete
  there.
* **Non-Cayley colourings.** These are the object of every other live direction; nothing here
  bears on them. In particular Claim 1 does not weaken W2, it only removes a special family.
* **Groups of order 52, 54, 56 beyond the abelian ones** (5 groups at 52, 15 at 54, 13 at 56);
  only the abelian ones plus, where noted, the dihedral group are covered.
* The profile instance at order 58 for `Z_58` is **logically implied** by the unconstrained
  `Z_58` instance, so it is a cross-check of the cardinality machinery at scale, not
  independent content.
* Nothing here was run with `native_decide` or any trusted oracle; no Lean.
* I did not attempt to improve on the record's `Z_58` result (same statement, independent
  derivation); the *new* content is the ladder at 50..57 and the completeness at 51/53/55/57.

## 5. Results

`status` = solver verdict; `proof` = bytes of the DRAT; `ok` = `drat-trim` replay verdict
against the regenerated CNF. Full sha256s in `out/results.json`.

| instance | group | n | status | vars | clauses | proof B | ok |
| --- | --- | --: | --- | --: | --: | --: | --- |
| Z_50_50_k4 | Z_50 | 50 | UNSAT | 100 | 1 007 | 11 741 642 | yes |
| Z_5xZ_5xZ_2_50_k4 | Z_5xZ_5xZ_2 | 50 | UNSAT | 100 | 1 007 | 37 522 760 | yes |
| Z_51_51_k4 | Z_51 | 51 | UNSAT | 100 | 1 043 | 152 | yes |
| Z_52_52_k4 | Z_52 | 52 | UNSAT | 104 | 1 082 | 13 972 155 | yes |
| Z_13xZ_2xZ_2_52_k4 | Z_13xZ_2xZ_2 | 52 | UNSAT | 108 | 1 089 | 9 558 095 | yes |
| Z_53_53_k4 | Z_53 | 53 | UNSAT | 104 | 1 118 | 30 583 803 | yes |
| Z_54_54_k4 | Z_54 | 54 | UNSAT | 108 | 1 161 | 278 | yes |
| Z_9xZ_3xZ_2_54_k4 | Z_9xZ_3xZ_2 | 54 | UNSAT | 108 | 1 165 | 458 | yes |
| Z_3xZ_3xZ_3xZ_2_54_k4 | Z_3^3xZ_2 | 54 | UNSAT | 108 | 1 177 | 458 | yes |
| Z_55_55_k4 | Z_55 | 55 | UNSAT | 108 | 1 197 | 41 142 169 | yes |
| Z_56_56_k4 | Z_56 | 56 | UNSAT | 112 | 1 240 | 11 725 420 | yes |
| Z_7xZ_4xZ_2_56_k4 | Z_7xZ_4xZ_2 | 56 | UNSAT | 116 | 1 247 | 7 055 140 | yes |
| Z_7xZ_2^3_56_k4 | Z_7xZ_2^3 | 56 | UNSAT | 124 | 1 269 | 10 330 778 | yes |
| Z_57_57_k4 | Z_57 | 57 | UNSAT | 112 | 1 280 | 176 | yes |
| Z_58_58_k4 | Z_58 | 58 | UNSAT | 116 | 1 323 | 18 797 947 | yes |
| Z_58_58_k4_prof | Z_58 + profile | 58 | UNSAT | 13 112 | 27 535 | 4 738 494 | yes |
| Z_58_58_k4_prof_rigid | Z_58, profile + rigidity | 58 | UNSAT | 568 520 | 1 156 990 | 78 722 421 | yes |
| D_29_58_k4 | D_29 | 58 | **UNKNOWN** | 172 | 2 205 | — | — |
| D_29_58_k4_prof | D_29 + profile | 58 | **UNKNOWN** | 13 168 | 28 417 | — | — |
| D_29_58_k4_prof_rigid | D_29, profile + rigidity | 58 | **UNKNOWN** | 568 576 | 1 157 872 | — | — |
| D_25_50_k4 | D_25 | 50 | **UNKNOWN** | 148 | 1 667 | — | — |

Controls (`out/`): `Z_5_5_k2` SAT (pentagon, checked on 10 triangles), `Z_6_6_k2` and
`D_3_6_k2` UNSAT with replayed DRAT (`R(3,3) = 6`), `Z_17_17_k3` UNSAT (`R(3,3,3) = 17`),
`Z_2^4_16_k3` and `Z_4xZ_4_16_k3` SAT with witnesses checked on all 560 triangles.

## 6. Reading of the result

* The Cayley/abelian family is **empty at every order in the critical window** 50..58, so no
  circulant-type construction can meet the cover's `R_4(3) <= 58` target, and — more to the
  point for the campaign — the known good colouring of `K_50` (the object behind
  `R_4(3) >= 51`) is **not abelian-Cayley**. Whatever structure that extremal object has, it
  is not translation invariance.
* **Independent cross-check at 50, from an existing artefact.** I checked the two K_50
  colourings in the repo (`artifacts/k50_blockcayley_Z4xZ4_m4.col`, `artifacts/k50_z4z4_m6.col`)
  with my own checker (`python3 check_artefact.py <file>`): both are valid (0 monochromatic
  triangles out of 19 600, symmetric, zero diagonal), and **neither is vertex-transitive** —
  the colour-degree profiles are not constant: `(9,13,13,14) x2`, `(15,11,11,12) x12`,
  `(15,11,12,11) x10`, `(15,12,11,11) x10`, `(16,11,11,11) x16` for the block-Cayley file.
  A vertex-transitive colouring has one profile, so those objects are not Cayley over *any*
  group of order 50 — exactly what Claim 1's UNSAT instance at 50 says, reached from the
  other direction. (Provenance: the artefact is member m4's; I only check it, and I claim
  nothing derived from it beyond this check.)
* This is the same conclusion the record reached at 58 for `Z_58`; the new content is that
  it holds *uniformly* in the window, and that at 51/53/55/57 it is complete for the whole
  Cayley family, not just the cyclic part.
* The one place a Cayley decision would have bought something new — `D_29` at order 58 — is
  exactly the one that is out of reach of a five-minute CDCL run: 43 inverse classes
  (14 pairs + 29 reflections) with **no** constraint among the reflection classes at all
  (the product of three reflections in `D_29` has odd parity, so no triangle is all-
  reflection). The instance is therefore a `K_29`-shaped forbidden-difference problem
  conditioned on the rotation colouring, and it is the hard case rather than a small one.
  Anyone continuing this direction should attack `D_29` with difference-set machinery, not
  with a bigger conflict budget.

## 7. Files

| file | what |
| --- | --- |
| `gy.py` | group tables + catalogue, inverse classes, exact encoder, exact checker |
| `card.py` | weighted exact-cardinality encoding (profile constraints) |
| `run_cayley.py` | decide one instance, export witness / DRAT, replay the DRAT |
| `selfcheck.py` | the four exactness checks of §2 |
| `summarize.py` | rebuild the table of §5 and `out/results.json` (with sha256s) |
| `check_artefact.py` | check a repo `.col` file independently and read off its colour-degree profiles |
| `rigid.py` | the kernel-checked per-(u,y) rigidity in Cayley form (built, validated, not decisive: §2b) |
| `out/` | CNFs, DRATs, solver and `drat-trim` logs, models, `results.json` |

## Coordinator's verification (2026-11-22)

* Four stored DRATs replayed with drat-trim against the stored CNFs:
  `Z_58_58_k4` `s VERIFIED` (1,181 of 1,323 clauses in core, 8.38 M resolution
  steps, **100 RAT lemmas** — a real search); `Z_51_51_k4` and
  `Z_3xZ_3xZ_3xZ_2_54_k4` `s VERIFIED` with **5-clause cores** (structural and
  shallow); `Z_5xZ_5xZ_2_50_k4` `s VERIFIED` with 922 of 1,007 clauses in core.
* `selfcheck.py` run: all four exactness checks pass — the cardinality encoder on
  186,069 pinned cases, the pipeline against brute force on 60 instances with and
  without the profile, and the classics (`R(3,3)=6`, `R(3,3,3)=17` at the cyclic
  group, a good `K_16` 3-colouring over `Z_2^4`).
* The cross-check at 50 recomputed here: both K_50 artefacts are valid and carry
  **6** and **5** distinct colour-degree profiles, so neither is vertex-transitive,
  hence neither is Cayley over any group of order 50.

**Correction.** "A Cayley object cannot witness `R_4(3) >= 52`" holds only for
*abelian* Cayley objects: at order 52 the groups are `Z_52`, `Z_13 x Z_2 x Z_2` and
`D_26`, and `D_26` was not attempted. The completeness claim at 51/53/55/57 stands
as stated, because the cyclic group is the only group of those orders.

**Scope.** The record already carries Anabanti (2023) as closing
group-partition/Cayley constructions for `n >= 51`. This is a certified,
independently encoded confirmation of a known exclusion — extended to all abelian
groups in the window and run with the W2 profile imposed as well — not new
mathematics, and it does not move the lower bound.
