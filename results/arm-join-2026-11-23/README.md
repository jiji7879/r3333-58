# The arm-join add-on: a conditional twenty-spoke theorem, verified by regeneration

Bundle: `K58_arm_join_solver.zip` (23.7 KiB), extracted into `.scratch/pg2/k58-solver-pair-glue/`.
The DRAT archives were not used; every certificate was rebuilt from its specification and re-solved.

## Verified here

```
tools/spoke_join.py witnesses
  Checked original-C
  Checked original-D
  Checked shared-13-14
  Checked complete-graph-at-nine-ten
  Checked two-complete-arms
```

**All 39 certificates regenerated**: each record's CNF rebuilt by `formula(record)` and required to
match the recorded SHA-256, then solved with the bundle's Kissat and checked with `drat-trim` —
**39 of 39, 0 failures, 13 min 42 s**.

## What it establishes

**A conditional `U+V ≥ 20` on row `4629be2de806`.** If the colour-2 arm's nine sorted masks begin
`(1, 8, 11, 13, 18)` then the bound is 20, by a finite census: those five masks permit 11 signature
lists and **118 labelled internal colourings**, and every one of the 118 is forced to `U+V ≥ 20` by
certified numerical rectangles. All nine masks fixed give 13 internal colourings; the reference `D`
list gives 16. The claim is recorded as `finite_census` in `benchmarks/spoke-join/summary.json` and
is conditional on the mask condition, not unconditional.

**An agreement obstruction.** The two saved 36-vertex colourings at `(9,10)` agree on 313 shared
assignments and differ on 38 of 351 shared edges. A certificate rules out changing **at most two** of
the 313, so any common completion must change at least three. Independently, a four-triangle
obstruction (vertices 50, 40, 55, 49 and edge 8–34) forbids every colour on that edge while those
eight private edges are kept.

**On row `076eafbfe47e`** the same full C mask list excludes `U ≤ 8, V ≤ 11` and `U ≤ 9, V ≤ 10`;
the `(10,9)` test reached its cap and is not decided.

**Witnesses** checked by the bundle's own tester: 13 C vertices plus all 14 D vertices on the shared
interface; a complete graph on 39 vertices realising the four words at `(9,10)`; and a 45-vertex
union realising them at `(13,14)` with both complete 14-arms.

## What it does not establish

- The bound of 20 is **conditional** on the mask condition. An unrestricted candidate at `(9,10)`
  need only have its smallest C mask `≤ 5`; that is stated as a necessary bound, not a proof that
  every candidate meets the reference list.
- On the central split, 22 of 45 pairs are excluded on row `4629` at `(9,10)` and **23 remain**,
  listed in `benchmarks/spoke-join/summary.json`.
- Both full rows remain **OPEN**.
