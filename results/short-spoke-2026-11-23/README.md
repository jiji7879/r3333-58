# The short-spoke bundle: a 21-spoke bound on branch 62, from a 35-vertex board

Bundles: `K58_short_spoke_solver_and_notes.zip` (164.5 MiB) and `K58_short_spoke_DRAT.zip`
(97.3 MiB), unpacked at `.scratch/ss/`. Both supplied, so this one is **replayed, not regenerated**.

## Verified here

```
sha256sum --quiet -c SOLVER_SHA256SUMS          -> clean
.venv/bin/python tools/check_short_spokes.py --workers 4
  22 certificates VERIFIED
  Checked physical maps, integer coverage, solver clauses and all witness colorings.
  652553307655...  spoke floor 21
  8a40a4423925...  spoke floor 19
  ec075047186a...  spoke floor 19
  f4f7ef740f40...  spoke floor 19
```

64 seconds for the full check, 45 seconds for `--branch62-only` (which verifies the five certificates
that alone imply 21). The verifier checks witness colourings edge by edge, recomputes the row hashes,
checks the physical maps, enumerates integer spoke pairs, tests the integrated clauses on all 5,776
ordered count pairs per published cut, rebuilds every certified CNF by SHA-256 and passes each
decompressed trace to `drat-trim`.

## What it establishes

**A 35-vertex board proves a spoke floor on five frozen rows**, where the previous work had only the
two published rows:

| branch | row hash prefix | floor on a 35-vertex board | conflicts |
| ---: | --- | --- | ---: |
| 14 | `ec075047186a` | `U+V >= 19` | 330,222 |
| 59 | `8a40a4423925` | `U+V >= 19` | 375,446 |
| **62** | `652553307655` | **`U+V >= 21`** | 301,365 + chain |
| 282 | `f4f7ef740f40` | `U+V >= 19` | 899,264 |
| 286 | `dd05194bd9aa` | `U+V >= 19` on both `(14,5)` and `(5,14)` | 613,912 / 690,872 |

**Branch 62's 21 is the strongest bound anywhere in this campaign.** The chain: `(14,5)` with
`U+V <= 19` is UNSAT (301,365 conflicts) gives 20; then at total 20 the smaller count ranges over
`0..10` and each range is excluded — `U <= 7` (7,063 conflicts), `U <= 8, V <= 12` (141,418),
`(U,V) = (9,11)` (633,415), `U <= 10, V <= 10` (1,969,012). Since a full colouring must satisfy both
35-vertex projections, whose union is the 44-vertex `(14,14)` board, **the bound of 21 holds on that
44-vertex board too**.

**This answers the question the previous swarm left open.** m4 asked whether a 35-vertex board forces
`U+V >= 19`, which would make the bill one instance per row instead of ~54,000 certificates. On these
five rows it does, and on branch 62 it forces 21. The direct-board route is real.

**And it does not generalise cheaply.** The first survey ran the canonical `(14,5)` board on all 159
eligible rows at 110,000 conflicts each: **157 reached the budget without a decision.** So the route
is confirmed on 5 rows and unsettled on 154. Two more rows of the original pair also stayed open on
direct 35-vertex searches at 1.8–2.0 M conflicts — the earlier bounds on those two use a different
proof.

**A proof shared by two rows**: the union of the allowed-colour sets of rows 286 and 62 on `(14,5)`
is a weaker common board whose `U+V <= 18` formula is UNSAT in 562,112 conflicts, so one certificate
transfers across two non-isomorphic frozen configurations.

## Not verified, or not decided

- **Row 286's pentagon items**: `verify_row286_spokes.py` needs `row286-pentagons/proofs/split-11-8.drat.xz`,
  which is not in either archive supplied. Its spoke evidence directory is present; the pentagon
  proofs are not. Row 286's floor-19 entry above is therefore reported from the doc, not replayed.
- Whether either 35-vertex board admits total 19 on row 286.
- Any full-row nonexistence: the full-row trials stayed OPEN at 250k–1.6M conflicts, and the bundle
  states there is **no measured speedup**.
