# Notes — R₄(3) ≤ 58

Numbered steps. Each one states a settled statement, where its argument is, and the command that
reproduces it. Nothing here is a new claim: every step transcribes an established result and names
its artefact. Where a step was re-run in the session of 2026-11-23 (second), the check entry in
`ledger.md` says so.

The goal and the standard of done are in `problem.md`.

---

1. **The goal, restated for the gate.** `R₄(3) ≤ 58`, i.e. no triangle-free 4-colouring of
   `K₅₈`. Current state: `R₄(3) ∈ [51,62]`; 31,751 of the 113,179 frozen rows are OPEN; all 381
   rows of the `(15,14,14,14)` profile are OPEN. Recorded at `review/RESULTS_2026-11-23.md:1-10`.

2. **The frozen cover is complete, unconditionally.** `K58.Replay.frozenCover : K58.FrozenCover`
   (`lean/K58/RawCover.lean`, `lean/K58/FamilyGluing.lean`, audited by
   `lean/ReplayCheck.lean`): every balanced root of a triangle-free 4-colouring of `K₅₈` falls in
   one of the 113,179 ledger rows. 1,588 generated modules are rebuilt from source by
   `bash lean/build.sh --replay`, which ends
   `Checked 1764 complete families, 190736 raw placements, 77557 omitted transports.`
   **This certifies the cover, not a refutation.** No row is decided by it.

3. **The kernel audit.** `lean/K58/Check.lean` lists 367 declarations and every one reports
   axioms inside `[propext, Classical.choice, Quot.sound]` — no `sorry`, no `native_decide`,
   checked by `bash lean/build.sh` (build order in `lean/order.txt`). The count was 80 at the
   start of the 2026-11-23 session and 34 the session before.

4. **Under reciprocity (R), 363 of the 381 rows of `(15,14,14,14)` fall.** `d_c(r) = 14 < 15`
   means no sender sits in a 14-arm, so the family word is empty and balance forces the uniform
   branch. Contrapositive: a surviving row needs a **non-reciprocal** edge. Kernel:
   `lean/K58/ArmSender.lean` (8 declarations, `H = w` everywhere). Record:
   `review/RESULTS_2026-11-23.md:45-48`.

5. **The partition-design family is empty, and at depth.** No board of any of the 138 designs
   carries 4 `C`-vertices and 4 `D`-vertices: one vertex kills 22, the same-board pair 114, then
   2+1→118, 2+2→128, 3+3→135, **4+4→138**. 276 oriented instances, all DRAT-accepted; controls:
   all 276 SAT once the sender is deleted. `results/wall-run/`,
   `review/RESULTS_2026-11-23.md:49-52`.

6. **The multiplicity layer leaves 44 profiles and cannot pin an arm.** 135 partitions of 14 are
   decided (53 with a design, 82 without). From the profile side, 48 candidates minus
   `(4,4,2,2,1,1)`, `(4,2,2,2,2,2)`, `(3,3,3,3,1,1)`, `(2⁷)` gives **44 survivors**; two
   independent routes agree, both kernel-checked (`lean/K58/Multiplicity.lean` 71 declarations,
   `lean/K58/DesignIncidence.lean`, `lean/K58/ProfilesIncidence.lean`). This is a statement about
   the uniform child: it does not decide a row.

7. **The third-colour matching law is a theorem of the instance, not a missing constraint.**
   Between two classes of a root the third-colour edges form a matching (checked at all 30 rooted
   views), hence `t(y) ≤ 5`, `Σ t = 65`, and at least nine of fourteen vertices attain five
   (`lean/K58/Weighted.lean`, `lean/K58/CountLaw.lean`). Adding it to a CNF measures nothing.
   Corollary: 8 fives + 6 fours ≤ 64, so ≥ 9 fives is forced.

8. **Six catalogue types are not excluded as arms.** Types 27, 28, 73, 157, 193, 261 each carry a
   kernel-checked 32-point witness with its fibre system, so the 22 design exclusions do not lift
   to types. `lean/K58/` (the witness modules listed in `lean/K58/Check.lean`),
   `review/RESULTS_2026-11-23.md`.

9. **OPEN — the cross-arm test, as shipped.** The package
   `K58_two_arm_compatibility` claims: a type-16 arm with the displayed equal-`Z` partition forces
   a singleton in every type-36 sibling. It is **not** in force in this folder: its proof archive
   (`K58_two_arm_proofs.zip`, SHA `ed94e74a…`, 6,273 rectangle + 240 table + 7 missing-neighbour
   proofs) was never supplied, so nothing in it can be replayed, and the claim is conditional on
   `K58.Classified 15` and on the six-set classification, neither of which is proved in the tree.
   What is measured: the argument covers 4 of type 16's 21 placements (one orbit); 7 orbits ×
   192 = 1,344 cases remain. Swarm `smwsyh6tk` is re-deriving the 192 cases independently.

10. **The exact 42-slot instance is `31746/152078`.** Command:
    `ladder.py --sizes 14,14,14 --total 14 --xt --tightcov`. The larger `45381/179318` build is a
    relaxation: it leaves the per-position total at ≥ 9 and admits `(4,4,4)`.
    `review/RESULTS_2026-11-23.md:93-95`.

11. **What the solve data says about the wall.** A 42-row sample (6 per profile, 12 s / 400k
    conflicts per case) closed **0 of 42**, 284 CPU-s, median 6.6 s, 0 formulas retained:
    `results/wall-sample/README.md`. This is consistent with every earlier measurement and is
    evidence that first-pass budgets do not touch these rows — it is not evidence of
    unsatisfiability.

12. **Literature state** (verified 2026-11-23 against DS1 rev. #18 and arXiv):
    `results/literature-r3333-2026-11-23.md`. Two details there matter operationally: Chung's
    printed 51-colouring matrix has a typo — a triangle `(31,7,28)` in colour 1 — so a naive
    transcription fails a colouring check; and the survey does **not** state that `R₄(3) = 51` is
    conjectured, only that it is "the most studied and intriguing open case".

13. **Routes tried and set aside** (each with the reason, so they are not re-opened):
    - nine clause-level interventions (degree cap, twin lex-leaders, SBVA, independent-set
      variables, pseudo-Boolean encoding, the 116-cell Hall cut, order-45 clauses, "≤12
      omissions", "≤3 per arm"): the best was −6%, the 116-cell cut was later shown structurally
      minimal, so none of them reach the rows;
    - word cubes at depth 2: 3.2·10¹⁰ cases;
    - the `(14,k)+XT` ladder: SAT on both templates at k = 6/7, and a decided rung cannot be
      patched upward (freeing 1–4 slots is UNSAT at once);
    - pinning the coverage profile; the some-six pair level (SAT); partition-design screens
      (inert — the stock queue is the empty cube, and the package's "4 OPEN of 7" was a
      parent-budget artefact);
    - codegree counting against the no-singleton case: a codegree-9 pair violates nothing held;
    - the multiplicity layer as a way to pin an arm; the matching law, the confinement ladder and
      parts of claim 1 as constraints (theorems of the instance).
    Records: `review/RESULTS_2026-11-23.md` and the swarm directories named there.
