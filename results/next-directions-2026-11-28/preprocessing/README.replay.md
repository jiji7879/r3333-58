# Preprocessing replay result

The coordinator replayed `reproduce.sh` from a fresh member-copy in
`coordinator-preprocessing/`, not from current repository files. It completed
successfully in about 37 s on the retained parent+cube, H7 and R11.

- The retained request has **184,337 clauses and 529,030 literals**. The reduced
  form removes **35.3% of clauses and 39.2% of literals**, written as 119,343
  clauses / 321,850 literals in the original member run.
- Independent MiniSat propagation checked the unit and clause prefixes, and
  multiset identity with the reduced formula. Both corruption controls were
  rejected.
- R11 is genuinely root-refuted. The DRAT prefix in both output encodings
  replayed with `s VERIFIED` at about 0.098 s.
- For the closed H7 CNF, both the reduced formula's proof against the **host**
  (`drat-trim -i`) and `prefix ++ proof` against the host replayed with
  `s VERIFIED` (0.765 s and 0.733 s in this replay). A corrupted prefix was
  rejected.
- Four-seed matched-open runs reproduce seed-dependent total-CPU behaviour:
  geometric mean 0.92968, with the same pattern of one seed regressing and
  others gaining rather than a stable speedup. Every run is OPEN.

**Conclusion:** can be considered only as an opt-in to reduce RSS and CNF
loading costs. It is **not** a CDCL performance improvement. The measured
reduction is about 12% RSS and 35% parse/bootstrap CPU in this panel. Prefix
creation/checking still costs about 1.3 s + 0.9 s before a leaf's search runs.
Under this cost model only leaf memory/loading can be the binding constraint.

The generated prefix must be joined with the leaf's **binary** DRAT file in the
correct order. A SAT assignment returned by a reduced query must be extended
with the prefix's forced/pure assignment and checked against the complete host
cube. `finalise` is unchanged. The proof can go on the host because propagation
is monotone, but a RAT step need not be monotone under clause-subset formation;
the tested closed cases did not involve that hazard, and it is not licensed in
general. Prefixes are cube-specific, not a freely reusable all-row simplifier.

The original member report `README.md`, integration sketch `INTEGRATION.md`,
implementation `prep.py`, independent prefix checker `check_prefix.py` and the
reproduction scripts are supplied. The numerical receipts for the coordinator
reproduction are `benchmark-replay.json` and `host-receipt.json`.
