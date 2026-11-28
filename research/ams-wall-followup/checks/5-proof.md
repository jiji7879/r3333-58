# Exact-parent semantic clause map for the retained K58 wall row

## Outcome

This direction produced an **exact clause-family map and independently checked allocation inventory** for the one requested parent, together with a precise list of the remaining physical-colouring obligations. It did not run a SAT solver, create an UNSAT proof, or claim a wall/profile/Ramsey closure.

The target is row `06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`, profile $(16,16,14,11)$, charge $7$, family `arm=1`, root kinds `T,U,-,-`, marked template `15,T`, `mark_position=0`, `root_position=7`, placement `[0,0,0]`. At repository HEAD `bb0544cfdc508c5e33de0855604ce90ee37978c8`, the retained hashes were checked again:

* parent: `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`;
* working CNF: `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38`;
* RUP/CAS prefix: `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3`;
* plan: `683969b82a6459befa58d75321fc1873dc26b63d01c5a9c64b8bfa0e46c1c29e`.

The independently re-emitted parent is byte-for-byte equal to the retained parent (`cmp` passed), including clause order and final newlines. The working formula has the same 19,533 variables, contains the 184,335 parent clauses as an exact prefix, and has exactly the planned 315 additional search-clause lines. The CAS prefix was hashed but **not replayed or treated as a parent proof**.

## 1. Exact formula inventory

The recipe is exactly `tables=True,total_critical=True,full_root=False`. The parent has 19,533 variables and 184,335 clauses.

| family | parent clauses (1-based) | count |
|---|---:|---:|
| host exactly-one constraints, seven interleaved clauses per edge | 1–11,571 | $7\binom{58}{2}=11,571$ |
| monochromatic-triangle exclusions | 11,572–134,995 | $4\binom{58}{3}=123,424$ |
| frozen signed physical units | 134,996–135,433 | 438 |
| 31 guarded sender counters and 15 support families, in generator order | 135,434–183,949 | 48,516 |
| unguarded marked-arm floor counter | 183,950–184,054 | 105 |
| unguarded total-critical floor counter | 184,055–184,335 | 281 |

The guard/support portion subdivides into 21,621 sender-counter clauses and 26,895 support clauses. There is no full-root floor counter. All 48 non-host suffix blocks and their per-block SHA-256 values are listed in `results/clause-blocks.json`.

### Host and frozen units

With $4\binom{58}{2}=6,612$ physical variables, literal $4i+c+1$ denotes colour $c$ on the $i$-th edge. Each edge has one four-literal at-least-one clause and six pairwise exclusions; each triple and colour has one negative ternary clause. Consequently a valuation of these variables satisfying the host family is precisely a four-colouring with no monochromatic triangle. This is a direct syntactic argument, not a trusted solver assertion.

The 438 frozen units are fully decoded in `results/frozen-units.json`: every record gives its parent clause, signed literal, endpoints, colour, value, and all generator provenance labels. Their source-label occurrences are:

* 57 root-profile assignments;
* 240 classified-root-template assignments (120 T16 and 120 U16);
* 105 marked-T15 assignments;
* 56 marked-neighbourhood assignments.

These total 458 labels but 438 unique units: 14 marked-template units duplicate root-profile units and six duplicate classified-root-template units. There are 396 positive and 42 negative units. The 56 marked-neighbourhood units contribute 14 positive memberships and 42 negative nonmemberships. The reconstruction of this provenance was compared with the generator's complete signed-unit list.

### Sender guards and counters

Only vertices in the two critical arms are possible sender generators here. There are 32 such vertices: 25 small-arm vertices are skipped, and vertex 17 in colour 1 is automatic because it has exactly 14 pinned hits. Its 14 positive pinned literals are explicitly listed in `results/senders.json`. No guard is allocated for vertex 17; this automatic sender reduces both initial floors from $7$ to $6$.

The other 31 vertices receive guards. Each guarded family has the exact form

$$\{\neg g_{x,c}\}\mathbin{\triangleright}\operatorname{AtLeast}(X_{x,c},b_{x,c}),$$

where $\triangleright$ means that the naive parent prefixes `-g` to **every** native Sinz clause. The inputs $X_{x,c}$, positive pinned hits, omitted literals, bound, allocation range, and every absolute parent-clause position are in `results/senders.json` and `results/counters.json`. The size distribution is exact:

| colour | multiplicity | inputs $n$ | bound $b$ | counter cells | clauses | recurrence / overflow |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 4 | 30 | 10 | 200 | 390 | 380 / 10 |
| 0 | 12 | 41 | 14 | 378 | 743 | 729 / 14 |
| 1 | 15 | 41 | 14 | 378 | 743 | 729 / 14 |

The 15 marked-arm guards belong to senders 18–32. The final floor inputs are therefore 15 marked guards with bound 6, and all 31 critical-arm guards with bound 6. They respectively use 54 and 150 fresh counter cells.

A separately written staggered-Sinz implementation matched **every actual counter clause in order**, not merely as a set. This covers all 31 guarded native at-least counters and both unguarded floor counters. The implementation also matched every allocation top. It is a computational binding to the current native definition in `lean/K58/EncoderExtensions.lean`, not a replacement for a Lean whole-formula equality proof.

### Support selectors

For each of the 15 marked-arm guards, the only classified target is arm 0. The actual catalogue is `allowed_supports(16,T,target_arm=0,marked_color=1)`. An independent direct connectivity/edge-count enumeration, rather than the source's degree shortcut, reproduced the catalogue exactly:

* 96 four-vertex paths;
* 16 five-cycles;
* **112 supports in total**.

The palette computed by the generator is `[2,3]`, but its P4/C5 test uses **only `palette[0] = 2`**, while excluding internal edges of marked colour 1. Thus a generic theorem saying “there is a P4/C5 in either remaining colour” would not prove membership in this emitted catalogue. The required statement is membership in this exact colour-2 catalogue. `results/support-catalogue.json` lists all 112 support sets.

Every one of the 15 emitted families has all 112 selectors, all 16 implications per selector, and one main disjunction. There are no omitted pinned implications (`must=cannot=empty`). Hence each family has

$$112\cdot16+1=1,793\text{ clauses},$$

and together they have 26,880 implications plus 15 disjunctions. For a support $P_i$, the implication signs are exactly the characteristic vector of the sender's 16 colour-1 adjacencies into arm 0: positive at indices in $P_i$, negative elsewhere. The second checker compared every one of these implications and all 15 main disjunctions against the parent bytes. Per-selector allocations and clause positions are in `results/support-selectors.json`.

### Total and disjoint fresh allocation

The 12,921 auxiliary variables admit the following complete accounting:

| role | variables |
|---|---:|
| sender guards | 31 |
| sender Sinz cells | 11,006 |
| support selectors | 1,680 |
| marked-floor Sinz cells | 54 |
| total-critical-floor Sinz cells | 150 |
| **total** | **12,921** |

Together with 6,612 physical variables this gives 19,533. `results/allocations.json` lists contiguous variable intervals with inclusive `first`/`last` bounds. The audit checked that these intervals start at 6,613, are pairwise disjoint, have no gaps, and end at 19,533. Guards and selectors are pairwise distinct. This discharges the **row-specific computational allocation inventory**, but not the Lean list assembly that must use it.

## 2. Exact conditional-Sinz boundary inventory

For one guard, write its hard native counter as $R\cup O$, where $R$ contains recurrence/main/forward clauses and $O$ contains overflow/bound clauses. The current parent emits

$$N_g=\{\neg g\lor C:C\in R\cup O\}.$$

The boundary form is

$$B_g=R\cup\{\neg g\lor C:C\in O\}.$$

On the exact parent there are **21,203 recurrence clauses and 418 overflow clauses** in the 31 guarded sender counters. A boundary conversion would therefore remove exactly 21,203 `-guard` occurrences and retain the required 418, without changing the number of clauses or variables. `results/counters.json` marks every absolute parent clause as `recurrence` or `overflow`.

The projected-equivalence argument is short and does not involve the physical bridge:

* $B_g\Rightarrow N_g$ immediately by clause weakening.
* If $g$ is true, both forms impose the same native at-least counter.
* If $g$ is false, $N_g$ is vacuous; for $B_g$, use the constructive Sinz recurrence extension on fresh counter cells. Guarded overflow clauses remain vacuous.
* The independent overflow clauses give the same violating-input rejection when $g$ is true. Dropping those guards as well would be unsound.

The total disjoint allocation above allows these per-counter extensions to be composed without changing physical inputs, guards, or previously allocated cells. This is an **encoder-equivalence inventory only**. No transformed-parent A/B was run here, so it is not evidence of a speedup and does not overturn the earlier slower boundary pilot.

## 3. Configurable maximal normal form audit

The accepted configurable-MCF premise was also checked independently on the exact parent. For internal edges of small arms 2 and 3:

* 20 edges are excluded because they occur in frozen units;
* the remaining **126 edges** are the configurable set $F$;
* none of their $4\cdot126=504$ physical variables occurs anywhere in the actual 49,340-clause non-host suffix (438 frozen units plus 48,902 threshold/support clauses).

The exact edges, physical variables, and 20 fixed exclusions are in `results/mcf-config.json`. A second checker recomputed disjointness against the parsed parent, not just against the traced suffix.

The safe-recolouring argument remains the following equisatisfiability argument. Given a good colouring, process $F$ in a fixed order: if an edge is not colour $c=0$ and no global two-edge $c$-path joins its endpoints, recolour it to $c$. No new $c$-triangle can arise, other colour classes only lose edges, old $c$-paths are never removed, and variables outside $F$—including all non-host auxiliary inputs—are unchanged. At termination, every $F$ edge is $c$ or has a $c$-path witness. Define each fresh witness by the conjunction of its two path edges; then its three defining clauses and the final disjunction hold. Conversely, deleting the new constraints from a satisfying augmented model gives a model of the original.

There are $58-2=56$ witnesses per selected edge, so the standard augmentation has exactly

$$126\cdot56=7,056\text{ variables},\qquad 126\cdot(3\cdot56+1)=21,294\text{ clauses}.$$

This is **not a DRAT implication**, not a new performance result, and not a licence for full/pinned MCF. In particular, including any of the 20 fixed exclusions violates the suffix-invariance premise used here.

## 4. Remaining full-parent semantic obligations

The exact map reduces the remaining bridge to the following concrete obligations; none is silently discharged by this audit.

1. **Physical realization of frozen units.** Prove that a physical semantic-row colouring, after the justified root/template/placement normalization, satisfies every one of the 438 signed units in `frozen-units.json`. The host syntax alone does not supply the root/template existence or placement theorem.
2. **Criticality into guard premises.** For every record in `senders.json`, prove that physical criticality supplies the stated pinned hits plus candidate threshold. This includes vertex 17's 14 pinned hits and the degree-14 accounting after the root edge is counted. A guard is only an auxiliary selector; its physical meaning is not asserted by the counter syntax.
3. **Floor witness selection.** Prove that the selected physical senders give at least six true guards among the listed 15 marked guards and at least six among the listed 31 total-critical guards, in addition to the automatic sender accounting. This is where the marked/total floors and $w(r)\le H(r)$ argument must enter. `full_root=False` must not be replaced by a stronger full-root claim.
4. **Actual support membership.** For each guarded sender 18–32 with its guard selected true, prove that its physical colour-1 neighbourhood in arm 0 is exactly one of the 112 supports in `support-catalogue.json`. This requires critical-support geometry in the specified template, path/cycle colour 2, and exclusion of internal marked-colour-1 edges. The existing Boolean selector-extension theorem takes this as a premise; it does not prove it.
5. **Lean allocation composition and list/byte identity.** Use the now-explicit disjoint intervals to compose the native-counter and support-selector extension lemmas, then prove that the resulting Lean CNF list is exactly the emitted ordered list and that its DIMACS serialization hashes to `90d06e...`. The independent ordered computational comparison is a useful blueprint, not the kernel equality itself.

Only after these obligations, and a separate ordinary whole-proof UNSAT certificate for the exact relaxation, could a physical-row UNSAT conclusion be entertained. No such certificate was produced here.

## 5. Verification and scope separation

Commands are recorded in `reproduce.sh`. The first program reconstructs the row, parent, gadgets, native Sinz streams, support catalogue, allocation intervals, and MCF premise. The second, separately written `verify_map.py` reparses the parent and checks the emitted maps against its bytes. The second-checker pass caught an off-by-one support-disjunction metadata offset during development; that generator metadata was corrected, the artifacts were regenerated, and the entire verification was rerun successfully.

Final `results/verification.json`: **PASS**, with 184,335 strict parent lines, 48 suffix blocks, 33 ordered counter streams, 26,880 selector implications, 15 selector disjunctions, 438 unit positions, 12,921 allocated variables, and 504 MCF-disjoint physical variables checked. Actual artifact hashes are in `SHA256SUMS`.

The three requested categories remain separate:

* **CNF performance:** no wall solver or cubing run was performed; no speedup is claimed.
* **CNF certification:** zero SAT/UNSAT verdicts, zero proof replays, and zero cube queries. The RUP/CAS prefix is a hashed input, not a verified parent refutation here.
* **Physical colourings:** the exact encoding/allocation map and outstanding semantic premises are supplied; the full-parent semantic assembly and colouring-level row closure remain unfinished.
