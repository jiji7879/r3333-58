# Case 0 — the 24 remaining patterns

The signed representative has index 0. The condition throughout is color 0 on (31,13) and color 1 on (42,13). The original pivot is (31,42). All colors use the physical labels 0–3.

| Pivot color | Input patterns | Newly closed | Remaining | Input arm colorings | Remaining arm colorings |
|---|---:|---:|---:|---:|---:|
| 0 | 7 | 7 | 0 | 69 | 0 |
| 3 | 17 | 17 | 0 | 148 | 0 |

## Consequences

Every arm alternative closes. Consequently (31,13) = 0 and (42,13) = 1 cannot both hold on the signed case-0 representative. The reusable binary clause on that parent is `-2721 -2766 0`. The two physical pivot branches 0 and 3 close under the two spoke assumptions. The independent verifier checks this binary clause by exhausting the certified alternatives. The open-leaves table has no data rows.

## Verification

The earlier signed checkpoint eliminates physical pivot colors 1 and 2. Under the condition, two checked disjunctions cover the 7 input words at pivot 0 and 17 input words at pivot 3. The package includes those original proofs and the earlier unsplit 24-word certificate.

For each input word, blocking every listed 14-vertex coloring gives an independently checked contradiction on its original K58 query. This proves the list exhaustive. A refutation either closes the whole word directly or closes an arm coloring. At a further split the verifier visits all four colors of the chosen edge. Before using a group of forced literals, it refutes the disjunction that at least one of them fails. Every terminal refutation uses a RUP proof on the full signed formula with the recorded assumptions. The overall implication is certified by this finite case analysis.

The search used three seconds per solver call. Proof validation runs to completion. The 24-pattern analysis is local to this representative and condition. Both unconditional pivot branches retain their previous production status.

From the extracted directory, run the following commands with Python 3 and a C compiler. Keep Python assertions enabled.

    sha256sum -c SHA256SUMS
    cc -O2 tools/drat-trim.c -o /tmp/k58-24-rup
    python3 replay.py /tmp/k58-24-rup

frontier.json supplies the machine-readable cover, all 217 arm colorings, the proof hashes and the remaining leaves. Physical variable 1 is color 0 on edge (0,1). The four consecutive variables for each unordered edge use colors 0,1,2,3, and all edges on vertices 0–57 follow lexicographic order.
