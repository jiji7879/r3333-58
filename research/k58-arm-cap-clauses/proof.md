**Status: NOT YET a general, production-ready solver improvement.** The work establishes one sound general constraint schema with independently reproduced isolated gains, a stronger measured phase policy on the selected panel, and a negative hard-row result for the Glucose-style reducer. The ledger goal remains open because no robust cohort-wide or end-to-end certificate-producing improvement was established.

# Scope and outcome

The inputs are the 1,300 historically completed `full_root=true` K58 rows, not the unresolved wall profiles. Nothing here is a new SAT model, row closure, upper-bound improvement, or result about $R(3,3,3,3)$. Only small panels were run; no 1,300-row campaign occurred.

The main result is not a new counting theorem. It is a compact **selector encoding** of the existing $4+4+5<14$ argument that is materially better than the direct hitting banks on some inputs and worse on others. The best measured configuration overall is phase guidance on the unchanged formula, not a clause bank.

# 1. General `two5` encoding

Let $g=g_{x,c}$ be the original forward guard requiring at least 14 colour-$c$ neighbours of $x$ in its three other root arms. Write $n_B$ for the realised colour-$c$ support in one such arm $B$. Since internal support edges have only two available colours, $n_B\le5$ by $R(3,3)=6$; no arm classification is needed. Under $g$, the three supports are consequently $(4,5,5)$ or $(5,5,5)$.

For each arm introduce a fresh selector $q_B$ and a fresh sequential-counter encoding of

$$q_B\ \Longrightarrow\ n_B\ge5,$$

with fixed positive spokes included in $n_B$ and fixed unavailable spokes omitted. Then, for every pair of other arms $B,D$, add

$$\boxed{\neg g\ \lor\ q_B\lor q_D.}$$

Every original model extends: with $g$ false choose every $q_B=0$; with $g$ true choose $q_B$ on two actually full arms. Each true selector admits the standard satisfying extension of its counter. The encoding therefore does not add or remove original physical models. It is an implicational extension, **not** a bank of old-variable DRAT clauses.

Rank 1300 adds 8,533 clauses and 4,923 fresh variables. The deterministic original-parent preservation and all auxiliary scopes were checked. The portable generator is [two5_encoder.py](work/two5_encoder.py).

## Independently reproduced performance

On original rank 1300, seed 0, the coordinator regenerated the exact augmented CNF, SHA-256 `fe9de879d99b320c57c7d90582842a532a045da9c3d90c8df5880d96498eb9af`, and reproduced its complete solver statistics:

| engine | stock conflicts | `two5` conflicts | change | stock → `two5` search CPU |
|---|---:|---:|---:|---:|
| CaDiCaL195 / PySAT 1.9.dev22 | 883,977 | 796,760 | **−9.87%** | 44.351 → 39.015 s (**−12.03%**) |
| native CaDiCaL 2.1.2 | 875,852 | 824,152 | **−5.90%** | 60.260 → 58.400 s (**−3.09%**) |

The coordinator's fresh PySAT run also reproduced 1,296,311 decisions and 98,781,013 propagations, versus stock 1,404,609 and 108,305,135. Generation takes about 0.45 CPU-s, separately from search.

This is only an isolated improvement. PySAT rank 1299 and rank-1300 seeds 1 and 2 regressed; the seed-0 three-row aggregate has fewer conflicts but higher total CPU; native rank 1200 has higher CPU and wall time despite slightly fewer conflicts. The native three-row CPU result remains mixed. No universal or production-default claim follows.

The direct lower-four/lower-nine counters, simple per-arm five-caps and large direct physical forms do not solve the performance problem either. Compact support-distribution encoding and policy/seed selection matter more than merely adding valid clauses.

## Soundness checks actually run

- All 32,768 two-colour $K_6$ colourings exhaustively checked; twelve $K_5$ witnesses establish sharpness at five.
- All 216 integer support triples and 220 active/inactive abstract selector extensions checked, including the total-13 counterexample $(5,4,4)$.
- Original CNF body and augmented hash checked byte-for-byte; all 168 pair-selector clauses on rank 1300 checked.
- Fresh coordinator solve reproduced the exact augmented-CNF statistics.
- A selected original-parent direct lower-bound proof was independently replayed with `-i -U -W`: all 16,661 normalized proof bytes consumed, one `s VERIFIED`, zero warnings/errors, zero RAT lemmas.
- The member's broader counter exhaustion (126,144 physical assignments on the actual gadget shapes) was read, but not independently repeated by the coordinator.

See [two5-finite.json](checks/two5-finite.json), [two5 coordinator receipt](work/m1-coordinator-r1300-two5.json), and [generation receipt](work/portable-two5.out). The two5 result is accepted in the ledger as a general mathematical schema plus a measured special case—not as a cohort-wide performance theorem.

**Certificate gap.** No original-parent DRAT derivation prefix for the new selector/counter definitions and pair clauses has been implemented. Mathematical model extension is not the same as a production certificate pipeline. A 1,300-row deployment should wait for that prefix and a representative full augmented-to-original proof lift.

# 2. Explicit phase guidance has the stronger measured panel

The accepted phase policy is exactly:

```python
solver.configure({"seed": seed})
solver.set_phases([-v for v in range(1, formula.nv + 1)])
answer = solver.solve_limited()
```

In the pinned PySAT binding, `set_phases` also sets `lucky=0` before writing per-variable forced phases. It changes no CNF clause and therefore no logical constraint.

Across the six completed seed-0 row pairs:

| measure | stock | explicit all-false | change |
|---|---:|---:|---:|
| conflicts | 6,029,773 | 5,283,249 | **−12.38%** |
| search CPU-s | 332.211 | 302.258 | **−9.02%** |

The coordinator independently recomputed this aggregate and reproduced rank 1300 exactly: 745,335 conflicts and 93,044,313 propagations, versus stock 883,977 and 108,305,135. At cap 800,000, guided rank 1300 was UNSAT while stock was OPEN. The K5 controls remain SAT and K6 UNSAT unchanged. The phase report's deletion-only correction and warning-free full-proof receipt were inspected; the large proof bytes were deleted only after that accepted replay, so the coordinator does not claim a fresh second replay of that deleted stream.

Individual regressions remain: rank 1298 conflicts increase slightly, and rank-1300 seed 1 increases by 6.02% with higher CPU. The phase subset was selected mainly on small historical proof size, so its aggregate is descriptive, not a cohort estimate.

**Do not substitute native `--no-phase`.** Fresh native tests gave 928,042 conflicts for `--no-phase`, 831,681 for `--no-phase --forcephase`, versus 883,977 stock and 745,335 explicit all-false. The API writes `phases.forced` and disables lucky phases; the CLI default interacts differently with saved/target phases. The accepted phase runner is [phase_pilot.py](work/phase_pilot.py).

Combining `two5` with all-false is not a synergistic improvement: rank 1300 took 847,047 conflicts, worse than either mechanism alone. Keep the policies separate.

# 3. Glucose-style learned-clause deletion

The supplied patch was rebuilt from its pinned CaDiCaL 1.9.5 source archive and five-file patch. The option remains off by default. It only changes which redundant learnt clauses are deleted; it does not add or delete structural input facts.

The fresh matched original rank-1300 run used rebuilt stock/hybrid binaries, identical input hash and seed, cap and proof logging:

| measure | stock 1.9.5 | Glucose hybrid | change |
|---|---:|---:|---:|
| conflicts | 883,977 | 941,707 | **+6.53%** |
| user CPU-s | 50.530 | 54.901 | **+8.64%** |
| DRAT bytes | 90,064,584 | 110,327,620 | **+22.50%** |
| peak RSS KiB | 68,172 | 106,912 | **+56.83%** |

The package's own bounded results are mixed too: strong improvements on some signed/local controls, regressions on others, no additional unsplit-row completions, and increased total unsplit CPU. On the completed hard-row test there is no support for enabling the reducer by default. This is one row and seed, not a universal judgment of the patch. Its hybrid proof has not received the clean core replay described next; the stock proof has.

The 90,064,584-byte stock DRAT first verified with visible pseudo-unit-deletion warnings. A deletion-free normalization of that core then passed `-i -U -W -t 600` with all 24,356,572 proof bytes read, one `s VERIFIED`, no warnings/errors and 0 RAT lemmas. An earlier full deletion-free check timed out at 300 seconds and is not counted. See [full stock proof receipt](checks/stock-full-proof.json) and [paired performance receipts](work/glucose-rank1300/receipts.json).

# 4. Other tested clause observations

- **Global degree cap.** $R_3(3)=17$ implies maximum colour-degree 16; the root colour has at most 15 cross-arm neighbours. On native rank 1300 this reduced conflicts from 875,852 to 828,729 (−5.38%) but CPU only from 52.421 to 51.554 seconds (−1.65%). This is a small one-row lead, not a replicated improvement.
- **Simple five-caps.** On the same completed comparison they increased conflicts to 888,836, propagations to 122,803,884 and CPU to 56.597 seconds. Guarded caps were nearly inert at smaller budgets; per-arm lower-four and pair-nine counters did not pay for their size.
- **Old direct paired-arm bank.** On the native completed comparison it increased conflicts to 968,863 and CPU to 61.316 seconds.
- **Signed size-two support certificates.** The independent mathematics and all 3,709/2,995 support checks on ranks 1200/1300 passed, including scope-negative controls and a warning-free representative original-parent replay. It was nevertheless rejected as a solver improvement: six-pair CPU increased 6.45% and wall increased 5.83%, with much worse selected subsets. See [rank-1300 finite verification](checks/m4-review/finite-1300.out) and [strict representative log](checks/m4-review/strict-candidate.log).
- **Proof-derived checkpoints.** A fresh stock full-row core contained 5,245 original clauses and its 15 final physical units let the same stock binary refute that exact source row in 0.04 CPU-s. That is not a transferable clause family or a general speedup. Core-only solving remained OPEN at 60 seconds, and no transfer or automatic relabelling was established.

# 5. What was not done

No production ledger, queue, code package or 1,300-row campaign was changed. No new SAT model or wall-row closure was found. No Lean or pure-kernel proof was requested or claimed. The historical 177.9 GB proof set was unavailable; the reported core observations come from one newly generated and replayed stock proof, not historical proof mining. Not every bound in every one of the 1,300 rows was individually replayed. Timing runs deliberately omit proof logging unless stated, and wall time on the shared VM is kept separate from conflicts and process CPU.

# Reproduction

Use the pinned python-sat environment. Generated output directories must be fresh.

```sh
PY=.scratch/k58/.venv/bin/python
$PY -B research/k58-arm-cap-clauses/work/two5_encoder.py 1300 \
  --mode two5 --out .scratch/arm-cap-research/portable-two5.cnf
python3 research/k58-arm-cap-clauses/checks/verify_two5.py

$PY -B research/k58-arm-cap-clauses/work/phase_pilot.py generate \
  --source "$PWD/.scratch/hard1300-paired-arm-v1/src/hard-study" \
  --rank 1300 --out .scratch/arm-cap-research/phase-r1300
$PY -B research/k58-arm-cap-clauses/work/phase_pilot.py run \
  --parent .scratch/arm-cap-research/phase-r1300 --policy all-false \
  --seed 0 --conflicts 1200000 \
  --out .scratch/arm-cap-research/phase-r1300-result.json
```

The complete working notes are in [notes.md](notes.md). The Siege ledger records the general `two5` theorem, the measured special cases, the phase policy, and the negative local Glucose result separately.
