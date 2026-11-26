# Swarm `smwwdcyxb` — final handoff (26 November 2026)

## Outcome

The swarm has ended with **eight accepted directions**. This is finite branch
progress and verified reduction work, **not a proof of `R(3,3,3,3) <= 58`**.
No full row of the 140 unrestricted OPEN `(16,16,13,12)` rows was closed, no
whole profile was eliminated, and no Ramsey bound moved. The platform's
"solved" state means accepted finite submissions were recorded; it does not
mean the original 140-row target became empty.

Work stayed within the target profile. No `(15,14,14,14)` case was selected or
solved. In particular, the `balance.py` perfect-balance default was not used as
an added hypothesis.

## Accepted directions and their exact limits

| direction/member | verified result | not established |
| --- | --- | --- |
| d1 / m4 | The strict case of each of the 140 target rows is covered by 25 one-small-critical cubes, giving 3,500 explicit first-level objects. Parent formulas were rebuilt and representative reductions replayed. A Lean witness chain was checked. | No individual cube or full strict branch was eliminated. Long CDCL runs were UNKNOWN. |
| d2 / m7 | A 343-node binary tree for the named augmented reciprocal CNF has 169 certified leaves and exactly three open cubes. All leaf formulas and proof artifacts were hash-checked; one large retained external proof was freshly replayed here. The two mixed-orientation 33-vertex zero-clone SAT models were fully checked. | No full frozen row or other ticket branch was closed. Two cubes have one positive clone selector; the third pins only 12, so they are not all "clone-free" in a loose natural-language sense. |
| d3 / m1 | A marked-free reciprocal parent for 70 TU rows and an exact four-way reduction; 15 verified local degree-case refutations for the K16 regularity table, plus a reproducible complete C4 family audit. | The reciprocal parent itself remained UNKNOWN. No row closure. |
| d5 / m8 | Hash-pinned active/inactive refinements for all 140 rows, including a complete independent second rebuild of all 280 frontier formulas, and kernel-checked ticket-mass lemmas. | Neither balanced-active nor balanced-inactive was refuted. Solver-strengthening experiments were only UNKNOWN. |
| d6 / m2 | All 2,830 stored entrance DRATs replayed, with CNF/proof hashes checked and 3,600 enumerated keys matched to their 770-case residual. Acceptance is limited to the two complete, 600-case families. | Not a global no-entrance theorem, and not the strict or balanced-active branch. |
| d9 / m3 | Complete finite independent certificates for the K15 and K16 U/T classification: 388 order-16 candidates, 1,021,416 initial order-15 candidates filtered to 7,145 survivors by independently verified exclusions, and complete split/blocking chains. The placement-orbit bookkeeping was also checked. | No row was eliminated. Earlier cover/raw-transport claims must not be resurrected as open gaps: the tracked 1,588-module replay independently verified `K58.Replay.frozenCover` with standard axioms. |
| d10 / m5 | A physical colouring checker passed twelve valid artifacts and rejected the labelled one-defect K51 artifact. The 16-vertex template files were explicitly matched to pinned templates. A fully critical attached 16-arm is realisable locally at K32. | Local search found no K58 model and no row model; that is not impossibility evidence. |
| d8 / m6 | Three of the original four open leaves are refuted with hash-matched DRATs for augmented formulas: n017, n022 and n024. Four marked-free TT/UU parents passed complete clause audits. Counting witnesses were re-verified in exact rational arithmetic. | Only `n025` remains in the original 13-leaf decomposition. The auxiliary leaves are not full rows. No full encoder bridge was delivered. The equal-kind parents remain unrefuted. |

## The entrance theorem, precisely

Let the root profile be `(16,16,13,12)` and let an entrance be a ticket from a
noncritical class. The accepted finite theorem excludes a 16-vertex brace for:

- **T/T** on the two 16-arms, with the entrance in the **13-class**;
- **U/T** on those arms, with the entrance in the **12-class**.

Each of the two named families (`TT:2:5,5,5` and `UT:3:5,5,5`) has
600 complete, independently replayed cases: **1,200 accepted cases**. An
earlier verdict that also named `TT:3` as complete was a judge bookkeeping
error, corrected in the [explicit erratum](verdict-correction-smwwdcyxb-m2.md).
The wider store has 2,830 replayed cases and 770 remaining `(5,5,5)` cases:

| family | verified | open |
| --- | ---: | ---: |
| `TT:2:5,5,5` | 600 | 0 |
| `TT:3:5,5,5` | 443 | 157 |
| `UT:2:5,5,5` | 596 | 4 |
| `UT:3:5,5,5` | 600 | 0 |
| `UU:2:5,5,5` | 591 | 9 |
| `UU:3:5,5,5` | 0 | 600 |

The 4,740 degree-15 brace cases of shapes `(4,5,5)`, `(5,4,5)` and `(5,5,4)`
are not completed. Entrance means $\beta_r\ge1$, **not** strictness
$\beta_r>\alpha_r$. Since $w(r)=32$ and $H(r)-w(r)=\beta_r-\alpha_r$, balanced
active also permits an entrance. No claim that $\beta_r=0$, no strict/mixed
closure and no every-root no-entrance theorem follows.

## Why two different C&C residuals are compatible

The reports concern different refinements at different times:

- m6 closes `n017`, `n022` and `n024` of the **original** four-leaf frontier by
  adding valid degree-cap/support-family clauses to each exact leaf formula.
  The original residual is therefore `n025` only.
- m7's later **343-node tree** further refines the augmented root into three
  open cubes: `r5_n025b2-019` (21 literals), `c485-022` (20),
  `c485_029-033` (12). All three begin with the six-literal `n025` cube. This
  does not conflict with m6's statement about the earlier, coarser tree.

Neither statement certifies the strict, mixed or balanced siblings. Nor does
m7's use of a root-supported C&C method erase the separate common-critical,
compositional or compositional-certificate arguments already checked elsewhere
in the repository.

## Equal-kind parents and the counting limit

The new `gen-TT.cnf`, `gen-UU.cnf`, `gen-TT-recip.cnf` and `gen-UU-recip.cnf`
parents are marked-free relations for reciprocal/root-residual-inactive cases
of the 56 TT and 14 UU rows. Full clauses, literal sets and hashes match. Equal
kinds correctly omit the mixed clone cap: complete 33-vertex equal-kind
colourings with 16 clones delimit that argument. These are new *marked-free*
parents, not a claim that ordinary marked frozen rows lacked parents.

Under the global common pair, $d_0,d_1\in\{15,16\}$, $d_2,d_3\le14$, and
$d_0+d_1+d_2+d_3=57$ give exactly the 12 emitted profiles, not an assumption
chosen for solver speed. Still, none of the four parents was refuted.

The stated counting model was independently checked with `Fraction` witnesses:
1,324 inequalities for the inactive child and 1,495 for the reciprocal child,
all in 912 nonnegative count variables. Hence this particular linear counting
layer cannot eliminate either child. The witness is a vector of cross-arm
counts, **not** a complete colouring or a physical countermodel.

The critical-source hypotheses used by the support clauses matter. The global
degree cap $d_c(v)\le16$ comes from `three_colour_seventeen`; familyA caps
require $c\ne q$; C4-free supports require a critical source. These are not
unconditional bounds of the form $|N_c(x)\cap A_c|\le5$ at arbitrary vertices.

## Verification receipts added and committed in this continuation

- [Scoped entrance audit](entrance-brace-audit-2026-11-26/AUDIT.md): all
  2,830/2,830 stored proofs replay VERIFIED, with the narrower 1,200-case
  accepted theorem. The approximately 8.1 GB proof archive stays at
  `.ultramath/smwwdcyxb/m2/proofs/` rather than being committed.
- [C&C frontier audit](cc-frontier-audit-2026-11-26/AUDIT.md): all 172 leaf
  formulas, all 169 identified proof artifacts, and a fresh 347.168-second
  external-proof replay. This was not a redundant DRAT pass over all 155 inline
  proofs one by one; their stored proofs and verification receipts were bound
  by hashes.
- [m6 audit](m6-audit-2026-11-26/): fresh clause validation for all four
  equal-kind parents, all 21 manifest hashes, exact rational witnesses, and a
  fresh n024 DRAT replay (`s VERIFIED` in 264.330 seconds). The n017/n022
  retained receipts and exact input/proof hashes were checked rather than
  redundantly replayed again in this continuation.
- [Strict-split audit](strict-split-audit-2026-11-25.md) and the existing
  cover, common-critical, classification and pentagon audits cited by the
  earlier status report remain separate results, not subsumed into a full-row
  claim.

Commits: `318d601` (scoped entrance checkpoint), `b0a8ab9` (completed entrance
replay and reciprocal C&C audits), and the final m6/handoff commit following
this file. All are on `main` without force-pushing.

## What remains genuinely open

1. A refutation or physical countermodel for a **full frozen row** under its
   own hypotheses, not merely a stronger leaf relaxation.
2. Strict, mixed, balanced-active and balanced-inactive alternatives across
   the 140-row target. Exact refinements exist; an exact frontier is not an
   elimination.
3. A complete semantic encoder bridge from real colourings to the emitted CNF
   auxiliary/cardinality selectors. m6 supplied useful finite leaf and parent
   progress, not this end-to-end bridge.
4. The uncompleted entrance cases above, including the 15-brace families, if
   this local route is chosen again. Earlier UNKNOWN caps do not decide them.

The productive next step is a new structural cut or a full-row semantic closure
with a checked DRAT proof—not another claim derived from a timeout or a local
search failure.
