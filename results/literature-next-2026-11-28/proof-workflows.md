# Next steps after the K58 SAT/Lean wall: proof and cube workflows

**Direction:** proof compression, checking, incremental traces, and exact cube reuse
**Repository inspected:** HEAD `211dd0b2b705efef7481d5cace379fea99a2a0ca`
**Bottom line:** try native LRAT first, then a two-level `cake_lpr` exporter, and only then incremental LIDRUP. A streaming LRUP checker is a conditional memory experiment. These do **not** supply a new Ramsey bound, close a wall profile, or discharge `ChainReady`.

## 0. Status and scope

The accepted interval remains $51\le R_4(3)\le62$ (Chung 1973; Fettes–Kramer–Radziszowski 2004, as recorded from DS1 rev.18, 24 April 2026). Current primary arXiv metadata, checked in this run at <https://arxiv.org/abs/2610.36648>, still gives **Milos Tatarevic**, *An upper bound of 60 for the Ramsey number R(3,3,3,3)*, v1 27 October 2026 and v2 6 November 2026. The GitHub user metadata at <https://api.github.com/users/milostatarevic> also gives **Milos Tatarevic**. Thus the old “M. Stojanović” local attribution should not be used. The repository is `milostatarevic/r3333-upper-bound`. Its two-solver/Lean claim is still a **preprint claim of $\le60$**, not an established bound and not independently DRAT-checked here. Nothing below proves $\le58$.

The frozen cover has 113,179 cases. The ordinary parent is a relaxation with `tables=True,total_critical=True,full_root=False`; frozen units alone are not a physical encoding. The retained arm-3 leaf and its cube `[-1413,1014]` remain OPEN. The new ordinary `PhysicalBridge` is a conditional satisfiability-existence assembly, not a CNF refutation. Candidate criticality/`deg`/`Sends`, exact 112-support membership, coded-plus-automatic guard-set equalities, and `ChainReady` remain semantic obligations. None of the four proposals below addresses those obligations. An UNSAT certificate applies only to its exact CNF and whatever separate mathematical bridge has actually been proved.

### Classification required for prioritisation

* **(a) New mathematical closure possibility:** **none found in this direction.** Better certificates cannot replace the missing physical realization, classification bindings, guard equalities, or `ChainReady`.
* **(b) Solver-throughput experiment:** only **P3, incremental LIDRUP**, might reduce repeated search/preprocessing across cubes. P1 measures certificate-production overhead, not a new search engine.
* **(c) Certificate/proof engineering:** **P1, P2, and P4**. These can reduce conversion, composition, storage, or checking costs after cubes close; they do not make an OPEN cube UNSAT.

## 1. What already exists and is therefore not proposed again

I read the five required files: `results/literature_status.md`, `results/literature-r3333-2026-11-23.md`, `review/DUGGAN_PAPER_ASSESSMENT.md`, `results/ams-wall-2026-11-28/arm3/retained-leaf/REPORT.md`, and `tools/color-resolved-wallcc/NATIVE.md`. I also inspected `tools/color-resolved-wallcc/{README.md,export_drat.py,native_leaf.py}`, `tools/adaptive_wall/{README.md,cubelearn.py}`, and `review/DECISION_FOR_CHATGPT.md`.

The repository already has:

1. Strict per-leaf ordinary-DRAT replay, full-byte/read checks, wrong-query and malformed-prefix controls, and explicit rejection of `OPEN`/timeout as UNSAT.
2. `export_drat.py::{compact_leaf,isolated_leaf}` and whole-parent replay. Compact lifting appends the negated cube to retained RUP steps and then derives split blockers. Isolated export uses private renamed variables and link clauses for RAT-capable proofs.
3. Exact child-core extraction, deletion reproof, learned clause `[-lit for lit in core_cube]`, signed-map transport, and target replay in `adaptive_wall/cubelearn.py`. Rebuilding that machinery is not new.
4. DRAT-to-binary-LRAT conversion and sampled `cake_lpr` replay. The recorded decision is on-demand conversion, not a second permanent proof archive; extrapolation was about 1.7 TB for the frozen cover.
5. Small Lean LRAT cores, with the documented whole-refutation memory failure. It is not a scalable new answer to replay every wall proof with the existing Lean `lrat_proof` command.
6. Fail-closed controls for unit-deletion warnings, malformed binary input, truncation, cross-stream splices, and self-consistent-but-wrong receipt mutations. The experiments below need new **format/semantics compatibility** controls, not another generic fake-checker suite.

Two local facts make the unused options concrete. First, the already bundled `tools/color-resolved-wallcc/bin/cadical-2.1.2` reports `--lrat`, `--idrup`, and `--lidrup`. Second, the 0404 experiment has a rejected 848,209,909-byte consolidated proof prefix, while its individual cube proofs remain separately valid. That is precisely the distinction between per-cube evidence and a checked composition.

## 2. P1 — Native LRAT plus Lrat-Trim, checked on demand (certificate engineering)

### Source and exact assumption

Florian Pollitt, Mathias Fleury, and Armin Biere, *Faster LRAT Checking Than Solving with CaDiCaL*, SAT 2023, LIPIcs 271, pp. 21:1–21:12, DOI [10.4230/LIPIcs.SAT.2023.21](https://doi.org/10.4230/LIPIcs.SAT.2023.21), full text <https://drops.dagstuhl.de/storage/00lipics/lipics-vol271-sat2023/LIPIcs.SAT.2023.21/LIPIcs.SAT.2023.21.pdf>.

* Section 4, pp. 21:5–21:6: LRAT antecedent IDs enable backward reachability/trimming from the empty clause. Lrat-Trim checks resolution chains and deletion discipline; forward checking uses less memory, while backward trimming must retain the proof. The paper reports typical 2–3-fold trimming, not a guarantee for K58.
* Section 5, pp. 21:7–21:9: on 127 UNSAT SAT Competition 2022 instances, their complete native-LRAT flow averaged 30% overhead over plain solving, versus 180% for DRAT and 125% for FRAT. Direct LRAT proof production itself averaged 5% overhead in their `/dev/null` comparison. These are **different instances and a 2023 solver**, so they are a hypothesis to calibrate, not an expected K58 speedup.
* Current upstream source: `arminbiere/lrat-trim`, latest commit inspected `423194927df747528d5b7364806b5b77b2660c12`, <https://github.com/arminbiere/lrat-trim>. Its README says it reads/checks/trims LRAT; `NEWS.md` documents binary-ID compatibility and simple RAT checking. `lrat-trim` is not the final trusted checker: replay its trimmed output with `cake_lpr` or another independently justified checker.

### Fit to the actual formulas

Run this on the **same exact** parent/cube, with the same seed and native policy. Do not regenerate only the host or frozen units. For the retained arm-3 setting, the input must include host + fixed units + all sender/support/bound suffix clauses and the exact split units. If optional 45-edge MCF clauses are present, the proof concerns that strengthened formula only; the normal-form reduction and all physical premises remain separate.

The candidate replaces

$$F\to\text{DRAT}\to\text{DRAT-trim search/elaboration}\to\text{LRAT}\to\text{verified check}$$

by

$$F\to\text{native LRAT}\to\text{Lrat-Trim dependency slice}\to\text{verified check}.$$

Trimming is proof-ID dependency slicing, not textual clause filtering. It can also produce a smaller clausal core, but any learned cube blocker must come from the **failed assumption core** and be replayed, as `cubelearn.py` already requires.

### Bounded local capability check actually run

I used the existing, already solved H=8 child at

`/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/k58-0404-word-search/H8-word0.cnf`

with query SHA-256 `e8cc97847a6cab9c277933d2dd0d6112c79b061bebb5af221d57df5d6d6a2229`, and wrote only under

`/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smx04thj8/m3/.scratch/native-lrat-h8/`.

The command used pinned CaDiCaL 2.1.2 SHA-256 `a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b` with `--seed=0 --lrat --binary=true -c 50000 -t 20`. The incumbent DRAT hash also matched its receipt (`55a3963489aad6bab8f2c3069f29045a94d88768f2529c242506f7f23c678eb2`); the new LRAT hash is `05f0d7f11d28e0a784cab3a1a737960fdc8bc5414cc246242d743bb668bd7b34`. Result:

| metric | stored native DRAT | direct native LRAT |
|---|---:|---:|
| conflicts | 49,226 | 49,226 |
| decisions | 307,381 | 307,381 |
| propagations | 12,350,047 | 12,350,047 |
| restarts | 3,189 | 3,189 |
| process CPU s | 1.58 | 1.83 |
| proof bytes | 9,529,642 | 14,594,230 |

Thus this one case preserved the search trajectory exactly, cost 1.158× CPU, and emitted 1.531× raw proof bytes. It is **not yet a win**: trimming, conversion, and verified-checking time must be included. Solver exit was 20 (`UNSATISFIABLE`). No wall search was run. **I did not install an external checker and did not independently replay this new LRAT**, so my receipt is a capability smoke, not a refutation certificate. Exact evidence: `.scratch/native-lrat-h8/{summary.json,solver.log,time.log}` in this member directory.

### Minimal 30-minute A/B

1. Use this H=8 case plus two already closed frozen-cover cases from the old DRAT/LRAT sample, including the heterogeneous `f1f2e034` if available. Do not use an OPEN wall parent.
2. Regenerate and hash-check every CNF; replay the incumbent DRAT first. Run fresh DRAT and direct LRAT with identical policy/seed and a cap known to close each case.
3. Build/pin Lrat-Trim `4231949…` and `cake_lpr` `033aad53d1733bd4b8ca41cf6f1b5fb5d84f8de2` only in an isolated tool directory (subject to the campaign's external-tool approval rule). Record binary/source hashes.
4. Compare **whole certificate pipelines**: solve + conversion/trim + verified replay + compression + maximum RSS + retained bytes. Validate the trimmed LRAT against the exact original CNF with `cake_lpr`.
5. New compatibility controls: alter one antecedent ID, feed the LRAT to a different parent hash, and truncate within a binary hint. These test native-LRAT integration rather than duplicating old fake-checker controls.

**Advance only if** both real cases pass independent replay and direct native LRAT improves either total certificate CPU by at least 20% or peak memory substantially without increasing final retained size. **Abandon** if the LRAT cannot be replayed, the changed proof overhead causes a previously closing case to time out, or trimmed end-to-end cost is no better than the incumbent on two of three cases. A positive H=8-only result licenses no extrapolation to the 11 wall profiles.

## 3. P2 — A two-level `cake_lpr` cube-cover export (certificate engineering)

### Source and exact method

Yong Kiam Tan, Marijn J. H. Heule, and Magnus O. Myreen, *Verified Propagation Redundancy and Compositional UNSAT Checking in CakeML*, International Journal on Software Tools for Technology Transfer **25** (2023), 167–184, DOI [10.1007/s10009-022-00690-y](https://doi.org/10.1007/s10009-022-00690-y), author-hosted full text <https://research.chalmers.se/publication/534843/file/534843_Fulltext.pdf>.

* Section 4.1: a top-level sequence adds/deletes clauses. Checking range $(i,j)$ establishes that satisfiability of the accumulated $F_i$ implies satisfiability of $F_j$. A complete set of ranges therefore composes without one monolithic underlying proof.
* Section 4.2, Figures 7–8: for exhaustive cubes $G_1,\ldots,G_n$, add $\neg G_i$ at the top level, justify each by the proof for $F\land G_i$, and finish with the cover refutation. A **proved failed-core subset** $H_i\subseteq G_i$ may replace $G_i$; arbitrary core deletion is not licensed.
* Sections 5.1–5.2: `cake_lpr <DIMACS> <COMP> i-j <LPR>` checks individual ranges and `... -check <OUTPUT>` checks their coverage and matching file hashes. The paper explicitly warns that users must supply the correct separate executions. Its MD5 is only convenience, not a cryptographic identity proof; retain SHA-256 in the campaign manifest.
* Section 6.4: a 5,226-line Erdős-discrepancy composition contained 20 million additions, with underlying LRAT files from 88 bytes to 110 MB. It checked in parallel with good speedup, but this memo does **not** propose saturating CPUs. The relevant new feature here is independent range semantics and avoiding one giant proof.
* Current official repository: `tanyongkiam/cake_lpr`, commit `033aad53d1733bd4b8ca41cf6f1b5fb5d84f8de2`, <https://github.com/tanyongkiam/cake_lpr>. Its README documents native binary LRAT/LPR, the two-level commands, and heap/stack flags. This inspected 1 November 2026 version says it is the last update before a replacement, so pin it rather than following a moving default branch.

### Exact fit to wallcc

For one parent $P$, reuse `export_drat.py::inspect/check_binding/validate_artifact` and its exact cube plan. Generate a separate underlying proof for each

$$P\land\bigwedge_{k<i}\neg H_k\;\longrightarrow\;\neg H_i.$$

The input $P$ must be the full ordinary parent (or an explicitly labelled strengthened parent), and the same checked `cas.drat` prefix must be included when applicable. Use **compact RUP-only lifting**, not a blind reuse of generic RAT steps: RUP remains valid with extra preceding blocker clauses, whereas RAT is not in general monotone under such additions. Keep `compact_leaf`'s unit-deletion filtering semantics and verify each generated proof independently.

The top-level file then contains the cube blockers in plan order and the exact split/cover derivation. This directly targets the failure mode in which all individual cube certificates are valid but an 848 MB concatenated prefix is not a certificate. It does **not** merge the 113,179 unrelated frozen-cover CNFs; those are different structural inputs, not cubes of one formula. It also does not turn the 67 high-$H$ scoped exclusions into a whole-parent cover.

### Minimal test, requiring no wall solve

1. Add an opt-in `export-lpr` beside, not in place of, `export-drat`. Start from one existing **complete** `wallcc` self-test cover that already passes both `verify` and compact `export-drat`. Convert each guarded leaf independently to LRAT/LPR and generate the summary and final cover proof.
2. Require `cake_lpr` range checks plus the final `-check` output, and compare with the incumbent whole-parent DRAT result, bytes, and sequential CPU/RSS. Then repeat on the already checked four-case resolution tree in `.scratch/k58-0404-cube67`, clearly labelled a scoped control, not a whole row.
3. Controls must reject: a missing final cover line; an interval gap; the right proof with a neighbouring cube; a prior-blocker clause omitted from the underlying input; a wrong parent hash; and a corrupted underlying antecedent. These controls target the new composition boundaries.
4. Only after those pass, apply it to an already completed real wallcc cover. Never use arm3, whose leaf is OPEN.

**Abandon** if the adapter needs unverified “proof hints” rather than a replayed derivation, if preceding blockers cannot be included without invalidating the chosen proof steps, if range/file consistency cannot be made fail-closed, or if total size/check cost exceeds the incumbent by more than 2× without a compensating trust or memory benefit. Parallel range checking is a later convenience, not a reason to adopt it.

## 4. P3 — One exact incremental LIDRUP cover versus fresh leaf jobs (throughput + certificate experiment)

### Sources and limitations

Katalin Fazekas, Florian Pollitt, Mathias Fleury, and Armin Biere, *Certifying Incremental SAT Solving*, LPAR 2024, EPiC Series in Computing 100, pp. 321–340, DOI [10.29007/PDCC](https://doi.org/10.29007/PDCC), full text <https://kfazekas.github.io/papers/FazekasPollittFleuryBiere-LPAR24.pdf>.

* Sections 2–3: each query is $(\Delta_i,A_i)$ against the accumulated clauses. An UNSAT query is certified by deriving $\bar A_i$, or a failed-core subset; an empty core means base-formula UNSAT. SAT and UNKNOWN are distinct statuses. LIDRUP adds clause IDs and antecedent hints to IDRUP.
* Section 4: the recommended checker input is **both the ICNF interaction file and the LIDRUP proof**. Proof-only mode requires independent assurance that recorded interactions match actual calls. It checks queries, models, weakening/restoration, and failed-core derivations. The paper leaves incremental proof trimming as future work and notes the acyclicity obligation.
* Sections 6–9: LIDRUP can be substantially larger than IDRUP but checks faster. Their BMC/SMT experiments support feasibility in those applications, not a K58 speedup. Online pipes avoid storage but can block if proof flushing is infrequent.
* Current checker source inspected: `arminbiere/lidrup-check`, commit `3ae8c23cd978c313ee14472327bf0f9560601015`, <https://github.com/arminbiere/lidrup-check>. Pin a checker compatible with the **2.1.2 trace**, rather than assuming current master and the old solver have identical formats.

Also relevant is Florian Pollitt et al., *CaDiCaL 3.0*, SAT 2026, LIPIcs 377, pp. 40:1–40:14, DOI [10.4230/LIPIcs.SAT.2026.40](https://doi.org/10.4230/LIPIcs.SAT.2026.40). Section 2 states that unconditional RAT addition is incompatible with incremental reasoning. Section 4 permits it only for latent extension variables absent from inputs and temporarily eliminated clauses, with an explicit allocation contract (LIDRUPE). The bundled 2.1.2 experiment must therefore stay within its supported incremental LRUP behaviour; do not add arbitrary BVA/RAT learned clauses and call the result LIDRUP-certified.

### Fit and risk

For an exact cube cover of one parent $P$, put every host and non-host base clause in the ICNF once. Every split literal remains an **assumption** in its `q` line; no cube literal is permanently added as an input clause. The candidate may reuse preprocessing and safely retained learned clauses between related cubes. Compare that against fresh default CaDiCaL jobs with the same cube order and per-query conflict caps.

The formula boundary is unchanged: ordinary $P$ is still all host + fixed-unit + 31-sender + 15-support + final-bound + split-related clauses at their actual variable IDs. Optional MCF is a different strengthened base $P'$, never silently part of the ordinary proof. A final solver-level `UNSATISFIABLE` after all cubes is not by itself a parent DRAT; closure requires checked ICNF/LIDRUP queries plus the independent exhaustive-cover derivation, or a subsequent ordinary parent proof.

### Minimal A/B

1. Choose an already complete small two/four-cube cover and one completed nontrivial real cover, not the current arm3 wall. Freeze full parent and cube hashes. Arm A solves each fresh child with DRAT; arm B makes one `p inccnf` sequence with identical cubes and `--lidrup`.
2. Check B with both ICNF and LIDRUP, not proof-only mode. Require every `q` to equal its planned cube, every `u` to be a subset of that query, and every SAT model to satisfy the full intended base. Preserve UNKNOWN as OPEN.
3. Feed proved failed-core blockers into P2's composition, or independently regenerate an ordinary parent proof. Include LIDRUP production/checking, parent composition, all I/O, proof bytes, and peak RSS in the comparison. Test offline and piped checking separately because they have different backpressure risks.
4. New negative controls: omit one literal from an ICNF `q` while leaving the proof unchanged; delete a required `u`; splice a valid trace from a different cube order; and treat a cube unit as a permanent `i` line. All must be rejected or explicitly marked non-equivalent, never promoted.

**Advance only if** the complete incremental interaction checks, a checked parent-level composition is retained, and total end-to-end CPU improves at least 10% on both cases with bounded trace growth. **Abandon** if checker compatibility is unresolved, only a trace prefix is available, no exact parent-level composition results, LIDRUP exceeds 1.5× the fresh proof bytes without a total-time win, or the two searches have incompatible work ids so the A/B cannot distinguish learning from luck. Failed BMC-style reuse would not be evidence that any wall cube is UNSAT.

## 5. P4 (conditional) — Stream native LRUP into `lrat_isa` (certificate memory engineering)

Peter Lammich, *Fast and Verified UNSAT Certificate Checking*, IJCAR 2024, LNCS 14739, pp. 439–457, DOI [10.1007/978-3-031-63498-7_26](https://doi.org/10.1007/978-3-031-63498-7_26). The official repository is <https://github.com/lammich/lrat_isa>, commit `99b832b501f473f7890f20b99755b5ace86eae48`.

The repository README—not an inferred paper abstract—establishes the compatibility boundary:

* the checker accepts **LRUP**, not arbitrary RAT/LRAT; successful output is `s VERIFIED UNSAT`;
* it can read the certificate from stdin, with documented `cadical -n -q --lrat ex.cnf - | lrat_isa ex.cnf` for CaDiCaL $\ge1.9.4$;
* formal verification is against a DIMACS grammar and down to generated LLVM. Building that generated checker requires Clang and Boost iostreams. Isabelle-2024 is needed to recheck/regenerate the formal proof, not merely to invoke the existing generated binary.

The full author PDF URL <https://www21.in.tum.de/~lammich/isabelle_llvm_par/IJCAR2024.pdf> returned **HTTP 403** to both direct fetch and `curl`. I therefore make no local performance claim from that paper; use the repository for capabilities and measure them here.

**Fit test only after P1 generates a checkable LRAT:** inspect the actual proof for RAT/negative-antecedent steps. If any are required, this route is closed for that proof. Otherwise stream P1's native output into the pinned checker on H=8 and one larger closed case, verifying exact parent hashes and comparing maximum RSS, total CPU, and final storage against offline Lrat-Trim + `cake_lpr`. Reject short reads, a SAT control, wrong CNF, and trailing garbage. Use only pre-existing build prerequisites; no external package installation is authorised here.

**Abandon immediately** on unsupported RAT, binary-format mismatch, unavailable prerequisites, pipe deadlock/backpressure, or no memory/storage advantage. This is an alternative checker for P1, not a fifth solver proposal and not a replacement for the P2 cover proof.

## 6. Global traps and no-go items

1. **No IDRUP/LIDRUP as ordinary DRAT.** An assumption conflict is not an empty clause of the parent. Require exact ICNF interactions and a separate exhaustive-cover proof.
2. **No unit-filtered prefix promotion.** Dropping deletion records to silence `drat-trim` warnings requires explicit normalisation and full replay. Never accept a valid prefix plus trailing bytes.
3. **No arbitrary assumption-core minimisation.** Deleting an assumption weakens the query and requires a new refutation. A core-derived $\neg H$ is usable only when $H$ is the independently checked failed core. Duplicate parent/cube units need multiset-aware treatment, as in `cubelearn.py`.
4. **No equisatisfiability/implication swap.** MCF normal forms, extension variables, RAT, and PR steps are not automatically parent-entailed clauses. A full refutation of the exact strengthened input can be valid, but individual exported lemmas need the separate reduction proof.
5. **No naive clause sharing across cubes.** Existing signed-map transport already specifies exact source-core inclusion, total variable mapping, and fresh target replay. LIDRUP is the controlled way to test retained learned clauses; ad hoc clause copying is not.
6. **No textual LRAT slicing or deletion “normalisation”.** Use clause-ID dependency trimming and replay. LRAT/LIDRUP clause IDs, hint order, restore/weaken state, and binary encoding are semantic.
7. **No hashes as evidence.** SHA-256 binds bytes but does not validate them or authenticate their producer. `cake_lpr`'s MD5 range tag is convenience only. Checker output must require the exact success line, exit status, complete input consumption, and bound query/proof hashes.
8. **No whole-wall extrapolation or second permanent archive.** Use one closed control and one heterogeneous closed real case, on demand. A timeout or failed local composition remains OPEN.
9. **No repeat of the old DRAT-to-LRAT blanket conversion, Lean `lrat_proof` on huge proofs, generic cores/signed transport, or parser toy controls.** Those already exist and have measured limitations.

## 7. Recommended order, cost, and information gain

| priority | expected information from a bounded ($\le30$ solver-minute) test | isolated implementation estimate | destructiveness |
|---|---|---|---|
| **P1 now** | Whether eliminating DRAT elaboration actually repays the measured direct-LRAT production/size cost on three heterogeneous closed cases | about 0.5–1 day for an opt-in driver, pins, and receipts | None to stock `run`/`finalise`; discard artifacts on failure |
| **P2 next** | Whether per-leaf proofs can be composed without the monolithic export while retaining a verified whole-cover result | about 2–4 days for range generation, conversion, and six new fail-closed controls | New opt-in exporter only; incumbent DRAT export remains the control |
| **P3 after P1/P2** | Whether safe cross-cube reuse outweighs LIDRUP size/checking and gives a real parent composition | about 3–5 days for ICNF integration, a 2.1.2-compatible checker pin, and composition | Highest protocol risk; never enable on production without a matched A/B |
| **P4 conditional** | Whether streaming an actually RUP-only proof removes the memory/storage bottleneck | about 0.5–1 day only if prerequisites already exist | Stop immediately on RAT/format/prerequisite mismatch |

Complete P1 first: the local smoke proves immediate compatibility but shows a 15.8% production-time cost and 53.1% raw-size increase, so only the full pipeline can justify it. P2 has the closest published correspondence to the actual cube-cover object and attacks the monolithic-composition bottleneck without touching solver policy. P3 is a falsifiable experiment, not a deployment recommendation. P4 is only viable for RUP-only proofs when memory is the limiting factor.

All four leave the physical `ChainReady` work exactly where it was. Their purpose is to make any future exact CNF closure cheaper to certify and compose, not to assert such a closure.
