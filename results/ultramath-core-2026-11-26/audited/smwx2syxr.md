# `smwx2syxr` — archival audit (Group A)

Read-only audit by swarm `smwx73ni9` / member m1, 2026-11-26. I read the member
transcripts, the receipts, the integration and cleanup records and the member
scripts under `.ultramath/smwx2syxr` (1,240,851,991 bytes, 652 files, m1–m8 +
`transcripts/`). No solver was run, nothing was deleted, no file outside
`.ultramath/smwx73ni9/m1/` was written.

**Swarm character.** This is the *engineering* swarm of the same campaign, not a
mathematical one: its brief (from `transcripts/m*.jsonl` `[USER]`) is exact,
reproducible, certificate-carrying solver plumbing for the K58
`(16,16,13,12)` rows — byte-exact A/B measurement, per-leaf DRAT conversion,
built-in guard families, encoder bridges. It is still the same campaign that must
not be read as a Ramsey result.

## 0. Bottom line

* 8 members, 8 submissions, **no judge rejection appears anywhere in the
  transcripts**; every transcript ends at
  `{"direction":"d…","submitted":true}`.
* **Coordinator acceptance evidence** (there is no per-direction verdict table
  for this swarm): `results/storage-cleanup-2026-11-26/README.md` retains
  "All of the accepted `smwx2syxr` working tree", and
  `results/solver-integration-2026-11-26/README.md` records the adoption of
  specific member artifacts into the shipped `k58-solver` package.
* **I verified byte-identity** of six member scripts against Git-tracked copies in
  `tools/selfcontained/wallcc/` (commit `94c7482`), see §3.
* Nothing here closes a row, moves a bound, or is a proof of
  `R(3,3,3,3) <= 58`. Every solver number is explicitly capped/UNKNOWN and the
  members say so; the value is tooling plus **measured delimitations**.

## 1. Accepted vs claimed / rejected / unreviewed

### 1.1 Verdict evidence

| source | path | what it establishes |
| --- | --- | --- |
| acceptance (swarm level) | `results/storage-cleanup-2026-11-26/README.md` (tracked) | "All of the accepted `smwx2syxr` working tree" retained |
| integration | `results/solver-integration-2026-11-26/README.md` + 47 logs (tracked) | which member artifacts were adopted and re-tested |
| submission record | `transcripts/m1..m8.jsonl` | one `ultramath_submit` each, reply `{"submitted":true}`, no rejection restart |
| receipts | member `*.json` receipts | self-tests the members claim |

No coordinator file enumerates per-direction verdicts for this swarm, so
"accepted" below means **accepted at swarm level by the two coordinator records**,
not "individually re-judged".

### 1.2 Per-member submitted content (all accepted at swarm level)

| m / dir | submitted result | integrated where |
| --- | --- | --- |
| m1 / d3 | kernel-checked `K58.sixteen_arm_outside_nonempty`, `arm_ind`, `saturation_clause` (axioms `[propext, Classical.choice, Quot.sound]`), discharge of `R33`/`R333` assumed predicates in `GapFamilies`; 82-clause set equality on 3 real parents | only `results/solver-integration-2026-11-26/m1-build.log` (tracked); the `.lean` sources are **not** in Git |
| m2 / d5 | `engine_conformance.py` + `adversarial_suite.py`: SAT only if the model validates against the adapter's own parse; UNSAT only on exact `s VERIFIED`; 39/39 mutation tests | `tools/selfcontained/wallcc/{engine_conformance.py,bcp.py}` (identical) |
| m3 / d8 | `rootreduce.py` + `check_trace.py`: certified root reduction 1,058,750 → 649,327 clauses on the marked-free reciprocal parent, 1,368,934 → 920,905 on its dcap variant, 7 negative controls rejected | `tools/selfcontained/wallcc/{rootreduce.py,check_trace.py}` (identical) |
| m4 / d4 | `entcap.py`: the certified entrance cut as a portable projection; coverage TT-- 56×13=728, TU-- 70×12=840, UU-- 0 (1,568 instances, 126 rows); T1–T7 pass | `tools/selfcontained/wallcc/entcap.py` (identical) |
| m5 / d7 | `rootsimpl.py` + `verify_cert.py`: entailed-closure simplification with replayed certificates; layer inertness census; matched-budget no-improvement | member directory (not separately packaged) |
| m6 / d2 | `leafcert.py`: per-leaf C&C certificate harness, 27 controls pass, independent exhaustiveness check | `tools/selfcontained/wallcc/leafcert.py` (identical) |
| m7 / d6 | `bridge.py` + `rebuild.py`: the aux/cardinality half of the semantic encoder bridge for `gen-TT.cnf` and `gen-TT-recip.cnf` (L1–L6) | member `out/…bridge.json`; not separately packaged |
| m8 / d1 | `k58x.py` + `receipt.json`: portable dcap builder, byte-exact reproduction, 232 blocks 0 failures, matched 100k-conflict budgets | member directory |

### 1.3 Rejected / unreviewed

* **Rejected: none recorded.** No `[USER]` restart message with a judge critique
  exists in any of the 8 transcripts, so no member of this swarm had a
  submission rejected. (Compare `smwwdcyxb`, where 5 rejections are on disk.)
* **Unreviewed: none identifiable.** But acceptance is swarm-level only (§1.1);
  I cannot show a per-direction "accepted" verdict from local material.
* **Superseded within the swarm (not judge-rejected):** m5's `REPORT.md`/
  `PROOF.md` cover the earlier directions; the accepted d7 text is the same
  file set (no d7→dX rename in this swarm, unlike `smwwdcyxb/m5`).

## 2. Exact scope and OPEN objects

**What the tooling may and may not assume** (these are the literal hypothesis
distinctions the reports depend on):

* `entcap.py` applies **only** to `(16,16,13,12)` roots and **only** to the two
  proven entrances: T/T at the **13-class** and mixed T/U at the **12-class**.
  `UU--` and the partial families get no cut. `--direct` encodes the actual
  theorem (outside-class count ≤ 14); it is **not** an unconditional global cap
  and must not be used on arbitrary roots.
* the 82 saturation clauses are justified by `K58.sixteen_arm_outside_nonempty`
  (proved in this swarm): `TriangleFree G`, `|A|=16`, no c-edge inside `A`,
  `w ∉ A` ⇒ some `a ∈ A` with `col w a = c`; **sharp** — `|A|=15` gives nothing.
  `p=q` stays open at 5 and is not claimed.
* `K58/GapFamilies.lean` (repo) was absent from `lean/order.txt` (no `.olean`,
  never built) and carried `R33`/`R333` as *assumed predicates*; m1 discharged
  them, so familyA/`five_bound`, familyB, familyC, `dual_five_bound`, `deg≤16`
  are unconditional modulo the committed `15≤d_a` flags.
* `gen-TT.cnf`, `gen-UU.cnf`, `gen-TT-recip.cnf`, `gen-UU-recip.cnf` and the
  `gen-L4` parents are **marked-free relaxations**: UNSAT transfers to the row,
  SAT does **not** refute a row.
* the dcap family `d_c(v)<=16` is genuine but mostly inert: **116 of 232** caps
  (colours 2,3) are implied by the parent's global at-most-14 flags, so 155,092
  added clauses are logically redundant; physical level-0 closure is
  **identical** in every variant (7,362; 29,389/29,388/29,380) and all growth
  (→27,597 / 44,165 / 10,245) is auxiliary-only.

**OPEN objects (inherited, none created):**

1. `n025` and the 3 open cubes (`r5_n025b2-019`, `c485-022`, `c485_029-033`) —
   the open frontier of `smwwdcyxb`; m6 re-measured `c485_029-033` as UNKNOWN at
   100k conflicts for kissat/cadical/inccnf.
2. the **declared bounds** of the cardinality-circuit layer are not certified
   (m7: "Not certified: the declared bounds").
3. whether the *pruned* dcap still closes `n017`/`n022` at m6's budget (m8's own
   caveat).
4. two 85/94 MB proofs were not replayed by m2 (m6 replayed n024 in 264 s).
5. no speedup: every A/B is a no-improvement or a cost measurement.

## 3. Retained in Git

`.ultramath/` is git-ignored. Retained copies are under `tools/`, `results/`:

| path | status | content |
| --- | --- | --- |
| `tools/selfcontained/wallcc/entcap.py` | tracked | = `m4/entcap.py` (SHA-256 prefix `20aed308ff950c70`, verified identical) |
| `tools/selfcontained/wallcc/rootreduce.py` | tracked | = `m3/rootreduce.py` (`b2320a4513e9d2c9…`) |
| `tools/selfcontained/wallcc/check_trace.py` | tracked | = `m3/check_trace.py` (`15e04949fd083c2f…`) |
| `tools/selfcontained/wallcc/leafcert.py` | tracked | = `m6/leafcert.py` (`0def7f048062d58f…`) |
| `tools/selfcontained/wallcc/engine_conformance.py` | tracked | = `m2/engine_conformance.py` (`1303cfecad803a2b…`) |
| `tools/selfcontained/wallcc/bcp.py` | tracked | = `m2/bcp.py` (`19e966095701a738…`) |
| `tools/selfcontained/wallcc/` (31 tracked files) | tracked, commit `94c7482` | the integrated toolkit |
| `results/solver-integration-2026-11-26/` (README + 47 logs) | tracked | adoption, re-tests, packaging |
| `results/storage-cleanup-2026-11-26/README.md` | tracked | names this swarm's working tree as accepted and retained |

**Not in Git:** m1's `lean/Saturation.lean` (6,158 B) and `lean/Discharge.lean`
(6,863 B) — the only *new kernel-checked mathematics* of the swarm. The tracked
`m1-build.log` proves they compiled against a hash-pinned copy of
`lean/K58/GapFamilies.lean` (`ada8b3ca…`), but `lean/K58/` (161 files) does not
contain them. m7's `bridge.py`/`rebuild.py`, m5's `rootsimpl.py`/`verify_cert.py`
and m8's `k58x.py` are also untracked.

## 4. Reproduction commands and source paths

Commands **I ran** in this audit (read-only):

```sh
cd .ultramath/smwx2syxr/m3 && sha256sum -c MANIFEST.sha256   # 9 OK, 24 lines improperly formatted (see §6.1)
for p in entcap.py rootreduce.py check_trace.py leafcert.py engine_conformance.py bcp.py; do
  sha256sum tools/selfcontained/wallcc/$p
  sha256sum $(find .ultramath/smwx2syxr -name $p | head -1)
done                                                          # all six identical
```

Member-documented reproduction (not re-run by me):

* m1: `bash build.sh` (26 s, exit 0) — atom map bijective 1..6612; builder output
  clause-set-equal to the justified 82; see also `results/solver-integration-2026-11-26/m1-build.log`.
* m2: `python3 adversarial_suite.py` (39/39; `receipts-suite.json` records
  `all_passed: true`, 3.17 s wall); `engine_conformance.py`, `bcp.py`.
* m3: `rootreduce.py` → `check_trace.py` (independent replay, byte-exact
  rebuild); `make_dcap_variants.py` reproduces the source `-dcap` file.
* m4: `entcap.py` + `test_entcap.py` (T1–T7), `coverage.py`, `run_ab.py`;
  `work/deltas.json` holds the A/B deltas.
* m5: `rootsimpl.py` + `verify_cert.py`; `layer.py`, `probe.py`, `selftest.py`.
* m6: `leafcert.py` + `selftest.py` (27 controls); `inccnf_probe.py`.
* m7: `rebuild.py` then `bridge.py` (L1–L6) on `gen-TT.cnf` / `gen-TT-recip.cnf`.
* m8: `k58x/k58x.py`; `results/receipt.json` has T1–T6 flags.

## 5. Raw-evidence inventory (bytes, measured)

| path | bytes | files | note |
| --- | ---: | ---: | --- |
| `.ultramath/smwx2syxr` | 1,240,851,991 | 652 | whole swarm |
| `m3` | 341,593,242 | 44 | `run/TTrecip/trace.json` 59,669,987; `run/TTrecip-dcap/trace.json` 77,827,960; variant CNFs |
| `m8` | 297,022,824 | 40 | `cnf/` (dcap variants); `receipt.json` |
| `m4` | 266,535,835 | 58 | `work/arm-*.cnf` (~33 MB each); `deltas.json` |
| `m5` | 138,931,439 | 264 | `out/*-simp.cnf` |
| `m7` | 70,617,489 | 14 | `out/gen-TT-recip.cnf` 37,157,479; `gen-TT.cnf` 32,739,619; bridge JSONs |
| `m1` | 66,731,055 | 22 | `.scratch/T2-*.cnf` 32.7 MB each; `lean/` 995 KB incl. `.olean` |
| `m6` | 48,986,203 | 121 | `control/n018/*.cnf` 21.7 MB each; `leafcert.py` |
| `m2` | 5,177,474 | 81 | receipts + `.scratch/suite` |
| `transcripts` | 5,256,430 | 8 | full member conversations |
| text/source files ≤2 MiB, all members | 7,908,268 | 261 | the "readable core" |

Hashes re-verified by me indirectly: `gen-TT-recip.cnf` = `f450ae9c…` with
1,058,750 clauses (m7 `bridge.json`; the same hash is one of the **21/21 OK**
entries of `smwwdcyxb/m6/MANIFEST.sha256`, which I ran).

## 6. Qualifications, corrections and what I could NOT verify

1. **`m3/MANIFEST.sha256` is corrupt**: 35 lines, of which 9 are valid checksum
   entries (all 9 verify OK) and 24 are pasted `ls -la` output ("WARNING: 24
   lines are improperly formatted"). Do not treat it as a 35-file manifest.
2. **Verification is sound but not attributive** (m2, accepted): an empty proof
   verifies any BCP-closed CNF; 3 of 20 bytes of a real proof verify; a stale
   proof replays after an invocation that died before opening it. Conflict
   budgets are bit-reproducible; **wall budgets are not** (2% back-to-back, 3.1×
   across sessions for the same 60 s command). 2 of 4 retained pilot
   certificates are vacuous.
3. **`inccnf` is not a certificate route** (m6): traces never contain the empty
   clause, `--idrup` is rejected by drat-trim, and an inccnf run stops at the
   first SAT (reversed order gives a 0-byte trace). The `c485_029-033` run left
   an 84,883,514 B, 2,529,429-line trace certifying nothing.
4. **Every A/B is a no-improvement or a cost** (m4, m5, m8): entcap decisions
   +20.1%/+86.1% on the TT parent (control +7.4%/+80.9%) and −5.3%/−8.7% on the
   TU parent (control −2.7%/−13.6%); root simplification 36.55M vs 40.48M
   propagations, no time gain; dcap costs 1.28–1.74× CPU/conflict. Do **not**
   read these as a speedup.
5. **Do not over-read the entrance cut**: it is valid only on TT:2 (13-class) and
   UT:3 (12-class); `UU--` and the 770 open entrance cases receive nothing.
6. **Not verified here:** `bash build.sh` (m1's 26 s Lean build), m7's
   1.0M-case gadget check, m6's 27 controls, m2's 39-test suite, m3's root
   reduction replay, m4's T1–T7. I read their receipts
   (`receipts-suite.json` `all_passed:true`, `receipt.json` T1–T6 `ok:true`,
   `bridge.json` L1–L6 fields) but did not re-run them. The byte-identity of six
   integrated scripts (§3) and all sizes/counts above **were** checked by me.

## 7. Retention recommendation

* **Keep (small, unique, not in Git):** `m1/lean/Saturation.lean` (6,158 B) and
  `m1/lean/Discharge.lean` (6,863 B) — the only new kernel-checked lemmas, only
  ~13 KB, and they exist nowhere else; `m1/PROOF.md`; `m2/PROTOCOL.md`,
  `m2/README.md`, `receipts-suite.json`; `m3/REPORT.md`; `m4/REPORT.md` +
  `work/deltas.json`; `m5/REPORT.md`, `PROOF.md`; `m6/REPORT.md`;
  `m7/results/bridge-report.md` + `out/*.bridge.json`; `m8/REPORT.md`,
  `results/receipt.json`. Total < 200 KB.
* **Manifest then drop:** `m3/run/` (137 MB of `trace.json` + variant CNFs),
  `m8/cnf` (~290 MB), `m4/work/arm-*.cnf` (~250 MB), `m5/out/*-simp.cnf`
  (~139 MB), `m7/out/*.cnf` (~70 MB), `m1/.scratch/*.cnf` (~65 MB).
  All are regenerable from the shipped builders; the scripts themselves are
  already in Git.
* **Repair before archiving:** `m3/MANIFEST.sha256` (§6.1) — regenerate from the
  builder, or keep only its 9 valid lines and say so.
* **Do not re-run:** the blanket degree-cap A/B, root-simplification timing, or
  inccnf leaf attempts. Accepted measured no-improvement records.
