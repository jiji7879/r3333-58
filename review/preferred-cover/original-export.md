# K58 representative-pair package: original-formula, export, queue and group-encoding audit

## Limited-use judgment

**Use the verified tables/exports as an exact local preprocessor and an unrestricted-row-root representative decision cover; do not spend a broad new K58 solver campaign on the present evidence.** I found no formula/export soundness defect. A preferred-job UNSAT closes only its exact restricted representative class. A whole ordinary row still requires strict UNSAT of every preferred class for that row, or a direct proof of its unrestricted parent. Transport below a pre-existing cube additionally requires permutation invariance of that cube.

**All 11,585 ordinary wall rows remain OPEN.** The change from 60,817,332 old labeled cells to 3,604,436 preferred jobs is scheduling compression, not 57,212,896 newly closed mathematical cases and not a reduction of the mathematical wall. D has 10,000/10,000 cap-OPEN outcomes. Together with the earlier validated unsplit A/B/C and 1,000-pattern experiments finding no solver improvement, this gives no reason to scale solver expenditure. I do **not** justify running another matched experiment now; the prerequisite new measurement would be a comparison on locally realizable surviving jobs with identical cold solver settings and retained proofs, not another unmatched fresh D batch. I ran no such experiment.

## Scope, private setup, and exact commands

Repository base was `8e5a10eb58de4c4b50b128eadc9a36c4b105ee4f`. I extracted only beneath `.ultramath/smwy7kg2n/m3/`; no shared/tracked file was edited, no nested run was started, and no SAT solver was executed. The only native checker calls were one-worker DRAT replays of existing proofs. Offline setup used the supplied Python 3.12 wheel and checker source in my extracted copy.

Input SHA-256 values:

```text
c59d0dbbd8e2108ab0f376377a489f26897246f3ff3d971983ebd5b3523e387a  K58_wall_10k_batches.zip
10398532cfbccfa8fcc680f34308ad9465d71f976cbac56b117298ff3a08cae6  K58_40000_pattern_trials.tsv
93055577ff1adb617949a66376c48940a3e1177a7874ff00bae7a2ed17c9386a  K58_wall_batch_handoff.md
```

Commands, from my member directory:

```sh
(cd bundle/K58_wall_10k_batches && sh setup.sh)
bundle/K58_wall_10k_batches/.venv/bin/python audit_d.py > audit_d_output.json
bundle/K58_wall_10k_batches/.venv/bin/python strict_replay.py > strict_replay_stdout.txt 2>&1
bundle/K58_wall_10k_batches/.venv/bin/python cross_original.py > cross_original_stdout.txt
```

Exit status was 0 for each. `audit_d.py` performs formula regeneration/parsing, direct combinatorial truth assignment, and queue arithmetic only. It has no SAT call. `strict_replay.py` invokes only `drat-trim -i -U` on existing proofs. `cross_original.py` regenerates formulas with the bundle and tracked encoders in separate processes, without solving them.

## 1. Original K58 parent identity

The extracted encoder is genuinely tied to the previously tracked FIRST parent, rather than merely passing self-hashes against a newly simplified generator:

* All ten bundled `engine/frozen/*.py` files are byte-identical to `tools/selfcontained/wallcc/frozen/*.py`. This includes `cover_evidence.py`, `dense.py`, `gluing.py` and `support_tables.py`.
* Bundled `inputs/wall.jsonl.gz` and tracked `data/wall.jsonl.gz` are byte-identical (SHA-256 `8d91ebc7d9fe6623bb04f6a0846953827a90265453c9dbcd51e3d1acf0c8bafd`).
* The only `engine/problem.py` diff from the tracked file is the fallback location of that same roster and an added `checked_case` helper; `row_formula` is unchanged.
* `cross_original.py` regenerated six FIRST parents independently through the bundle and tracked entry points. Every full row ID and parent SHA-256 matched, covering all four nominated arm sizes and including the first D row. Results are in `original_source_audit.json`.
* `audit_d.py` regenerated all **512** cold FIRST parents and their ten-unit raw queries. Every stored parent and query SHA-256 matched, involving **499 distinct parent hashes**. Every original parsed clause was preserved as a prefix and exactly the ten physical units were appended. All 512 receipts remain `OPEN` at cap 512, not closure.

For the first D row `f936154b8863241cffd794e00baece058d5fef6bc3f7396c9fcbe7a1b48a7894`, the original parent is:

```text
p cnf 19070 181818
SHA-256 ccf8b9e9fdc387efa61eab85e7d1cfc1fedda15afd0f05bf711dc98cdfce0481
```

This establishes original-formula identity for the tested transport path; it does not independently reopen or reprove the earlier first-tier mathematical derivation.

## 2. What raw, sorted and preferred exports mean

I regenerated and parsed all three conventions for the first D job, words `00020 01000`. The physical cube is

```text
6366 6406 6502 6443 6474 6370 6409 6506 6446 6478
```

The independently parsed exports are:

| Convention | Header | Added clauses over original | Query SHA-256 |
|---|---|---:|---|
| raw | `p cnf 19070 181828` | 10 | `c28ff93460900066851ef9efa3eabc1a18a28b254b7b11368c1ae63eb90f0fa7` |
| sorted | `p cnf 19094 182080` | 262 | `9aad0ec607d847515ddcb6457f570592d3cca49cee39fbb8f71f91aae0f84541` |
| preferred | `p cnf 20635 187926` | 6,108 | `e2a86483100cf96bc6560581556d341d06b21c32105062bf1c29f4a1d7f6b5b5` |

For raw, the entire suffix is exactly the ten unit clauses. For sorted, the suffix is the independently reconstructed full-outside lexicographic guard followed by those units; this is the two-smallest convention. For preferred, the final twelve units are the ten physical units plus the two-literal owner assumption for this catalog pair, and the preceding extension sorts only positions `O[2:]` and constructs occurrence/ownership indicators.

The conventions are **not interchangeable restrictions**:

* Raw fixes only two nominated stars. Its UNSAT closes that raw formula.
* Sorted additionally requires the entire outside word list to be sorted.
* Preferred fixes the chosen catalog pair, sorts the tail, and requires that this be the least preferred pair present anywhere in the outside word multiset. The chosen pair need not be the two smallest words.

Consequently, one preferred UNSAT does **not** in general refute the old raw cell having the same ten pins. The canonical preferred label of a full coloring depends on its other outside words; raw interfaces have no unique representative map. The useful theorem is instead solution-dependent: given a complete parent solution, choose its least present preferred pair, rename witnessing outside vertices, sort the tail, and obtain a preferred representative. This is exact at the unrestricted root only with the separately audited physical/auxiliary symmetry.

### Independent preferred-clause test, without SAT

For each of the **3,330** stored complete-arm SAT witnesses, `audit_d.py`:

1. recomputed every legal word and the witness's least preferred pair;
2. selected two vertices attaining that pair, relabelled them to the nominated slots, and sorted all remaining vertices;
3. directly checked the relabelled three-color arm's triangles, pentagon and nominated pins;
4. constructed semantic truth values for every lexicographic, site, occurrence and ownership auxiliary;
5. evaluated every clause emitted by `preferred_extension`, the ten physical units, and the exact `owner` literals.

All clauses passed. The counts were 1,272 / 1,049 / 692 / 317 witnesses for sizes 11 / 12 / 13 / 14, and these relabelled witnesses hit **every one of the 1,214 / 941 / 530 / 156 preferred catalog pairs**, respectively (2,841 total). The witness-to-owner mapping SHA-256 is `49afd5146ac41b48fdf1084aa469afa4f6b12e1207cb75da770d00fc4a949384`.

Clause inspection explains the result. The gates imply absence of all pairs through the current index; ownership assumes absence of all earlier pairs and falsity of the current absence gate, while the ten pins guarantee presence of the current pair. Unequal pairs use occurrences of both words; equal pairs require two distinct sites. This implements least-present-pair ownership. The 3,330-witness check is an implementation/model audit, not a replacement for the exhaustive local cover proofs.

## 3. Group encoder versus original degree/support predicates

`cheap.py` uses a shared physical graph and group-level cardinality/support auxiliaries, with each row's signed units supplied as assumptions. I checked the decisive guard simplification on every roster row:

* **11,585 rows**, **36 distinct group formulas**, and **175,794 nominated-arm sender vertices**;
* every group fixed pin is in the exact original signed pin set;
* **11,585** bypass flags are assumptions-forced true exactly when the original sender has `needed <= 0`;
* the other **164,209** sender vertices use the non-bypassed guard path.

The exact correspondence is as follows. Let the unsimplified group candidate list be $C$, with $k$ candidates forced positive by a row. After removing pins and edges with another known color, let $U$ be the remaining candidates. Original `marked_threshold` uses:

* an automatic sender when $k\ge14$, decreasing the marked/total-critical goals and imposing no support table;
* otherwise a guarded sender feasible exactly when $|U|\ge14-k$, with $\operatorname{AtLeast}_{14-k}(U)$ and, for the marked arm, support clauses;
* no selectable sender when $|U|<14-k$.

The group's guarded $\operatorname{AtLeast}_{14}(C)$ is, under those same row assumptions, feasible exactly when $\operatorname{AtLeast}_{14-k}(U)$ is feasible. `per_row` forces the bypass true precisely for $k\ge14`; otherwise it forces the bypass false and requires the support guard. Generating support selectors from group-fixed data and then imposing the row assumptions gives the same admissible supports as prefiltering with the full row pins. Counting automatically true guards is equivalent to the original decrement of constant sender contributions. Guards are implications, in both encodings, so a feasible sender may still remain unselected unless required by the marked/total-critical cardinality goal.

Crucially, a false group-level answer is not simply promoted to an original-parent closure: `cheap.certify` regenerates the original parent and exact convention query for a fresh proof attempt. A timeout/`None` becomes `OPEN`; a satisfying physical model requires independent validation. The sorted local-table shortcut returns `UNSAT_SORTED_ARM` before that full-parent proof block, so those statuses must be described as local-table exclusions, not stored per-job full-parent DRAT certificates.

I found no guarded-support/degree unsoundness in this path. This does not turn capped group probes into whole-row evidence.

## 4. Queue semantics checked over the entire remaining domain

Independently of a preview or another 10,000-job draw, I enumerated the full position permutation used by `campaign_queue.py`:

```text
complete preferred domain       3,604,436
D positions excluded               10,000
remaining positions checked     3,594,436
stride                            104,729
gcd(stride, remaining)                  1
duplicate/unmapped positions             0
```

Every remaining position occurred exactly once, and the exact complement of the enumerated permutation was the stored D set. The first 200 independently unranked positions matched the row/pair outputs of `campaign_queue.batch(0,100) + batch(100,100)`; their 200 reported raw-global IDs were also distinct. The complete position-sequence SHA-256 is `e46b631864747b9a15fdcf9eb16f4d5e8187259f1938ea321b89b573e728ee77` (little-endian 32-bit preferred positions). Thus the queue's nonoverlap/exclusion mechanism is sound as implemented. This does not imply that its OPEN jobs are closed or that a new sweep is useful.

## 5. Strict proof transport and the packaged `-w` issue

Every bundled proof wrapper I inspected uses `drat-trim -i -w`, with `-U` added for RUP-only checks. Here `-w` suppresses warnings. This is a protocol nonconformance with the requested never-`-w` audit, although warning suppression alone is not evidence that a proof is false.

I therefore regenerated every one of the **42** stored full-FIRST-parent sorted-guard transports and replayed its existing lifted proof using:

```sh
tools/drat-trim query.cnf proof.rup -i -U
```

There was deliberately no `-w`. Results: **42/42 `s VERIFIED`**, checker exit 0, every reconstructed Python receipt exactly equal to its stored record, every decompressed lifted-proof SHA-256 matched, and none of the 42 logs contained a warning, error, or `NOT VERIFIED` string. Freshly compiled checker SHA-256: `a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066`. Commands and outputs are in `strict_logs/`, with machine-readable results in `strict_replay_output.json`.

These 42 proofs establish only 42 finite original-parent-plus-guard exclusions. They are not 3.6 million representative proofs and not whole-row closures. C's 2,418 sorted statuses likewise are not 2,418 individually archived full-parent proof files.

## 6. Usefulness and stopping decision

Directly parsed probe totals are:

| Probe | Outcomes | Conflicts |
|---|---|---:|
| A+B raw | 20,000 OPEN | 2,576,473 |
| C raw | 10,000 OPEN | 1,288,377 |
| C sorted | 7,582 OPEN; 2,418 UNSAT_SORTED_ARM | 1,011,952 |
| D preferred | 10,000 OPEN | 1,289,283 |

The recorded C sorted run used different grouping, incremental history and worker count from C raw; its runtime is not a controlled speed comparison. The sorted statuses are already exact local-table exclusions, not newly solved whole K58 rows. D provides no positive selection or closure signal, and tiny conflict-cap overshoots are not a hardness ranking.

The defensible limited use is therefore to apply the independently certified local exclusions before conflicts and retain the representative mechanism for possible future exact root proofs. The package does **not** establish a faster solver on surviving jobs, full-row search cost at longer budgets, or useful per-job proof sizes. With no D closures and prior unsplit/pattern improvements absent, **stop rather than scale**. Any future closure claim must regenerate the original parent and exact owner guard, preserve the physical cube, and pass `drat-trim -i` without `-w`; OPEN and timeout records must remain OPEN.

## Evidence map

* `audit_d.py`, `audit_d_output.json`: all parent/query, export, direct preferred-clause, complete queue and roster/group checks.
* `cross_original.py`, `cross_original_stdout.txt`, `original_source_audit.json`: tracked-versus-bundle original parent/source checks.
* `strict_replay.py`, `strict_replay_stdout.txt`, `strict_replay_output.json`, `strict_logs/`: strict one-worker replay of all 42 full-parent transport examples.
* `artifact_sha256.txt`: hashes of the audit scripts, outputs and this report.
