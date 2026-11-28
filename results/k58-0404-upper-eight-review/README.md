# Independent review: `K58_0404_upper_eight_certificates.zip`

## Outcome

**The supplied \(H \le 8\) certificate is independently verified for its stated scope.**
It is a real strengthening of one original first-tier parent, not a whole-row proof.

* Archive SHA-256: `56f5b85641a305aa5aea9f86b4abd362a388ce492abcf7dfc1dab53cce5b1d1d`.
* Frozen row: `0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296`.
* Original parent SHA: `a062b827b34fa73ccd610b2a932e007e48ba217d85c7dea00f9a1a73dbdb62fe`.
* Strengthened CNF SHA: `87bc5a174c86dc99abe963ce9c71e5fe5492a78368558fb17a356b06d741894a`.
* Whole row: **OPEN**. The archive itself also reports its strengthened-parent search as OPEN.

## What the bound actually says

Let `F` be the original first-tier parent, 19,425 variables / 184,117 clauses, aligned with the pinned row and regenerated independently. The certificate's statistic is the number of colour-0 edges from 0-indexed vertex 17 to 0-indexed sites 1..16.

The parent pins the spokes at sites 1, 4, 6, 8 and 15 to colour 1. The eleven remaining opportunities are sites `2,3,5,7,9,10,11,12,13,14,16`. Eleven first-miss cases plus the all-hit case cover exactly 67 masks with at least nine colour-0 hits among these eleven sites.

All twelve leaf queries and proofs independently reproduce their recorded SHA-256 values. Both independently generated LRAT and normalized DRAT checks passed all twelve. **Nine Kissat proofs use RAT; the other three (the first two large CaDiCaL cases and full-high11) had zero RAT in their checked cores.** RAT must not be mistaken for an error, and `-U` is not valid for those nine cases. Raw `-W` also stops on deletion handling; accepted normalized checks use `-i -W` with RAT enabled and preserve every addition, exactly one empty-clause addition included.

The 12 leaf UNSATs therefore imply `H <= 8` *for this parent.* A separate verified local CSP has no `H = 0` word, and the small minimum-word RUP derivation pins the unique `H = 1` word, with its lone colour-0 hit at site 16. The bundled conditional endpoint query and proof also verify.

Each nine-subset of the eleven opportunities is consequently forbidden. The resulting **55 nine-literal clauses** append to the original parent without changing variables or renumbering clauses. The rebuilt strengthened CNF is **byte-identical** to the supplied `strengthened.cnf`. The clause block alone only bounds the eleven variables; the five pinned spokes are load-bearing for the literal `H <= 8` statement.

## Independent checks

* `python3 replay.py <solver> --lrat` completed all 12 DRAT and LRAT checks, the lower endpoint and both local model checks.
* The parent and strengthened CNF were regenerated independently, with the expected hashes.
* Strict forward/binary processing stopped on the raw deletion convention as expected; it did not yield a proof verdict. Replaying deletion-stripped files with RAT enabled gave **12/12 exit 0, exact `s VERIFIED`, zero warnings and complete normalized-proof reads**.
* Every mask of the **2,048** boolean assignments was checked: every `H >= 9` mask appears in exactly one leaf, and no other mask appears in any leaf.
* The independent local-word census reproduced **5,224** words. The bound removes **203**, leaving **5,021**. This is **3.885% of that local relaxation**, not 3.885% of the open global problem.
* A different genuine first-tier parent rejected the proof (`s NOT VERIFIED`). A truncated binary stream cut at a command boundary was read completely but rejected (`c ERROR: no conflict`). These controls do not invalidate the passing originals.

The two included 38- and 40-vertex models are induced-subgraph witnesses only. They are not models of the 58-vertex row.

## Essential scope warnings

1. **Two unrelated statistics are called H here.** This certificate's `H` counts colour-0 spokes from a particular mark to 16 sites. Other project records count high/contact sites, or use the root ticket statistic `H(r)`. The row's separately reported `H >= 11` figures are different quantities and **do not contradict this certificate's `H <= 8`**. They must never be composed as if they were the same statistic.
2. **Do not splice the 55 clauses across row names, renumberings or formulas.** They are physical-literal clauses, but their validity is established for this parent. A formula that adds the same parent constraints also inherits them; a different parent needs a fresh derivation.
3. **No completion is hidden here.** The local-word census is a relaxation. The four previously open child cubes also remain open: propagation adds no spoke units under this clause block. The supplied strengthened-parent search reached a conflict cap and stayed OPEN. No timeout is SAT or UNSAT evidence.
4. **Process hardening, not a proof gap:** the replay has no timeout/memory cap for the checkers and normally uses temporary disk for decompression. Use an explicit scratch temp directory and keep logs. Do not rely on zip CRC, manufacturer receipts or a mere `VERIFIED` substring as semantic validation.

## Recommended use

Keep `strengthened.cnf` as an optional, hash-pinned constraint set **only for this same parent and its added cubes**. Do not update the production ledger or expect it to close `0404c3a2…`. The genuine gain is a small, certified local narrowing plus a reusable constraint block for subsequent work on this specific row; it is not a new Ramsey result or an existing-row speedup.

See [verification-summary.json](verification-summary.json) for compact machine-readable identities and controls. Full working inputs and logs are under `.scratch/k58-0404-upper-eight/`; large proof payloads and unfinished searches were not copied into this result directory.
