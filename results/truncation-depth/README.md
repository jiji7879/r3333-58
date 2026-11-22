# Truncation depth of the known objects: exactly 3, and every obstruction is one shape

Member m10 of swarm `smwrmwgf7`, direction d11, accepted 2026-11-22. I re-ran
`score.py`, `depth.py --kmax 3`, `verify_drat.sh` and `extremal2.py` before
acceptance; the numbers below are the ones those runs print.

## The local object and the depth

For a set `S` of slots of a pair-level witness, a *local object* is the witness's
words on `S` plus a colouring of the pairs inside `S` with (P1) the arm colour
never used inside its own arm, (P2) `colour(x,y) = f` requiring
`M_f(x) ∩ M_f(y) = ∅`, and (X) no monochromatic triangle. Every genuine object
restricts to a local object on every subset of its slots.

`depth.py` searches subsets in increasing size. Result for every pair-level and
two-arm witness in the record: **no dead pair, and truncation depth exactly 3** —
`pair58_Tminus` 0 / 514, `p58` 0 / 524, `p58_cc` 0 / 459, its own plain model
0 / 456, and `14+14` 50, `14+13` 44, `14+13_cap` 55, `14+12` 40, `14+12_cap` 52.

**Lemma 1 (the shape of every obstruction).** With three vertices, if any of the
three admissible-colour lists has two elements one can always choose a
non-constant triple; so a triple is infeasible **iff all three lists are the same
singleton `{c}`**. Verified on all 514 and all 524 obstructions
(`nogoods_pair58.json`, `nogoods_p58.json`), and it is what the campaign had only
exhibited one instance of (`WALL` §29).

**Reconciliation with `results/local-obstruction/`.** m7 counted within arms and
reported 119 for `pair58_Tminus`; m10 counts all `C(42,3) = 11,480` triples and
reports 514. Both are right: of the 514, **119 are within-arm and 395 cross-arm**
(computed here from m10's own `depth.feasible`). Two independently written
checkers, one object.

## Every 14-slot arm needs a generic word — but not for the recorded reason

`WALL` §(line 1151) argues "three copies of one word force its empty colour, so
copies <= 2 per arm, and an all-extremal arm cannot fill 14 slots". The middle
step is a non sequitur: seven distinct extremal words twice each is fourteen
slots, and `extremal.py` counts **2,244,026** all-extremal size-14 arms that pass
pairwise admissibility. The conclusion is nevertheless true, but it needs the
triple condition: with Lemma 1 imposed the count is **0 for every arm colour**
(`extremal2.py`, 3,843 / 3,783 / 3,093 nodes). Three copies of one extremal word
already violate Lemma 1, so the multiplicity bound is a consequence, not a
hypothesis. Record corrected.

## Certificates, and their exact scope

* `enc.py --pin-design log/design.blocks` plus the pair families: UNSAT, kissat
  7,839 conflicts, DRAT `s VERIFIED` by drat-trim, core 3,153 of 99,330 clauses
  with 82 RAT lemmas. Scope: **the design pin is not a consequence of the
  branch**, so this says that this sharp design does not lift to the pair level,
  not that the branch is impossible.
* `enc.py --pin pair58_Tminus.wit` with the sixth arm lemma: UNSAT at 0 conflicts,
  `s VERIFIED` — a certificate that those 42 words violate the lemma, which the
  record had as a measurement (cliques 9, 9, 10 against the bound 5).
* the depth-3 word assignment `t3v2_pin`: UNSAT at 0 conflicts, `s VERIFIED`.
* controls: the plain pair level built here is SAT in 12 s (kissat) / 6.4 s
  (pysat), so the encoder is not over-constrained; the strengthened objects are
  UNKNOWN at 300 s and 620 s and are reported as measurements only.

## A hazard worth knowing

`artifacts/k15_link_Tminus_m5.col` and `artifacts/k15_template_Tminus_aut2_m4.col`
are the same template under different labelings. Pinning a witness written against
one into an encoder built on the other gives a **1-conflict, 0-decision UNSAT in
0.05 s** — the `ERRATA` signature. Mixing the two artefacts is the way to generate
a fake refutation here.

Rerun: `bash verify_drat.sh` (needs `.scratch/satcheck/bin/{kissat,drat-trim}` and
the CNFs `make_all.sh` builds), `python3 depth.py <wit> --kmax 3`,
`python3 extremal2.py --arm {1,2,3}`.
