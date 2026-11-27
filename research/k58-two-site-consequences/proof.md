PROVED — only the literal, scoped evidence claims below. This does not prove a
Ramsey bound, close representative 0 or either whole pivot branch, close a wall
row, or exhibit a K58 model.

# Scoped audit of `K58_two_site_consequences`

## 1. Objects and exact notation

The audited input is
`attachments/let-s-try-and-rbdv/K58_two_site_consequences.zip`, SHA-256
`7cb24544a5f8d3afe78e0fb9cc2f7cc3318a87a15a8bbf34af1893b48059e48d`.
All 444 entries of its shipped `SHA256SUMS` pass without truncation.

Let $P$ be the decompressed `signed-parent.cnf.gz`, with
`p cnf 19218 178823` and SHA-256
`ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`.
Its complete 58-vertex four-colouring constraint families were regenerated and
found as actual signed clauses:

| family | number |
| --- | ---: |
| at least one colour per edge | 1653 |
| at most one colour per edge | 9918 |
| negative monochromatic-triangle exclusions | 123424 |

These are present in $P$, `row-0.cnf.gz`, and all 47 reconstructed owner
parents. Additional signed/owner units and auxiliary clauses are retained.
The restored campaign source `revised.py::export` regenerates all 47 owners;
all 47 parent hashes and all 47 owner cubes match the package. This is not a
general claim about the provenance of every historical event digest.

The two trigger pins and pivot-use convention are

$$
T=((31,13)=0\land (42,13)=1),\qquad T\longleftrightarrow\{2721,2766\},
$$

and $5249+h$ is the variable for pivot $(31,42)=h$. A word $w=c_1c_2c_3c_4$
assigns those colours to
$(39,44),(40,41),(40,42),(40,44)$, using variable groups
$5945+c,6001+c,6005+c,6013+c$.

For each word $w$ define two different queries:

- **search:** $P+\{(31,42)=h\}+T+$ the four word units;
- **unsplit:** $P+T+$ the four word units, **without any pivot unit**.

None of these units is already fixed by $P$. `branch-h.cnf.gz` is a stronger
object, not an alias for $P+\mathrm{pivot}$: it has 31 ($h=0$) or 34 ($h=3$)
additional clauses beyond $P$, including the pivot and arm exclusions.
A proof of search or unsplit must therefore not be described as applying only
on those strengthened branches.

## 2. The twelve full-parent refutations

The claimed local-pivot listing is reproduced exactly:

| local pivot $h$ | closed word |
| --- | --- |
| 0 | `1113` |
| 3 | `0133,1013,1133,1333,3010,3031,3101,3103,3111,3133,3301` |

For every listed $(h,w)$, both the search query and the pivot-free unsplit query
were reconstructed and their archived SHA-256 values matched. The proof file
name is exactly `sha256(decompressed proof)+".rup.gz"`. All 24 resulting
binary DRAT replays passed all of the following:

- freshly compiled `tools/drat-trim.c`;
- arguments `-i -U -t 300`, **not `-w`**;
- return code 0;
- exactly one line `s VERIFIED` after CR/LF normalisation;
- zero `WARNING` and zero `ERROR` strings;
- no `NOT VERIFIED`, `UNKNOWN` or `DERIVATION` status;
- `0 RAT lemmas in core` (the RUP-only replay);
- the checker reports reading every byte of the supplied proof.

The per-case query/proof hashes and strict results are retained in
[checks/2-closure-receipts.json](checks/2-closure-receipts.json).

**Scope correction.** The eleven colour-3 and one colour-0 labels name the
locally generating words. Since the unsplit query has no pivot unit, each
unsplit refutation excludes its word under $T$ **regardless of pivot colour**.
Two representative unsplit proofs were also explicitly reused with the pivot
pinned to each of colours 0,1,2,3: all eight fresh cross-pivot checks passed.
This does not make any of the 24 remaining cases closed in any branch.

## 3. Exact local tables and the remaining 24-word frontier

The local projection uses the 30 vertices
$V=\{0,1,\ldots,15,31,\ldots,44\}$ and retains every clause all of whose
variables are physical edge variables within $V$ or owner auxiliaries
$18388,\ldots,19218$. Untrue/unmentioned variables are false under the
package's local-witness predicate; this is a finite local-model test, not a
total SAT assignment. Care is needed not to discard the owner clauses.

For both pivot signatures the pinned projection has **24,686 clauses**:
19,485 physical-edge-only clauses and 5,201 clauses involving owner
auxiliaries, in total using 831 such auxiliary variables. An earlier audit
projection accidentally retained only 19,485 and was rejected; its corrected
check matches the complete projection clause for clause.

The eight exact local tables were recomputed and all eight block-cover proofs
strictly replayed. Their word sets are:

| trigger condition | pivot 0 | pivot 3 | intersection |
| --- | ---: | ---: | ---: |
| neither | 57 | 36 | 29 |
| only $(31,13)=0$ | 57 | 36 | 29 |
| only $(42,13)=1$ | 57 | 36 | 29 |
| both | 8 | 28 | 0 |

All 315 witness entries in these eight tables were evaluated, not merely
counted, against their complete retained clauses and pins. Maximum measured
monochromatic degree was 15, which respects the specified $\le16$ cap.
The block-cover proofs complement those witnesses: outside a listed table,
the corresponding full pinned signed-parent formula is refuted. Exactness
does not rest on JSON metadata alone.

After the twelve full-parent closures, the exact remaining cases are:

- pivot 0 (7): `0001,0301,0311,1001,1310,3130,3310`;
- pivot 3 (17): `0103,0300,0303,0330,1103,1300,1301,1303,1313,1330,3001,3011,3110,3131,3300,3303,3330`.

`conditional-frontier.json` lists precisely these 24 distinct words. For each
pivot separately, its blocking clauses cover that branch's residual words, and
one further unsplit proof covers the common 24-word disjunction under only
$T$. The unsplit frontier query SHA-256 is
`d8c13f675dd31906da90e137722b135131445e25c93e710536487fa049da2270`.
All three proofs passed strict fresh replay.

**The 24 words are OPEN.** Their records contain about three seconds of
bounded search and no closure proof. No full-parent SAT model was obtained.
In particular, `OPEN` does not mean SAT, and one must not turn the trigger-level
frontier into closure of a pivot branch. Both whole branches and representative
0 remain open.

## 4. The 47 owner guard variants and two-site consequences

The owner indices are 47 distinct signed-parent guard variants of **one row**,
not 47 independent Ramsey cases. On them, the antecedent is
$A=((1,42)=3\land(4,31)=0\land(4,42)=1)$ and the tested target is
$(31,42)=3$.

The recomputed statuses are 14 `FORCED` and 33 `LOCAL_COUNTEREXAMPLE`, with:

- 11 records with a local antecedent witness:
  `0,3,5,7,11,12,19,23,24,25,32`;
- three genuinely impossible full antecedents `14,31,36`;
- 33 local, non-pivot-colour-3 witnesses.

Complete antecedent/subset coverage was checked. For live indices
`3,5,7,19,23,32`, the two pins $(1,42)=3,(4,42)=1$ already force the target;
all one-pin proper subsets have local witnesses. For live indices
`0,11,12,24,25`, all three pins are needed. For `14,31,36`, the three-pin
antecedent is impossible; the formal `FORCED` field is vacuous there and says
nothing has been forced under a feasible premise.

All 157 local owner/lattice witnesses satisfy the exact projected parent,
their complete specified pin list, aux range and degree cap. All 17
owner/antecedent proofs and all 17 subset-lattice proofs passed strict
warning-free replay. The separately written finite checker repeated the 17
owner-level proofs and the 14 minimal-lattice proofs; the full package verifier
under the strict proxy also passed the whole lattice.

`LOCAL_COUNTEREXAMPLE` is a misleading name for a **proper 30-vertex witness**,
not a global counterexample to the guarded implication. These 47 variants do
not by themselves cover the 11,585 production wall rows, and this subset is
not a uniform theorem on all rows or a blanket global forcing claim.

## 5. Other evidence and archive limits

The supplied full verifier was run under a strict checker proxy. Its **196**
checker calls all passed with the exact-status/no-warning gate, totalling
40.612 seconds of checker time on the final fresh execution. This included owner and subset proofs, cuts,
resolved clauses, ordinary-row evidence, pair covers, signature/control
covers, residual frontier and conditional recolouring. In particular, the
supplied two-branch pair searches remain 25 and 30 OPEN; their exact cover
proofs do not comprise SAT models.

Every relevant proof/query identity was rehashed, and formula regeneration was
not replaced by an assertion that manifest entries match. The accepted
archive/provenance audit agrees byte-for-byte with separate receipts for
parent identities, event bindings, secondary objects, final sums, search
identities and the frontier. Its missing historical event proof bytes remain
missing: 111 `.rup.gz` files are present, 99 referenced by JSON, and 12
unreferenced files were not used as evidence. Historical event-level digests
without supplied bytes were **not** counted as replayed proofs.

The earlier archive report's statement that its particular missing
`case0_report_audit/` recipe blocked source regeneration is not a general
workspace impossibility. The restored `audited-K58/revised.py::export` route
was separately run for all 47 formulas and matched; see
[checks/owner-regeneration.json](checks/owner-regeneration.json).

## 6. Checker defect and repair

The package's own verifier invokes drat-trim with `-w` and accepts a
substring `s VERIFIED`. This is not an acceptable validation standard.
A demonstrative corrupted proof still emits `s VERIFIED` with return code 0
and a warning in plain mode, while `-w` hides that warning and the original
criterion accepts it. The strict proxy removes `-w`, requires an exact single
status line, and rejects warning-bearing outputs.

The original twelve proofs, block covers and other accepted replays themselves
pass in that stricter mode. This report certifies those corrected replays, not
the original `-w` acceptance rule. Wrong-query and genuinely truncated-proof
controls were rejected. A two-byte tail deletion that remained accepted is
not, by itself, a valid negative control and is not claimed as one.

## 7. Reproduction ledger and what was not done

- [checks/2-compute.md](checks/2-compute.md): commands, hashes, timings and
  finite outputs. The independent checker passes 3,701 assertions and 42
  strict DRAT calls.
- [checks/2-model.md](checks/2-model.md): the three accepted independent
  directions, including repairs of genuine audit defects. The abandoned
  counting direction is not counted as evidence.
- [checks/2-read.md](checks/2-read.md): reading against the supplied claim.

No new SAT/SLS search, production sweep, production-ledger mutation or Ramsey
bound computation was started. No OPEN case was promoted to UNSAT or SAT.
No new Lean formalisation was started, and no Lean theorem is claimed: these
refutations are DRAT/RUP evidence checked by the native checker, not kernel
certificates. The input formulas and owned parents were regenerated for this
audit; full upstream historical event derivation remains outside the supplied
replayable evidence. All of those limitations are part of the result, not
qualifications to be silently dropped.
