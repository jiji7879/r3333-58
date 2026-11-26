# K58 wall closeout: certificates and remaining frontier

## Status

Ultramath campaign `smwxbvh79` has finished. All six finite reports are accepted after artifact and proof checks. **No whole frozen row has been closed and $R(3,3,3,3)\le58$ has not been proved.** The board's “solved” status means these bounded finite results are accepted, not that the Ramsey problem is solved.

Do not splice clauses or DRATs between the baselines and augmented formulas. Their auxiliary variable allocations are different. The reciprocal results below concern row `0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296`.

## Independently replayed finite certificates

### 1. The unaugmented 26-literal C26 region

The parent is the original reciprocal root (SHA-256 `aa23de814810dc2b5515955a0aa318eab72df81c4541006fde253b39c48d2b44`, 305,513 variables, 834,101 clauses), plus these fixed unit literals:

```text
-305498 -305501 -305503 -305505 -305512 -305482 -305483 -305484
-305485 -305486 -305487 -305488 -305489 -305490 -305491 -305492
-305493 -305494 -305495 -305496 -305497 -305499  305500 -305502
 305504 -305506
```

This is the nested region called `c488_021-007`, inside `c485_029-033`. Its containment was checked against the preserved split tree.

| artifact | SHA-256 | notes |
| --- | --- | --- |
| `.ultramath/smwxbvh79/m5/artifacts/pair-305507/baseline-parent.cnf` | `e60385d2874bceef813aafe144c4a8391eb3e7317af8a50b725f0159e2d16130` | 305,513 variables / 834,127 clauses |
| `.ultramath/smwxbvh79/m5/artifacts/pair-305507/negative.drat` | `a867d051a62ecfaa06f45c5a17395d0c890ef31fefa4afaf606845b550be5f8` | 100,900,149 bytes |

Coordinator-native `drat-trim` replay against the **bare parent** returned code 0 and `s VERIFIED` in 67.855 checker seconds; see `judge-bare-parent-replay.log`. The same proof also replayed against the bare negative child and the reported H7-augmented forms. Hence the unaugmented C26 region is UNSAT without relying on H7. Different auxiliaries and decision trajectories preclude a matched speed comparison with older UNKNOWN runs.

This does **not** close `c485_029-033`, a reciprocal child, the row, or either remaining 140-row profile.

### 2. A separate H7-augmented C26 parent composition

Member m2 merged the complementary $\pm305507$ child certificates into an ordinary binary-DRAT proof. Its input is the reciprocal root, the same 26 units, and a reverse-H7 block with fresh variables `305514..305599`; it is **not** the unaugmented formula above.

| artifact | SHA-256 | notes |
| --- | --- | --- |
| `.ultramath/smwxbvh79/m2/work/merge-305507/parent.cnf` | `27d40700033eb1b9c98eef4ba40710d3eac698e3fedbf9e356e5438fdecf90bf` | 305,599 variables / 835,933 clauses |
| `.ultramath/smwxbvh79/m2/work/merge-305507/parent.drat` | `db74bd1d2463bc7a231e1e1382f3a4041ef6376ab5deb92a0f50278e4bf9d2e0` | 57,479,584 bytes |

Coordinator replay returned code 0 and `s VERIFIED` in 180.275 checker seconds (`judge-merged-parent.log`). Member m2's second fresh replay returned `s VERIFIED` in 218.998 seconds. The certificate contains real RAT core lemmas and refutes only the exact augmented parent it was checked against.

### 3. The full first-tier-row exact-H6 layer on `0093…`

For `0093a6b3560baf862882ee0b8751440e309bef4ce5022d9d37797c97f8f75c96` (profile `(16,15,13,13)`, branch 224), m4 supplied and the coordinator replayed:

| artifact | SHA-256 | notes |
| --- | --- | --- |
| `.ultramath/smwxbvh79/m4/out/eq6-compose/0093-EQ6-full.cnf` | `71f325f2c01a98d623051c4c7bc06a2905a9e6dbc65b0ed578e3a40b4db0fb9e` | 22,157 variables / 225,725 clauses |
| `.ultramath/smwxbvh79/m4/out/eq6-compose/0093-EQ6-full.trimmed.drat` | `6b978f32e8d81b1468dcd3c826ae0d7cff961609fd77ca81694dfe49cf520353` | ordinary DRAT |

The checker returned code 0 and `s VERIFIED` in 34.248 seconds (`judge-eq6-full.log`). The query carries the actual first-tier-row body, the forward-3/reverse-6 prior cuts, exact reverse H=6, complete high/low-word definitions, and a disjunction over all 2,415 admissible six-high selectors. The proof's ten explicit physical maps cover all selectors. This is a full-row **exact layer**, not closure of the entire frozen row.

With the supplied reverse H>=6 floor and the completed replayed exact 6, 7, 8 and 9 layers, this row has reverse **site-contact H>=10**. It does not have a certified H>=11. Its remaining local exact-10 frontier is **142 source orbits / 1,286 labelled masks**. Both its exact-H10 and H>=11 whole-row regions remained OPEN at one million conflicts.

### 4. Reverse site-contact H>=11 on two rows

On rows `0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296` and `8f9f3644c15b423945ba11e778540f6cf6234d095e7493ed24dd537f1c8db31a`, the complete exact 6--10 layers refute 2,415, 5,455, 6,435, 5,005 and 3,003 labelled masks per row, respectively. Their normalized 42-vertex input is `a9ed9506b66e66226d295a874f3502b06b72ec7997b7af925edfd3e436bc1cd3`, with 402 signed pins, contact index 9 and palette `[0,2,3,1]`.

All ten centre-fixing source-template maps and physical high-site sets were reconstructed for each row. Every destination query was byte-identical to its replayed donor query. Together with the already checked reverse H>=7 floor, exclusion of exact 7--10 gives **reverse site-contact H>=11**, not the root ticket statistic $H(r)$. There is no H>=12 claim here.

| exact layer | query SHA-256 | proof SHA-256 | coordinator replay |
| --- | --- | --- | --- |
| 7 | `c2089a27db02c8d845095688ba6dcec80f56dca9ede6a1114379f85c5cf465e0` | `dc7fd3891d8cf3e60b4631920ba292c18f0b9a499e36c926fc2049c731d41c64` | verified, 4.674 s |
| 8 | `6ae94997440c9b96716d088ccb1355e4ca92b1a0aee276b3602a13fc397e2041` | `f5988fe3851f27d9c6d449742b9652f0050a2499a98fa5dd9f605fde8bc437b6` | verified, 5.772 s |
| 9 | `7f0a6f60927755353f34c479b5c5fdf8c7eb397650e7d5805d8c554155c7798a` | `5921516b142d8c47557dbf382fde1212313e533b20665461f21d065807fbf768` | verified, 8.355 s |
| 10 | `655aeadbf6852b4ab8322d8830fad84a47b48128260fba56eb7107e3dd23e229` | `bca0866053c6277d0007f83eb374b2b84a947950b85b92dab31cd62ee5098184` | verified, 41.566 s |
| 11 (partial only) | `fcf787182ed58af3cb01a5e577749a7b17c038227ace60eb356a9de6d0d9500c` | `9e3fcde518542bc346cf37310782eee28ea3dfc2fd0b31cdb50832e071b76472` | verified, 16.213 s |

The partial exact-11 proof covers 64/153 orbits / 590 masks per row. **89 representatives / 775 labelled exact-11 masks per row remain unresolved in this older chain.** No local SAT or OPEN result is a K58 countermodel.

### 5. m6's exact H11p binary-split-tree residuals

H11p means the reverse H>=11 contact block plus the **same replayed 590 exact-11 physical exclusions**, built with fresh reciprocal-root auxiliaries. It is not the baseline formula and not an H>=12 claim.

m6 produced 14 terminal UNSAT proofs. Each was replayed twice by m6 and again here after checking the exact CNF/proof hashes:

| parent | exact terminal decomposition | residual left |
| --- | --- | --- |
| H11p `c488_021-002` | 14 UNSAT, 1 OPEN | `c488_021-032` |
| H11p `c488_021-001` | 14 UNSAT, 2 OPEN | `c488_021-032`, `c488_021-033` |

The cover audit re-streamed every root/cut/cube byte, checked every $\pm$ signed split, and regenerated both frontier receipts byte-for-byte. See `.ultramath/smwxbvh79/m6/frontier-c488_021-001.json` and `frontier-c488_021-002.json`.

The seven-branch subtree H11p **`c488_021-005` is closed** by its exact binary cover (`m6-closed-subtree-coordinator-replay.json`). Fresh native replay of those seven proofs took 148.6 s. The other seven terminal proofs also passed fresh replay (201.7 s). All fourteen are indexed in `m6-all-terminal-proofs-coordinator-replay.json`.

Seven separately receipted 300-second experiments were OPEN; their unfinished traces were discarded. None is evidence of UNSAT, parent closure or speedups. The **original three baseline reciprocal leaves remain open**. In particular, the C26 and H11p refinements do not close `c485_029-033`, let alone the row.

## Standard-kernel guard theorem

m1's original guard used `native_decide`, which was not accepted as a standard-kernel proof. The coordinator replacement `lean-check/ContactBridge.lean` has structural proofs of the two finite guard/cardinality equivalences and ordinary `decide` only for the tiny one-sided example. It preserves `floor_step` and `reverse_H11_of_exact6_to_exact10`.

```sh
lean results/wall-closeout-2026-11-26/lean-check/ContactBridge.lean
```

Lean 4.33.1 completed in about 2.5 s. `flagClauses_eq_meaning`, `flagClauses_true_iff`, `floor_step` and `reverse_H11_of_exact6_to_exact10` have exactly `[propext, Classical.choice, Quot.sound]` as axioms. There is no `sorryAx` and no `native_decide` dependency. The one-sided control is axiom-free. See `lean-check/standard-kernel-build.log`.

This proves the Boolean guard and layer-lifting argument only. The SAT refutations, classifier completeness, physical pins and ten maps remain external evidence; this file does not supply the whole Ramsey semantic bridge.

## Reconstructing the 775-mask versus 210-mask residual comparison

`compare_residual_masks.py` checks the coding using the supplied `portable.py` and all ten source actions. On `0404`, the attached `results/next-low-orbits.tsv.gz` lists 210 four-low placements in exactly 26 source-template orbits.

The old receipt uses 11 **high** bits at source indices 1--15. The new file uses 4 **low** bits at those same indices. The correct conversion is

$$\text{low\_mask}=65534\mathbin{\mathtt{XOR}}\text{high\_mask}.$$

Direct integer comparison is meaningless, and `(1<<15)-1` is the wrong complement because it also flips the unused bit 0. With the correct conversion, the 210 placements are contained in the old 775-mask residue.

**Conditional on independent verification of the newer exclusions**, the remaining frontier would be 210 masks / 26 orbits, having excluded 565 of the old 775 masks and 63 of its 89 representatives. This comparison does not run any new proof file, certify that exclusion, promote a lower bound, or apply 0404's new data to `8f9f`.

## Evidence not supplied

The new report claims reverse H>=10 on 93 rows, reverse H>=11 on 52, and both directional floors H>=11 on 0404. Those broader statements were **not** independently verified here. `K58_H_common_floor_01.zip` and `K58_H_common_floor_02.zip` were not attached. The solver bundle contains 289 JSON ledgers and two gzip files under `data/`, but **zero native DRAT files**. The other 21 proof archives are also absent.

Please supply at least the two common-floor archives for replay of the common cohort theorem. The 52-row stronger cohort also requires its companion archives.

## Reproduction pointers

- m3 complete layers: `.ultramath/smwxbvh79/m3/README.md`, `coordinator-replay.log`, `evidence/replay-summary.json`.
- m4 exact layer: `.ultramath/smwxbvh79/m4/REPORT.md`, `compose_eq6.py`, `out/eq6-compose/composition.json`.
- m6 split covers: `.ultramath/smwxbvh79/m6/REPORT.md`, `audit_frontier.py`, `closure-c488_021-005.json`.
- Fresh terminal proof replay: run `python3 results/wall-closeout-2026-11-26/check_m6_subtree.py`, then `python3 results/wall-closeout-2026-11-26/check_m6_all_terminals.py` from the repository root.
- Mask comparison:

```sh
PYTHONPATH="$PWD/.ultramath/smwxbvh79/m1/.deps" python3 \
  results/wall-closeout-2026-11-26/compare_residual_masks.py \
  --out results/wall-closeout-2026-11-26/residual-mask-comparison.json
```

Large proof artifacts remain in `.ultramath/smwxbvh79/`, including the retained m2, m3, m4, m5 and m6 evidence. This compact receipt directory is not raw-proof preservation.
