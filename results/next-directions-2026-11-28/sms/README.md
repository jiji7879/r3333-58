# Restricted one-colour SMS/export on the retained K58 parent — bounded result

## Coordinator verification

The ended member run could not receive a formal swarm verdict, so this is an
**independently replayed bounded result**, not an accepted member report. A
scratch-only rerun of `run_all.sh` passed in 77.59 s wall (41.21 s solver CPU,
198,528 kB peak). It regenerated the same 765 clauses and every validation and
toy receipt byte-for-byte except process timings. Both run orders remained
`UNKNOWN` with identical counters. Baseline CPU geomean was 8.053 s, verified
clauses 6.230 s and the corrupted control 6.320 s: again the corrupted arm was
similarly fast, so there is **no validated symmetry-breaking speedup**. The
coordinator receipts are `coordinator-ab-summary.json` and
`coordinator-ab-runs.jsonl`.

No proof of physical model-set invariance exists. Native SMS still needs Boost
and its reviewed adapted CaDiCaL dependency; this is explicitly a local
lex-leader rule, not stock SMS. The production solver defaults, frozen ledger
and physical `ChainReady` premises are unchanged. This does not alter
$51\le R_4(3)\le62$.

The original report follows. Its relative paths now refer to this directory;
the reproduction uses the existing `.scratch/k58` Python environment.

Member `m6`, swarm `smx06hpp8`, direction `d5`. Repository HEAD `e43e78e`.
Nothing outside this directory was modified. Production run/finalise, the frozen
ledger, encoding defaults, `lean/order.txt` and other sessions' files are
untouched. No bound changed: `51 <= R_4(3) <= 62`; `<=60` remains the unverified
preprint claim.

## Bottom line

| state | result |
|---|---|
| **native upstream SMS** | **BLOCKED**, exact missing bits in [`sms-blocker.md`](sms-blocker.md). Nothing was bypassed, no SMS verdict used. |
| **capability** | A bounded one-colour lex-leader generator exists and works (labelled substitute, **not** SMS). Whole-formula reindexing by a recorded bijection round-trips byte-identically. |
| **proof** | 765 emitted clauses pass independent re-verification (tier, group membership, unit+cube preservation, strict lex indicator, reduction, augmented-formula consistency). Complete rule validation and orbit-survival controls on a K5 toy. **This is a checked cut set, not a soundness proof for the CNF.** |
| **throughput** | One matched 200 000-conflict A/B, both run orders: baseline 8.401 s, augmented 6.655 s geomean solve CPU (ratio 1.263, 0.596x propagations, 1.441x decisions), RSS +1%. **A same-size corrupted control is equally fast (6.44 s).** So the CPU difference is a CDCL-trajectory effect, not a benefit of the clauses. **No throughput win is claimed.** |
| **status** | All arms `UNKNOWN` at the cap. **OPEN is not UNSAT.** No SAT/UNSAT answer was obtained, so no model/proof gate was entered. |

**Decision: the direction is not worth continuing on this parent** unless someone
proves colour-0 `H`-invariance of the physical model set and finds a clause
source that is not a bounded prefix of the one-colour lex-leader family (see
"What would have to change" below).

## 1. Exact objects used

```
row     06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06
profile (16,16,14,11), charge 7
recipe  tables=True, total_critical=True, full_root=False
parent  p cnf 19533 184335  sha256 90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae
+cube   p cnf 19533 184337  sha256 8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8   (cube -1413, 1014)
438 explicit signed units (396 positive, 42 negative), re-derived from the frozen recipe
candidate group H = Sym({38..46}) x Sym({52..57}); 51 transpositions, |H| = 9!*6! = 261273600
```

Both hashes reproduce from `regen.py` (`regen.json`: `parent_match` and
`parent_cube_match` both true) in 0.3 s.

## 2. What was generated

`gen.py` enumerates one-colour lex-leader certificates for colour 0 with the
candidate group above. Rule: with `W(G)[r] = 1` iff pair `r` (row-wise
upper-triangle order) has colour 0 and `W(p.G)[r] = W(G)[phi(r)]` for `phi`
induced by `p^{-1}`, a certificate is a partial assignment `A` such that every
total word extending `A` has `W(p.G) < W(G)` with a fixed first difference of
`(1,0)`. The clause `not A` then holds at every orbit-minimal representative.
`A` is always `root_closure(F) union decisions`; literals falsified by the root
closure are dropped (equivalence modulo `F`); a certificate reducing to the empty
clause would make `F` trivially BCP-UNSAT and is excluded (none occurred).

```
clauses 765 = 51 transpositions x (1 + 2 + 4 + 8) prefix patterns
lengths  {2: 51, 4: 102, 6: 204, 8: 408}
generation CPU 0.15 s (60 s cap not reached; no randomness, so it reproduces exactly)
root closure: 1864 literals, 418 of 1653 colour-0 positions fixed
```

This is a **bounded subset** of the one-colour lex-leader family: only colour 0,
only transpositions, prefix depth <= 3 rows. It is much weaker than the full
static comparator that an earlier pilot found cost 4.75x propagations.

## 3. Independent verification (`verify_clauses.py`, status PASS)

Per clause, recomputed without trusting the generator:

* every literal is a physical colour-0 variable (`4r+1`, `r <= 1652`), length >= 2,
  no duplicates, no complementary pair;
* the recorded transposition lies inside one twin cell;
* the transposition maps the 438 explicit signed units **and** the cube onto
  themselves (recomputed from `gluing.units` + the frozen row);
* the strict lex indicator holds symbolically for the full certificate, with the
  recorded witness as the first difference and values `(1,0)`;
* the emitted clause is exactly the negation of that certificate minus
  closure-false literals, and no dropped literal is true under the closure;
* 60 random total extensions per clause confirm the strict decrease numerically
  and agree on the witness.

Global: `augmented.cnf` = parent+cube + 765 clauses
(sha256 `d5e315250d226c88e47330b760a0f04d587d38c366dbf7e7b06419bf23f6903e`)
survives unit propagation; its closure size equals the parent's (1865), so no
clause is unit or propagation-redundant, and 0 clauses are satisfied by the
parent closure (none vacuous).

## 4. Toy controls (`toy_control.py`, K5 edge-4-colourings, no mono triangle)

The rule is checkable exhaustively at this size, which is impossible on K58.

| test | result |
|---|---|
| T1 rule vs brute-force lex order, **all 1024 words** | 0 mismatches |
| T2 generated clauses at every orbit minimum (273 960 orbits) | 0 violations |
| T3 invariant model set (542 952 models) | **0 empty orbits** |
| T4a non-invariant restriction `colour(0,3)=0` | 108 174 / 122 577 orbits **emptied** |
| T4b non-invariant restriction `colour(0,4)=0` | 0 emptied |
| T5 one literal sign flipped | 151 383 / 273 960 orbits **emptied** |

T4a and T5 show the survival test has teeth. T4b is recorded because not every
non-invariant restriction fires: the failure needs to interact adversarially with
the lex order. T1 also covers my own earlier mis-numbering bug (below).

## 5. Recorded bijection (`reindex.py`)

```
old 4r+1+c  ->  new r+1 (c=0), new 1654+3r+c (c=1..3);  aux 6613..19533 unchanged
parent_cube.reindexed.cnf sha256 56853172f15d21a0d75522fe6c5c3804eb9472a27014ccbdcfb3d09d14c6fef5
round trip back to the original bytes: byte-identical
765 clause images all inside new variables 1..1653 (the SMS edge block)
clauses.reindexed.txt sha256 e2f2d30fa1b81b78a64a81b268c4a7e6e8c3a709ba1e8499dc88a7f6e3bcb06d
```

No clause was added, removed or weakened by the renumbering.

## 6. Matched A/B (`ab_bench.py`, `summarise.py`, `ab_summary.json`)

Incumbent `pysat.solvers.Cadical195` (CaDiCaL 1.9.5), PySAT 1.9.dev22
(`pysolvers` sha256 `cda792186335cb628804eaf73f2c6008699d7c983188053ffa5c9c118a6be3b3`),
jobs 1, 200 000-conflict cap, **both run orders** (baseline->augmented and
augmented->baseline). PySAT's `Cadical195` exposes no seed; the arms are matched
on build, cap and order. Per-run receipts are in `ab_summary.json`.

| arm | solve CPU (s) | geomean | propagations | decisions | restarts | peak RSS (KB) | status |
|---|---|---|---|---|---|---|---|
| baseline | 8.508, 8.296 | 8.401 | 69 573 821 | 751 001 | 10 633 | 69 984 / 70 004 | UNKNOWN |
| + 765 verified | 6.645, 6.666 | 6.655 | 41 482 509 | 1 082 485 | 11 609 | 70 712 / 70 536 | UNKNOWN |
| + 765 corrupted (control) | 6.477, 6.507 | 6.492 | 49 655 914 | 1 142 940 | 10 266 | 69 616 / 69 532 | UNKNOWN |

Both orders give byte-identical conflict/decision/propagation/restart counts, so
the measurements are deterministic. Ratios: baseline/verified CPU **1.264**,
propagations 0.596x, decisions 1.441x, RSS 1.010x.

**Interpretation.** The corrupted control — the same 765 clauses with the last
literal of each negated, i.e. deliberately unsound — is just as fast
(baseline/corrupted 1.294). Any 765 short clauses therefore shift CaDiCaL's
trajectory and per-conflict cost; the verified set has no advantage over a
garbage set of the same shape. Both real arms stop at the conflict cap, so
nothing is learned about search-space reduction. **No throughput benefit is
claimed and the direction is not extended.**

Total active solver CPU: **43.2 s** (limit 30 min). Generation CPU: 0.15 s
(limit 60 s). No wall sweep, no second row, no K51 run, no MCF, no solver other
than the incumbent.

## 7. A bug that was caught, and the checks that caught it

The first generator read the root closure from the **reindexed** variable
numbering while the propagation ran on the **original** DIMACS numbering. That
produced a spurious "the closure already witnesses lex non-minimality for 20 of
51 transpositions" and one nonsense clause. It was caught because the reported
row-0 values contradicted the explicit units (`colour(0,52) = colour(0,53) = 3`
forces `W[0,52] = W[0,53] = 0`, but the buggy read gave `0,1`), and by T1 on the
toy. With the numbering fixed: **0 of 51** transpositions are non-minimal under
the root closure, and the emitted set is the clean 51 x 15 family. No result in
this report depends on the buggy version.

A second defect, also caught and fixed: the first DFS branched only on the first
transposition's blocking position, so it emitted 1 clause in 60 CPU-s.

## 8. What is NOT established

* **No soundness proof of the cut.** The min-orbit argument needs (i) the
  physical model set `M` of the row to be invariant under `H`, and (ii) every
  physical model to extend to a model of the CNF. Both remain campaign
  obligations. The 51 transpositions preserve the 438 units, the cube and the
  abstract counter/support specs, but that is **not** a proof of (i) or (ii), and
  the frozen units alone are still a relaxation.
* **No stock-SMS claim.** The generator is a substitute; it does not reproduce
  SMS minimality search, learned-clause policy, witness format or CaDiCaL
  integration. T1/T2/T3 establish the *rule*, not SMS conformance.
* **No four-colour projection certificate.** Only colour 0 was broken; combining
  four single-colour lex orders would need the two-level argument in
  `results/literature-next-2026-11-28/dynamic-symmetry.md`, which is not done.
* **No verdict.** `UNKNOWN` is not `UNSAT`. No model was found, no proof was
  produced.
* `ChainReady`, candidate/112-support criticality, the coded/automatic physical
  guard equalities and hbase/hvars remain exactly as open as before.
* No Lean work was done in this direction: no new module, no `lean/order.txt`
  entry, no `*.olean`. Nothing here induces a Lean build obligation.

## 9. What would have to change for this to be worth another run

1. Prove colour-0 `H`-invariance of `M` for this row, so the cuts are sound at
   all. Without it the A/B is only a hint generator, which is what it is.
2. Find a clause source that is not a bounded prefix of the one-colour
   lex-leader family. On this parent the room is thin: the root units already fix
   every colour-0 edge at vertex 0, so rows 0 of the lex word are equalities, and
   the useful short clauses are the row-1..3 family generated here.
3. Solve both arms to a verdict, which turns this into a model/proof-gate
   experiment, or measure at a much larger cap with a matched work budget — the
   former is what actually decides anything, and neither is available in a
   bounded pilot.

## 10. Files and reproduction

```
./run_all.sh                       full pipeline, 87 s wall, 43 s solver CPU
sms-blocker.md                     native SMS prerequisite audit, exact missing bits
regen.py            regen.json     exact parent/cube regeneration and hashes
sms_lib.py                         coordinates, H, bijection, lex-indicator rule
bcp.py                             numpy unit propagation + scalar reference
gen.py              gen_receipt.json, clauses.txt
verify_clauses.py   verify_receipt.json      independent re-verification (PASS)
reindex.py          reindex_receipt.json      recorded bijection, byte round-trip
toy_control.py      toy_receipt.json          K5 complete-rule and orbit controls
ab_bench.py         make_corrupted.py         A/B arms incl. the trajectory control
summarise.py        ab_summary.json, ab_runs.jsonl, clauses.reindexed.txt
```

The four large `.cnf` files are deleted to keep the directory small; `./run_all.sh`
rebuilds each one deterministically and every receipt pins its SHA-256. The
interpreter is the repository's existing `../../../.scratch/k58/.venv/bin/python`
(PySAT 1.9.dev22) with `/opt/math/lib/python3.12/site-packages` added to
`sys.path` for numpy 2.5.3; nothing was installed.
