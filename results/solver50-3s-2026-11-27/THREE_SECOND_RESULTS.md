# Three-second K58 representative experiments

Repository base: `d19284ac7a1698a3296197cf0c133c6d5c1331e6`.

## Bottom line

**We obtained four independently replayed full-representative proofs at a three-second CaDiCaL search budget, on new cases that had been OPEN at conflict cap 128.** These are exact original first-tier parent-plus-sorted-guard formulas, and a hash-matched malformed-prefix proof was rejected.

**They are not new exclusions beyond the exact local arm table.** All four cases are also `REFUTATION_CANDIDATE`s in that table. I consequently do not claim a general solver winner or a whole-row result. All 11,585 ordinary wall rows remain OPEN.

I also ran a fresh matched comparison on 12 locally surviving `ARM_WITNESS` cases. **Zero closed in either arm**, so I stopped without increasing the cap or adding a split.

## What was measured

| Experiment | Result | Interpretation |
|---|---|---|
| 24 direct sorted classes excluded from the six supplied fresh controls | **4 `VERIFIED_UNSAT`, 20 `OPEN`** | Four full proofs, directly on first-tier parent plus exact sorting guards. Not new beyond the local table. |
| Same 24 through shared incremental CaDiCaL, separated into 18 group states | **4 direct-verified UNSAT, 20 shared OPEN** | Architecture works; sibling reuse does not establish a demonstrable speedup. |
| 12 locally surviving sorted `ARM_WITNESS`, frozen before any run | **0/12 direct, 0/12 shared** | No new exclusions beyond the local table. Stop. |
| Two known fast liveness queries | **2 `VERIFIED_UNSAT`** | Controls only; excluded from comparison denominators. |

The direct 24-job cohort took **60.1250225692 s of summed search time** across **66.830150947 s of coordinator wall time**. The shared cohort took **60.091214285 s**, a ratio of **0.9994377003** relative to direct. The matched search timers start after encoding and solver initialization; proof checking is separate. These timing scopes must not be conflated with a hard end-to-end cap.

For the matched 12-job survivor comparison, actual shared elapsed search time was **36.008881505 s**, against independently validated fresh direct time **36.058130637 s**. They closed none. Strict replayed direct receipts were used rather than accepting a group-local UNSAT label.

## Direct proof summary

| Test index | Sorted words | Search seconds | Proof SHA-256 | Proof bytes |
|---:|---|---:|---|---:|
| 4 | `01220 / 02210` | 0.007431 | `c9e665b63b62713178017a3daa63a9891b3236a99ba1ecd11af3cc355f39f66c` | 9,291 |
| 13 | `01002 / 01010` | 0.015476 | `32f9d84ec65d4bfb18bfb7535e5399ecaf4f3d1da84e0575372010e6348d6dde` | 705,368 |
| 20 | `00020 / 00220` | 0.036820 | `9f9dddb7d170c417ffc680bb9354efdad3b550ae9cf7c60e22e8bb5715f4ff59` | 703,411 |
| 23 | `01022 / 01200` | 0.015549 | `aca4917b7f81926522d01f770a636e355497d3aba0d06e18fd08099fba994b23` | 701,396 |

Total direct proof size is **2,119,466 bytes**. All four proof/logic queries and all other OPEN receipt paths are in the evidence bundle. `local-classification.json` explicitly shows that each is also locally excluded, rather than pretending otherwise.

## Independently audited architecture and scope

Four accepted Ultramath directions and coordinator reruns established:

- **Strict solver controls:** all nine supplied three-second control proofs replay against exact parents, cubes and queries with `drat-trim -i` only. A wrong prefix and a wrong-formula control fail with `s NOT VERIFIED`.
- **New mathematical cover:** 1,101,974 representatives and all 885 labels/minimal-deletion witnesses check out. All 678 cover and joining-edge checks pass, including 304 new-cover and 304 sorted-cover RUPs and all 35 new edge local/full-parent pairs. This is scheduling compression only.
- **Original export/group encoding:** the original parent is respected. A shared-cube assumption is not automatically portable proof evidence to a different query. Regenerated shared-state comparisons preserve group identity and row assumption hashes.
- **Historical core claims:** old physical-core/proof files and all eight matched cases are absent from this wall's roster. Historical core reuse therefore contributes nothing here.

The general incremental design reuses CaDiCaL within a block, not proof bytes across unrelated parents or ownership guards. No cached terminal receipt was trusted without exact full-query checking.

## The two-arm quotation

The independently checked artifacts do **not** support the quoted `121/128`, `2/128`, `0/128` or complementary return/no-return figures on `1445e0649f7d`.

The supplied target has eight cap-128 receipts, no target 3-second trial, and no such complementary split. Strict replay establishes exactly two representative closures under `sorted`, words `00220/01201` and `00210/01201`. Neither belongs to the new 50-pair cover. The target's original parent hash is `c5549e8a2ae86391ba28a77d56118aa0c4b36a4732f49abc05c6ff3cb8895ad1`.

All 50 new-cover joint-support witnesses and 792 older raw projection witnesses on this target are checked models, not refutations. No justified joint-support 3-second experiment follows from them. Any row-closing result still requires a full exact cover with every job refuted, not these selected class exceptions.

## Why I stopped instead of scaling

The only controlled-positive signal is the ability to emit full parent proofs for the already locally excluded rows. The locally realizable `ARM_WITNESS`, earlier preferred and new 1,101,974-job cover samples give no three-second closure. Existing preferred/new-cover samples also remain entirely OPEN at cap 128, including 50,000 plain new-cover and 50,000 joining-cut cases. A 560-conflict count difference of the latter does not establish a speedup; workers, grouping and verification loads differ.

Use the independently checked local table and apply its physical sorted exclusions before spending search. If full parent proof artifacts are wanted, direct CaDiCaL at three seconds is a proven way to obtain them on a selected locally excluded class. Do not read from those results that locally realizable K58 jobs have become cheap, or that an entire wall row or a Ramsey-number bound has changed.

## Validation and evidence

- `direct-summary.json`, `direct-run.log`, `proof-index.json`
- `shared-summary.json`, `shared-run.log`, `shared-direct-audit.json`
- `survivors-summary.json`, `local-classification.json`
- `runtime.json`: exact solver/checker/hash versions and timer scope
- `verify50-strict.log`: full campaign replay with `-i` throughout
- `tools/solver50/runtime-changes.patch`: destination allocation plus strict checker patch against the supplied source
- `local-classification.json`: the proof/local-table overlap and the 0-survivor result

The source-supplying 50k archive's original **4,838** manifest hashes passed before the strict checker edits. The package `sha256sum` and all Python/C++17 build steps used offline wheels only. Proofs are supplied separately in the handover ZIP linked by this report; no claims are made from a skipped check or nominal cap alone.
