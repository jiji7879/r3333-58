# The 19-spoke bound, replayed here from the solver archive alone

Bundle: `attachments/let-s-try-and-wcbj/K58_solver_and_proof_notes.zip` (46.7 MiB), unpacked at
`.scratch/pg/k58-solver-pair-glue/`. **The two DRAT archives the notes ask for
(`K58_DRAT_1_foundations_and_endpoints.zip`, `K58_DRAT_2_interior_splits.zip`) are not present**,
so every stage was run in *regenerating* mode (no `--stored-only`): the verifier rebuilds each CNF
from the row and re-derives each refutation with the bundled Kissat.

## Result: all four stages pass, in 18 min 18 s

```
signatures   Verified the signature and incidence bounds, four K13 witnesses, and 8469 catalogue
             pentagons.  Verified 562 marked 14-arm pentagons on 381 parents.  Verified every
             sector split below 18 on both rows.
endpoints    (7,11) and (10,8): unresolved branches 0, on both rows.
interior     Verified 121 certificates.  U<=8 and V<=10 jointly impossible on both rows;
             (8,10) excluded on both.
balanced     (9,9) excluded on both; 96 local certificates and both parent gluing certificates
             replayed.  "Together with the preceding exclusions, both rows require at least 19
             spokes."
```

Environment: `python3 -m venv .venv` plus the vendored `wheels/` (python-sat 1.9.dev22), no network.
Four workers. So the claim `U+V >= 19` on rows `076eafbfe47e` and `4629be2de806` is reproducible
**without any of the shipped certificates**, at 18 minutes for both rows.

## What the census says about generalising it

Computed here with the bundle's own `pentagons(case)` and `row_info(case)` over all 381 rows of the
profile:

| quantity | value |
| --- | ---: |
| rows with a marked pentagon in arm 2 **and** one in arm 3 | 169 |
| of those, rows where the construction applies (`family.arm = 1`) | **159** |
| core pin counts among the 159 | **215 (134 rows), 225 (25 rows)** |
| rows needing their own board argument after pin containment | **134** |
| difference between the two published rows | 10 |

**Correction (m1 of swarm `smwtqk6ku`, verified here).** The first version of this file counted 169
rows and 185 core pins throughout. Both were contaminated by **ten rows with `family.arm = 0`**,
where the marked colour is the pentagon's own colour and `U,V` would count the wrong thing; those
ten are the only ones with 185 pins. On the 159 that carry the argument the counts are 215 and 225.
The 165 distinct pin sets and median difference 84 were computed over all 169 and stand as stated.

All 169 share the same shape — pentagons at exactly `{30..34}` and `{44..48}`, a 26-vertex core
(`{0} + A + both pentagons`), 185 pinned core edges — but the pin patterns differ substantially. The
two published rows are the **closest pair in the family** (10 edges apart), which is why the pilot
looked tractable.

Consequences:

- certificates **do not transfer** between rows; generalisation is per-row certification;
- **isomorphism does not help**: all 159 relevant rows are pairwise non-isomorphic. Verified here by
  9,211 VF2 tests on the coloured 26-vertex cores (vertex types plus negative pins), 0 isomorphic
  pairs — a fourth program agreeing with m1's three. Classes: 163 over the 169, i.e. a 3.6 % saving
  and none on a relevant row;
- the one real saving is **pin containment**: 25 of the 159 sit on a 215-pin board, so 134 board
  arguments cover all 159 (15.7 %). Verified here, difference exactly 10 literals in every pair;
- measured cost: 18 min 18 s for two rows, so **about 20 h wall for the 134 boards** at the same
  parallelism (the earlier ~60 CPU-hour and ~26 h figures are superseded);
- the driver is hard-wired (`CASES = (ps.SOURCE, ps.SECOND)` in `tools/nine_spokes.py`, and
  `validate()` refuses any other case), so extending it is a code change, not a rerun.

## What is not established here

- Nothing about whether `U+V >= 19` actually shrinks a row's search. The bundle evidences a 60.4 %
  CPU saving only on the *pilot branches* with the signature ordering, not on a full row.
- Nothing about `U+V = 19` being unattainable; the notes say that is open, and if it fails the bound
  becomes 20 rather than 19.
- The claim is on two rows of 381 in this profile, which is 381 of the 11,585 wall rows. Neither row
  is closed, and `R_4(3)` remains in `[51,62]`.
