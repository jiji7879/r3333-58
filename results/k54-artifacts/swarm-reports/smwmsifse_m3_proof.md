# Kernel-checked UNSAT for the K54 cut certificates, and an audit of the archived traces

Member m3, direction d3 (kernel-checked core refutations). All work is in
`.ultramath/smwmsifse/m3/`; nothing in the archive or the repo was modified.

## 1. What is proved

For **91 distinct CNF instances** of `work/k54` (every cut instance there whose
proof trace replays at all), the statement

> the clause set of that CNF is unsatisfiable

is proved **by the Lean 4.33.1 kernel**, with `#print axioms` equal to
`[propext, Classical.choice, Quot.sound]` (nothing else — in particular no
`Lean.ofReduceBool`, no `native_decide`, no `sorryAx`).

The proof object is a Lean theorem produced by Mathlib's `lrat_proof` command
(`Mathlib/Tactic/Sat/FromLRAT.lean`), which replays an **LRAT** trace as a
kernel-checked refutation. drat-trim is used in this pipeline only as a
**DRAT→LRAT translator and core extractor**; its verdict is not part of the
trust base, because a wrong translation would simply be rejected by the kernel.

Instances covered (all under `work/k54/`):

| family | distinct instances | what the instance encodes |
| --- | ---: | --- |
| `ours_m3check-*.cnf` | 44 (23 live-07, 18 live-14, 3 local-15) | one cut each: distinct outsiders witnessing `count_{k} ≥ m` for the listed columns, on the full 54-vertex graph |
| `ours/cegar-local-15/itNNNN*.cnf` | 44 (of 80 files) | CEGAR-loop cuts/blocks of local-15 |
| `ours/core/{s,x,l15-pin6}.cnf` | 3 | small theory cores (25, 11, 64 clauses) |
| `ours/cert-live-07-a`, `cert-live-14-a`, `cert-local-15-b` | 3 | the replay-recorded cuts: local-15 `-u[354,1] -u[323,1] -u[70,1]`, live-07 `-u[83,1] -u[52,2]`, live-14 `-u[1,1] -u[8,2]` |

94 results over 91 distinct clause sets; three of the named certificates coincide
byte-for-byte with instances already listed (`cert-local-15-a` =
`ours_m3check-local-15-loop-it00`, `certs/cut1` = `cegar-local-15-it0000-red`,
`certs/cut2` = `cegar-local-15-it0001-red`).

Measured sizes: core CNFs 11–480 clauses, LRAT traces 38 B–37 270 B, Lean
5.4–48.2 s per instance, **0 RAT steps in every core** (Mathlib's checker is
RUP-only, so this was checked per instance). One instance sha256 is exactly the
documented local-15 cut:

```
945c876c6937dda9e9464237203ea4e18e0518f1414df25a8858ed958b3e8cd8
  work/k54/ours/cert-local-15-a.cnf == work/k54/ours_m3check-local-15-loop-it00.cnf
```

so the archived cut `-u[354,1] -u[323,1] -u[70,1]` (4608 vars / 73 165 clauses,
core 64) now has a kernel-checked refutation.

### The three claims are kept apart

* (a) *one fixed count vector unrealizable* — not claimed here;
* (b) *a board excluded* — **not claimed**; I claim nothing about any of the 72 boards;
* (c) *a seed excluded* — **not claimed**.
What is claimed is: for each listed instance, the instance's clause set is
unsatisfiable, kernel-checked. Turning that into a cut statement over the outer
count variables uses the previous session's argument that the instance encodes
the board graph, its pins and the joint lower bounds with *genuinely distinct*
witnesses (`ours/check_oneside.py`, `ours/check_m3_cuts.py`, `ours/cut.py`).
That graph→CNF step is not formalised here and is not mine.

## 2. Negative result: 8 archived traces do not replay

`audit.py` runs `drat-trim <cnf> <drat>` on **every** archived pair (145 rows:
`work/k54`, `ours/`, `ours/certs/*`, `ours/cegar-local-15`, `ours/core`).
95 distinct pairs verify. **8 do not** — the trace derives no conflict, i.e. it
contains no empty clause:

| instance | trace bytes | drat-trim |
| --- | ---: | --- |
| `ours/cert-live-07-m7a.cnf` | 808 001 536 | `c ERROR: no conflict` / `s NOT VERIFIED` |
| `ours/cert-local-15-c.cnf` | 903 344 128 | same |
| `ours/core/l15-cut3.cnf` | 159 821 824 | same |
| `ours/core/pair-01.cnf` | 32 819 315 | same |
| `ours/core/pair-02.cnf` | 33 986 372 | same |
| `ours/core/pair-12.cnf` | 33 683 791 | same |
| `ours/rc.cnf` | 26 652 672 | same |
| `ours/t46.cnf` | 826 | same |

For the two ~1 GB traces the cause is visible: the file ends **mid-record**
(`…0a a2`, no terminating `0x00`), so the solver was killed while writing.
The eight are consistent with runs that hit a budget; **budget exhaustion is not
evidence**, so each of these is reported **OPEN, not refuted**.

Consequence for the hand-off's claim "local-15 also: `-u[354,1] -u[323,1] -u[69,1]`
(core 107)": `ours/cert-local-15-c.cnf` is that instance, its only archived proof
does not replay, and the CNF is **not decided** by CaDiCaL 3.0.1 at 300 000
conflicts (35 s, exit 0 = UNKNOWN) nor by Kissat 4.0.4 in 250 s. That cut should
therefore be treated as unproven until a fresh trace is produced. Everything
else in the "44 further cuts" list (23 live-07, 18 live-14, 2 local-15) is
kernel-checked (§1).

## 3. Where the kernel wall is (measured, not guessed)

The natural next target is the board-level counted refutation of **live-17**
(124 959 vars / 256 747 clauses; my decompressed copy hashes to the archive's
`3fc1016d…6f15aa`). Its CaDiCaL proof core is 70 973 clauses and drat-trim emits
an LRAT of 53 114 049 bytes / 103 656 lines / 7 492 002 resolution steps, still
with 0 RAT steps. `lrat_proof` on that pair **was killed by the OOM killer after
617 s** on this 15 GB, 4-core box. So:

* cut-level certificates (≤ 480 clauses, ≤ 37 KB LRAT): kernel-checked in seconds;
* a whole count refutation (7.5 M resolution steps): beyond a plain LRAT replay here.

The extracted objects are kept (small): `.scratch/l17/core.cnf`
(70 973 clauses, sha256 `c5619f34bad92bb6fe20fb9f619de689e8584ecc9c9ec5239cf3cbf1ccf19205`)
and `.scratch/l17/core.drat`
(sha256 `507380b944d302ed4fd4aadd6b829473fe22301890ce5e2fcfeb1982c6dfc381`);
`drat-trim core.cnf core.drat -L core.lrat` regenerates the 53 MB LRAT in ~5 s.

Two untried routes to cross that wall: split the trace at intermediate clauses
and kernel-check the pieces, or formalise the archive's 29-node / 19-leaf integer
tree (`checkpoints/counted/tree-live-17.json.gz`, ~250 integer separating
inequalities per leaf), which is far smaller than 7.5 M resolution steps.

## 4. Files and exact commands

| file | content |
| --- | --- |
| `kcheck.py` | the pipeline: drat-trim (verify + core + ASCII core lemmas) → drat-trim on the core → LRAT with core-relative ids → clause-inclusion check → `Cert.lean` → `lean` → JSON record |
| `sweep.py`, `sweep_dir.py` | drive `kcheck.py` over the top-level cut instances / a directory, grouping by CNF sha256 |
| `audit.py`, `AUDIT.tsv`, `AUDIT.log` | the full replay audit of every archived pair |
| `kc/`, `kc-cegar/` | per-instance `core.cnf`, `core.drat`, `core.lrat`, `Cert.lean`, `lean.log` |
| `kc/manifest.jsonl`, `kc-cegar/manifest.jsonl` | sha256 of instance/core/LRAT, core sizes, RAT counts, axioms, timings, Lean output |
| `probe.py` | cheap DRAT→core→LRAT probe without a Lean run |

```
cd .ultramath/smwmsifse/m3
python3 sweep.py                                            # 46 instances, ~8 min
python3 sweep_dir.py <k54>/ours/cegar-local-15 kc-cegar      # 44 instances, ~21 min
python3 kcheck.py kc core-s <k54>/ours/core/s.cnf <k54>/ours/core/s.drat
python3 audit.py                                            # 145 rows, ~4 min
lean "$PWD/kc/ours_m3check-live-07-loop-it15/Cert.lean"      # one instance end to end
```

(`lean` must see an absolute path: `include_str` resolves relative to the file's
own directory. `LEAN_PATH` is the VM default with the built Mathlib.)

Each `Cert.lean` is self-contained apart from `import Mathlib`:

```lean
import Mathlib

lrat_proof unsat_ours_m3check_live_07_loop_it15
  (include_str "core.cnf")
  (include_str "core.lrat")

#print axioms unsat_ours_m3check_live_07_loop_it15
```

## 5. Residual trust surface

The kernel guarantees the proposition that `lrat_proof` states, namely
`∀ a₀ … a_{N-1} : Prop, <the CNF as a formula>`. The mapping from the bytes of
`core.cnf` / `core.lrat` to that proposition is done by Meta-level parser code in
Mathlib (small, but not itself verified). Two machine checks tighten the rest:
`kcheck.py` verifies every core clause occurs verbatim in the instance (so
UNSAT of the core implies UNSAT of the instance), and the instance sha256 is
recorded next to every result, so the kernel-checked statement is tied to an
exact file. Not verified anywhere here: that the instances faithfully encode the
board (that is the graph→count argument), and the marginal/coverage model.
