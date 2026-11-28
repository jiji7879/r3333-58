# FKR early attachment-cover feasibility: checked stop

**Status: bounded negative result, independently replayed. No attachment cover or
Ramsey-bound conclusion.** Member m4 ended without submitting a formal swarm
report; the coordinator has verified its final artifact rather than treating a
missing submission as acceptance.

## Counts

| object | checked weak-isomorphism count |
|---|---:|
| order-16 marked colourings (FKR reference) | **533** |
| order-16 overlaps (FKR reference) | **724** |
| order-15 marked colourings | **3,402** |
| order-15 overlaps | **31,283** |

The CAT58-relevant family with attachment size $k\ge3$ contains
**714** 16/16 overlap types and **30,998** 15/15 overlap types:
**31,712 configurations**. This exceeds the declared early-census engineering
cutoff of 10,000. The proposed continuation therefore stops; no recursive
pullback, wall encoding, or cover construction follows.

This is not a proof that no more compact attachment cover could exist. It is
failure of this experiment's declared continuation condition. The small
symmetry groups of the deleted order-15 templates are the measured reason for
the explosion.

## What was checked

1. A scratch replay of `fkr/run_census.py` completed in **727.68 s** (727.52
   user CPU; 252,844 kB maximum RSS; empty stderr). Every census field matches
   the member's receipt except for timing strings and corrected provenance.
   All 196,604 stored subset transport witnesses pass, as do the two-layer
   weak-isomorphism computations and their small-order brute-force controls.
   See `replay-verification.json`, `fkr/run_census.json` and
   `full-replay.time`.
2. A separately written verifier, `check_subset_orbits.py`, does not import the
   member's orbit enumerator. It re-derives weak groups, direct subset orbits,
   representative transports and Burnside counts for all four templates. It
   passed in **83.70 s**, independently reproducing every per-order subset
   count and checking all 196,604 subsets under both named and weak groups.
   See `subset-orbits.json` and `subset-check.log`.
3. The original receipt's provenance named an obsolete `census_k58.py` rather
   than the executed driver. The integrated driver records itself. This is the
   only semantic-source edit besides adapting the scratch path; the overlap
   enumerator is byte-identical. Source hashes and the precise comparison are
   in `replay-verification.json`.

The member's original receipt is retained at `fkr/member-run_census.json`, and
its original report at `REPORT.md`, with `receipt.json` as its summary. Those
remain separately identified from the coordinator's replay. The `exploratory/`
reorganised folder retains only the warning note describing the rejected
reductions, not superseded programs.

## Trust and scope

The order-15 census relies on the external classification of the two good
$K_{15}$ colourings as deletions of the two $K_{16}$ templates. The two-$K_{16}$
classification is likewise an input. Both are stated premises here, not
re-proved by this enumerator. CAT58 and its bound are formalised elsewhere in
the project; no global use of the theorem is made by the stop arithmetic.

The checked 533/724 figures are Tables 5 and 6 only. The old 2004 programs and
later filters/counts are not independently validated here. This is not a proof
of physical $K_{58}$ incidence structure, an SAT refutation, or `ChainReady`.
The accepted interval remains $51\le R_4(3)\le62$, with no claim of 58.

## Reproduction

The independent subset check is quick:

```sh
python3 -B results/next-directions-2026-11-28/attachment/check_subset_orbits.py
```

The full replay is an intentional single-worker, roughly 12-minute computation:

```sh
cd results/next-directions-2026-11-28/attachment/fkr
python3 -B run_census.py > run_census.json
```

It uses only the pinned repository Python and the frozen template matrix. It
does not call a SAT solver, read a wall ledger, use the network, or install
anything. No CNFs, solver proofs, archives or compiled outputs are committed.
