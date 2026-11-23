# R₄(3) ≤ 58

**Object.** `R₄(3) = R(3,3,3,3)` is the least `n` such that every colouring of the edges of
`K_n` with four colours contains a monochromatic triangle.

**Known.** `51 ≤ R₄(3) ≤ 62`. Lower bound: Chung, *On the Ramsey Numbers N(3,3,...,3;2)*,
Discrete Math. 5 (1973) 317–321, Zbl 0258.05111. Upper bound: Fettes–Kramer–Radziszowski,
*An upper bound of 62 on the classical Ramsey number R(3,3,3,3)*, Ars Combin. 72 (2004) 41–63,
Zbl 1075.05057. Both attributions read off Radziszowski's survey DS1 rev. #18 (24 April 2026),
p. 56 — see `results/literature-r3333-2026-11-23.md`. A November 2026 preprint
(Tatarevic, arXiv:2610.36648v2) claims `≤ 60`. It is unrefereed and is **not** used as a
hypothesis anywhere in this folder.

**Goal.** `R₄(3) ≤ 58`: no triangle-free 4-colouring of `K₅₈` exists.

**What counts as done.** One of:

1. a refutation of every one of the 113,179 frozen ledger rows, each with a CNF rebuilt from
   that row and its recipe, an UNSAT proof accepted by `drat-trim` against the rebuilt CNF, and
   the hash recorded; or
2. one structural lemma that empties all seven small profiles at once, proved in Lean with no
   `sorry` and no `native_decide`, axioms inside `[propext, Classical.choice, Quot.sound]`.

**Not counted as done.** A local-search or min-conflicts failure; replaying a package's own code
as verification of that package; an audit that decides nothing; a statement whose hypothesis is
the open problem; a certificate produced with `native_decide`; a closure whose CNF was not
rebuilt from the frozen row.

**Where the standing state lives.** `review/PROFILE_15141414_STATE.md` for the
`(15,14,14,14)` profile, `review/RESULTS_2026-11-23.md` for the session record, `PLAN.md` for
the campaign plan. This folder is the gate-checkable summary; it must not contradict them.
