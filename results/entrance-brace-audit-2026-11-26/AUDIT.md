# Scoped entrance proof store — independent audit in progress

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

**Accepted scoped theorem.** The three complete, independently replayed
families have 600 cases each:

| family | certified scope |
| --- | --- |
| `TT:2:5,5,5` | two 16-arms carry T/T, entrance in the 13-class |
| `TT:3:5,5,5` | two 16-arms carry T/T, entrance in the 12-class |
| `UT:3:5,5,5` | two 16-arms carry U/T, entrance in the 12-class |

These 1,800 DRAT certificates exclude a 16-vertex entrance brace in exactly
those cases. No `(5,5,5)` case outside them, no partial `UT:2`, `UU:2`, `UU:3`
family, and no broader wording is part of the acceptance. In particular, the
report's headline about *every* root is not established by the store.

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
