# Lean checks for entry 13

Command: `bash lean/build.sh` as background job jmx0hmr7s; full versions and
maxima are in `root-build.log` beside this file.

Outcome: **exit 0**, elapsed **281.39 s**, maximum RSS **6,782,744 KiB**.

The module sequence included all four CounterNeighbours modules (including all
15 independently evaluated emitted-input audits), ClassifiedBridge,
CountedSenderReady and K58.Check. The root audit prints
`K58.R3Counter.counter_inputs_audit`,
`K58.R3Counter.exists_neighbour_finset_emitted`,
`K58.R3Counter.emitted_sender_step_ready_of_counter_count`, and
`K58.R3Counter.emitted_sender_step_ready_of_emitted_count_classified`.
Every one has only propext, Classical.choice and Quot.sound. No `sorryAx`,
`native_decide` or custom axiom occurred.

Across the root build and independent m3/m5 audit logs, 501 `depends on axioms`
outputs were mechanically scanned for unwanted names: none were found.
Axiom checking supports proof status, not mathematical fidelity; statement
scope was reviewed separately in `13-read.md` and `13-model.md`.


## Strengthened root build

After an adversarial semantic review, the root build was rerun. Final retained
result: **exit 0, 5.82 s, maximum RSS 6,813,156 KiB**. The modules
`PhysicalGuard`, `CountedSenderReady` and `K58.Check` now include the physical
catalogue mask, agreeing-atom proposition, bare-ready vacuity theorem and a
guard-true agreeing-atom witness. Every reported axiom is still within the
permitted standard set. Audit assessments generated during failed intermediate
edits were not used; the saved log is the final successful invocation.
The dependency-aware build leaves unchanged audited counter inputs at their
previously checked artifacts, as intended; those were rebuilt in the first
root run documented above.
