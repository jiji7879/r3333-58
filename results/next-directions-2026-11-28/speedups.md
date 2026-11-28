# Solver speedups: what is now implemented, and what to try next

**Bottom line.** The certified-processing side has usable improvements. There
is currently **no verified general CDCL-search speedup** to deploy. Native C&C
LRAT output is now an explicit opt-in with checkered premises and cache binding;
DRAT and ordinary solver defaults are unchanged. No wall profile, `ChainReady`
or Ramsey interval has changed.

## Implemented and checked

### 1. Native LRAT in the actual C&C engine
Use `--engine native --proof eager --lrat-trim PATH`, optionally adding
`--lrat-trim-sha256 HASH`. [`src/lrat_optin.py`](lrat-optin/src/lrat_optin.py) checks the exact solver input, and `campaign.py` verifies every appended CAS cut from the parent once per run. Every leaf receipt binds the checker and that premise. `verify` replays LRAT with a whole binary parse.

Coordinator checks: **24/24** full controls, **native default regression passed**, and **native default DRAT proof bytes unchanged**. On H8, ordinary proof checking cost 0.899 s versus 0.079 s of CPU. But raw LRAT was 14,594,230 bytes versus DRAT's 9,529,642 and leaf RSS rose to 156,036 KiB from 86,228 KiB. This is a proof-checking choice, *not* a blanket speedup. See [details](lrat-optin/README.md) and [reproduce](lrat-optin/REPRODUCE.md).

The smaller standalone adapter in `tools/lrat_pipeline/native_solve.py` trims LRAT and replays two independent unverified implementations before retaining it. Existing `finalise` was **not** changed to accept LRAT as DRAT.

### 2. Exact physical/emitted bridge
`lean/K58/EmittedBridge.lean` and `TargetUnits.lean` now establish the arm-label coordinate order, its physical valuation, and the root/T16 units that the support transport needs. The whole root Lean build passed in 19.67 s; all checked axioms stay within the allowed foundational set. This is genuine progress on the semantic gate. It is **not** the final guard-exhaustiveness or `ChainReady` argument. Remaining obligations are the count-to-finset bridge, key bookkeeping, classification and sequential assembly: [bridge](bridge/README.md).

### 3. Admission and reuse gates
A separate [admission utility](admission/RESULTS.md) passes its 26 adversarial tests and reproduces all six published verdicts. It can reject cap-as-UNSAT, unpinning, ignored options, seed artefacts, hidden regressions and unsound controls. It judges receipt structure and cost arithmetic only; it does **not** replace proof/model verification.

The exact K15 clause family was also measured and is **not** a speedup: lower decisions, more propagations, and no reproducible total-CPU benefit. UP-trivial rules are explicitly removed before judging 600 nontrivial clauses. See [clause reuse](clause-reuse/README.md).

## What else is reasonable, with a measured route

1. **When memory is the binding constraint, prefer the existing native backend as an opt-in.** Seven measured leaves showed about **0.94× process CPU and 0.53–0.59× peak RSS**. But on the closed H8 family, native CaDiCaL needed 49,226 rather than the incumbent's 32,316 conflicts and cost 2.727 versus 2.281 certificate CPU seconds. This is a memory trade-off, not a universal engine switch. See [backend evidence](backend/ADOPTION.md).

2. **Use proof-carrying preprocessing only if leaf RAM/startup is the bottleneck.** One-shot simplification removes 35.3% of clauses and 39.2% of literals and cuts RSS by 12% and parse/bootstrap CPU by 35%, with replayed prefixes, composition and corruption controls. Its seed-locked search cost ranges from 0.719× to 1.145×, so it is *not* a CDCL speedup. Already-run [reproduction](preprocessing/README.replay.md) has DRAT prefix plus proof accepted and the corrupted prefix refused.

3. **Try a small fixed set of alternative seeds before escalating the cap, as a controlled experiment.** A closed H8 instance that misses at seed 1 (60,002 conflicts and OPEN) closes at seed 3 (14,492). This is a measured *case*, not a seed portfolio policy or proof of cheaper coverage. Other seeds are worse elsewhere. Any seed retry needs a normal retry budget, verified artifact on success, original status on every attempt, and independently preserved search counters. Escalating cap without testing seeds would spend more CPU for no established advantage.

4. **Prefer finishing the physical bridge over further tuning.** The substantial remaining obstacle is to transform the emitted 41-bit count into an explicit `Finset` of 14 physical colour-1 neighbours, plus the small `expandKey` / `ColourUnit.ofEdge` bookkeeping bridges, the applicable classification and the final chain. That is more useful for the campaign than changing another solver phase.

## Do not re-run as expected improvements

- `stabilize=0,rephase=0`: early CPU falls, but closes neither H7 nor H8 at 200,000 conflicts and stays OPEN at 1,000,003 on H8. That is a cap trajectory artefact, not an optimization.
- KMT: lower memory but worse CPU (1.2576× at 100k, 1.2344× at 1M).
- Global/pinned/arm-3 MCF, full static lex, conditional Sinz, and the one-colour
  lex generator whose deliberately corrupted control had the same effect.
- The tested CaDiCaL checkproof=0 shortcut: both settings produce identical raw
  and trimmed proofs and identical counters, but its four CPU ratios are
  0.9887, 1.0268, 0.9640 and 1.0207 (geometric mean 0.9998). It is available
  as a tested option, **not** an implemented improvement. See
  [checkproof comparison](lrat/checkproof-comparison.json).

All reported certificates and performance claims remain scoped to their exact
inputs, seeds, caps, checker identity and physical premises. OPEN or UNKNOWN is
never UNSAT. Accepted $51\le R_4(3)\le62$ is unchanged.
