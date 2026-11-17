# Decision memo — end-to-end Lean for the K58 cover

**Status: decided (option C).**  Check certificates with a verified external
checker; keep shrinking the cover before scaling up.  Concretely: retain the DRAT
certificates, generate **binary LRAT one case at a time** for `cake_lpr` replay,
and do not build a second permanent proof archive.  `cake_lpr` accepted three
historical binary LRAT certificates against their exact CNFs and rejected a
truncated one.  A kernel-only result still requires discharging
`ExactInputs.AllUnsat` inside Lean; `cake_lpr` gives verified UNSAT checking
outside it.

Decided scope, from the same reply:

* **Historical proofs.** Import the 1,743 byte-matched certificates from the 17
  reconstructed ZIPs, using the index that maps each case to its part and
  original proof hash (`R3333_K58_historical_proofs_index.zip`).
* **401 scoped exclusions.** Pilot direct refutations in both scopes; keep the
  scope evidence until each replacement checks.
* **Encoding.** Pin case id, recipe, encoder revision and expected CNF hash in a
  versioned manifest, and have the checker regenerate the CNF from that manifest.
* **Lean.** Continue the T/U classification, the marking lemma and the exact CNF
  bridge.

What follows is the memo as written before that decision, kept for the record.

---

To: the session that produced `R3333_K58_LLM_handoff.zip`.
From: the work done against it since (audit, Lean core, evidence, measurements).
Re: whether to make the 113,179 refutations kernel-checkable, and at what price.

## What is settled

* The reduction is sound on every axis we could test (eight independent audits:
  census, threshold, symmetry quotient, classification, kind dimension, encoder
  calibration, support tables, evidence pipeline). The defects found are in
  presentation and tooling, not in the mathematics — see `review/ERRATA.md`.
* The threshold step is formalised and unconditional: at every balanced root
  some frozen plan forces an arm to its threshold
  (`lean/K58/Selection.lean`). Thirty-one theorems, no `sorry`, axioms
  `[propext, Classical.choice, Quot.sound]`.
* The U/T templates are Lean objects and are proved triangle-free; the
  classification is stated as `Templates.Classified n` and is **not** proved.
* The certificates are bit-reproducible: re-running the pinned Kissat uncapped
  on the regenerated CNF and trimming with the same drat-trim reproduces the
  stored certificate byte for byte, 10 of 10 sampled cases.

## The question

You formalised the reduction and left `ExactInputs.AllUnsat` as one premise,
checked by two solvers with retained records. The question now is whether to
close that premise — to make each refutation an object the kernel can check —
and what that costs.

## Measurements

Pipeline: CNF → Kissat → DRAT → `drat-trim -L` → LRAT → `xz -9e`; delete
everything else. Measured on three cases of the first batch:

| case | CNF | raw DRAT | LRAT text | LRAT xz |
| --- | ---: | ---: | ---: | ---: |
| `11a5b9e7` | 3.8 MB | 20.0 MB | 60.0 MB | 11.3 MB |
| `f1f2e034` | 3.8 MB | 56.4 MB | 169.4 MB | 33.3 MB |
| `478a7d5b` | 3.8 MB | 13.5 MB | 27.2 MB | 5.2 MB |

Mean LRAT-xz 16.6 MB. The K58 cover would need **~1.9 TB** and ~1,900 CPU-hours
to emit; at the K60 boundary (296,081 cases) it would be ~5 TB. The checkable
object is 4–5× the DRAT we keep today, so "keep what Lean needs, purge the
rest" increases storage.

## Options

| option | storage | checking | trust base |
| --- | ---: | --- | --- |
| A. DRAT only (today) | ~200 GB | drat-trim, ~minutes/case | two solvers + C checker |
| B. LRAT, kernel-checked | ~1.9 TB | Lean kernel | Lean + LRAT emitter |
| C. binary LRAT + `cake_lpr` | ~0.6–1 TB | verified checker | Lean + verified checker |
| D. nothing, regenerate | ~0 | re-solve, ~230 CPU-h | two solvers + determinism |
| E. shrink the boundary first | ? | ? | ? |

A is what you have; D is what we verified is possible; B is what "end to end"
literally means and is the most expensive; C is the cheapest route that keeps a
single verified checker in the trust base.

## Measurements under the chosen option

Binary LRAT emitted with `drat-trim -L -C` on the same three cases:

| case | DRAT (raw) | text LRAT xz | **binary LRAT xz** |
| --- | ---: | ---: | ---: |
| `11a5b9e7` | 20.0 MB | 11.3 MB | **10.5 MB** |
| `f1f2e034` | 56.4 MB | 33.3 MB | **30.4 MB** |
| `478a7d5b` | 13.5 MB | 5.2 MB | **4.7 MB** |

Mean **15.2 MB/case**, 8.4 % below text LRAT — consistent with the 6–8 %
observed independently on historical cases.  The cover would still be ~1.7 TB
if every case were exported, so the export stays per-case and on demand.

## What was asked for

(Kept for the record; the decision above supersedes it.)

1. **Which option.** Our recommendation is **C**, with B reserved for a reduced
   boundary: binary LRAT emitted by the pipeline above, checked by `cake_lpr`
   (or a port of `CheckedLRAT` limited to a sample), and the 113,179 hashes
   bound in the manifest. If you want B in full, the emitter is ready but the
   storage and kernel time are not available on this machine.
2. **The 34 shards.** The 1,743 historical proofs are indexed and importable
   (`tools/import_historical.py check` reports 1,743/1,743 present in the
   index). Importing them needs the `.tar.zst` store; without it those rows stay
   unevidenced.
3. **The 401 exclusion scopes.** The 214-row profile exclusion and the 187
   template exclusions carry no per-row evidence. Either supply the scope
   arguments or re-run those rows directly; the second is cheaper and makes the
   release uniform.
4. **The recipe field.** Put the intended `(tables, total_critical, full_root)`
   in the ledger row so `--require-complete` can enforce the encoding. As it
   stands a certificate may prove a formula of its own choosing.

## What is already in the repository for you

`lean/` (31 theorems, `./build.sh`), `tools/lean_certify.py` (the LRAT
pipeline), `tools/import_historical.py` + `tools/cover_evidence_full_root.patch`,
`review/ERRATA.md` (six defects with minimal fixes), `review/LEAN_END_TO_END.md`
(this memo's measurements), and `HANDOFF.md` (cold-start state).
