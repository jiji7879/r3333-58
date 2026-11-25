# JOB A — do the eligibility certificates of the 40.8% case reduction survive?

**Answer: yes. Route taken: the SAT route (build the tightness instance myself and
refute it), not the handoff's weighted certificates. 0 counterexamples, nothing
sampled, 0 unverified outcomes.**

* All **161 stored partitions** (63 for pole 0, 48 for pole 2, 50 for pole 4) of
  `results/cover.json` are eligible: every subset of every part is tight.
* Beyond that, **every position set that the certificate table calls tight at size
  4…8** — the table's whole useful domain — is genuinely tight, for all three
  poles: 5980 masks.
* Total: **18 595 UNSAT instances over 7087 distinct position sets**, each
  certified by a DRAT proof that `drat-trim` accepts (`s VERIFIED`, exit 0) on the
  exact CNF, and each confirmed by a second solver (Kissat). 93.7 M conflicts.

Object of the check: the handoff at `work/k54cut` (read only). Its parts have sizes
5…8, so subsets of size 0…8 are all that `all_cuts` can ever need; sizes 9…13 are
*never* claimed tight by the certificate table (their bounds are 12,14,17,22,30,35),
so no eligible partition can contain a part of size ≥ 9. Nothing was decompressed
and nothing in the archive was written; `python src/cut_cover.py` in the archive
still passes and still prints the published totals.

## 1. The statement being decided

For one H42 side (14 vertices: pole `a` + 13 nonpoles) and `P` a set of nonpoles:

    capacity(P) = #{ outsiders w : the whole c-support S(w) of w lies inside P }
    P is TIGHT  <=>  capacity(P) <= |P|.

Refutation form used: the instance with `k = |P|+1` outsiders, each of which must
have its whole c-support inside `P`, must be UNSAT. (UNSAT at `k` implies UNSAT at
every larger `k`, since a larger family contains a `k`-subfamily.)

## 2. The CNF (`tightlib.py`, independent implementation; no code from the handoff's src)

* Template vertices `0..13` carry the 3-colouring H42 (colours 0,1,2; `-1` = loop);
  colour `3` is the special colour `c`.
* One exactly-one-of-{0,1,2,3} group per edge that touches an outsider: every spoke
  `(w,v)`, and every outsider–outsider edge.
* Spokes to template vertices outside `P` are restricted to `{0,1,2}` — that is the
  hypothesis “S(w) inside P”. The pole is never in `P`, so its spokes are ordinary.
  That exclusion is **forced, not assumed**: a `c`-spoke `w—a` to the pole would
  make the triangle `(w,a,x)` monochromatic in `c` for any `x` in `T(w)`, and every
  edge from the pole `a` to the opposite template has colour `c` (the handoff's own
  step: “Neither can include a pole”). Dropping the exclusion makes every instance
  SAT, so it is exactly the hypothesis that carries the count.
* One “no monochromatic triangle” clause per (triple, colour) for every triple
  containing an outsider: with one template edge (colour `H42[u][v]`), with two
  outsiders, and with three outsiders. Triples inside the template are fixed by H42.
* Variant **C** adds “each outsider has at least one `c`-spoke”: sound (S(w) ≠ ∅ in
  the real K54) and a strengthening. It is run on all 4082 masks of size 5…8 and on
  the 2892 stored-subset masks; it never changed a verdict.
* Instances: at most 23 vertices, 648 variables, 3936 clauses.

## 3. Calibration of the encoding against facts computed independently by the handoff

| check | handoff's independent result | this encoding |
|---|---|---|
| capacity(∅) | 0 (no empty c-support) | k=1 UNSAT |
| capacity(singleton) | 1 | k=2 UNSAT |
| capacity(2-set) | 2 | k=3 UNSAT |
| capacity(3-set) | 3 | k=4 UNSAT |
| capacity(4-set), pole-0 nonpoles | 4, except 12 exceptions at 5 (`results/saturated4.json`, `src/cap.cpp`) | k=5: exactly 8 of 715 SAT, their canonical forms are exactly the **2 orbits** of the 12 exceptions; the other 707 UNSAT |

The last row is the sharp one: the encoder reproduces `cap.cpp`'s table exactly —
including the 12 exceptions — on a completely different code path.

## 4. Results — the stored partitions (this is the eligibility claim)

`s5-8` = the gap sizes, variants A and C; `s0-4` = the sizes the requester had
already verified, re-done here with our own instances (variant A).

| pole | partitions | fully eligible | non-tight subsets | masks 5/6/7/8 | instances 5–8 | masks 0/1/2/3/4 | instances 0–4 |
|---|---|---|---|---|---|---|---|
| 0 | 63 | **63** | **0** | 584 / 328 / 87 / 8 | 2014 | 1 / 13 / 78 / 275 / 549 | 916 |
| 2 | 48 | **48** | **0** | 638 / 358 / 92 / 8 | 2192 | 1 / 13 / 78 / 280 / 582 | 954 |
| 4 | 50 | **50** | **0** | 489 / 241 / 55 / 4 | 1578 | 1 / 13 / 78 / 276 / 511 | 879 |
| total | 161 | **161** | **0** | 2892 masks | 5784 | 2749 masks | 2749 |

Counted with multiplicity over the parts (a position set shared by several parts is
tested once per distinct set): pole 0 needs 1941/664/119/8 subsets of sizes 5/6/7/8,
pole 2 1536/544/104/8, pole 4 1470/480/78/4. `verify_eligibility.py` walks all
subsets of all 161 partitions and finds no missing verdict and no non-tight set.

## 5. Results — the certificate table's whole tight-claimed domain

The table makes two kinds of claim: tight (bound ≤ |s|), and, for sizes ≥ 9, only
non-tight bounds. Every set that the table calls tight in sizes 4…8 — for all three
poles, whether or not it lies in a stored partition — was tested:

| pole | size 4 | size 5 | size 6 | size 7 | size 8 | masks |
|---|---|---|---|---|---|---|
| 0 | 625 | 790 | 450 | 109 | 10 | 1984 |
| 2 | 639 | 838 | 472 | 100 | 8 | 2057 |
| 4 | 634 | 804 | 418 | 78 | 5 | 1939 |
| total | 1898 | 2432 | 1340 | 287 | 23 | **5980** |

All 5980 are UNSAT at k=|P|+1 (10 062 instances including variant C). The size-4
exceptions are excluded by the handoff's own convention; the stored parts contain
no exception (and all 3350 of pole 0's part-level 4-subsets were tested anyway).
So the table's tightness claims are correct everywhere they can influence an
eligibility computation, which is stronger than “the 161 stored partitions are fine”.

## 6. The tests are sharp, not vacuous

For **all 8872 tested masks** (5980 tight-claimed + the stored-subset masks) the
instance with only `k=|P|` outsiders is **SAT**, and every model was re-checked
**semantically** from the definitions rather than from the clause list: exactly one
colour per edge, no monochromatic triangle in any triple containing an outsider,
every outsider's c-support inside `P`. **0 semantic failures**
(`results/sharpness-all.json`, `results/sharpness-tightclaimed.json`). Hence
`capacity(P) = |P|` **exactly** on every mask, and the certificate value
`bound = |P|` (checked: `cert_bound == |P|` for every mask, using the handoff's own
group from `data/orbits.json`, which equals my 8-element group) is attained, not
merely an upper bound.

## 7. Evidence and how to replay it

* `tightlib.py` — encoder; automorphism group of H42 (order 8) and canonical forms.
* `run_tight.py POLE [--sizes 5,6,7,8] [--masks f.json] [--out d] [--jobs N] [--variants AC]`
  — the driver: regenerates every instance deterministically, solves with CaDiCaL
  3.0.1, writes the DRAT, re-solves with Kissat 4.0.4, checks the DRAT with
  `build/drat-trim`.
* `verify_eligibility.py` — maps verdicts back onto the 161 stored partitions,
  subset by subset; writes `results/eligibility.json`.
* `recheck.py` — second-party replay: regenerate the CNF from `(pole, mask, variant)`,
  compare its sha256 with the recorded one and with the stored file, compare the
  stored DRAT's sha256, re-run `drat-trim` and Kissat. 129 instances (every instance
  slower than 1 s plus 25 random per group): **0 failures**.
* `sharpness.py` — the k=|P| sharpness and semantic re-check (`--all`).
* `results/manifest.tsv` — one row per instance: pole, batch, size, mask, variant,
  variables, clauses, certificate bound, **sha256 of the CNF**, **sha256 of the
  DRAT**, drat-trim verdict, Kissat verdict, seconds, conflicts. Manifest sha256
  `eebc508e39e7e3cdb960e92c3ab2ee274affd953531524ef2675e03b103cd3bf`.
* `results/pole-{0,2,4}/{,sub4/,all4/,all578/}` — the exact gzipped CNF and DRAT of
  every instance (`s<size>-<mask>-<variant>.{cnf,drat}.gz`), plus `rows.jsonl`.
* Inputs hashed: `data/h42.json` sha256 `eb9c7864…`, `results/cover.json`
  sha256 `32e95d8a…`, `data/local_bounds.json.gz` sha256 `8985b552…` (files of
  `work/k54cut`, unmodified).
* Cost: 18595 instances, 93.7 M conflicts, slowest 10.1 s, median 0.031 s,
  p90 0.165 s; wall clock ≈ 50 min on ≤3 cores, peak RSS < 1 GB.
  On disk: 1.9 GB (0.15 GB CNFs, 1.74 GB DRATs). Any file can be deleted and
  rebuilt from its manifest row; nothing else depends on them.

Redo from scratch (the archive is only read):

    python3 run_tight.py 0 --out results/pole-0 --jobs 3        # stored subsets 5..8
    python3 run_tight.py 2 --out results/pole-2 --jobs 3
    python3 run_tight.py 4 --out results/pole-4 --jobs 3
    python3 run_tight.py 0 --masks results/masks/tightclaimed-0-all578.json --out results/pole-0/all578 --variants AC
    ...  (the other batches; the manifest lists every instance)
    python3 verify_eligibility.py
    python3 recheck.py --random 25
    python3 sharpness.py --all
    python3 sharpness.py --all --dirs results/pole-0/all4,...,results/pole-4/all578

## 8. Scope, and what this does not say

* Verified: the tightness inputs of the reduction, everywhere they matter — all
  161 stored partitions and the certificate table's whole tight-claimed domain.
  **The eligibility claim survives intact; no counterexample exists in the tested
  domain.**
* Not touched here: the orbit/ledger accounting of the reduction (separately
  audited clean by m3), the crossing-cut theorem's counting half (m2's
  packing-bound direction), the 8-seed restriction (m3), the Job B count models
  (m4/m5/m6).
* This is a statement about position sets and their capacities (claim class (a)).
  It says nothing about any individual count vector, any board, or seed 12 as a
  whole — nothing here excludes a board or a seed.
* Interpretation caveat, for completeness: the instances decide the A-side
  statement, which is what the theorem needs (“Tightness of the parts gives
  |M| ≤ |B1|+|B2|”). A SAT answer would have needed care, because a real colouring
  also constrains the outsiders' mutual edge colours from the B side, so a pure
  A-side SAT model need not be realizable. Every answer here is UNSAT after a DRAT
  check, so no such caveat applies to any conclusion above.
