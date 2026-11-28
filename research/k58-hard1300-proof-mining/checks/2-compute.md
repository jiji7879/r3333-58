# Recomputation and native checks (kind: compute)

The commands below were actually run from the repository root, with `.scratch/massive-clean-install/k58-solver/.venv/bin/python` for Python code.

## Inputs and native K58 execution

`work/prepare.py` invokes the authoritative unpack's frozen-ledger lookup and formula generation with `tables=True,total_critical=True,full_root=True`. It asserts the complete manifest input hash for both ranks and writes the exact parent plus recipe/identity metadata to `.scratch/hard1300-proof-mining/`. Rank 1300 is also tested byte-for-byte against the previously audited `.scratch/k58-candidate-verification/proof/rank1300/rank1300.cnf`.

For each rank, `tools/color-resolved-wallcc/wallcc.py run` was called on that exact external CNF with:

```text
--depth 0 --jobs 1 --engine native --native-policy default
--cas off --pivot-color off --proof eager
--conflicts 2600000 --seconds 360 --check-seconds 150
```

The jobs used rank-unique `--out` directories. Each `verify` and compact `export-drat` completed with `VERIFIED_UNSAT`. The observed actual search costs are 36.94/42.46 CPU-s, not externally projected or estimated times. All parent/raw/export hashes are independently recomputed in `work/native-receipts.json`.

## Cores and checker modes

The two core-extraction paths using raw warning-visible DRAT completed with `s VERIFIED` and zero RAT in core. They wrote 99,634,032 and 121,695,451-byte text lemma streams. `work/strip_text_drat.py` retained every addition byte and only deleted textual deletion commands. Each JSON receipt records complete input-byte accounting and one terminal empty addition. `-I -W -U` then returned zero, `s VERIFIED`, no warnings and zero RAT on both reduced core/lemma inputs. `work/core-verification.json` ties these stages to their hashes and exact 5,186/5,204 reduced-core counts.

Contrasting failed paths are recorded honestly: a 90-second normalized-plain run hit `s TIMEOUT`, and 240-second `-u -W -U` runs also hit `s TIMEOUT`. They did not emit successful core files. They are not counted as certificates or as nonexistence conclusions. The binary normalizer initially refused the text streams; no mixed-format helper or incorrect binary/ASCII flag was silently accepted. The eventual reduced proofs use `-I`, not `-i`.

## Repeated analysis

`work/inspect_cores.py` compares semantic clause sets (allowing harmless literal-order differences) and produces the width/core inventories. It uses indexed subset membership to test literal-set subsumption, not a clause signature or a guessed parent mapping. Its current bounded summary files are `core-comparison.json` and each rank's `core-candidates.json`.

`work/probe_common.py` then used four shared clauses on each full root, for eight exact RUP checks. Every log is `s VERIFIED` with no warning and no auxiliary literal in its core. `common-probe.json` stores every parent/query/proof/core hash and decoded edge/colour witnesses. The two named pin-triangle patterns and the two palette residuals were independently decoded, so these passes are not miscalled new reusable theory.

`work/filter_common.py` screened all 2,346 common candidates under the exact parent and the negated cube using the supplied `python-sat==1.9.dev22` and CaDiCaL with `conf_budget(0)`:

```text
1297: 2346 refuted, 0 UP-unresolved
1300: 2346 refuted, 0 UP-unresolved
```

A positive satisfiable-unit and a negative unit-cube control both passed. These are solver triage calls, not native RUP certificates for all 2,346 candidates, not parent model classifications, and not a theorem that no other clause is generalizable. Full detail is in `common-filter.json` and `triage-controls.json`.

The obsolete `scan_proof.py` was removed rather than retaining an unused slow alternative. A first implementation's format assertions and summary-key errors were corrected with no alteration to the frozen input data or weakening of a proof requirement. No production ledger, queue, archive or default encoding was changed. No Lean theorem or second model reading was requested; the formal coverage here is native DRAT/RUP and bounded recomputation, without Ultramath or warning suppression.
