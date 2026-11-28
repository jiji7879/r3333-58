# Pre-registration: capped-conquest selection plus selective MCTS A/B

Written before any new probe or cubing run in this directory.

## Frozen inputs and scope

Only row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile `(16,16,14,11)`, charge 7, is used on the wall. The copied ordinary inputs must retain:
parent `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`, working `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38`, RUP/CAS prefix `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3`. The ordinary parent is a relaxation of the physical semantic row. No timing result, SAT result, or incomplete proof is a physical-colouring result. There will be no production sweep or other wall row.

The benchmark is the retained already-solved control with parent `50a187c65b7a5a9c839a95053a7e1133bbf697aa3806790d87b83bd1e7a65530`, working `356fd5ce1472e9ef078288032f7a1e3ceb885cc32af331abc766a6fea92bc269`, CAS prefix `ce64dbfe40c45bc82c8aa742e3caba5e50b6200dec62648f414598f6f64da856`. Its shape is fixed at root 4141 plus two depth-one splits (four leaves). This is a new cost-rollout policy experiment on the control, not a repetition of the old propagation-only rollout.

## Policy frozen before measurement

At every selected prefix, use the current-generic AlphaMapleSAT `MarchPysatPropagate` restricted to the exact recorded 896-literal control/wall arm-pair pool. Retain its `LIMIT_TOP_3` ordered shortlist. Obtain the ordinary current-generic MCTS full-rollout/two-simulation choice as the tie-breaker (reusing the retained exact control tree; running it fresh on the selected wall prefix). Put the MCTS choice first and append the other shortlisted variables in propagation order.

For every candidate, run fresh CaDiCaL 1.9.5 *both-sign* child probes using the exact working CNF and prefix. Probe cap is 20,000 conflicts, proof logging off. Select the candidate by the lexicographic key `(number of OPEN children, sum of conflicts_used, candidate order)`. Thus resolved leaves and both child costs matter; an all-OPEN tie is decided by the pre-obtained MCTS order, never by elapsed time or a post-hoc choice. SAT would be recorded as relaxation-level SAT_UNVERIFIED until its complete model was checked, never as a colouring model. No proof is inferred from a probe.

On the control, run the selected exact four-leaf cover afresh at 350,000 conflicts per leaf with eager proof logging and strict whole-byte additions-only DRAT replay against original parent+cube. Account separately for shortlist/MCTS preparation bomb, nonselected and selected probe work, final search, and checking. Compare with retained greedy (226,881 final conflicts) and both actual MCTS records without conflating simulation counts.

On the wall, select the not-yet-re-cubed depth-two leaf with the smallest retained 1,000,000-conflict CPU time: `[1413,-1417]`. Freeze its exact parent plus units `1413,-1417` by hash. Run *two* one-split cubers on this same prefix: the new cost20k/full20-two-simulation selector above, and the accepted shallow ten-simulation MCTS baseline. Each resulting pair of children gets a fresh 1,000,000-conflict/300-second eager-proof attempt. If a selected split is absent or cubing exceeds its cap, that route is OPEN cubing only. If both policies emit the same tree, search it once and say so. Cap the main full-rollout cubing at 1,200 seconds. Never infer nonexistence of a cover from that cap.

Replace exactly `[1413,-1417]` in the retained five-leaf frontier, audit the resulting full six-leaf binary covers, and retain per-query parent/proof hashes for every positive result. Stop any experiment whose individual proof exceeds 1,000,000,000 bytes. The expected total is at most 6,240,000 wall-search/probe conflicts (3*2*20,000 + 2*2*1,000,000) plus cubing and control work, comfortably below a 30-minute sequential leaf budget based on the retained 55–63 CPU-s/million measurements.

## Negative-result criterion and semantic separation

A timeout alone is not the deliverable. If the method does not improve the closed control, report the measured source of loss (probe overhead, all-OPEN saturation, wrong hard-side ranking, or unchanged tree) quantitatively. Wall all-OPEN saturation means the 20,000-conflict rollout has no discriminating conquest signal at this prefix; it does not rank true UNSAT cost and does not imply SAT/UNSAT. CNF performance, ordinary per-leaf certification, and physical-colouring semantics stay in separate sections. No row/profile/Ramsey closure will be claimed.
