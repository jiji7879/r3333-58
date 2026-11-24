# The high-spoke branch on row 4629: verified, and it closes nothing

Bundle: `K58_high_branch_solver_and_notes.zip` (8.6 MiB), unpacked at `.scratch/hb/`. It ships the
**CNFs** and the manifest but not the proofs, so every certificate was regenerated here.

## Verified by regeneration

```
55 certificates, each CNF rebuilt from cnf/<name>.cnf.xz and required to match the manifest's
SHA-256 before solving, then solved and checked with drat-trim:
  55 of 55 regenerated, 0 failures, 12 min 22 s
```

## The structural claim, checked independently

For `p` in the marked pentagons, `F(p) = N_1(p) ∩ A`. Since `A` omits colour 0 internally and colour
1 is impossible inside `F(p)`, `|F(p)| <= 5`. The five sites of `A ∩ M` carry no red edge to `p`, so
`F(p)` lies in the remaining ten. **The bundle asserts exactly three 5-sets can occur; the judge's own
enumeration finds exactly those three and no others:**

```
A cap M = [1, 4, 5, 7, 14]        F = [2, 3, 6, 8, 9, 10, 11, 12, 13, 15]
independent 5-subsets of F:  3
   (2, 3, 6, 8, 13)   (6, 9, 12, 13, 15)   (8, 10, 11, 13, 15)
equals the bundle table: True
```

## What the bundle establishes

- **Sixfold repetition is impossible**, with caps 5, 5 and 6 per set — and the `F_2` cap sharpened to
  five by the three-point rule. Six copies would already contribute 30 spokes, so a counterexample
  would automatically be in the high branch.
- **A sharp three-point pentagon lemma**: for any three points of a two-colour pentagon, at most two
  outside vertices avoid the third colour to all three. In either 14-arm **at least seven of the nine
  ordinary vertices** send red to a specified triple, and an explicit `K_14` attains seven. The proof
  is four lines of hand argument plus an eight-vertex DRAT check.
- **The numerical maximum `U = V = 25`**: all three sets must occur and `F_2` at least twice. The
  27-vertex projection admits 3,890 ordered assignments of the sets, 3,631 after the count and
  placement bounds, all excluded by grouped certificates.
- **The `(13,14)` repair bound**: holding the 909 present edges of the partial `K_45` fixed leaves 41
  of the 81 inter-arm edges with no legal colour; completing those two arms requires changing **at
  least 25 old edges and at least 9 ordinary vertices**. Both bounds are attained in the covering
  problem; no recolouring achieving either is known.

## What it does not do

**The branch `U+V >= 20` remains OPEN.** The whole first-pass formula hit a 2,200,000-conflict cap,
the re-rooted formula 1,800,000, and the final first-pass and retry formulas 1,200,000 each; all six
degree distributions inside the marked vertex's arm also stayed open. The results are **necessary
conditions** for a completion, not a refutation, and the bundle says so.
