# Scoped entrance proof store — independently verified

Source: `smwwdcyxb/m2`, direction d6. The accompanying checks do not modify the
source proof store.

The currently verified mathematical scope is **only the explicitly certified
(case family, case key) list**. No strict-cell, mixed-cell, frozen-row or profile
elimination is claimed. Entrance means a ticket from a noncritical class, which
is $\beta_r\ge 1$; strict is $\beta_r>\alpha_r$, and balanced-active has
$\alpha_r=\beta_r\ge1$. The submitted broad headline is not accepted.

The source archive has 3,600 enumerated $(5,5,5)$ cases. Its current residual
list assigns 2,830 cases to verified certificates and 770 to OPEN. The manifest
also contains two earlier UNKNOWN attempts with no stored proof. Counts must
therefore filter records by `drat == "VERIFIED"`, not count manifest lines.

**Correct accepted scope (see also [verdict correction](../verdict-correction-smwwdcyxb-m2.md)).**
Only two complete, independently replayed families have 600 cases each:

| family | certified scope |
| --- | --- |
| `TT:2:5,5,5` | two 16-arms carry T/T, entrance in the 13-class |
| `UT:3:5,5,5` | two 16-arms carry U/T, entrance in the 12-class |

These 1,200 DRAT certificates exclude a 16-vertex entrance brace in exactly
those cases. `TT:3` is only partly covered (443/600), so an earlier verdict that
included it as a complete family was a scope bookkeeping error. No `(5,5,5)`
case outside the two complete families, no partial `TT:3`, `UT:2`, `UU:2`,
`UU:3` family, and no broader wording is part of the accepted theorem. In
particular, the report's headline about *every* root is not established.

At the start of this audit 2,824 of all 2,830 stored proofs had been
independently replayed; the six others are being replayed by
`replay_missing.py`, at most two at a time. The 1,800 accepted cases were all
already in that successful replay log. This additional work audits the rest of
the temporary store; it does not widen the accepted theorem or solve the open
cases.

A 10-minute-38-second `check_store.py` pass rebuilt all 2,830 certified CNFs to
their recorded SHA-256 values, checked all 2,830 compressed-proof hashes, and
matched all 3,600 enumerated keys to the 770-case residual (six families of 600;
3,200 raw configurations reduced to 600 distinct cases per family). There were
no mismatches. That pass stopped at the separate replay-completeness guard
because its count was 2,825/2,830. It was not a failed proof or mismatched
formula; `store-audit.json` records that intermediate status.

The $(4,5,5)$, $(5,4,5)$ and $(5,5,4)$ shapes (entrances with degree 15) are not
part of this certified store. Their 4,740 cases remain an open separate task..

## Final replay result

All six omitted proofs subsequently printed `s VERIFIED`. Their additional
replay times were 184.299, 582.515, 944.861, 804.433, 685.134 and 686.110
seconds. Combining these receipts with the unchanged structural audit gives
**2,830/2,830 verified stored proofs**, with independently checked CNF hashes,
compressed-proof hashes and actual CNF-against-proof verification. The frozen
source fingerprints are recorded in `geometry-receipt.json` and rechecked by
`finish_audit.py`; see `finish-audit.log` and `store-audit.json`.

There are still **770 OPEN cases** of the $(5,5,5)$ shape in this enumeration:
157 in `TT:3`, 9 in `UU:2`, 4 in `UT:2`, and all 600 in `UU:3`. The two
complete accepted families total 1,200 cases; all other stored certificates,
including those in `TT:3`, are partial-family evidence only. They do not change
the acceptance's scope. A 16-brace theorem at every
$(16,16,13,12)$ root is **not** established. An entrance is $\beta_r\ge1$, not
strictness $\beta_r>\alpha_r$, so neither strict nor balanced-active is closed.
Neither this store nor the separate reciprocal C&C audit closes a frozen row,
reduces the 140 target rows to zero, or moves a Ramsey bound.

Reproduce with:

```sh
python3 results/entrance-brace-audit-2026-11-26/replay_missing.py
python3 results/entrance-brace-audit-2026-11-26/check_store.py
python3 results/entrance-brace-audit-2026-11-26/finish_audit.py
```

The approximately 8.1 GB compressed DRAT archive remains at
`.ultramath/smwwdcyxb/m2/proofs/`; it is intentionally not duplicated or
committed. `check_store.py` rechecks the complete geometry rather than relying
only on the smaller finalisation pass. `replay_missing.py` reads, but never
rewrites, that archive.
