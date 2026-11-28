# Selective capped-conquest re-cubing on the K58 wall

## Outcome

**The new cost-rollout route did not produce a certified or demonstrated faster wall decomposition.** I actually ran current-generic AlphaMapleSAT and a genuinely different two-sided CDCL cost rollout on a new subtree of the exact wall parent. Both cubers emitted covers. All four final wall children stayed **OPEN at 1,000,000 conflicts**. The wall obstruction is precise: every candidate child saturated the 20,000-conflict cost probes, so cap-normalised conquest cost is identical for all candidates; the raw policy selected a different split only because CaDiCaL overshot its cap by zero or one conflicts. That overshoot is not a conquest-cost signal.

The closed control gives a useful bounded calibration, not a deployment case. The hybrid selected `4937/4149`, and all four fresh leaves were strictly certified (`CHECKED_UNSAT`) at a total of **284,528 conflicts**. This improves final conflicts by 8.13% over the actual two-simulation setting's `4793/4149` tree, and reproduces the ten-simulation setting's tree with 3.13x less preparation time than that ten-simulation run. It is nevertheless **1.2541x greedy's final conflicts**, and preparation plus leaf search is **119.012 s**, versus **9.557 s greedy** and **53.444 s for the actual two-simulation setting**. There is no favourable overall benchmark against the incumbent greedy splitter.

No wall leaf proof, physical-colouring conclusion, profile exclusion, row closure, or Ramsey-bound change is claimed.

## 1. Frozen identities and actual software

Only wall row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile `(16,16,14,11)`, charge 7, was searched. No other wall row or production sweep was run.

| input | SHA-256 |
|---|---|
| ordinary wall parent | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` |
| original working CNF | `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38` |
| RUP/CAS prefix | `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3` |
| target working CNF (`1413,-1417` appended as units) | `b02bdad1b719a4f5e333437f407643c180c222e15b73bf60811dc2c1795cf6ec` |
| closed-control parent | `50a187c65b7a5a9c839a95053a7e1133bbf697aa3806790d87b83bd1e7a65530` |
| closed-control working CNF | `356fd5ce1472e9ef078288032f7a1e3ceb885cc32af331abc766a6fea92bc269` |
| closed-control RUP/CAS prefix | `ce64dbfe40c45bc82c8aa742e3caba5e50b6200dec62648f414598f6f64da856` |

The exact baseline archive `k58-massive-solver.zip` has SHA `cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a`. The ordinary parent and working/CAS plan are unchanged. AMS was the copied current-generic source at commit `215224bb04c46b8c220f413a4c3e64962741812b`, using the accepted `ams_tree.py` adapter and exact recorded 896-variable arm-pair pool. python-sat was `1.9.dev22`; final search used fresh CaDiCaL 1.9.5 processes. `PREREGISTRATION.md` was written before probes and fixes the root, subtree, candidate order, caps, selection rule, and accounting.

### Necessary two-simulation scope correction

The setting named `rollout-extra=20,sims=2` is **not an observed depth-20 MCTS rollout**. In current `MCTS.py`, simulation 1 initialises the root `Ps`; simulation 2 expands root actions and initialises child `Ps`. At a fresh nonterminal node, no simulation remains to expand a child's action, so effective expansion depth is at most one. The wall run also printed `NO EXPLORATION`. The genuinely different simulations here are the fresh, two-sided capped CaDiCaL conquest probes. Nothing follows about higher-simulation or actually deeper MCTS.

## 2. Pre-registered CNF-performance policy

At each selected prefix:

1. Use current-generic `MarchPysatPropagate`, restricted to the recorded pool, and retain its ordered top-three BCP shortlist (`LIMIT_TOP_3`). Do not change CNF clauses or discard either sign.
2. Put the exact two-simulation AMS choice first, then the other shortlisted variables in BCP order.
3. For each candidate, run fresh CaDiCaL on both children at 20,000 conflicts, proof logging off, and save/hash the exact effective working query before solving.
4. Select lexicographically by `(number of OPEN children, sum of conflicts_used, candidate order)`.
5. Run the selected final children afresh with eager proof logging. Every final query is original parent plus its cube; every positive result requires ordinary strict `drat-trim -i -U` replay after deletion-record stripping, with no warning suppression.

An OPEN probe was used only as a search heuristic. Probe UNSAT text on the closed control was not treated as a certificate; certification comes only from the separate final eager-proof runs below.

## 3. Closed control: performance and CNF certification

The retained control root was fixed at `4141`. The actual shortlists and selections were:

* prefix `[-4141]`: BCP `[4793,4937,4265]`; two-simulation choice first; selected **4937**. At 20,000 conflicts, 4937's positive child used 3,887 conflicts and its negative child stayed OPEN. Every child of 4793 and 4265 stayed OPEN.
* prefix `[4141]`: BCP `[4149,4551,3441]`; selected **4149**. Its positive child used 511 conflicts and its negative child stayed OPEN. For 4551 the corresponding values were 1,312 and OPEN; both 3441 children stayed OPEN.

Notably, **greedy's second splits 4909 and 5137 are absent from these AMS top-three shortlists**, so this candidate restriction cannot recover the incumbent greedy tree at these nodes.

The selected cover has four exact leaves and cube SHA `2410a437a0f302cb6eabc057b28a2d5f748a64b13f0ee79bac214e4459cb5c0e`. Fresh final searches reproduced the conflicts on the nose: `156505, 3887, 123625, 511`, total **284,528**. Every leaf reached an ordinary UNSAT result and passed strict whole-byte additions-only RUP replay: return code 0, exactly one `s VERIFIED`, zero warnings/errors, and zero RAT lemmas in core.

### Matched cost, including the rollout policy

The following excludes checking time from every row so preparation and search use the same scope. Component sums combine separately measured commands on the shared VM; they are not repeated-run confidence intervals.

| policy | second splits (- root / + root) | cubing/preparation elapsed s | final conflicts | leaf-search elapsed s | preparation + search s |
|---|---:|---:|---:|---:|---:|
| retained greedy | 4909 / 5137 | 0.720 | **226,881** | 8.837 | **9.557** |
| configured extra20, two simulations | 4793 / 4149 | 40.643 | 309,710 | 12.801 | **53.444** |
| configured extra20, ten simulations | 4937 / 4149 | 306.456 | 284,528 | 11.337 | **317.794** |
| new hybrid (cached exact two-sim choice + new shortlist/probes) | 4937 / 4149 | **97.879** | 284,528 | 21.134 | **119.012** |

The hybrid's 97.879 s preparation consists of 40.643 s exact two-simulation cubing (cost included even though its retained cube was reused), 36.087 s for new shortlist construction, and 21.149 s for new two-sided probes. Those probes used 185,721 conflicts; probes plus final searches used 470,249 conflicts. Fresh final search/checking took 47.27 s command elapsed in total, of which the four worker elapsed times sum to 21.134 s. Old and new checking envelopes are therefore not compared.

This is a real control calibration: the cost rollout extracts the better known MCTS tree without ten simulations, but is still decisively worse than greedy and worse end-to-end than the cheap two-simulation setting. One control is not a general performance theorem.

## 4. Actual wall selective re-cube A/B

The pre-registered target was the **previously untouched `[1413,-1417]` leaf**, not the prior negative-side recube. Both current-generic cubers ran on the identical target working CNF `b02bdad1…` and completed:

| cuber | emitted split | cubing elapsed s | local cube SHA-256 |
|---|---:|---:|---|
| shallow, ten simulations | 1426 | 27.437 | `2cfe4f1fe9a4261a4900b8750250dd80db2e74c6643d2eefd2dce84001bbfd47` |
| extra20 setting, two simulations | 1426 | 21.071 | `7477ae62fed1bb130a60d11e2f424e10849b46ddd5a9e33edf99622e3d2fe85a` |

The two local files differ only in line order. There was no cubing timeout and no nonexistence inference.

The BCP shortlist was `[2744,1222,1426]`, reordered as frozen to `[1426,2744,1222]`. All six candidate children stayed OPEN. Raw conflict sums were 40,001 for 1426, **40,000 for 2744**, and 40,001 for 1222; hence the frozen raw rule chose 2744. This is exactly the undesired stopping-artifact preference described above, not evidence that 2744 was easier.

Both final pairs then ran at 1,000,000 conflicts per child, with 300 s worker caps. All stayed OPEN, so no proof exists for any of them.

| policy | split | final conflict total | final CPU s | final elapsed s | preparation + final elapsed s | whole-command CPU s |
|---|---:|---:|---:|---:|---:|---:|
| raw hybrid | 2744 | 2,000,002 | 131.044 | 156.378 | **201.656** | **159.500** |
| matched shallow AMS | 1426 | 2,000,002 | 153.414 | 161.632 | **189.068** | **172.250** |

The single raw run has less measured CPU but 6.66% more preparation-plus-search elapsed time. It saves no conflicts and closes no leaf. This mixed observation is **not an independently established faster/easier decomposition**, and no repeated-run speedup is claimed.

Replacing exactly `[1413,-1417]` in the retained five-leaf frontier gave two independently audited full six-leaf covers:

* raw 2744 frontier: SHA `1e1be8651a05725447fbf2855794c4bda96af80a164af4d5207fba2bf9573666`;
* 1426 frontier: SHA `05e0b9c28c4ee1ed67a1497b382bedb6f5a325ac746387bcbb2dc57de86403f7`.

These are exact ragged binary decompositions, not refutations. The other four inherited leaves remain OPEN as before.

### Post-hoc cap-normalisation diagnostic (not a rewritten experiment)

`analyze_results.py` independently recomputes ranking with every OPEN child charged exactly the common 20,000-conflict cap, rather than its zero/one-conflict overshoot. Control selections remain 4937/4149. On the wall all three keys become exactly `(2 OPEN, 40000)` and the pre-obtained MCTS order chooses **1426**. No new leaf search is needed for that diagnostic: the identical 1426 pair was already measured and is OPEN. The raw 2744 artifacts are retained unchanged to prevent post-hoc replacement of an unfavourable experiment.

## 5. Exact CNF certificate bindings (closed control only)

Below are the original-parent query and the **checked additions-only normalised proof** hashes. Raw binary leaf and joined-prefix proof hashes are also explicit in every receipt and in `results/independent-byte-audit.json`.

| cube | original-parent query SHA-256 | normalised proof SHA-256 |
|---|---|---|
| `[-4141,-4937]` | `e7fa2b2a5dc9d2a783b0a187a7fb902c4b6f133bc65b63bc66299959fb8c65a5` | `6e6f37bb56bbdba8c0f66b0718ff55c0a7ab0f08f266bbf98dfed5ff54e4f9ae` |
| `[-4141,4937]` | `85f1627d335a173d2b9759d5219493d86735321b155840360f1dbba3f69a6f39` | `f7e33a4fa07b1a77fdaf05260d4d2b8c062a84b6aa3a43e46a9a39eca0481070` |
| `[4141,-4149]` | `47d987f3c1421151685eef89e1005ef47574076db989bc508ac3b77a9522b583` | `d7b39bde56aaaaa52cb365d04b1e7ec9e0a2b9e4be1ee54a948c5cef4c7204b8` |
| `[4141,4149]` | `683c840a08ad39abe78f3940d20994dbc5f33f8c73ac7e01e5c16ef0f05498b6` | `fc732beccd8b23e0fe8f842258a5cf701045d928e242f42b1331276b249ff3d9` |

Every wall query also has an explicit hash and no proof hash (because there is no proof):

* `[1413,-1417,-2744]`: `42a6f8683c016f5e48235d73c1f4bf548f23395b8e9e420cf391f07922ed8d22`;
* `[1413,-1417,2744]`: `f4f8fd0878081dd8f8ee3e25738b2ee44f55d015780aca09fcdb4adb53b58182`;
* `[1413,-1417,-1426]`: `62e0dbda99c2cbfb06e2fd1a9fca0b4c69650861db535e8086a334aa991efe22`;
* `[1413,-1417,1426]`: `4f082a3b211da0624d55a1ce525a4e96192dc9f485b0c03c4195c2ed1fa7196d`.

`analyze_results.py` independently reconstructed and compared whole bytes for **26 queries** (8 final + 18 probes), recomputed hashes for **12 control proof files**, rechecked all strict logs, re-audited three full binary covers, and checked all frozen input identities. Every proof is below 1,000,000,000 bytes. The retained `drat-trim` binary has SHA `a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066`.

## 6. Strict separation from physical colourings

* **CNF performance:** all timings, conflict counts, split choices, and OPEN outcomes above.
* **CNF UNSAT certification:** only the four closed-control parent+cube queries in Section 5. Their checked proofs do not certify the wall parent. Neither a timeout nor a probe status is a proof.
* **Physical colourings:** no new result. The ordinary wall parent is the first-tier `tables=True,total_critical=True,full_root=False` **relaxation** of the semantic row. Even a future complete UNSAT cover would require the unfinished full-parent Lean/DIMACS assembly before any physical-row statement. SAT of the relaxation would likewise not supply a physical model. No such SAT result occurred here.

## 7. Precise structural blockers and limits

1. **No cap-normalised wall cost signal:** all six 20,000-conflict candidate evaluations had both children OPEN. Their normalised cost vectors are identical by definition. These probes cannot rank true conquest cost; raising the cap is an untested new experiment, not a conclusion that “more time” will work.
2. **Cap overshoot fabricated the raw choice:** `conflicts_used` may be 20,000 or 20,001 on OPEN. Choosing 2744 from those values measures stopping mechanics, not difficulty. The actual 1,000,000-conflict runs did not justify the raw preference with a verdict or conflict saving.
3. **Shortlist exclusion on the control:** greedy's 4909/5137 were absent. The restricted policy can improve MCTS choices yet remain structurally unable to select the observed incumbent at those nodes.
4. **Two simulations are not depth-20:** the source-level depth-one ceiling means this experiment does not test the imagined deep MCTS rollout. It tests the exact setting plus new CDCL probes only.
5. **No wall certificate or robust runtime win:** all final statuses are OPEN; one shared-VM run gives mixed CPU/wall observations, not an independently established speedup.

The eight completed experimental command envelopes total **496.24 elapsed-s (component sum)** and **404.88 CPU-s**, with 4,120,006 wall probe/final conflicts. This stayed below the 30-minute/6,240,000-conflict wall envelope in `PREREGISTRATION.md`. An initial AMS invocation failed immediately because the SAT virtualenv omitted NumPy; it did no search. The accepted launcher convention (system scientific interpreter plus existing python-sat site-packages) fixed this without installation. The successful rerun log is retained; that rerun overwrote the immediate startup-failure log, so no surviving original failure log is claimed.

## 8. Reproducibility and source reconciliation

Start in `.ultramath/smwzzs8qs/m2/`.

* `PREREGISTRATION.md`: frozen policy and resource limits.
* `inputs/cost-select-run.py`: byte-preserved source used for the raw runs, SHA `88d6ff5112abbbe7f511ce2a4751eec26afe36e17fcd5fa6d5f4dbc2f427b0f3`.
* `cost_select.py`: only a post-run descriptive boolean fix (`tie_broken_by_preregistered_mcts_order` previously also marked a unique first-candidate win as a tie). Selection keys and emitted cubes are unchanged; raw result files were not rewritten. Current SHA is in the manifest.
* `analyze_results.py`, `results/summary.json`, `results/normalized-selection.json`: independent arithmetic, byte audit, and cap-normalisation diagnostic.
* `results/control-cost20k-final-leaves/*/receipt` data and whole logs: exact control query/proof bindings.
* `results/wall-positive-recube/`: both cubers, all probe data, final OPEN receipts, exact full-frontier audits.
* `REPRODUCE.md`: verification commands and exact environment. `SHA256SUMS` files bind inputs, scripts, report, and results after all edits.

Run `python3 analyze_results.py` and `sha256sum -c SHA256SUMS` for local integrity. The former regenerates the compact JSON reports from retained whole artifacts; it does not simulate a successful wall proof.
