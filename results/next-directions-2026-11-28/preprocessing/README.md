# One-shot proof-carrying CNF preprocessing — measured, bounded, mostly negative

Member m4, swarm `smx0er1f6`, direction d3. Repo HEAD `e856d75`. Everything here
lives under `.ultramath/smx0er1f6/m4/` (git-ignored); nothing outside it was
edited, no production `run`/`finalise`, solver default, encoder or ledger was
touched.

**Verdict in one paragraph.** A one-shot, proof-carrying simplification of the
retained parent+cube removes 35.3 % of the clauses and 39.2 % of the literals,
cuts RSS by 12 % and CNF parse+bootstrap CPU by 35 %, and yields a fully
checkable DRAT prefix (verified here three independent ways, with corruption
controls that fail closed). It does **not** give a reproducible CDCL speedup:
across four seeds at a matched 100k-conflict cap the total-CPU ratio
(reduced/host) is 0.959, 1.145, 0.719, 0.943 — geometric mean 0.929, one seed
clearly worse, and the sign of each seed's effect tracks its propagation count,
i.e. trajectory divergence rather than the reduction. Exact subsumption — the
one redundancy family that would be free at run time — finds **5 clauses out of
184 337**. So on this host: adopt nothing as a search speedup; the RSS/parse
reduction and the certificate-composition recipe are the only real products.

## 1. What was measured, and on what

| item | value |
|---|---|
| host CNF | `.scratch/m7/stock-cube.cnf`, sha256 `8791f627…60a8`, 3 493 031 B, `p cnf 19533 184337`, i.e. the retained parent 06861a3d with cube `[-1413, 1014]` appended as units |
| host structure | 440 units, 36 992 binary, 134 649 ternary, 12 241 quaternary, 15 × 113; **no duplicate clause, no tautology** |
| root UP closure | 1 865 forced variables (440 host units + 2 cube units + 1 425 derived), no root conflict |
| reduced CNF | sha256 `c3239878…1142`, 2 172 405 B, 119 343 clauses, 321 850 literals (−35.3 % / −39.2 %), same variable numbering, nvars still 19533 |
| prefix (ASCII) | sha256 `9b610644…7ea`, 1 832 338 B |
| prefix (binary) | sha256 `f44f2835…bbb`, 698 340 B |
| prefix content | 13 416 additions (1 425 derived units + 11 991 shortened clauses) and 78 410 deletions |
| simplification cost | 1.3 s CPU in Python including every internal re-check (whole CNF in RAM, 157 MiB RSS) |

Reduction accounting: 66 414 non-unit clauses dropped as satisfied by the
closure, 11 991 shortened, **5** exactly subsumed, 0 duplicates introduced, 0
duplicates found in the host (H7, used below, has 5 duplicate unit clauses).
Pure-literal elimination
is implemented but **not enabled** in any measured arm, so nothing is claimed
about it.

## 2. The proof contract (this is the part that works)

A prefix is emitted so that `host − deletions + additions = reduced` *exactly, as
multisets*. Consequences, each checked rather than asserted:

1. **Independent prefix check** (`check_prefix.py`, MiniSat 2.2's propagation
   from the pinned python-sat wheel — a different engine from the CaDiCaL used
   for measurement, and a different implementation from `prep.py`): all 1 425
   unit additions and all 11 991 clause additions are RUP with respect to the
   host *alone*, which is stronger than RUP at their position, so the prefix is
   order-insensitive. Plus the deletion multiset and the identity above. 0.9 s.
2. **Corruption controls**: flipping one derived unit's sign and, separately,
   dropping one literal from an added clause are each rejected with three
   independent diagnostics.
3. **Composition on a real closed case** (H7, sha256 `2286ae68…`, 184 188
   clauses): native CaDiCaL 2.1.2 `--seed=0` closes host and reduced in 1.03 s and
   1.06 s CPU. The proof produced **on the reduced formula** is accepted by
   `drat-trim -i` against the **host** (`s VERIFIED`, 0.78 s), and
   `prefix ++ proof` is also VERIFIED against the host (0.75 s). Corrupting one
   prefix unit makes that composition `s NOT VERIFIED`.
4. **A closed leaf that never needed search**: R11 (sha256 `b3a5bded…`, 173 819
   clauses) is refuted by root unit propagation alone — 1 332 derived units plus
   the empty clause, `s VERIFIED` by `drat-trim` in 0.10 s, in both encodings.
   Its incumbent 1 514-lemma DRAT proof has one lemma in the core.

So: *proofs port downward for free* (unit propagation is monotone in the clause
set), but only as **RUP**; a RAT step is anti-monotone and a subset formula can
break it. Both closed cases here had 0 RAT lemmas in the core, so the hazard did
not bite — that is a measurement, not a guarantee.

## 3. The speedup measurement (negative)

Matched A/B, one fresh process per call, PySAT CaDiCaL 1.9.5 (`python-sat`
1.9.dev22), identical seed and conflict cap, arm order swapped per seed, CPU from
`time.process_time` inside the worker plus `RUSAGE_CHILDREN` outside. All runs
OPEN at the cap (100 000–100 005 conflicts); **OPEN is not UNSAT**.

| seed | total-CPU ratio | propagation ratio | RSS ratio | decisions host → reduced |
|---|---|---|---|---|
| 0 | 0.959 | 1.033 | 0.892 | 529 694 → 505 919 |
| 1 | 1.145 | 1.475 | 0.871 | 777 586 → 501 813 |
| 2 | 0.719 | 0.551 | 0.882 | 438 703 → 748 725 |
| 3 | 0.943 | 1.043 | 0.874 | 541 800 → 503 653 |

geometric mean **0.929**, median 0.951, range 0.719–1.145; RSS consistently
−12 %; parse+bootstrap CPU 0.0766 s → 0.0496 s per call.

Controls and replications, all on the same host and cap:

* A first arm that dropped the host's unit clauses (a *weaker* problem, not a
  simplified one) gave 0.799 / 1.147 / 0.975 / 0.785, geomean 0.915, RSS 0.845;
  at cap 200 000 it gave 0.777 / 1.249, geomean 0.985.
* Same seeds, same sign pattern across all arms and both caps: seed 1 loses
  15–25 %, seeds 0/2/3 gain 4–30 %. The effect is seed-locked, deterministic and
  correlated with the propagation count, not with the clause count.
* KMT (accepted prior work) was rejected at a 0.90 geometric-mean bar. This
  direction does not reach that bar at n = 4 (0.929), and its per-seed sign
  flips, so it is rejected on the same rule, not on taste.

**Mechanism.** After root propagation the solver has already derived the whole
closure, so 66 414 of the 78 405 removed clauses were invisible to the search
anyway; the only database that really shrinks is the 11 991 shortenings (6.5 %).
What changes is the *order* in which the remaining clauses are watched and
bumped, hence a different search tree — which is worth ±30 % on its own. That is
also why shrinking the variable count (KMT, −31.6 % variables) was measured
earlier as +25.8 % CPU at 100k and +23.4 % at 1M: on this instance the search
tree, not the database, is the cost.

## 4. What cannot be adopted (recorded so it is not re-run)

* **Removing provably redundant encoding**: dead here. Exact subsumption finds 5
  clauses of 184 337 (0.003 %), zero duplicate clauses in the host, zero
  tautologies. There is nothing to remove.
* **One-shot simplification as a CDCL speedup**: not established; sign-flipping
  across seeds; stopped after two arm variants and two caps (bounded stopping
  rule: abandon when the geometric mean exceeds 0.90 or any seed regresses
  > 1.10, which happened at the first four-seed panel).
* **Adding the closure units instead of dropping them** (the second arm): needed
  for equivalence, does not change the verdict (geomean 0.930).
* **Renumbering / variable elimination / compact formula**: prior evidence
  (KMT) already rejects the direction on this host; not re-presented.
* **Two bugs found by controls, both of which would have produced silently wrong
  artifacts** (kept as cautionary notes):
  1. ASCII DRAT has **no** `a` addition marker (only binary does). A prefix
     written with `a` makes `drat-trim` auto-detect *binary* and parse the text as
     garbage; it then reports only `c ERROR: no conflict`, never "invalid step".
     A partial DRAT file therefore needs its own checker.
  2. Deleting a host **unit** clause is not neutral: `drat-trim` silently ignores
     unit deletions in backward mode, so the checker keeps the unit and hides the
     hazard. Fixed by never deleting units the reduced formula keeps.

## 5. What is adoptable, and exactly how

Only as an **opt-in** to the leaf writer, never as a default:

* `prep.py` — standalone, deterministic, fail-closed: refuses on a host hash
  mismatch, re-verifies every claim internally, exits 1 with `problems` on any
  inconsistency, exit 3 if the instance is already root-refutable.
* `check_prefix.py` — accepts or rejects a prefix against a host with a second
  solver's propagation, plus the multiset identity.
* `bench.py`, `reproduce.sh` — the matched A/B harness and a one-command
  reproduction of every number above (38 s wall, ~5 s solver CPU).

Integration sketch and its fail-closed conditions are in `INTEGRATION.md`; it is
a diff *proposal* against `tools/color-resolved-wallcc/native_leaf.py`, not
applied. The decisive fact for the coordinator is that `campaign.py::replay`
already checks `cas.drat ++ leaf_proof` against `parent.cnf` + cube units with
`drat-trim -i`, so the only change needed is that the leaf proof becomes
`prefix.bdrat ++ leaf.bdrat` and the leaf is solved on the reduced CNF. Nothing
in finalise changes, because the object being checked is still the host cube
formula.

## 6. Scope limits

No wall sweep, no FKR rerun, no K51 campaign, no automorphism assumption, no
global install. Two closed cases (R11, H7) and one open retained cube were used;
all CNF/proof artifacts stay in this ignored directory. `51 ≤ R_4(3) ≤ 62` is
unchanged; no cube, cover, profile or `ChainReady` claim of any kind is made
here. Timing figures are CPU seconds on a shared 4-core VM, four seeds and one
cap, and are reported as a measured spread rather than a point estimate.
