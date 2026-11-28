# P1: native LRAT versus DRAT certification, on already closed cases

**Direction:** proof/certificate engineering (P1 of
`results/literature-next-2026-11-28/proof-workflows.md`).
**Status of the underlying mathematics:** unchanged. Accepted interval is still
$51\le R_4(3)\le 62$; nothing here closes a wall profile, moves a cube from OPEN
to UNSAT, or touches `ChainReady`, the frozen ledger, `run`/`finalise`, or any
production encoding default. Every claim below is about four **already closed**
CNFs and their exact bytes.

**What was missing before this run and exists now:** an *installed* independent
LRAT replay. The earlier slip (`checks/native-lrat-h8.json`) says
`"independent_lrat_replay": "NOT RUN: no local LRAT checker was installed"`.
It has now been built from pinned public source, self-tested, and run on every
case, together with a second checker implementation written from scratch here.

## 1. Pins

| object | identity |
|---|---|
| CaDiCaL | `tools/color-resolved-wallcc/bin/cadical-2.1.2`, sha256 `a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b`, reports `2.1.2` |
| drat-trim (incumbent) | `tools/color-resolved-wallcc/bin/drat-trim`, sha256 `48891f3f9dfccbbebfc6a21fa9e6daa6b674900a3f65b16a0b0f7f21d8a03bce` |
| lrat-trim (**new**) | source commit `423194927df747528d5b7364806b5b77b2660c12` (the commit the memo inspected), source tarball sha256 `e71af67672133ed0c6a0885fc2b1959682430fdd5fa8456ea692505d18f6cdd3`, built locally with `gcc -Wall -O3 -DNDEBUG`, binary sha256 `f1eb1a4486274c35f4accf7bc13b595cfdbcf2d7c9aa6b46fb281f19d0d52895`, reports `0.2.1-rc3` |
| second checker (**new**) | [`lrat_rup_check.py`](lrat_rup_check.py), sha256 `f0eb3f5d419f23b9843fcc5a5aba8f5b512db2a4dbfd8a9b469d7e11df4771b2`, RUP-only LRAT, written here, *unverified code* |
| compiler | gcc 16.2.0 (conda-forge), python 3.12.14 |

The checker was trusted only after its own suite passed: `parse` 90 tests,
`regr` 1, `trim` 39, `fail` 9, `check` 20, `usage` 69, all exit 0. The `fail`
suite is the point: it is known to reject before it is asked to accept.

## 2. Routes compared, on the same exact input and seed

For every case the CNF is copied and its sha256 asserted against the recorded
query hash, and both solver arms run CaDiCaL 2.1.2 with `--seed=0 -c 50000 -t 20`
(the DRAT arm adds `--binary=true`, the LRAT arm `--lrat --binary=true`).

* **A (incumbent)** solve → DRAT → `drat-trim <cnf> <proof> -c`.
* **A′ (the step native LRAT is supposed to remove)** the *same* DRAT →
  `drat-trim <cnf> <proof> -L <lrat>` elaboration → `lrat-trim` strict check;
  then the trimmed variant of that elaborated proof.
* **B (native LRAT)** solve → LRAT → `lrat-trim <cnf> <proof> <trimmed>` →
  three replays of the trimmed artifact: `lrat-trim` backward, `lrat-trim -S`
  forward, and the second checker. `lrat-trim --rup` additionally certifies that
  the proof contains **no RAT step at all**.

Fail-closed: a hash mismatch, a solver exit other than 20, a checker without its
exact success line, a differing search trajectory between the two solver arms, or
a negative control that is not rejected aborts the run. `10` (SAT), `0` (UNKNOWN)
and timeouts are never recorded as UNSAT.

## 3. Results

CPU is process CPU (user+sys) from `/usr/bin/time -v`; RSS is that tool's peak
`Maximum resident set size` for the named stage; bytes are retained certificate
bytes on disk.

| case (input) | route | solve CPU | certify/check CPU | **total CPU** | retained bytes | checker peak RSS |
|---|---|---:|---:|---:|---:|---:|
| **H8** K58 0404 child, `p cnf 19425 184188`, sha `e8cc9784…` | A | 1.88 | 1.07 (drat-trim) | **2.95** | 9,529,642 | 84 MB |
| | A′ | 1.88 | 1.18 elaborate + 0.07 strict | **3.13** | 15,358,198 | 84 MB |
| | **B** | 1.92 | 0.09 trim + 0.05 replay | **2.06** | **6,503,105** | 45 MB |
| **H7** K58 0404 child, `p cnf 19425 184188`, sha `2286ae68…` | A | 1.21 | 0.85 | **2.06** | 7,114,766 | 81 MB |
| | A′ | 1.21 | 0.93 + 0.05 | **2.19** | 9,484,053 | 81 MB |
| | **B** | 1.32 | 0.06 + 0.03 | **1.41** | **4,056,058** | 36 MB |
| **N14** reciprocal-0404 leaf, `p cnf 305513 834106`, sha `92be6247…` | A | 0.23 | 0.56 | **0.79** | 2,308,201 | 111 MB |
| | A′ | 0.23 | 0.60 + 0.08 | **0.91** | 5,727,659 | 111 MB |
| | **B** | 0.23 | 0.07 + 0.07 | **0.37** | 2,494,126 | 48 MB |
| **R11** wall leaf (15,15,14,13), `p cnf 18497 173819`, sha `b3a5bded…` | A | 0.03 | 0.12 | **0.15** | 6,707 | 69 MB |
| | A′ | 0.03 | 0.12 + 0.01 | **0.16** | 1,105,650 | 69 MB |
| | **B** | 0.03 | 0.00 + 0.01 | **0.04** | 520,186 | 10 MB |

Adding the second checker to route B: H8 3.05 s, H7 2.05 s, N14 1.12 s, R11 0.19 s.

Ratios B against A: CPU 0.698, 0.684, 0.468, 0.267; bytes 0.682, 0.570, 1.081,
77.559. Peak checker RSS: 86,168→45,652 kB (H8), 82,840→37,288 (H7),
113,912→48,880 (N14), 70,424→10,676 (R11).

On the two K58 cases the memo's advance gate is met with margin: total
certificate CPU −30 % (H8) and −32 % (H7), retained bytes −32 % and −43 %,
checker RSS −47 % and −55 %, and every proof is RUP-only. On the two
preprocessing-dominated heterogeneous inputs CPU also drops (−53 %, −73 %) but
the retained LRAT is **larger** than the DRAT (2,494,126 vs 2,308,201; 520,186 vs
6,707). Section 5 explains why; it is measured, not smoothed over.

## 4. The independent replay (the actual deliverable)

For every case the trimmed LRAT replays against the **original** CNF, not against
a reduced base:

| case | trimmed proof sha256 | additions | hint steps | `lrat-trim` backward | `lrat-trim -S` forward | second checker | `--rup` on the untrimmed proof |
|---|---|---:|---:|---|---|---|---|
| H8 | `ae25a7a40dfe91ce…` | 32,106 | 1,482,249 | rc 20, `s VERIFIED`, 0.05 s | rc 20, 0.05 s | rc 20, 1,482,249 steps, 0.99 s | rc 20 |
| H7 | `224dc08dc4311107…` | 22,086 | 876,012 | rc 20, 0.03 s | rc 20, 0.03 s | rc 20, 876,012 steps, 0.64 s | rc 20 |
| N14 | `f6f2290c5e65307b…` | 3 | 7 | rc 20, 0.07 s | rc 20, 0.07 s | rc 20, 7 steps, 0.75 s | rc 20 |
| R11 | `54d594fcdcea7181…` | 309 | 1,005 | rc 20, 0.01 s | rc 20, 0.01 s | rc 20, 1,005 steps, 0.15 s | rc 20 |

Two implementations of the LRAT/RUP semantics, written independently (one in C by
Pollitt/Biere, one by me in Python), accept the same trimmed proof of the same
CNF. The second checker is RUP-only and refuses RAT steps, which is what makes
`--rup` passing the relevant precondition.

**Trust boundary, stated plainly.** Neither checker is formally verified.
`lrat-trim` is the pinned tool the memo names as the first stage; my Python
checker is unverified code whose value is only that it is a second, independent
implementation. This is strictly stronger than the previous state (`NOT RUN`) and
strictly weaker than a verified checker.

## 5. Two integration facts a headline number would hide

**(a) Trimmed proofs elaborated from DRAT do not replay strictly.** In all four
cases `drat-trim -L` output is fine untrimmed (`lrat-trim` strict: rc 20), but its
*trimmed* form is refused:

```
lrat-trim: parse error …: deleted clause '184189' at byte 2 is neither an
original clause nor has been added (use '--relax' to ignore such deletions)
```

`drat-trim` emits deletions for clauses it introduced; trimming drops those
clauses but keeps the deletions. The trimmed elaborated proof only replays with
`--relax`, a relaxation of the deletion discipline, so the receipt records it as
`relax=True` and it is never quoted as a plain success. Native LRAT (route B) has
no such problem: it trims to a strictly replayable file. That is a second,
qualitative advantage of route B over A′, and it is why the A′ row quotes
untrimmed bytes.

**(b) A trimmed LRAT's size is (core derivation) + (one id per dropped input
clause).** Measured on the ASCII trim:

| case | additions | hint steps | deletion ids | consequence |
|---|---:|---:|---:|---|
| H8 | 32,106 | 1,482,249 | 239,040 | derivation-dominated: B is 0.68× A |
| H7 | 22,086 | 876,012 | 220,452 | derivation-dominated: B is 0.57× A |
| N14 | 3 | 7 | 834,112 | deletion-dominated: B is 1.08× A |
| R11 | 309 | 1,005 | 174,437 | deletion-dominated: B is 77.6× A |

On a 305k-variable formula refuted by 3 additions, or a leaf refuted after one
conflict, the "certificate" is almost entirely the list of input clauses the core
does not use — for N14 the trim makes the file *bigger* (2,393,381 → 2,494,126
bytes). Deleting those lines would be a textual normalisation of the kind the
memo forbids, so it is reported rather than promoted.

## 6. Negative and positive controls

Twelve per case, all executed, all rejecting where they must (the driver aborts
otherwise). Representative exact outcomes on H8; the other cases follow the same
pattern and are recorded per case in `pipeline-receipt.json`.

| control | result | message |
|---|---|---|
| DRAT fed to a LRAT checker | rc 1 | `negative identifier in clause addition` |
| same-shape wrong CNF (H7 CNF + H8 proof) | rc 1 | `propagating antecedents does not yield conflict while checking clause '185730'` |
| 90 % truncation of the trimmed proof | rc 1 | parse failure |
| empty clause removed | rc 0, no `s VERIFIED` | `WARNING no empty clause added in input CNF nor input proof` |
| one antecedent id altered (`135043`→`1` on line 2) | rc 1 | antecedent deleted/absent |
| literal flipped in a clause the proof **uses** (id 512) | rc 1 | `antecedent 512 is satisfied under the current assignment` |
| satisfiable 3-clause formula with the same proof | rc 1 | `deleted clause '4' … is neither an original clause nor has been added` |
| unmodified ASCII proof re-checked | rc 20 | positive control |
| literal flipped in a clause the proof **does not use** (id 1) | rc 20, expected | a refutation is its derivation: the proof uses 9,217 of 184,188 clauses, so mutating the other 174,971 cannot invalidate it |

Two of these deserve their exact scope. The satisfiable-formula control is the
weakest of the twelve: the proof is refused at the deletion layer because it does
not apply to a 3-clause formula at all, so it demonstrates "no certificate is
produced", not "a structurally applicable but invalid certificate is caught" —
constructing the latter would require a proof whose clause graph matches a
satisfiable formula, which cannot exist. The unused-clause row is deliberate: an
"any byte change must fail" test would be wrong, and a control that cannot be
explained is worse than no control.

## 7. Determinism and compute

Four full pipeline runs (one after deleting all copied inputs, so the last one
rebuilt everything from the pinned repository files) produced **identical** DRAT,
LRAT, trimmed-LRAT and elaborated-trimmed hashes on all four cases; wall/CPU
numbers vary by a few percent between runs, hashes do not. The regenerated DRATs of H8 and H7
equal the retained proofs byte for byte (`55a39634…`, `1831a7b7…`), the
regenerated LRAT of H8 equals the earlier slip's `05f0d7f1…`, and the deterministic
counters reproduce exactly: `49226/307381/12350047/3189` (H8),
`23143/64576/10376030/571` (H7), 1 conflict (R11).

Compute per full run: solver 6.85 s CPU (all four cases), route-A checking 2.60 s,
route-A′ checking 3.26 s, route-B checking including the second checker 3.27 s.
Four recorded runs plus two ad-hoc reproductions put the whole direction at
≈35 s of CaDiCaL CPU, far inside the 30-minute budget. No wall search, no cube
campaign, no second parent, no sweep.

## 8. What a *verified* checker would still need (exact blockers on this VM)

* `cake_lpr` (`tanyongkiam/cake_lpr` @ `033aad53…`): needs the CakeML compiler.
  `command -v cake cakeml sml mlton polyml` returns nothing; there is no SML
  toolchain on disk. A pre-built release binary would be an unreviewed
  executable, which the rules exclude, so none was fetched.
* `lrat_isa` (`lammich/lrat_isa` @ `99b832b5…`): the generated checker needs
  Clang **and** Boost iostreams; `/usr/include/boost` does not exist and
  `clang++` is not installed. Isabelle-2024 is additionally absent.
* Smallest approval that would change this: permission to install a CakeML
  toolchain and Boost headers, or to use a pinned pre-built `cake_lpr` with a
  recorded source-to-binary provenance path. Until then "independently replayed"
  here means *two independent implementations agree*, not *a verified checker
  accepted*.

## 9. What this does not show

* No wall row, cube, profile or parent is closed. R11's sibling cubes are OPEN;
  using the closed leaf says nothing about them. N14's `summary.json` records four
  OPEN leaves of the same tree.
* No bound change, and no extrapolation of these timings to the 11 wall profiles
  or to 113,179 frozen-cover cases.
* The heterogeneous cases are *plumbing* tests, not throughput tests: R11 closes
  after 1 conflict, N14 after one preprocessing-level refutation. The only
  non-trivial searches here are the K58 0404 children.
* `drat-trim` is still trusted as the incumbent checker for route A; the new
  independent replay covers the LRAT side. Route A's `s VERIFIED` was reproduced,
  not independently re-implemented.
* A SAT model, an UNSAT proof and a verified checker are three different things;
  this report asserts only the second.

## 10. Files

| file | role |
|---|---|
| [`run_pipeline.py`](run_pipeline.py) | the whole experiment: assertions, three routes, three replays, twelve controls per case, receipt |
| [`lrat_rup_check.py`](lrat_rup_check.py) | second independent RUP-only LRAT checker |
| [`receipt.json`](receipt.json) | the submitted run: commands, exit codes, CPU, RSS, bytes, hashes and controls |
| [`coordinator-receipt.json`](coordinator-receipt.json) | the earlier independent replay |
| [`rehearsal-receipt.json`](rehearsal-receipt.json) | replay from the integrated tools helper |

The member's further repeated runs behind the determinism claim remain under
`.ultramath/smx06hpp8/m5/`. A later coordinator replay again matched the DRAT,
native-LRAT, trimmed-LRAT and search-counter identities on all four inputs; its
timings are separate from the table above. The committed helper pins all four
input and fresh-proof hashes rather than learning an unpinned value.

Re-run with `python3 run_pipeline.py` (≈7 s of solver CPU plus ≈7 s of checking);
it rebuilds everything from the pinned binaries and public inputs and refuses to
finish if any assertion or control fails.
