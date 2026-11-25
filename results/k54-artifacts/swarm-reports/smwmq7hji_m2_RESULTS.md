# local-15 cut audit: what the archive's core certifies, and a new certified cut

Member m2, direction d8. All paths below are relative to
`.ultramath/smwmq7hji/m2/`. Archive is read-only and only imported.

## 1. Reproduction of the archived evidence

    cd <archive>
    python3 pilot/lift_counts.py local-15 pilot/runs/local-15-cadical/counts.json 2 out.cnf.gz

Re-running that gives 4654 variables, 63668 clauses and sha256
`e499e127a1ec5a07bd0c2070539fafbbed3be95003ff3c963c8a8dc36ec1e36f`, exactly the
archived pair-two lift. CaDiCaL 3.0.1 refutes it; DRAT sha256
`51322e66947adeea90e0fa326ebc4b3834078aa6a4ff51af4ec1f04f045eb5a1`, matching the
archive. `build/drat-trim <cnf> <proof> -c core.cnf` prints `s VERIFIED` and yields
the 67-clause core (2 lemmas, 89 resolution steps) whose variables mention only
H42 side-1 vertices 14,16,20,24,25,26, outsiders 37,40,49 and matching variables
4632,4635,4650 — the archive's KEY OBSERVATION.

Files: `work/l15/two.cnf`, `work/l15/two.drat`, `work/l15/two.core.cnf`;
script `work/l15_main.py`.

## 2. The archive's reduced instance does not certify a left-column cut

`ours/cegar-local-15/it0000-red.cnf` (and the same construction rebuilt here) pins
**both** signatures of the three witnesses: left signature 0 **and** right
signature 32. The right signature is not a variable of the left column, so this
instance is not a relaxation of "one outsider in each of the three left columns".

Evidence (`work/l15_decide.py`):

* 31 vertices (28 core + 3 witnesses), left **and** right pins: UNSAT, drat-trim
  VERIFIED, 64-clause core.
* 31 vertices, left pins only: **SAT** in 0.0 s, and the model is a genuine
  triangle-free 4-colouring of all C(31,3) triangles (all four colours, board pins
  respected). The three witnesses have right signatures 2, 32, 32.
* The 54-vertex instance with the three left pins only (all triangles, the 23 other
  outsiders free and lex-sorted) is still UNKNOWN after 3M conflicts / 277 s — it is
  the hard direct-graph regime. So no sub-instance certificate exists for the
  left-column cut, and none is claimed.

Useful lemma that does hold: if the three columns have **pairwise distinct
rectangles** then any graph realizing a count vector with all three counts >= 1 has
three **distinct** witnesses, because a count vector assigns each outsider to
exactly one rectangle. So the "one outsider witnesses two cut literals" hazard
cannot arise for such triples; only the free opposite-side signature is a real gap.

## 3. The correct one-side cut, rebuilt from the board spec

The core's strong pins are the side-1 signature-32 units (the side-0 signature-0
pins are only "not all anchors" disjunctions). Dropping the left pins keeps the
instance UNSAT, so the cut is over the **side-1** columns.

`work/l15_cut_side1.py` builds, from `checkpoints/counted/src/board.py` plus pins,
the full 54-vertex board graph (all triangles) with witnesses 28,29,30 pinned
one-side to (rect, side 1, sig 32), rectangle c-support enforced on both sides,
other 23 outsiders free:

* 4608 variables, 73186 clauses, sha256
  `34b54d13abae0422190e0b638d1cdd1610fcceb72dfe30e5e47fcd3bc9a8d72e`
* CaDiCaL: UNSAT in 0.02 s; DRAT `9047806c6225990f16227bf40b645aa32701800e7d6d6be2907122a8c14e3e81`;
  drat-trim `s VERIFIED`, 64-clause core on vertices {14,16,20,24,25,26,28,29,30}.
* Cut: `-u[354,1] or -u[323,1] or -u[70,1]` = `[-1670,-1482,-451]`
  (columns 354=(3256,2128),1,32; 323=(7416,2048),1,32; 70=(11448,80),1,32).
  This agrees with m5's independently mined cut.

## 4. The whole signature family, and which cuts are redundant

`work/side1_family.py`, `work/summarize_cuts.py`. Achievable side-1 signatures
(`projected_words`) are {2,16,32} for rectangles a,c and {32} for b, so there are
9 triples. Seven are UNSAT with drat-trim `s VERIFIED`; (2,32,32) and (32,32,2) are
UNKNOWN at 200k conflicts and are **not** claimed.

For five of the seven the outer count CNF **plus the three occupancy units is itself
UNSAT** (DRAT verified): those cuts are already implied by counting and add nothing
to the outer model. Only two strengthen it:

| columns | clause | CNF sha256 | core | sampled killed-vector lower bound |
| --- | --- | --- | --- | --- |
| 354,323,70 (m5) | -u[354,1] -u[323,1] -u[70,1] | `34b54d13abae0422...` | 64 | >= 372 |
| **354,323,69 (new)** | -u[354,1] -u[323,1] -u[69,1] | `ce68d2ac8d0e0371...` | 107 | **>= 491** |

The lower bounds come from 25 s of model enumeration of `outer + units` with no
other cuts applied; they are lower bounds on distinct count vectors, not exact
counts, and neither cut is claimed to contain the other.

## 5. What is verified and what is not

Verified here, with exact hashes and replayed DRAT: section 1, section 2's
31-vertex instances (UNSAT one and SAT one), section 3, and every entry of section
4's table including the five redundancy proofs.

Not done / not claimed: no board is closed; the soundness of the outer count CNF
itself is taken from the archive (m6/d9's direction); no census; no claim about the
two UNKNOWN signature triples; the Lean kernel check of the core (direction d8's
original plan) is **not finished** — `work/refute.py` generates a resolution
refutation but currently returns a non-empty final clause, so nothing Lean-checked
is claimed.

## Reproduce

    python3 work/l15_main.py          # sections 1-2 (archive reproduction)
    python3 work/l15_decide.py        # section 2 SAT/UNSAT pair
    python3 work/l15_cut_side1.py     # section 3 CNF
    python3 work/side1_family.py      # section 4 (9 triples)
    python3 work/summarize_cuts.py && python3 work/redundancy.py
