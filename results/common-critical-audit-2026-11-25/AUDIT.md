# Independent audit: two colours cannot both have minimum degree 15

Date: 2026-11-25.

## Verdict

**Accepted as a verified finite computational proof.** The complete advertised
certificate was replayed: two catalogue refutations and 247 slot + 247 word
refutations, 496/496 in total. The mathematical reductions, catalogue normalisation,
embedding implications and exact orbit cover were checked as well; this is not an
inference from solver exit codes or a bounded search.

For any nonempty finite complete graph with a triangle-free four-colouring, for
any two colours `a,b` there is therefore a vertex with `d_a(x) <= 14` or
`d_b(x) <= 14`. Equivalently, **at most one colour can be critical at every
vertex**, where critical means colour degree at least 15.

This is not merely the earlier n025 result. It eliminates common-two-critical
configurations directly on physical colourings, without invoking a row CNF or its
semantic bridge. It does not prove the full upper bound, close any unrestricted
frozen row, or eliminate the strict/mixed/balanced nonreciprocal alternatives.

## What was replayed

Sources:
- `attachments/let-s-try-and-rbdv/K58_common_critical_color_certificate.zip`,
  SHA-256 `9bd2f2ee9f3815746fe0a98a747c10cb1c507f8e4fb7983e23e933546cde686a`;
- `attachments/let-s-try-and-rbdv/K58_common_critical_color_proof.md`,
  SHA-256 `3e9ec39e1dbf39358a6d636a60215912ebfb4186bccb641273d986ce749f943b`;
- `attachments/let-s-try-and-rbdv/K58_pentagon_wall_solver.zip`,
  SHA-256 `ac95cc8023f79ebba411f0cccf29ab03b5d1619ada3ed1f37d9678d307ebf354`.

Extraction is in `.scratch/common-critical-audit/`. Every entry in both packages'
`SHA256SUMS` passed.

The complete common-critical replay was run with two workers and a project-local
`TMPDIR`. Output (`full-replay.log`):

```json
{"checked": {"catalog": 2, "slots": 247, "words": 247}, "orbits": 247, "placements": 4356, "total": 496}
```

Wall time: **156.76 s**. The archive contains all 496 distinct CNF hashes and all
496 distinct compressed DRAT hashes (6,501,939 bytes of DRAT after decompression),
so no external proof archive was needed. The included checker returned success with
`s VERIFIED` on every rebuilt input.

## Why the finite certificate has the right semantics

### 15/16-point catalogues

A triangle-free three-coloured clique of size 15 or 16 has a vertex with five
neighbours in one colour (at most five by `R(3,3)=6`). Those five neighbours form
a two-coloured pentagon. The verifier checks proper colourings, prescribed rim and
diagonal colours, and sorted columns for all 66 `K15` and six `K16` entries. The
blocked CNFs' DRAT refutations establish completeness after this normalisation.
Deleting each possible unnamed vertex of every `K16` entry gives exactly the 66
`K15` entries, proving the required extension property.

The sorting auxiliaries are one-way prefix-equality indicators: when preceding
coordinates are equal they force nondecreasing colours. They do not force a false
converse, so every physically colour-sorted assignment admits an auxiliary extension.
There is no hidden symmetry restriction.

### The 25-vertex construction

If both colours were critical everywhere, choose 15 `a`-neighbours of `r` to form
`L`. Extend its three-coloured `K15` to a `K16`, whose colour degrees are all five.
Deleting the extra vertex gives ten vertices of `L` with five internal `b`-neighbours.
Choose such a `y`, then choose 15 ambient `b`-neighbours of `y`, including those five,
to form `R`. The hypotheses of the 25-vertex obstruction follow exactly.

The two arms use common vertices 20--24 and disjoint ten-point tails. `L` omits `a`,
`R` omits `b`; all 66^2 = 4,356 catalogue pairs are covered by 247 orbits under the
common dihedral action and arm exchange. `tables.orbits()` recomputes each orbit and
checks the disjoint total count, not just a representative hash.

For a genuine critical neighbourhood, the actual embedding into a 16-point template
satisfies both encoders:
- slots retain distinct template positions and their prescribed pair colours;
- words preserve the vectors into the four/five anchors and allow all pair colours
  obtainable from distinct compatible positions;
- when four anchors give repeated words, distinct compatible positions remain allowed.

Both encoders are thus necessary-condition encodings in the right direction: an
ambient colouring extends to the CNF by choosing its real embeddings. A refutation
of either necessary condition excludes the ambient colouring. The additional
five-anchor cases are optional relaxations; the remaining 17 orbits also use the
four-anchor conditions, as the manifest's 230/17 split records.

## Independent consequence checks

### Reciprocal colourings

Every colour degree on `K58` is between 9 and 16. The union of colour-`c`
neighbourhoods of two vertices in different components of the colour-`c` graph is an
independent set of at least 18 vertices, contradicting the bound 16 obtained from
`R(3,3,3)=17`. Every colour graph is connected. Under edgewise ticket reciprocity,
criticality for a colour is therefore constant on all 58 vertices. Pigeonholing
`57 > 4*14` supplies some critical colour at every vertex; the new theorem permits
only one common critical colour.

Thus a reciprocal colouring's root has exactly one critical colour, with profile
`(15,14,14,14)` for critical degree 15 or `(16,14,14,13)` for critical degree 16.
After the excluded profile, **only `(16,14,14,13)` remains eligible for reciprocity,
not proved realizable**. This supersedes the practical need for reciprocal C&C on the
other wall profiles. The earlier n025 closure is the special common-pair case.

### The current wall labels (not the whole cover)

An independent scan of `.scratch/k58/case-ledger.jsonl.gz` found exactly the same
11,204 IDs as the included wall file, across the six allowed wall profiles. It also
reproduced:
- 11,116 rows with at least two critical root colours;
- 70 rows, all in `(16,14,14,13)`, with one critical root colour and a different
  critical colour at the mark;
- 18 rows, also `(16,14,14,13)`, with that sole critical colour at both labels.

The first 11,186 rows force at least 15 one-way tickets. For the 11,116 with at least
two critical colours at the root, the reciprocal alternative is directly impossible.
The last 18 permit reciprocity at the level of root labels only; no existence is
asserted. These counts describe the current raw wall, not all 113,179 frozen-cover
rows and not the folded OPEN total.

### 15/30-ticket bounds

The additional counting arguments hold under the stated hypotheses:

1. If a colour has at most two low-degree vertices, the catalogue ensures each of
   those vertices has at most four relevant `b`-neighbours among the ten internal
   degree-five vertices. A suitable `y` then has no `b`-edge into the low set, and
   selecting its neighbours recreates the 25-vertex obstruction. The incidence count
   gives
   `16|X_b| >= |H_a| + #{r : d_a(r) = 16}`, hence at least four low vertices in every
   other colour on `K58`.
2. A mixed colour cut has size between 9 and 14 when the low side has one vertex and
   at least 15 otherwise. The untouched-high/low argument uses an untouched high edge
   `uv`, an untouched low vertex `w`, and disjoint pairs `N_c(u),N_c(w)` and
   `N_c(v),N_c(w)`. Each pair has total degree at least 24 and needs at least eight
   joining edges or would yield an independent set larger than 16. Adjacency of `u,v`
   in colour `c` makes `N_c(u)` and `N_c(v)` disjoint, producing 16 crossing edges.
3. Consequently any `K58` colouring has zero unreciprocated tickets or at least 15.
   Two colours critical somewhere force the latter case. If every vertex has equal
   total incoming and outgoing tickets, at least one mixed colour with at least two
   low vertices supplies 15 outward tickets and vertexwise balance forces at least 15
   further inward tickets, giving at least 30 one-way edges.

This is a structural constraint on the remaining branches, not a refutation of them.
The auxiliary 15-ticket CNF was inspected as well: prefix-count indicators are
two-sided and exact; selected edges must have endpoint criticalities in different
states in their actual colour; every physical completion with 15 such edges admits an
auxiliary extension. No perfect-balance assumption is used.

### The old template-classification gap is bypassed

Every entry of the new 66/6 catalogues was tested against the existing `U` and `T`
templates using exact vertex-and-colour backtracking. Results
(`catalogue-isomorphism-check.json`):

| order | entries | U | T | other |
|---:|---:|---:|---:|---:|
| 15 | 66 | 11 | 55 | 0 |
| 16 | 6 | 1 | 5 | 0 |

Together with the certified catalogue completeness and the pentagon normalisation,
this independently establishes `Classified 15` and `Classified 16`. It bypasses m3's
missing independence-filter implementation and deleted proofs; it does not retroactively
make that earlier submission self-certifying.

## Scope of the auxiliary wall solver and remaining work

The package's row-label counts and pilot rebuilds pass (`verify.py --scope-only`,
`check_pilots.py`, and `ticket_cut.py --audit`). Its additional four ordinary word
exclusions, 20-degree capacity bound, and native strengthenings do not give unrestricted
row closures. The separate 83 DRAT packages named in its README were not attached, so
those extra claims were **not** independently certified here. No UNKNOWN run was treated
as a verdict.

The missing earlier four-row DRAT shards are no longer needed merely to reject
reciprocity on rows whose roots have two critical colours—the global theorem does that.
They remain necessary for the older unrestricted `d_0(q) <= 14` and associated word
claims.

No Lean formalisation of the new finite obstruction was written in this audit. The
acceptance is of the explicit catalogue/DRAT computational certificate and its checked
mathematical composition, not a claim of kernel-only proof.

## Reproduction

```sh
cd .scratch/common-critical-audit/K58_common_critical_color_certificate
export TMPDIR=/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/common-critical-audit/tmp
python3 verify.py --jobs 2
```
