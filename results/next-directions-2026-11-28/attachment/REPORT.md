# Early FKR attachment-cover feasibility / calibration at $K_{58}$

Direction 4 of swarm `smx06hpp8`, member `m4`. All work is in this directory; no
production file, frozen ledger, other session's file or encoding default was
touched. No SAT solver was run: everything below is exact integer combinatorics.

## 0. What this settles

| item | state |
|---|---|
| FKR2004 Table 5 (533 marked colourings), all 16 per-order rows | **reproduced exactly**, two independent methods |
| FKR2004 Table 6 (724 overlaps), all 16 per-order rows | **reproduced exactly** |
| CAT58 same-degree family $15/15$ (new census) | **completed**: 3,402 marked, 31,283 overlaps |
| K58 "early census below $10^4$" go criterion | **FAILS**: 31,712 normalised configurations, $3.17\times$ the cut-off |
| recursive pullback relation, cover, wall reduction, bound | **not attempted / not claimed** |

The verdict is the bounded negative result the review memo anticipated: the
early case description of the CAT58 attachment cover does **not** stay compact
at $K_{58}$, so the direction is closed at its declared abandon criterion
("stop if the early census exceeds the declared cut-off"). The two reference
censuses it also demanded are, by contrast, now exactly calibrated with
machine-checked witnesses.

## 1. Pin and inputs

* Repository HEAD for this work: `e43e78e`. While it ran, other sessions
  committed `012c7a2` (Lean CAT58 + attachment bounds) and `a58f7d7`; neither
  touches the inputs used here.
* Seeds: `tools/color-resolved-wallcc/frozen/gluing.py`, sha256
  `ca534d9d5dca23f2b29e9180db633114a1c45743b22fdf8262c7793e85227b48`
  (unchanged at the newer HEAD). It transcribes Tatarevic's
  `formal/src/R4333Lean/CriticalTemplates.lean` (commit `6c3f2fd`):
  `DIFFERENCE_COLORS` on $\mathbb F_2^4$ plus the 16-edge `TRADE` set.
  `U` is the untwisted (Greenwood–Gleason) seed, FKR's $T_2$; `T` is the twisted
  seed, FKR's $T_1$. `U^-`, `T^-` are vertex deletions (any vertex; both seeds
  are vertex-transitive).
* Re-derived here, not taken on trust: both 16-point seeds are triangle-free,
  every vertex has colour degrees $(5,5,5)$, each colour class has 40 edges;
  $|\mathrm{Aut}_{\text{named}}(U)|=160$, $|\mathrm{Aut}_{\text{named}}(T)|=32$,
  $|\mathrm{Aut}_{\text{named}}(U^-)|=10$, $|\mathrm{Aut}_{\text{named}}(T^-)|=2$
  (matches the frozen module's own asserts), and the weak groups have order
  $6\times$ those (all six colour permutations are realised).
  $U \not\simeq_{\text{weak}} T$ and $U^- \not\simeq_{\text{weak}} T^-$
  (zero named isomorphisms after each of the six colour relabellings).
* Definition sources: FKR2004 Section 5 as mapped page-by-page at
  `https://erdosproblems.ai/wiki/library/ramsey_theory/fettes_kramer_radziszowski_2004_upper_bound_62/section_5_pipeline`
  (read for the exact propositions, Tables 5–8 and the weak-isomorphism
  convention; the publisher PDF itself is an image-only scan). Journal record:
  Ars Combinatoria 72 (2004) 41–63.
* **External premises, not re-proved here**: Kalbfleisch–Stanton (exactly two
  good 3-colourings of $K_{16}$, not weakly isomorphic) and Heinrich (exactly
  two $(3,3,3;15)$-colourings, each a vertex deletion of a $K_{16}$ seed). These
  are exactly the premises FKR2004 and the review memo already consume. CAT58
  itself and its upper attachment bound are used as stated in
  `results/literature-next-2026-11-28/attachment-structure.md` §3 and are now
  formalised by a sibling direction at commit `012c7a2`
  (`K58.cat58`, `K58.attachment_bound`); the census below uses only the
  *shape* of that conclusion.

## 2. Objects and equivalence (exact definitions used)

**Marked colouring** of order $k$: a seed $S\in\{U,T\}$ (or $S\in\{U^-,T^-\}$)
with a nonempty marked subset $A\subseteq V(S)$, $|A|=k$. Two are equivalent iff
some vertex bijection $V(S)\to V(S')$ carries $A$ to $A'$ after a permutation of
the three seed colours (weak isomorphism, FKR2004 p. 54).

**Overlap** of order $k$: two K16 copies of seeds $S_1,S_2$ glued along a shared
set $A$ of order $k$; a linking $\theta$ is a *named-colour* preserving bijection
between the two marked subsets (FKR2004 p. 56), so the shared edges agree and
every edge between the two copies stays uncoloured. Two overlaps are equivalent
iff there are seed isomorphisms $\varphi_1,\varphi_2$ **with the same colour
permutation** $\pi$ (the shared edges force this) and a vertex bijection of the
glued object; the two copies may also be swapped.

**Two-layer decomposition used for the count.** Layer 1 fixes the three colour
names (strong isomorphism). Strong overlap classes are indexed by
(family up to copy swap, strong class of $A$, strong class of $B$, orbit of
$\theta$ under $\mathrm{Stab}(A)\times\mathrm{Stab}(B)$). Layer 2 applies the
$S_3$ colour permutations to the whole object: every $\sigma$ is realised on
every seed, so $\sigma$ acts on the strong class set, and the weak classes are
its orbits. This is what makes "weak colour permutation" explicit rather than
implicit, and it is the only place colour permutation enters.

## 3. Reference calibration (FKR2004 Propositions 5.1 and 5.2)

Marked colourings, per order $k=1,\dots,16$ (`marked`, all numbers recomputed):

```
printed Table 5 : 2 3 7 21 34 66 83 99 83 66 34 21 7 3 2 2   total 533
reproduced (S3) : 2 3 7 21 34 66 83 99 83 66 34 21 7 3 2 2   total 533
reproduced (Burnside, independent formula):
                  2 3 7 21 34 66 83 99 83 66 34 21 7 3 2 2   total 533
per seed, S3 quotient:
  U : 1 1 2 5 8 14 17 20 17 14 8 5 2 1 1 1     (117)
  T : 1 2 5 16 26 52 66 79 66 52 26 16 5 2 1 1 (416)
```

Overlaps, per order $k=1,\dots,16$:

```
printed Table 6 : 3 7 20 54 74 109 110 116 91 69 35 22 7 3 2 2  total 724
reproduced      : 3 7 20 54 74 109 110 116 91 69 35 22 7 3 2 2  total 724
by family (weak classes / strong classes):
  U16/U16 : 117 / 573   per order 1 1 2 5 8 14 17 20 17 14 8 5 2 1 1 1
  U16/T16 : 111 / 576   per order 1 2 5 13 18 25 20 15 7 3 1 1 0 0 0 0
  T16/T16 : 496 / 2751  per order 1 4 13 36 48 70 73 81 67 52 26 16 5 2 1 1
total strong classes 3900  ->  724 weak classes
```

Independent cross-check of the overlap stage: an explicit union-find over
labelled triples $(A,B,\theta)$ under the colour-preserving groupoid (including
the copy swap, no canonical keys) reproduces the strong per-order counts at
$k=1,2$ for all three families: $1,3$ / $1,9$ / $1,18$.

## 4. New: the $15/15$ same-degree family

CAT58 gives same *degrees*, and the $K_{62}$ bound $k\le 14$ is not available at
$K_{58}$ (it uses minimum degree 13; the formalised `attachment_bound` only gives
$k\le d_c(v)-\max(0,d_\gamma(u)-11)$, which is vacuous when $d_\gamma\le 11$).
So a cover must include $15/15$ attachments with all orders $3\le k\le 15$, and
the high-overlap rows $k=14,15$ as well as $16/16$ with $k=15,16$.

Marked colourings over $\{U^-,T^-\}$ (new, no published target):

```
per order k=1..15: 3 13 51 145 312 517 659 659 517 312 145 51 13 3 2   total 3402
Burnside cross-check: identical        per seed U^-: 1 3 10 27 56 91 115 115 91 56 27 10 3 1 1
                                                  T^-: 2 10 41 118 256 426 544 544 426 256 118 41 10 2 1
```

Overlaps over $\{U^-,T^-\}$ (new):

```
per order k=1..15:
  17 268 1720 4369 5969 6080 5086 3740 2283 1151 434 132 26 6 2     total 31283
by family (weak / strong):
  U15/U15 :  2768 / 16411   per order 2 13 58 163 319 486 559 510 354 193 77 25 6 2 1
  U15/T15 :  7710 / 46138   per order 5 74 467 1218 1798 1856 1328 672 229 54 7 2 0 0 0
  T15/T15 : 20805 / 124483  per order 10 181 1195 2988 3852 3738 3199 2558 1700 904 350 105 20 4 1
total strong 187032 -> 31283 weak
```

Cross-check at $k=1,2$: explicit union-find gives $6,63$ / $27,438$ / $45,1029$
strong classes, matching the canonical-key route.

Why it explodes: the deleted seeds have tiny symmetry
($|\mathrm{Aut}(U^-)|=10$, $|\mathrm{Aut}(T^-)|=2$ versus 160 and 32), so an
order-15 neighbourhood carries almost no redundancy; $T^-$ alone has 16,639
strong classes of subsets.

## 5. The $K_{58}$ early-census verdict

```
16/16, k>=3 :   714   (ordinary 3..14: 710;  k=15 adjacent: 2;  k=16 high: 2)
15/15, k>=3 : 30998   (ordinary 3..13: 30990; k=14 adjacent: 6;  k=15 high: 2)
normalised early census (both families, k>=3, weak classes): 31712
declared engineering cut-off: 10000        ratio 3.171
```

The go criterion "the complete early census stays below $10^4$ normalised
configurations" is **not met**, so the direction's continuation condition fails
before any recursive pullback is built. Nothing here is a cover, a wall
reduction or a bound: it is the size of the first case split, and it is too big
by a factor 3.2 even before the further-critical-neighbourhood filters that the
2004 method uses are attempted (those filters are themselves not valid at
$K_{58}$: they need the $K_{62}$ profile arithmetic).

## 6. Machine-checked covering witnesses

* Every nonempty subset of every seed has an explicit transport witness: a
  stored vertex permutation $g$ with $g(A) = $ the retained representative.
  All **196,604** witnesses (65,535 + 65,535 + 32,767 + 32,767) were
  re-verified from scratch: $g$ preserves the named colouring and really maps
  $A$ onto the stored representative. Zero failures.
* Every overlap class is stored with a concrete labelled representative
  $(A,B,\theta)$; the enumeration ranges over **all** labelled triples (every
  class pair and every named-colour preserving linking), so every labelled
  overlap maps into a counted class by construction, and the canonical key is a
  complete invariant of the class (asserted to be injective on the enumerated
  set).

## 7. Controls

Positive: relabelling both seeds by the colour permutation $(2,0,1)$ leaves the
533 and 724 censuses unchanged (the $S_3$ layer is invariant), while the same
census on a deliberately corrupted seed with one inserted monochromatic triangle
is rejected. Negative: dropping a family changes the counts (16 marked classes
with only $U$, 416 with only $T$; overlaps $U/U+T/T$ only 613 of 724), and the
$K_{62}$-excluded rows are non-empty here ($16/16$: $k=15$ gives 2, $k=16$ gives
2; $15/15$: $k=14$ gives 6, $k=15$ gives 2), so they cannot be dropped.

Two *wrong* reductions are kept in `exploratory/` with their failures, because
they are the evidence for the semantics chosen here: (i) fixing one
representative per marked-colouring class and counting linking orbits gives 609
instead of 724 (at $k=2$ it gives 4 instead of 7) because a marked-colouring
class need not meet that slice in a named-colour-preserving way; (ii) the
colour-preserving groupoid alone gives 8 at $k=2$ because it does not generate
the copy swap, which is a genuine isomorphism of the glued object.

## 8. What is *not* established

1. No independent check of FKR2004's programs or of its downstream stage counts
   (129, 124, 454, 452, 512, 5, 8191). Only Tables 5 and 6 were calibrated; the
   later stages consume further criticality that $K_{58}$ does not supply.
2. No cover. The census counts case *types*; it proves nothing about which
   types occur in a good $K_{58}$ colouring, and no SAT encoding was produced.
3. No new pullback relation, no attachment units injected into any frozen
   parent, no wall solver run, no bound change. $51\le R_4(3)\le 62$ stands, and
   $\le 60$ remains only the preprint claim.
4. The $15/15$ branch rests on the Heinrich classification as an external
   premise (statement depth, as in the review memo).
5. CAT58's upper attachment bound is used, not re-proved, here (it is proved at
   commit `012c7a2` by a sibling direction).
6. The 3,402 / 31,283 numbers for the deleted seeds are new computations with no
   published target; they are internally cross-checked (Burnside; brute-force
   groupoid at $k=1,2$) but not externally calibrated.

## 9. Reproduction

```
cd .ultramath/smx06hpp8/m4/fkr
python3 run_census.py > run_census.json        # 730.9 s CPU, deterministic counts
```

`run_census.py` asserts, in order: the template audit, the transport witnesses,
Table 5 (two methods), Table 6, the brute-force cross-check, the $15/15$
Burnside cross-check, the $15/15$ brute-force cross-check, the colour-relabelling
invariance, and the corrupted-seed control. It exits non-zero on any mismatch.
Most of the CPU is the $T^-/T^-$ family (124,483 strong classes).

Hashes (sha256): `templates.py`
`2e74f9c2004f3db6b18256b47e3c3b0b9ee1339b934c1a903578cf887b130f4a`,
`census_generic.py`
`f510845b42517c6b1863688c42c64d18eef92dd2f33889ff9ba6d6775e19a0b2`,
`run_census.py`
`3b0359428a805f980276d06d8f1b80cd68ea1522368d35b722a7d0681d919a1f`,
`run_census.json`
`25494224ee4874db85d93a57d36f5e15b184e1fb5d8f0e842aaf5aed009132f0`.
