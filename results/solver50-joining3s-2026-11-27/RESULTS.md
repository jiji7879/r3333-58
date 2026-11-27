# Mandatory joining-colour probe — 2026-11-27

## Outcome

**Zero new representative closures and zero whole-row closures.** All 11,585
ordinary wall rows remain OPEN, and no Ramsey bound changes. The bounded probe
does not justify scaling the parent/child search or claiming a solver winner.

Two fresh positive controls produced exact full-query DRAT proofs. All eight
queries on four genuinely unprobed new-cover representatives consumed their
three-second search deadline and remain OPEN.

| experiment | fresh CaDiCaL calls | result |
| --- | ---: | --- |
| Existing sorted positive controls | 2 | 2 `VERIFIED_UNSAT`, independently replayed again |
| Four `round50` representatives and their sole unrefuted joining children | 8 | 8 `OPEN`, no proof emitted |
| New representative classes closed | — | **0 of 4** |
| Whole original rows closed | — | **0** |

## Exact candidate results

Every candidate has a complete physical four-colour split. The three branches
other than the listed surviving child have strict RUP proofs against that
candidate's exact full representative. Thus a strict child proof would close
its representative; a timeout does not. Parent and child are logically
equivalent after these branch refutations but are not byte-identical.

| arm | offset | row prefix | words | parent conflicts / status | child conflicts / status |
| ---: | ---: | --- | --- | ---: | ---: |
| 11 | 51,630 | `6ba2d5cdff5b` | `12210/21001` | 86,181 / OPEN | 95,478 / OPEN |
| 12 | 51,724 | `5a16bbab7360` | `20101/21010` | 77,915 / OPEN | 78,017 / OPEN |
| 13 | 50,010 | `75b56ee615bc` | `02210/10012` | 77,322 / OPEN | 81,234 / OPEN |
| 14 | 50,004 | `e34a3a35383e` | `01201/21010` | 66,271 / OPEN | 79,246 / OPEN |

The candidate schedule uses `PC`, `CP`, `PC`, `CP` by arm and reverses pair
order in the second wave. The exact full row IDs, query paths and SHA-256
hashes are in `execution-plan.tsv`. Ordered and conservative reversed
identities were absent from 189,824 prior representative identities. A final
combined TSV/JSON check covered 1,782 recorded query hashes: all eight new
queries were absent, and only the two intentional controls were prior
duplicates.

## Timing and process controls

Each formula ran in a new process with a fresh proof-logging CaDiCaL 1.9.5
instance. No learned state, cached terminal verdict or legacy proof core was
reused. The three-second native timer starts after CNF decoding and solver
initialization. A separate parent-controller watchdog enforces a six-second
solve-phase deadline with 0.05-second polling, and a 120-second whole-worker
cutoff fails closed. These are not
three-second end-to-end wall-clock guarantees.

The controls took 0.006294 and 0.035837 search seconds. Candidate search time
summed to **24.0183153211 s**; including controls, summed search time was
**24.0604469511 s**. The execution phase took **25.7589463978 s** of
coordinator wall time, excluding preparation and final independent replay.
Conflicts describe these selected calls only and are not a normalized measure
of solver or splitting efficiency.

## Verification

- The final preparation has **12 exact complementary full-query RUP proofs**:
  seven immediate monochromatic-triangle branches and five transported local
  exclusions, across all four candidates.
- `verify_joining3s.py` independently regenerated each representative and
  child, checked the host's four-colour at-least-one and pairwise-at-most-one
  clauses, replayed all 12 complementary proofs and rejected all four
  empty-proof controls.
- Both fresh control proofs replayed again with unrestricted DRAT
  `drat-trim -i -t 300`, with no `-w`. RUP-only `-U` is restricted to the
  existing RUP branch artifacts.
- The two new control proofs contain 9,291 and 703,411 bytes.
- All ten processes have solve-start/solve-finish watchdog markers and no
  worker failure logs.
- Applying the first fresh control proof to the second control's different
  query returned `s NOT VERIFIED`; see `fresh-wrong-query.log`.
- The three accepted Ultramath reports under `.ultramath/smwyejhdn/` are audits
  of proof transport, split semantics and selection only. They are not treated
  as new wall closures.

No negative inference is drawn beyond the measured cohort: OPEN means no
closure at this budget, not evidence of satisfiability or of global solver
difficulty. The six-pair reserve schedule in m3's `probe-v1/` was superseded by
m3 and was not combined with this primary run.

## Files and reproduction

Small records committed here:

- `summary.json`: all ten actual receipts, timings, hashes and closure fields.
- `preparation.json`: exact four-colour branch identities and checker receipts.
- `execution-plan.tsv`: frozen control and candidate schedule.
- `run.log`: preparation and per-query execution output.
- `verify.json`: independent replay totals.
- `fresh-wrong-query.log`: fresh wrong-query negative control.

The complete 115 MB working evidence, including exact CNFs, compressed and raw
proofs, model/checker logs, and the audited candidate inputs, is handed over as
`dist/k58-joining-color-probe.zip`, not committed to Git.

Run from the repository root with the supplied `K58_wall_50k` source bundle
installed at `ROOT`:

```sh
ROOT=/absolute/path/to/K58_wall_50k
OUT=.scratch/solver50/joining3s-reproduction
"$ROOT/.venv/bin/python" tools/solver50/joining3s.py "$ROOT" \
  --design .ultramath/smwyejhdn/m3/execution-ready --out "$OUT"
"$ROOT/.venv/bin/python" tools/solver50/verify_joining3s.py "$ROOT" \
  --prepared "$OUT"
```

The handover archive contains the relevant m1 input artifacts and m3 design
under the same relative paths, so extracting it beside the tools also permits
this command. The external source bundle remains a prerequisite. `--prepare-only`
performs only query regeneration, branch transport and strict proof checks;
it launches no SAT search. Every execution requires a new output directory.
