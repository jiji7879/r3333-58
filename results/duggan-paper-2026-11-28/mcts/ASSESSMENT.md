# Duggan/AlphaMapleSAT applicability to the K58 wall

## Verdict

**A direct transfer of Duggan's 2024 AlphaMapleSAT cuber is not applicable to this four-colour encoding.  After the necessary rewrite to the current generic implementation and an arm-pair candidate filter, a small matched experiment did not improve on the repository's splitter, and no wall leaf closed.**  This is a bounded negative assessment of that proposal, not a proof that no MCTS policy can help and not a change to $51\le R_4(3)\le62$.

The useful precise obstruction is in Duggan's actual pinned 2024 source. Its prior array is sized by `order*(order-1)`, while its action map is sized by `2*MAX_LITERALS+1`. Duggan's two-colour setting makes these compatible. At K58, `order=58` gives only 3,307 prior slots, but there are $4\binom{58}{2}=6612$ physical colour literals and 13,225 actions. In a direct restricted-pool probe, the 2024 code raised `IndexError` while assigning its prior. Without the pool restriction, it did not emit even a depth-two cover on the known-solvable control in a 420-second cubing cap. The generic 2025/2026 rewrite removes this graph-specific assumption, but that is a code migration, not a drop-in use of Duggan's implementation.

After that migration:

* On the real top-ranked OPEN wall row, shallow MCTS produced a valid four-leaf cover and a valid selective depth-three refinement. **All four depth-two leaves and both new depth-three children stayed OPEN at $10^6$ conflicts each.**
* On one previously solved control parent, both greedy and MCTS covers fully closed with strict DRAT replay. The current generic MCTS using the full 20-step rollout and ten simulations required **284,528 conflicts versus 226,881 for greedy** ($1.2541\times$), 11.282 versus 8.835 CPU-s of leaf search, and **306.456 versus 0.720 seconds for cubing/preparation**. These are one-instance measurements, not a general slowdown theorem, but they supply no justification for a wall deployment.

## What Duggan actually contributes beyond existing C&C

Chapter 3 of Duggan's paper describes two relevant mechanisms:

1. Use AlphaMapleSAT's MCTS to choose split variables, stopping a branch when split+BCP+simplification has assigned a chosen number of variables.
2. Send only hard instances back for further cubing. Duggan's trigger was a proof larger than 7 GB, normally after 8--10 hours; cubes already solved are not re-cubed.

The AlphaMapleSAT preprint supplies the immediate prior

$$s(v)=\operatorname{prop}(v)\operatorname{prop}(\neg v)+\operatorname{prop}(v)+\operatorname{prop}(\neg v),$$

PUCT selection, nonterminal propagation-rate rewards, and choice of the action with the best long-term reward. Duggan's `MathCheckRamsey` code confirms the 7 GB threshold via `proofsize 7168`.

The repository already has fixed-depth two-sided lookahead, exact binary covers, fresh per-leaf workers, selective refinements, and DRAT export. Therefore, **only MCTS search/evaluation and the specific hard-leaf feedback rule were candidate new elements here.** Recommending cube-and-conquer, DRAT, parallelism, or $(1+\ell)(1+r)$ lookahead again would add nothing.

### Provenance qualification

Duggan's Ramsey repository pins `alpha-zero-general` commit `547eb661833d635a81255e444626e2dd6ac2b77a`; its driver defaults to two MCTS simulations. I fetched that exact commit. The separate public `AlphaMapleSAT` repository starts only in June 2025; its current commit here is `215224bb04c46b8c220f413a4c3e64962741812b`. The arXiv v1 text specifies 30 simulations and $c_{\mathrm{puct}}=5$, whereas the pinned code exposes defaults 10 and 10 and the Ramsey driver supplies 2. I therefore distinguish three things rather than claiming a historical reproduction:

* **2024 direct-source check:** exact Duggan-pinned code; direct cubing attempt and interface-failure control.
* **Current generic full-rollout control:** current code, 20-step extra MCTS horizon, two and ten simulations.
* **Wall pilot:** current code, ten simulations, shallow emitted-depth horizon, plus selective re-cubing.

Sources: [Duggan paper](https://uwaterloo.ca/computational-mathematics/sites/default/files/uploads/documents/research_paper_conor_duggan.pdf), [AlphaMapleSAT v1](https://arxiv.org/abs/2401.13770v1), [Duggan's Ramsey repository](https://github.com/ConDug/MathCheckRamsey), [pinned 2024 cuber](https://github.com/piyush-J/alpha-zero-general/commit/547eb661833d635a81255e444626e2dd6ac2b77a), and [current cuber commit](https://github.com/piyush-J/AlphaMapleSAT/commit/215224bb04c46b8c220f413a4c3e64962741812b).

## Exact cover and certificate interface

For any CNF $F$ and literal $x$,

$$F\equiv(F\land x)\lor(F\land\neg x).$$

Iterating at any OPEN leaf gives an exact cover regardless of the split heuristic. Restricting the **candidate pool** does not restrict models: both signs of every chosen split remain. An UNSAT leaf must nevertheless be certified against the original parent plus its cube, not inferred from an incremental status or a conflict cap.

My experimental `ams_tree.py` applies only the recorded candidate pool. `audit_cubes.py` independently checks that every internal node has complementary literal children and that no sibling/leaf is missing. `run_leaves.py` uses fresh CaDiCaL calls and, on actual UNSAT, joins the existing RUP/CAS prefix to the ordinary binary leaf proof, removes binary `d` records while preserving every addition, invokes `drat-trim -i -U` with no warning suppression, and retains the query/proof hashes. A second independently built checker repeats every retained positive replay.

This is not a new mathematical certification principle—the repository already describes it—but it is the exact interface needed by this transfer. No parent claim is allowed until every cover leaf is certified and a parent-level proof/export is checked.

## Real wall-row experiment

Row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile $(16,16,14,11)$, charge 7, is the top row of the repository's 2026-11-28 wall ranking. I used the exact retained ordinary parent and working formula:

| binding | value |
|---|---|
| parent SHA-256 | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` |
| working SHA-256 | `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38` |
| RUP/CAS prefix SHA-256 | `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3` |
| variables / parent clauses / working clauses | 19,533 / 184,335 / 184,650 |
| existing greedy splits | root 1413; negative 2206; positive 1426 |
| MCTS splits, 10 simulations | root 1413; negative 1014; positive 1417 |
| candidate pool | the existing 896 arm-pair literals |

The independently checked four-cube cover had every leaf run afresh with eager proof logging and a $10^6$-conflict/300-second cap. All four returned OPEN at the conflict cap; the unfinished proof streams were not retained as evidence. The retained greedy receipts at the same budget are also four OPEN. Search CPU was 237.208 s for MCTS versus 272.629 s in those older receipts, but MCTS cubing itself took 66.957 s. Since no leaf reached a verdict, this is not a measured speedup or a proof of better cubes.

I then selected the hardest OPEN MCTS leaf by measured search time, `[-1413, 1014]`, and re-cubed it once. MCTS chose 1421. Both children again returned OPEN at $10^6$ conflicts. The exact remaining frontier is thus

```text
[-1413, -1014]
[-1413, 1014, -1421]
[-1413, 1014, 1421]
[1413, -1417]
[1413, 1417]
```

`results/wall-refined-frontier-audit.json` verifies that this five-leaf ragged tree is a complete binary cover. **This is a decomposition receipt, not five UNSAT results and not a row closure.** No full-rollout MCTS wall run was made; the wall verdict above is explicitly for the shallow variant plus its selective refinement.

## Solvable matched control: where cube quality can actually be compared

The wall experiment alone cannot rank splitters if everything exhausts its budget. I therefore used the already-known control case `0f9ba81047f417888a4c5291b6529e2ebca30f08d0412361e6e86b53b859580d`, without changing its recipe. Fresh preparation reproduced exactly:

* parent `50a187c65b7a5a9c839a95053a7e1133bbf697aa3806790d87b83bd1e7a65530`;
* working `356fd5ce1472e9ef078288032f7a1e3ceb885cc32af331abc766a6fea92bc269`;
* RUP/CAS prefix `ce64dbfe40c45bc82c8aa742e3caba5e50b6200dec62648f414598f6f64da856`;
* greedy splits 4141, 4909, 5137 and four expected DRAT hashes.

Both methods had the same 900-literal candidate pool, four-leaf depth-two tree, fresh CaDiCaL 1.9.5 worker, 350,000-conflict cap, and strict replay. All leaves in every row below are independently `CHECKED_UNSAT`.

| policy / second split $(-,+)$ | conflicts by cube (root-negative pair, root-positive pair) | total conflicts | search CPU-s | cubing/prepare s |
|---|---:|---:|---:|---:|
| greedy 4909 / 5137 | 110065, 1 / 116814, 1 | **226,881** | **8.835** | **0.720** |
| shallow MCTS-10, 4793 / 4149 | 21385, 164189 / 511, 123625 | 309,710 | 12.788 | 102.183 |
| full-rollout MCTS-10, 4937 / 4149 | 3887, 156505 / 511, 123625 | **284,528** | **11.282** | **306.456** |

The full-rollout two-simulation run generated the same tree as the shallow ten-simulation run in 40.643 s. The full ten-simulation negative branch changed to 4937. Only those two new leaves had to be searched; the positive cubes reuse identical query/proof bindings. For each full-rollout cover above, all four resulting proofs are valid. The greedy proof hashes reproduce the repository's earlier benchmark bytes exactly.

A separate $K_6$ two-colour Ramsey control produced a nontrivial additions-only RUP certificate, accepted with return code 0, exactly one `s VERIFIED`, no warning/error, and 0 RAT lemmas. The same proof against satisfiable $K_5$ returned `s NOT VERIFIED`. Across all experiments, `results/second-checker-summary.json` records **11/11 successful second-binary replays and zero failures** (ten distinct K58 leaf proofs plus the $K_6$ control). `selftest.py` also tests invalid covers, ragged covers, malformed binary proofs, query-header uniqueness, totals, and all eleven second-checker receipts.

## Applicability by requested target

| target | assessment |
|---|---|
| **(i) proving small-wall rows UNSAT** | **Not demonstrated and not ready to deploy.** The real pilot leaves a checked five-leaf OPEN frontier. The solvable control's MCTS cover was worse in conflicts and vastly more expensive to construct. Duggan's 7 GB re-cube rule is a resource heuristic, not a new structural constraint. |
| **(ii) proving Lemma L or reducing profiles** | **No transfer.** MCTS changes a CNF search tree only; it supplies no incidence-level fact about critical degrees, no profile elimination, and no progress on Lemma L. |
| **(iii) finding a K51 colouring** | **No direct benefit established.** This is an UNSAT-oriented cubing heuristic. If any leaf returned SAT it would still require a complete model check on all original clauses and the separate K51 semantic bridge. No model was produced here. |
| **(iv) proof-certificate tooling** | **A concrete but non-novel implementation cross-check.** Exact tree audits, fresh leaf DRAT, additions-only normalization, and second-checker receipts worked. These should be reused as protocol, not advertised as new Ramsey coverage or a new solver improvement. |

## Concrete next experiments—not a production sweep

1. **Do not run the pinned 2024 binary on K58.** If a historical implementation matters, first isolate its two-colour prior/action layout in unit tests over $4\binom n2$ literals. The current generic rewrite is the appropriate codebase for any further experiment.
2. **Gate further MCTS work on a second known-solvable parent from a different template/profile.** Pre-register identical parent/candidate pools, the full rollout, two simulations (Duggan's driver default), and complete proof verification. Continue only if total conflicts and end-to-end CPU including cubing both beat greedy. The first such control failed that gate at ten simulations; it has not been tested at two on a second parent.
3. **If that gate ever passes, run exactly the same top wall row with full rollout/two simulations and the same $10^6$ leaf cap.** Keep the five-OPEN-leaf frontier as the comparison; do not sample the other 11,584 rows and do not turn a cubing/SAT timeout into UNSAT evidence.
4. **Do not adopt propagation count as a proxy for wall difficulty without calibration.** The control already shows that a deeper propagation-reward rollout improved the MCTS tree relative to its shallow version but still trailed one-step greedy. A useful alternative would require a separate, independently checked reward experiment based on capped conquering cost; that is new research, not Duggan's method.

The present evidence favours structural clause development for Lemma L/the small wall over an MCTS production campaign.

## Limitations

One wall row and one solvable control are not enough to infer a universal ranking. Timings are sequential observations on a shared four-core VM, not 128-core throughput. The wall greedy receipts were retained historical runs on the identical formula/budget, whereas MCTS wall searches were fresh; control searches were all fresh. Fixed depth two was used for exact A/B covers, not Duggan's assigned-variable stopping threshold. The Duggan-pinned two-colour code was not rewritten internally to fix its action layout; the current generic implementation was used after the source incompatibility was established. No full-rollout wall run, K51 run, production sweep, new profile proof, or Ramsey-bound inference is claimed.
