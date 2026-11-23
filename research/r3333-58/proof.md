# R₄(3) ≤ 58 — status

**Status: NOT YET.** The goal is not proved. `R₄(3) ∈ [51,62]` exactly as before; 31,751 of the
113,179 frozen rows are OPEN and all 381 rows of the `(15,14,14,14)` profile are OPEN. No case has
been closed and no bound has moved. What follows is what *is* settled, what is conditional, and
what was checked by whom.

Gate: `python3 .skill/siege-workflow/scripts/ledger.py gate research/r3333-58` prints

```
NOT YET: the goal #1 is open
```

## Settled, with the argument

| # | statement | where |
|---|---|---|
| 2 | the frozen cover is complete: every balanced root of a triangle-free 4-colouring of K₅₈ lies in one of the 113,179 rows | `K58.Replay.frozenCover`; replay rebuilt 1,588 modules, exit 0 |
| 3 | 367 declarations in `lean/K58/Check.lean`, axioms inside `[propext, Classical.choice, Quot.sound]`, no `sorry`, no `native_decide` | `bash lean/build.sh` |
| 4 | under reciprocity (R), 363 of the 381 rows fall; a survivor needs a non-reciprocal edge | `lean/K58/ArmSender.lean` |
| 5 | no board of any of the 138 designs carries 4 C-vertices and 4 D-vertices (276 DRAT, 276 SAT controls) | `results/wall-run/` |
| 6 | conditional on the uniform child, 44 multiplicity profiles survive and cannot pin an arm | `lean/K58/{Multiplicity,DesignIncidence,ProfilesIncidence}.lean` |
| 7 | the third-colour matching law is a theorem of the instance, not a constraint: ≥ 9 fives | `lean/K58/{Weighted,CountLaw}.lean` |
| 8 | types 27, 28, 73, 157, 193, 261 are not excluded as arms (24 witnesses) | `lean/K58/` witnesses |
| 10 | the exact 42-slot instance is `31746/152078` | `ladder.py --sizes 14,14,14 --total 14 --xt --tightcov` |
| 11 | 42-row sample of the wall: 0 of 42 closed at 12 s / 400k conflicts | `results/wall-sample/README.md` |
| 12 | 51 is Chung 1973, 62 is Fettes–Kramer–Radziszowski 2004 (Zbl 0258.05111, Zbl 1075.05057) | `results/literature-r3333-2026-11-23.md` |

## Conditional or open

- **#9, the cross-arm test, is OPEN, not proved.** A type-16 arm forcing a singleton in a type-36
  sibling is a package claim whose 6,273 rectangle + 240 table + 7 missing-neighbour proofs were
  never supplied; it is conditional on `K58.Classified 15` and on the six-set classification. It
  covers 4 of type 16's 21 placements, leaving 1,344 cases. Swarm `smwsyh6tk` is re-deriving the
  192 cases independently.
- **#6 is conditional on the uniform child.** It says nothing about a row.
- **The 113,179-UNSAT premise is an explicit hypothesis**, never a fact: it is the cover's
  conclusion, not an input.
- **The ≤ 60 preprint (arXiv:2610.36648v2) is not used.** Unrefereed; its Lean reduction and its
  two-solver refutations were not read or reproduced here.

## Checks run, and checks skipped

- Run in this session: the Lean build (`bash lean/build.sh`, job `jmwt370gt`), the literature
  lookups (DS1 rev. #18 p. 56, zbMATH, arXiv abstract page, GAP order counts 51–58), and the
  four one-hour solver records described below.
- **Skipped:** no row of the cover was refuted; no CNF was rebuilt for a new case; the six-distinct
  join layer (24,844 + 13,082,964 joins, 9,226 sender refutations) was **not** verified by anyone
  in this session; the two-arm proof archive is still missing, so m6's audit of its seven
  certificates remains unconfirmed; no LRAT checker ran.

## The four one-hour records

See `results/wall-hour-2026-11-23/README.md` for the numbers. In one line: an hour and 200 M
conflicts per case does not close a wall row, and the certificate stream alone runs to several GB
per case.

## Looked up

`results/literature-r3333-2026-11-23.md`: DS1 rev. #18 (24 Apr 2026) p. 56 for both bounds and for
the typo in Chung's printed matrix (a triangle `(31,7,28)` in colour 1); zbMATH records for Chung
(Zbl 0258.05111) and Fettes–Kramer–Radziszowski (Zbl 1075.05057); arXiv:2610.36648 v1→v2 metadata;
GAP 4.14.0 / smallgrp 1.5.4 counts for orders 51–58.
