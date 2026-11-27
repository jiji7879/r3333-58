# K58 case 0 — joint choices and certified subcase closures

Twelve assignments that have explicit 30-vertex colorings are impossible on the full signed K58 representative. They lie under the condition that edge (31,13) has physical color 0 and (42,13) has color 1. The pivot is (31,42). Both whole pivot branches remain open.

## The four-edge test

Read a word from left to right as the physical colors of (39,44), (40,41), (40,42), (40,44). The local projection retains root 0, second-arm vertices 1–15, nominated-arm vertices 31–44, and the owner clauses whose variables it retains. Every positive example satisfies the signed local clauses and maximum monochromatic degree 16 on those 30 vertices. To certify completeness, the verifier blocks every witnessed word and replays an unsatisfiability proof on the original full physical child under the specified conditions.

| Assumptions on the two spokes at vertex 13 | Words at pivot 0 | Words at pivot 3 | Words occurring at both |
|---|---:|---:|---:|
| Neither | 57 | 36 | 29 |
| Only (31,13) = 0 | 57 | 36 | 29 |
| Only (42,13) = 1 | 57 | 36 | 29 |
| Both | 8 | 28 | 0 |

Each single assumption preserves the entire corresponding set of words. Both together make the two sets disjoint. A separate pair of checked local colorings agrees on every edge except the pivot when the two-spoke condition is omitted.

| Pivot | Locally witnessed words under both assumptions | Full K58 proof | Open after three seconds per word |
|---|---:|---:|---:|
| 0 | 8 | 1 | 7 |
| 3 | 28 | 11 | 17 |

Pivot 0 closed on word 1113. The open words are 0001, 0301, 0311, 1001, 1310, 3130, 3310. Pivot 3 closed on 0133, 1013, 1133, 1333, 3010, 3031, 3101, 3103, 3111, 3133, 3301. Each word closure also replays on the unsplit signed parent with both spoke assumptions. The full remaining disjunction is in conditional-frontier.json. Its scope is the two-spoke condition. The rest of representative 0 remains open. No K58 model was found.

## Choices at two distinct second-arm vertices

On the row containing indices 0–46, check the three simultaneous assumptions (1,42) = 3, (4,31) = 0, (4,42) = 1. For 11 representatives they force (31,42) = 3, and each has a local coloring exhibiting the assumptions. In three others (14, 31 and 36), the assumptions themselves are impossible. Each of the remaining 33 admits a checked local coloring with the assumptions and a different color on (31,42).

For indices 3, 5, 7, 19, 23 and 32 the shorter assumptions (1,42) = 3 and (4,42) = 1 already force (31,42) = 3. Retaining either alone has a local counterexample in each case. The target is the same physical edge throughout. The checkpoint may use a different production pivot on another representative. On index 0, testing all 25 locally feasible assignments at sites 1 and 4 under pivot 0 and all 30 under pivot 3 on K58 left each open after three seconds. The exact per-branch disjunctions have independent proofs.

## Other reusable clauses

The original 26 signed exclusions gave 19 distinct clauses on representative 0. Four omit the pivot color. Resolving clauses from opposite branches and using the verified four-color cover gave 11 further joint exclusions beyond unit propagation and ten that already follow by propagation.

One ordinary-row rule is independent of the owner. If (31,z), (31,7) and (31,11) are all color 3, the ordered colors on (z,7) and (z,11) cannot be (0,1) or (1,0). Both orientations replay directly on three ordinary rows for every z in {32,34,36,37,38,39,40,41,42,43,44}. These rows contain 141 original representatives. Their half-open index ranges are [0,47), [757026,757073), and [894484,894531). These conditional exclusions retain all representative indices. No production sweep or production ledger update was performed.

## Independent verification

Extract the ZIP, enter its directory, and run the following with Python 3, a C compiler, and assertions enabled.

    sha256sum -c SHA256SUMS
    cc -O2 tools/drat-trim.c -o /tmp/k58-two-site-drat-trim
    python3 verify.py /tmp/k58-two-site-drat-trim

The verifier uses ordinary Python and drat-trim in RUP-only mode. It reconstructs the 47 parent formulas and verifies their hashes against archived production events. The degree cap is checked on the local models, and every full subcase closure replays directly on its original formula. OPEN records describe bounded searches. The discovery scripts additionally require the restored campaign and preceding pilot directories.
