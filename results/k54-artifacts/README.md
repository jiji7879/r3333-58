# K54 artifacts rescued from the swarm directories (19 Nov 2026)

`repo/.ultramath/` is gitignored and was pruned on 25 Nov. These are the certified artifacts that
existed **only** inside it, copied here first. Everything below was verified during the session whose
record is `results/K54_REPORT_FOR_LLM.md`.

| dir | contents | why it matters |
| --- | --- | --- |
| `lean-capacity-8/` | `Capacity.lean`, `Check.lean`, `build.log` | the capacity table 16/5/2/1 as a board-independent Lean 4.33.1 theorem; axioms `[propext, Classical.choice, Quot.sound]` |
| `lrat-cores/` | 53 directories, 153 files: `core.cnf`, `core.lrat`, `Cert.lean`, transcripts | 94 cut cores kernel-checked through Mathlib's `lrat_proof` (LRAT <= 37 KB each, 0 RAT lemmas) |
| `marginal-cuts/` | `cuts.tsv` (533 rows), `replay_cuts.py` | the complete single-column marginal cut frontier for local-15 / live-07 / live-14, every row DRAT-verified |
| `coverage/` | `COVERAGE.md`, `CUTS.md`, `COVERAGE-MUX.md` | the coverage keystone argument for all 15 priced boards, and the cut-uniqueness note |
| `packing/` | `RESULTS.md`, `capacity.json`, `direct.json`, `enum_check.json`, `multiplicity.json`, `replay.json`, `CrossCut.lean` | the 4/4/3 packing bound (4, 4, 3 attained) and the capacity table, all DRAT-backed; the CNFs themselves were 21 MB and were not kept |
| `eligibility/` | `eligibility.json`, `manifest.tsv`, `results.md`, audit scripts | exhaustive eligibility of all 161 certified partitions: 18,595 UNSAT instances, 0 failures |
| `reports/` | member reports for live-16, fresh-07, the trust-base audit, the coverage extension | the prose behind the numbers |

Not copied (regenerable, and large): the millions of clauses of CNF, the 533 DRAT files, and the
21 MB of packing CNFs. Each report names the command that rebuilds its instances.
