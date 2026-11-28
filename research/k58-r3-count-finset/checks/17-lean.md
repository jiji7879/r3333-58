# Lean checks for entry 17

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
