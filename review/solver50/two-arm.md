# Direction D audit — row `1445e0649f7d`, profile `(16,14,14,13)`

## Verdict

**Unsupported split/count claims; two exact representative closures only; row still OPEN.**

The three supplied artifacts do not reproduce the quoted `121/128` two-arm,
`2/128` one-arm, or `0/128` one-arm claims. They contain only eight
cap-128 target receipts (one older raw receipt plus seven ledger receipts),
zero target 3-second trials, and no return/no-return split or complementary
status accounting. Those quotations must not be promoted into a split proof
or a row closure. This is an artifact-provenance verdict, not a claim that no
other experiment could ever produce those numbers.

Independently of the solver's `OPEN` labels, the existing local table gives a
sound refutation of exactly these two representative queries:

* `sorted`, words `00220/01201`;
* `sorted`, words `00210/01201`.

I regenerated the original first-tier parent, signed physical sorting guards,
and ten-literal cubes, lifted the existing local RUP, and checked each query
with **`drat-trim -i -U`, never `-w`**. Both returned `s VERIFIED`. The shared
local proof also passed independently, and a substantive first-step tamper
returned exit 1 with `s NOT VERIFIED`.

Neither pair belongs to the target's 50-pair new root cover. Indeed none of
the eight probed pairs belongs to that cover. Thus these closes are useful
exact representatives under the `sorted` convention, but **do not reduce the
new 50-job cover, close the unrestricted parent, or close the row/profile**.
No bounded 3-second joint-support refutation is justified by these artifacts:
the relevant target projection has checked models, not refutations.

## Input integrity and target census

Repository HEAD was `d19284ac7a1698a3296197cf0c133c6d5c1331e6`.
All 4,838 entries in the bundle's `SHA256SUMS` passed. The supplied external
`K58_wall_150000_representatives.tsv.gz` is byte-identical to the bundle's
`round50/campaign-ledger.tsv.gz` (gzip SHA-256
`897334cfcaceae03f13a0d242fb886c0633bc712d353a094373f7e5b5a539743`;
decompressed SHA-256
`63bbb8b466013c456367d5029b2cf73d162830be34ee2fb71c300b66fc06191b`).
Input hashes are in `INPUT_SHA256`.

The actual target receipts are:

| Convention | `w/z` | Cap | Conflicts | Solver status | Existing local/projection status | Independent verdict |
|---|---|---:|---:|---|---|---|
| raw (older trials) | `01200/12010` | 128 | 130 | OPEN | arm witness; joint SAT | not closed |
| sorted | `00220/01201` | 128 | 130 | OPEN | `EXCLUDED` | **strict representative UNSAT** |
| sorted | `00210/01201` | 128 | 128 | OPEN | `EXCLUDED` | **strict representative UNSAT** |
| sorted | `00010/00200` | 128 | 129 | OPEN | `ARM_WITNESS` | not closed |
| sorted | `00000/00002` | 128 | 128 | OPEN | `ARM_WITNESS` | not closed |
| preferred | `00021/00201` | 128 | 129 | OPEN | joining colors after proofs `{2}` | not closed |
| preferred | `00100/01021` | 128 | 128 | OPEN | joining colors after proofs `{1,2}` | not closed |
| preferred | `00121/01210` | 128 | 128 | OPEN | joining colors after proofs `{1,2}` | not closed |

`OPEN` is a budget outcome, not SAT evidence. Conversely, the two new strict
verdicts do not rewrite history: the campaign's own solver record remains
`OPEN`, while its independently applicable local table supplies the proof.

The three timed collections contain 12, 6, and 6 trials respectively. The
number naming this target is 0 in every collection. No target 3-second solve
was present, and I launched none.

The old row index gives 5,190 unrestricted live pairs, 651 admitted by the
column rule, 317 locally colorable two-smallest pairs, and 156 old preferred
jobs. The new queue has 50 jobs at global cover positions
`[90159,90209)`. The batch is stride-permuted, so these positions alone do not
show batch membership. Directly checking the target IDs in the 150,000-row
ledger gives **zero `round50` jobs**, hence all 50 are untested in the supplied
new-cover pass. `round50/queue.tsv.gz` records `root_status=OPEN`.

## Exact parent/query and proof identities

The target has pentagon `[31,32,35,33,34]`, selected outside vertices
`36,37`, physical palette `[1,0,3]`, and arm size 14.

The unaugmented original first-tier parent (`row_formula(row, 'first')`, hence
`full_root=False`; no balance or retry premise) is:

* `target/parent-first.cnf`;
* header `p cnf 18603 179242`;
* SHA-256 `c5549e8a2ae86391ba28a77d56118aa0c4b36a4732f49abc05c6ff3cb8895ad1`.

Each sorted query appends 336 signed physical sorting clauses and ten cube
units, producing header `p cnf 18635 179588`. The physical auxiliaries do not
collide with the parent. The source path is
`representatives.full_query(..., 'sorted')` plus independently replayed
`physical_order.mapping`; both cube literal lists are retained in
`target/receipt.json`.

| Exact sorted query | Query SHA-256 | Lifted proof SHA-256 | Strict result |
|---|---|---|---|
| `00220/01201` | `24f7d0ffd1d94c0f54b363e35166a38caded77252616bef22282ad7b4855a75f` | `46dc1170b79f69f0bb296733fe6446eee350a71260b8a00eeab4b9f37c0364f2` | `s VERIFIED` |
| `00210/01201` | `7bacb466aa497f01e946d0a6fbd999557604f73d90b2bab5d9230587ba28d898` | `46dc1170b79f69f0bb296733fe6446eee350a71260b8a00eeab4b9f37c0364f2` | `s VERIFIED` |

The lifted bytes are the same because the local forbidden-pair lemmas and
signed arm embedding are shared; the different ten cube literals are already
in each query. Each query was nevertheless regenerated and checked
separately. This avoids treating a naked `EXCLUDED` label as proof.

The shared local certificate is
`results/sorted-proofs/14-01201.rup.gz` from the supplied bundle. Its
regenerated query has SHA-256
`6043400033c77368341a049154402ce7d8219e6148f568185266174b1f3d214d`;
its decompressed proof has SHA-256
`86d1b17c65a30ca3a37ed0580bbc69a8b457627edf125332f77decb80f3b1fff`.
The receipt's five `covered_first_words` are precisely the allowed local
cases; both target first words are outside that list. The local query and RUP
are exported as `target/local-14-01201.{cnf,rup}` and passed `-i -U`.

For the two `ARM_WITNESS` jobs I checked the stored complete sorted-arm
models with `sorted_arm.validate`. These are local arm models only, not K58
models or complementary full-parent closures.

### Checker commands and controls

The actual positive pattern (run once locally and twice physically) was:

```sh
bundle/K58_wall_50k/tools/drat-trim target/local-14-01201.cnf target/local-14-01201.rup -i -U
bundle/K58_wall_50k/tools/drat-trim target/sorted-00220-01201.cnf target/sorted-00220-01201.rup -i -U
bundle/K58_wall_50k/tools/drat-trim target/sorted-00210-01201.cnf target/sorted-00210-01201.rup -i -U
```

All three exited 0 with `s VERIFIED`; logs are the corresponding
`target/*.strict.log`. `target/sorted-*.map`, `.local.rup`, and `.lift.rup`
retain the relabeling inputs and output used by `tools/relabel`.

For the negative control, only the first binary proof operation was changed
from addition (`a`) to deletion (`d`):

```sh
bundle/K58_wall_50k/tools/drat-trim \
  target/local-14-01201.cnf target/local-14-01201.tampered.rup -i -U
```

It exited 1, reported `c RUP check failed` and `s NOT VERIFIED`; see
`target/local-14-01201.tampered.strict.log`. (Edits only to ignored/final
redundant operations are not used as the negative result.)

## Joint-support and complementary-scope decision

The target's signed geometry key is `6151016d31e79ca8a8f0b4c2`, with a
24-vertex raw joint projection (15 marked-template vertices plus nine arm
vertices outside the pentagon).

* All 50 new-cover records under this exact key in
  `round50/joint/all-classes.tsv.gz` have explicit models. I rechecked each
  with `joint50.check`, including the selected words, sorted remainder,
  minimum new-cover pair, and marked-template constraints.
* All 792 records under this exact key in the older `results/raw-glue.tsv.gz`
  retry table are `SAT` with explicit models. I rechecked every model with
  `raw_glue.validate`. This is the table's sample/geometry scope, not a proof
  of all 5,190 raw pairs or any full parent.

Consequently the nominated-arm plus marked-template/joint-support projection
cannot supply a refutation of this target under any solver timeout. A 3-second
run there would only rediscover feasibility or time out on a weaker projection.
The target is also absent from the separate three-arm sample, so that sample
does not supply a stronger target projection either.

There is no return/no-return pair in the supplied target receipts. The numeric
`branch=4` is the frozen row's branch identifier, not a complementary logical
return split. With no two branch formulas and no statuses on both branches,
there is no complementary closing argument to promote.

**No joint-support experiment queries are offered.** The coordinator may
reuse the two existing strict sorted-representative refutations without any
new budget or binary depth, but must not count them against the 50-job new
cover. Any further target work would have to address exact full-parent cover
jobs and information beyond the checked projection; that is not justified
here as a 3-second joint-support experiment.

## Reproduction and files

From member directory `.ultramath/smwydhgx1/m2/`:

```sh
./REPRODUCE.sh
```

This safely extracts only under `bundle/`, verifies all bundle hashes and the
external/bundled ledger identity, builds the supplied checker/relabel tools
and offline Python environment, and runs `audit_target.py`. It launches no
K58 SAT search and uses no warning-suppressing checker invocation. The full
machine-readable census, cubes, hashes, scope fields, commands and negative
control are in `target/receipt.json`; exact CNFs/RUPs and checker logs are in
`target/`.

Primary files:

* `REPORT.md` — this verdict;
* `audit_target.py` — artifact-only regeneration and strict checking;
* `extract_bundle.py`, `REPRODUCE.sh`, `INPUT_SHA256`, `checksums.txt`;
* `target/receipt.json` and `target/*.strict.log`;
* `target/sorted-00220-01201.{cnf,rup}` and
  `target/sorted-00210-01201.{cnf,rup}`.

No commits, shared edits, nested swarm, or new K58 searches were made.
