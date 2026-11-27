# K58 two-spoke clauses and the frontier of representative 0

All indices refer to the original 983,774-entry live revised-owner roster. Number vertices 0 through 57 and colors 0 through 3. Four consecutive DIMACS variables correspond to the four colors of each edge, in lexicographic order of its endpoints. Closures below exclude assignments of edge colors within the indicated owner.

## Two proof cores with 53 physical instances

On the first wall row, the established representative-0 clause is `-2721 -2766 0`. This forbids color 0 on (13,31) together with color 1 on (13,42). Of the other 46 owners of the row, separate certified searches proved the same two assumptions contradictory on 36, 38 and 40. The other 43 were unresolved by those searches. The proof for 38 has the short geometric explanation below.

The two proofs originating at 36 and 40 transfer to 26 and 27 signed representatives respectively. The 53 include the two source owners and span 27 distinct wall rows. The programs relabel physical vertices and colors, shift owner auxiliary variables and replay the transported proof on the recipient's signed CNF plus only the two proposed colors. A transfer certifies the disjunction of their negations. Fixing one color forces the other spoke to avoid its listed color.

`proof-transfers.tsv` lists all 53 directly insertable clauses, their recipients and their hashes. Each row belongs only to the signed parent shown in that row. `transfers.json` contains replay receipts. `hard-maps-36.json` and `hard-maps-40.json` describe the substitutions. The search used sufficient conditions for a match, so further embeddings can exist.

For a new candidate, supply its vertex and color map in the format of an entry in one of the hard-maps files. The last integer argument before the checker is the DIMACS variable count of the recipient ordinary wall row, before appending its revised-owner encoding. The script writes a proof and prints the clause after successful validation.

    python3 transport.py 36 candidate-map.json signed-parent.cnf.gz 18387 /tmp/k58-spoke-rup candidate.rup

The 53 tested pairs all escaped unit propagation with the inherited arm-domain rules. On four matched three-second controls with Wave A's six extra rule families and both proposed colors fixed, CaDiCaL returned UNSAT on representatives 40, 29018 and 29022. Representative 36 timed out. `matched-controls.json` records these outcomes. The timing controls are empirical and the transported proof establishes each exclusion independently.

## A four-color triangle argument

Take an ordered nominated arm. Denote pentagon sites 0 and 4 by u and a, and the arm vertex at zero-based site n−3 by v. The pentagon fixes ua to color α. On the six revised owners in `canonical/rules.json`, av is forced to color β, local palette color 0. Each canonical forced edge has a checked RUP proof. Suppose there is a two-edge path from an outside vertex x to a in each of the other two colors, δ and γ. If xu had color α and xv had color β, every color of xa would complete a monochromatic triangle.

On representative 38, x=13, u=31, a=34 and v=42. The colors 0, 1, 2 and 3 of (13,34) are excluded through vertices 31, 42, 15 and 10 respectively when the spoke pair is fixed.

`clauses.tsv.gz` lists 9,288 distinct representative/clause pairs on 6,617 representatives and 6,489 rows. Each entry gives the physical vertices, witnesses, palette and two negative DIMACS literals. Replay checks every row placement against the frozen source geometry and verifies full physical proofs on eight examples covering all six classes. The previous arm-domain records already forbid local colors 1 and 2 on av for all six owners. The root arm color excludes the fourth physical color. Consequently adding the binary clause makes this existing propagation explicit. The catalog search required x and both intermediate vertices to lie in the same other fixed critical arm. It also required xu, xv and xa to lack a positive row pin.

## Representative 0

The signed owner has key `00000,01022` on the first row. Its physical pivot is (31,42). Previous signed proofs exclude colors 1 and 2. The covers below use no spoke assumptions.

| Pivot color | Arm colorings in exhaustive cover | Certified exclusions | Open arm colorings |
|---|---:|---:|---:|
| 0 | 1,417 | 0 | 1,417 |
| 3 | 345 | 20 | 325 |

The 91 digits of each arm coloring give the physical colors of the lexicographically ordered internal edges on vertices 31 through 44. Replay checks its triangle constraints, nominated pentagon, owner words and sorted tail. For each pivot, a RUP refutation on the signed parent with all listed arm colorings blocked proves coverage. A surviving coloring can still fail to extend to K58. The global parent and both surviving pivot colors were unresolved in separate three-second strengthened calls.

`case0/arm-clauses.cnf` provides 20 clauses to append to the signed parent of representative 0. Eleven exclude cubes with 82 pins and were discovered using triangle constraints on two arms and four other marked vertices. Nine exclude cubes with 13–16 pins and were discovered using the earlier two-spoke clause. All 20 final proofs replay on the exact signed parent plus their listed arm pins alone. The package discharges the earlier spoke lemma inside the corresponding physical proofs. The count of 20 follows by matching each cube against every coloring in both covers. All 36 four-edge signatures under pivot 3 still have a surviving arm coloring.

`case0/frontier.json` stores the surviving zero-based arm indices and the proof matches for excluded indices. `case0/arm-0.json` and `case0/arm-3.json` resolve every index to a full arm assignment. `case0/exclusions.json` indexes the physical proofs. The production ledger is separate from this targeted experiment.

## Offline verification

Use Python 3.10 or later, with assertions enabled, and a C compiler. The verifier uses the Python standard library. It rebuilds the hard-transfer proof streams from their two donor cores, reconstructs the signed CNFs from the stored byte prefixes and suffixes, checks the exported clauses, and runs drat-trim in RUP-only mode. To limit parallel verification, set K58_WORKERS to a positive integer.

    sha256sum -c SHA256SUMS
    cc -O2 tools/drat-trim.c -o /tmp/k58-spoke-rup
    python3 replay.py /tmp/k58-spoke-rup

Every physical receipt binds a SHA-256 digest of its signed formula with assumptions to a proof digest. Solver time limits applied to discovery and controls. Proof verification runs to completion.
