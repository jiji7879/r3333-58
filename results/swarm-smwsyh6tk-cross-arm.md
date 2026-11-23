# Swarm `smwsyh6tk` — the cross-arm layer, decided. Final board.

Ended **solved**, 8 of 8 directions accepted (m1, m3 and m5 after judging; m2, m4, m6, m7, m8
accepted earlier). 2026-11-23. **No cover row changed state; `R_4(3) ∈ [51,62]`.**

## What this swarm settled

The two-arm package `K58_two_arm_compatibility` claims: a type-16 arm forces a singleton in every
type-36 sibling. Its proof archive (`K58_two_arm_proofs.zip`, SHA `ed94e74a…`) was **never
supplied**, so nothing in it could be replayed. The swarm rebuilt the whole chain and decided it
three independent ways.

| dir | member | result |
|---|---|---|
| d6 | m1 | rectangle layer rebuilt from the definition; **2,541-core irredundant certificate** (package: 4,869) for all 192; **all 2,733 proofs replayed by the judge, bit-identical** |
| d4 | m3 | pair census (4,236 placements / 219 types / 21 / 3, three implementations agree); **288 shipped cases re-decided, 240 UNSAT with DRAT, 48 SAT with witnesses**, two independent encodings |
| d1 | m5 | third decision of the 192; **UNSAT also under the union of both template rootings**, so the convention does not matter; **extends the test to the whole three-placement family: 1,152 instances, all UNSAT** |
| d7 | m7 | the theorem's **premises decided**: template premise kernel-checked unconditionally, last step of the six-set classification kernel-checked, census reproduced |
| d2 | m6 | the four shipped order-30 colourings all excluded, **but only one of the package's seven certificates carries its board**: the fourth board survives every one-vertex test and needs a two-vertex certificate, which m6 supplies. Also: type 16 admits no board of the corner's design at all (28 DRAT) |
| d5 | m8 | **the cube filter never fires on the real queue** and its showcase is vacuous: the rule needs a complete 91-edge internal colouring, and no queue row fixes more than 13 |
| d9 | m2 | omission layer re-decided on **all 4,724 joins** (4,800 instances, DRAT replayed), plus the all-full K27 corner in all 30 (arm, sender) forms |
| d8 | m4 | arm layer kernel-checked in Lean (alternating count vectors, the factor 16, site systems, pairwise inequivalence of the four placements) |

## What the judge verified independently

- **m1**: rebuilt the entire archive from `cert_min.json` and `cert.json` alone in a fresh manifest —
  **2,733 of 2,733** CNF *and* proof SHA-256 identical, every one `s VERIFIED`. Note that m1's own
  `replay.py` skips tags already present, so a naive re-run verifies nothing.
- **m3**: after one rejection for shipping only 32 of its 288 records, the ledger arrived complete;
  the judge had already re-run records 0 and 12 through m3's pipeline with identical hashes.
- **m5**: judge decompressed two retained certificates and ran `drat-trim` directly (VERIFIED,
  hashes matching), ran `make_sample.py` and got the CNF rebuilt with an identical proof hash, and
  confirmed from `res_bo*.json` that all 192 are UNSAT under the union of both rootings while the
  SAT controls stay SAT.
- Judge's own probes: three declared cores UNSAT in both encoders with singles and non-census pairs
  SAT; the MILP control feasible with no cores and infeasible with the certificate; irredundancy of
  18 sampled cores; the 453 two-entry core census recomputed.

## The two errors found in the package

1. **The seven missing-neighbour certificates are under-specified**: one of the four order-30
   boards survives every one-vertex test and needs a two-vertex certificate (m6, verified).
2. **The cube filter is inert**: it never fires on the real queue, and its showcase cube is
   vacuous (m8).

Neither affects the 192 cases; both belong in the errata record before anything is published.

## What is still open

- **Cross-arm depth**: the test decides a *pair* of arms. It says nothing about the third arm, and
  nothing at all about a full K₅₈ colouring.
- **Type-level pairs**: m3 prices the complete census at 1.15 G cases (~130 compute-years); the
  cheapest complete family (all 36 ordered pairs among the six three-placement types) is 20,736
  cases, ~21 h. Only type 16 against the six has been done (1,152 instances).
- **Type 16's other 17 placements** against type 36 are untouched (m3: 4,032 cases).
- Everything remains conditional on the template and six-set classifications, which m7 now decides
  in the kernel — so the chain's remaining input is the campaign's own cover, not the package.
