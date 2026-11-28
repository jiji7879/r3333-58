# Sender-only `kmtotalizer` replacement on the retained K58 parent: implementation and bounded A/B

Member `m7`, swarm `smx06hpp8`, direction 5. Repository HEAD `e43e78e`, read-only use of
`tools/color-resolved-wallcc/{problem.py,frozen/*}`, pinned interpreter
`.scratch/k58/.venv/bin/python` (python-sat 1.9.dev22). All new files are in
`.ultramath/smx06hpp8/m7/`; generated CNFs live in the ignored `.scratch/m7/` and are
reproducible in under a second from `kmt_wall.py`.

**Result, in one line:** the sender-only `kmtotalizer` parent is emitted *and verified*
to be exactly 13,364 variables / 176,660 clauses with every non-sender clause, every
support selector, both final Sinz counters, the host body, the 438 frozen units and the
cube preserved under an explicit allocation map; the pre-registered parent+cube A/B then
measures KMT **1.258x search CPU at 100,000 conflicts and 1.234x at 1,000,000** (geometric
means of seeds 0/1) with **9.5% / 14.5% lower peak RSS**, all eight calls **OPEN**. The
throughput gate fails at both caps; nothing about `ChainReady`, physical colourings or a
Ramsey bound changes.

## Exact objects

| object | SHA-256 | size |
|---|---|---|
| stock parent (regenerated) | `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae` | 19,533 vars / 184,335 clauses / 3,493,016 B |
| stock parent + cube `[-1413,1014]` | `8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8` | 184,337 clauses |
| **KMT parent** | `6e71fc07c907f7947a35565d04c3459cf90ac05dc5c4789ffe1cd27f078b6441` | **13,364 vars / 176,660 clauses** / 3,339,511 B |
| **KMT parent + cube** | `fdb46b2f8cddc74053809a8106801a327af32cc0ef191247b8980a0200779afd` | 176,662 clauses |

The rebuilt stock bytes equal the retained parent hash, and appending the cube as two
unit clauses reproduces the recorded parent+cube hash `8791f627...` exactly — an
independent confirmation that this is the coordinator's cube convention. Deltas:
**-6,169 variables, -7,675 clauses, -12,385 counter literal occurrences, -153,505 bytes**,
i.e. the memo's prediction holds exactly and is now an emitted artifact rather than an
estimate.

What was replaced: exactly the 31 guarded sender counters, 4 of shape
`AtLeast(30,10)` and 27 of shape `AtLeast(41,14)`, with the production naive guard
(`-g` prepended to every emitted clause). Sinz totals 11,006 aux / 21,621 clauses become
KMT 4,837 aux / 13,946 clauses. Not replaced: the two final counters
`AtLeast(15,6)` on 15 arm-sender guards and `AtLeast(31,6)` on 31 critical-sender
guards, which remain Sinz (`EncType.seqcounter`) in both parents.

## Preservation receipt (`stage1.json`)

`kmt_wall.py` is a private copy of `frozen/dense.py::marked_threshold` with one
`sender_encoding` knob and a logical-block transcript. In stock mode it reproduces the
production clause list **elementwise** (`production_copy_faithful: true`), and the
whole-file bytes match the retained parent.

Every emitted literal is labelled by the logical object it belongs to: physical edge
(`1..6612`), sender guard ordinal, or an offset inside a support/final auxiliary block.
Comparing the two transcripts:

| block class | count | result |
|---|---:|---|
| host body clauses | 134,995 | byte-identical prefix in both files |
| frozen signed units | 438 | identical clause list |
| sender gadgets | 31 | candidate literal lists and bounds identical; encodings differ by design |
| support blocks (P4/C5 selectors) | 15 | **clause-for-clause identical** under the map |
| final counters | 2 | **clause-for-clause identical** under the map |
| positional mismatches over all 17 non-sender blocks | 27,281 clauses | **0** |

Explicit allocation map (`stage1.json → allocation`): 31 old→new guard pairs (the first
sender's guard keeps id 6613; the last moves 18,839 → 12,885), 15 support blocks with
base shifts `-3159, -3374, ..., -6169` (step -215, matching the 215-auxiliary saving of
one `AtLeast(41,14)`), and the two final blocks shifted by `-6169`. Support selectors
renumber only: 1,680 selector ids in 15 blocks of 112 (96 P4 + 16 C5 palette patterns),
each block's internal offset preserved exactly. 1,227 physical literals participate and
are untouched (`physical_literals <= 6612`).

## Projected guard/support semantics (`stage2.json`, `stage2b.json`)

Per actual gadget, both encodings, 39,744 solver calls, all controls passing:

| check | stock (Sinz) | KMT |
|---|---|---|
| `F & g & AtMost(k-1)` UNSAT (enforcement, exact) | 31/31 | 31/31 |
| witness input set of size exactly k SAT | 3,294/3,294 | 3,294/3,294 |
| `F & -g & all inputs false` SAT (guard-false freedom) | 31/31 | 31/31 |
| unguarded clause set rejects a violation (negative control) | 31/31 | 31/31 |
| gadget built at bound k+1 rejects an exactly-k assignment | 31/31 | 31/31 |
| gadget built at bound k-1 accepts an exactly-(k-1) assignment | 31/31 | 31/31 |
| true gadget rejects exactly-(k-1) | 31/31 | 31/31 |

The witness family per gadget is deliberately positional, not random: all `k`-windows
(`n-k+1`), plus "first `k-1` plus each index", plus "last `k-1` plus each index", i.e.
109 sets at `n=41` and 82 at `n=30`. Exhaustive equivalence of both guarded encodings
over **every** guard/input assignment for `n = 1..9`, every `k`, is 32,776 checks with
**0 mismatches**; the `AtMost(k-1)` test encoder has its own accept/reject control at
each of the four actual shapes so the enforcement test cannot pass by over-restriction.

Finally, root-level BCP on parent+cube (438 units and the 2 cube literals already in the
files) derives **1,865 literals in both formulas, with identical logical sets after the
map and zero disagreements** (`stage2b.json`).

**What this licenses and what it does not.** Enforcement is exact at the real shapes.
Extension (every satisfying input set must extend) is exhaustive only up to `n = 9` and
otherwise positional-witness tested, so the honest statement is: the projected relation
holds on everything tested, and the only gap is a non-exhaustive extension test at
`n = 30` and `n = 41`. A satisfying model of either parent projects to a model of the
other at the level of physical + guard + support + final objects; no gadget auxiliary is
claimed to be canonical. This says nothing about physical colourings, candidate
criticality, `ChainReady`, or any bound. If a future run ever returns SAT or UNSAT on the
KMT parent, the model must be extended back and re-checked clause by clause against the
stock parent, and a proof must be replayed against `6e71fc07...` / `fdb46b2f...` — not
against the stock bytes.

## Matched benchmark (`bench/`, `kmt_bench.py`)

Fresh CaDiCaL 1.9.5 through pinned python-sat 1.9.dev22, one subprocess per call, no
proof logging, `conf_budget(100000)`, cube appended as units, seeds 0 and 1, alternating
arm order. All four calls **OPEN** at the cap (100,000-100,002 conflicts): *not* UNSAT.

| seed | order | arm | search CPU s | decisions | propagations | restarts | peak RSS KiB |
|---:|---|---|---:|---:|---:|---:|---:|
| 0 | 1st | stock | 3.7333 | 529,694 | 32,489,100 | 7,141 | 96,592 |
| 0 | 2nd | KMT | 4.2593 | 363,429 | 43,472,331 | 7,577 | 87,592 |
| 1 | 1st | KMT | 4.3452 | 400,550 | 44,109,768 | 8,670 | 86,508 |
| 1 | 2nd | stock | 3.1347 | 777,586 | 21,181,699 | 7,779 | 96,748 |

Parse CPU 0.026-0.030 s and bootstrap CPU 0.054-0.059 s per call, both arms; driver wall
16.8 s for the four calls; total solver CPU in this experiment about 32 s including the
determinism replicate.

* CPU ratio KMT/stock: **1.14089** (seed 0) and **1.38616** (seed 1), geometric mean
  **1.25756**.
* Peak RSS ratio: **0.9068** and **0.8941** — a real 9.5% geometric-mean reduction.
* Decisions fall (529,694→363,429 and 777,586→400,550) but propagations rise
  (32.5M→43.5M and 21.2M→44.1M): the smaller counter buys less branching and pays more
  propagation per conflict. This is the same shape as the already-rejected
  conditional-Sinz measurement, in the opposite direction of the desired trade.
* Determinism: three independent runs of the four-call driver reproduced every search
  statistic exactly; only CPU moved (geometric means 1.2576, 1.2424, 1.2885). Re-running
  `reproduce.sh` reproduced `stage1.json` and `stage2b.json` byte-identically and
  `stage2.json` except for its wall-clock field.

Pre-registered gate: stop on a semantic-control failure, on a KMT call error, or on a
>0.90 geometric-mean CPU ratio without a memory benefit. The CPU gate fails at 100,000
conflicts by a wide margin. Because a 9.5% memory benefit exists, the memo's literal stop
rule does not fire, so the one stage it permits was run: the same matched pair at
1,000,000 conflicts/seed, which has to reach <=0.80 CPU ratio with no propagation or
memory regression.

| seed | arm | search CPU s | conflicts | decisions | propagations | restarts | peak RSS KiB |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | stock | 61.1720 | 1,000,000 | 2,318,963 | 381,196,308 | 33,143 | 116,516 |
| 0 | KMT | 63.8966 | 1,000,002 | 2,105,737 | 395,209,230 | 32,356 | 99,296 |
| 1 | KMT | 67.5537 | 1,000,003 | 2,124,252 | 396,050,662 | 32,618 | 108,776 |
| 1 | stock | 46.3078 | 1,000,000 | 4,314,184 | 261,551,338 | 36,281 | 126,716 |

All four are **OPEN** (not UNSAT). CPU ratios 1.04454 and 1.45880, geometric mean
**1.23441**; peak RSS ratios 0.852 and 0.858. The gap does not close with a longer cap,
the <=0.80 gate fails, so this direction stops here: no second wall row, no
literal-order or proximity follow-up, no MCF/global-cardinality rewrite, no package
installation. Cumulative solver CPU in this direction, all stages and replicas, is about
4.8 minutes.

## Status classification

* **Completed implementation:** private generator, stock byte-equality, KMT emission,
  allocation/identity maps, gadget and root-propagation controls — all checked.
* **Completed bounded measurement:** four capped parent+cube calls, all OPEN; negative
  throughput result with a measured memory side effect.
* **Capability-only:** none claimed for proofs; no DRAT/LRAT was produced here and no
  checker was invoked.
* **Still open (pre-existing, untouched):** physical candidate criticality,
  coded/automatic guard equalities, 112-support membership as a physical fact,
  `ChainReady`, the three-relaxation bridge, and the accepted interval
  `51 <= R_4(3) <= 62`. `OPEN` is not `UNSAT`; the <=60 preprint claim remains
  unverified.

## Files

| file | purpose |
|---|---|
| `kmt_wall.py` | instrumented generator (stock/KMT), cube appendix, labelling |
| `kmt_stage1.py` → `stage1.json` | regeneration, emission, block identity, allocation map |
| `kmt_semantics.py` → `stage2.json` | 39,744-call gadget control battery |
| `kmt_bcp.py` → `stage2b.json` | root-propagation agreement |
| `kmt_bench.py` → `bench/`, `.scratch/m7/bench-1m/` | A/B driver, per-call receipts, `analysis.json` |
| `reproduce.sh` | exact commands |
