# Queued: the next swarm (the external review's §4 material)

**Consumed, 2026-11-23.**  `smwrmwgf7` and `smwrzh71x` closed on 2026-11-22, and the
material below was worked by swarm `smwsjya54` (2026-11-23, 8 accepted of 8).  Status
of each target:

* **Target A, the four-multiset corner** — **decided** by m1 of `smwsjya54`.  The four
  three-copy multisets at census rows 229, 240, 254, 266 of the 12312 corner are
  UNSAT at order 35 in all four instances, both palettes and both orders (16/16),
  SAT at orders 30-34; census re-derived from `r333_14.mc` alone.  Mask-dependent
  (102 gives 16/16, 4618 and 9236 only 7/12), so it stays attached to that gauge.
  Scope: one arm type of 332, four of 65 three-copy multisets.
* **Target B, U-07** — **not attempted, and not attemptable**: the strings `U-07`, the
  hash `7c72e9ac` and the numbers 1,936 / 212 occur nowhere in this workspace except
  this file, and the "companion research ZIP" was never supplied.  Two members
  abandoned it for that reason.  If the material ever arrives, this is the target.
* **Target C, the orbit quotient** — **decided** by m2 of `smwsjya54`: 651 / 332 / 115
  reproduced, and the 345 named orientations hit only 332 classes with 13 doubled, so
  the sieve is **37 of 332**, never 45 of 345; `WALL` §12's inference is false.

The companion ZIP that *did* arrive (`K58_repeated_neighbourhoods_and_arm_exclusions`)
is a different package and is written up in `results/repeated-neighbourhoods/`.

**Original text below.** To be launched when `smwrmwgf7` and `smwrzh71x` have finished.
Source: `attachments/let-s-try-and-wcbj/K58_15141414_research_report.md` §4, whose
ledgers live in a "companion research ZIP" that is **not** in this workspace — so
every number below has to be re-derived here before it can be used, and the first
job of the swarm is to check them, not to trust them.

## Why this is worth a swarm

The review's §4 is the only material anyone has sent that is *smaller* than every
object this campaign has failed to decide: a four-multiset corner of one frozen row,
and a repeated-neighbourhood experiment at order 37 with 212 representatives. The
profile programme is blocked at 42 slots and 26 slots; a 30-vertex corner with four
cases is a different order of magnitude.

## Target A: the four-multiset corner of the frozen `T` row

Frozen row `baa4e014b07b43acbad015f706dfdc73ebf494593ac3f8e0aae2a2323ea30357`;
root physical vertex 0, `A` = 1–15, `B` = 16–29, `C` = 30–43, `D` = 44–57; marked
sender vertex 6 with colour-0 support `{16,17,18,19}` in `B`.

Fix `B` to Wesley row 1 with catalogue colour 2 representing physical colour 0;
require `m(x) = 5` on `B` only and full sending on `A`. Then, with **catalogue**
positions and (as the review states) `P = {1,2,5,6}`, `F = {5,6,7,8,11}`,
`G = {5,7,8,9,11}`, `J = {6,7,8,10,11}`:

    n(P) = n(G) = n(J),        n(F) + 2 n(P) = 5,

where `n(Q)` is the number of `A` senders whose support in `B` is exactly `Q`.

* Verify that identity first, from the frozen input, before using it (§2 of the
  review derives it from `H = {1,2,3,4,7,8}`; that derivation is checkable by hand).
* The five-copy family (`n(F) = 5`, `n(P) = 0`, six multisets) is **already
  excluded** — the companion-pentagon projections, twelve positive `K_30` matrices
  and sixteen replayed proofs, per the review and `WALL` §27. Do not redo it.
* **The target: `n(F) = 3`, `n(P) = 1`** — 65 one-arm incidence multisets, of which
  the review says **four** admit the marked path `{3,4,12,13}` (bit mask 12312).
  Permit every assignment of equal-support occurrences to real sender labels, both
  remaining palettes and every compatible path labelling. Decide at order 30
  (`r + A + B`), then add the prescribed `C` vertices.
* Acceptance: UNSAT for all choices, with DRAT replayed against a CNF regenerated
  from your own encoder and an exactness argument for the projection; or one
  surviving case with a witness. Either is a result; neither closes a frozen row by
  itself, and the report should say which hypotheses the corner carries (B-only
  uniformity, full sending on `A`) and what they cost.

## Target B: U-07, the repeated-neighbourhood experiment

Input hash `7c72e9ac…`, a `U15` large arm with all fifteen senders and a
distinguished sender whose neighbourhood is `U16` — so it belongs to the some-six
side, not to the uniform child.

* 14 senders always give at least 28 pentagons across three arms, so one arm gets
  at least ten, and the catalogue bound for a family with all pairwise intersections
  at most three is nine — hence some pair overlaps in four or five positions.
* The review reports 1,936 alignments in the named family all having a good joint
  37-vertex projection with sizes `(3,5,14,14)`, reducing to 212 representatives;
  four broader whole-host inputs stay open.
* Target: decide the 212 representatives, or a principled subfamily of them, with
  replayed proofs; or show the reduction itself is wrong (it is a claim about a
  quotient, and quotients have been the failure mode twice this campaign).

## Target C: the orbit quotient of the one-arm catalogue

The review recomputes the older support sieve: the 45 rejected / 300 passing **named
orientations** become **37 rejected / 295 passing distinct types** once orbit keys
are recomputed under the symmetry the search actually uses. Our record has the
345/45/300 numbers and treats `results/arm-alphabet-14/` as the authoritative
count of 332 types (325 not template restrictions), which is a different quotient.
Reconcile the two, and say which symmetric group each count is modulo — that
distinction has already caused one wrong claim in this campaign (`WALL` §33).

## Read first

`review/PROFILE_15141414_STATE.md`, `review/WALL_15141414_SWARM.md` §§27, 33–42,
`review/ERRATA.md`, and `.ultramath/smwjjvf2f/`, `.ultramath/smwridmzp/` for what
the pentagon and transfer programmes already settled.

## Rules

One solver process per member, ~5 minutes wall per run on a 4-core box; DRAT
replayed against a regenerated CNF for every UNSAT; witnesses checked from the
definition by a second program; an over-constrained cardinality cluster is the
failure mode that has voided four results here — test the satisfiable side first.
