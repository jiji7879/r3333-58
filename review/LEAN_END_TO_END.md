# What "Lean end to end" costs

Asked whether the proof could be Lean end to end, with the computation producing
only what Lean needs and everything else purged.  The pipeline exists
(`tools/lean_certify.py`); this note records what it actually costs.

## The pipeline

For each case: regenerate the CNF from the frozen ledger row, solve with the
pinned Kissat, convert the DRAT proof to **LRAT** with `drat-trim -L`, compress
the LRAT with `xz -9e`, then delete the CNF, the DRAT and the uncompressed LRAT.
What survives is one compressed LRAT per case plus a JSON record binding it to
the CNF hash.  LRAT is the format a kernel-side checker can consume; DRAT with
RAT steps is not.

## Measured on three cases of batch 1

| case | CNF | raw DRAT | LRAT (text) | LRAT (xz) | stored DRAT.gz |
| --- | ---: | ---: | ---: | ---: | ---: |
| `11a5b9e7` | 3.8 MB | 20.0 MB | 60.0 MB | **11.3 MB** | 1.0 MB |
| `f1f2e034` | 3.8 MB | 56.4 MB | 169.4 MB | **33.3 MB** | 7.4 MB |
| `478a7d5b` | 3.8 MB | 13.5 MB | 27.2 MB | **5.2 MB** | ~1 MB |

Mean LRAT-xz: **16.6 MB per case**.  The Lean-consumable artifact is therefore
**4–5× larger than the DRAT certificate we keep today**, and 7–18× larger before
compression.  Purging the CNF (3.8 MB) and the DRAT (13–56 MB) does not offset
that: the LRAT is the biggest file in the pipeline.

Extrapolated to the 113,179 cases of the frozen cover: **~1.9 TB** of LRAT-xz.
Emitting it cost ~60 s of CPU per case here (solve + `drat-trim -L` + `xz`),
i.e. ~1,900 CPU-hours for the cover, before any checking.

## The trade, stated plainly

| keep | size | who can check it |
| --- | ---: | --- |
| nothing; regenerate | ~0 | nobody without re-solving (bit-reproducible, 10/10 verified) |
| DRAT.gz (today) | ~200 GB | drat-trim (C, unverified) |
| LRAT.xz | ~1.9 TB | an LRAT checker, in principle the Lean kernel |
| LRAT.xz, binary format | est. 0.6–1 TB | same, smaller |

So "purge the rest to save space" does not hold: the checkable object is the
expensive one.  What saves space is the opposite choice — keep only hashes and
regenerate, which is cheap in bytes and expensive in trust (the solver is
unverified) and in review time (~230 CPU-hours of solving).

## Status of the pipeline

`tools/lean_certify.py` is tested and produces the records above.  Two things
are **not** done: no LRAT checker was run on the emitted files in this session
(`drat-trim -L` emits its verified core, but no independent LRAT check was
performed), and there is no Lean-side LRAT consumer in this repository — the
pinned K60 development has one (`formal/src/R4333Lean/CheckedLRAT.lean`) and
porting it is the natural next step.
