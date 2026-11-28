# Attempt to verify row `0404c3a2…` using the upper-eight certificate

## Status: **the row remains OPEN**

The new bound is real and useful, but it has not produced a complete original-parent proof of this row. The original first-tier parent is `a062b827…` (19,425 variables, 184,117 clauses). Nothing here changes the ledger, the profile or a Ramsey bound.

## What was newly verified

### 1. Every complete \(H\ge9\) cube is UNSAT

Rather than relying only on the twelve first-miss branches—which also carry disjunction side conditions—I generated **67 complete masks** over the eleven free colour-0 sites: 55 with \(H=9\), 11 with \(H=10\), and one with \(H=11\).

Each query is the original parent plus exactly eleven unit literals. **All 67 returned UNSAT.** The corresponding DRAT payloads were replayed after deletion normalisation: exit 0, exact `s VERIFIED`, zero warnings and complete proof reads. Each role is an independently refuted cube, not a completed original-parent DRAT.

I also compiled their lifted blocking clauses correctly and tested a four-case resolution tree. That small combined proof passed strict `-i -U -W`: exit 0, `s VERIFIED`, zero RAT. The full consolidated \(H\le8\) prefix was **not accepted by the checker**; a later all-case shortened-check also timed out. Consequently no consolidated proof prefix is claimed. The individual 67 cube closures remain valid. Metadata is under `.scratch/k58-0404-cube67/`; discarded composition attempts are not evidence.

### 2. Some high-\(H\), exact 16-site word children close

| exact case | conflicts | result |
| --- | ---: | --- |
| \(H=8\), first sampled word | 49,226 | UNSAT in about 1.6 s; normalized proof replay passed |
| \(H=7\), first sampled word | 23,143 | UNSAT in about 1.2 s; normalized proof replay passed |

The solver specialist independently reproduced those and four other high-\(H\) child closures. Six compressed proof payload SHA-256 values round-trip to the reported bytes. I additionally reconstructed the \(H=8\) child from the original parent and its 16 units and replayed its text DRAT: **exit 0, `s VERIFIED`, zero RAT** in 2.251 s. These are exact child proofs, not a row-wide closure or a count of disjoint completed classes.

### 3. The lower-\(H\) families do not become easy

* The unique \(H=1\) word remained OPEN at **1,000,001 conflicts** under both default and search-only CaDiCaL (about 67 s and 38 s here).
* All **10** \(H=2\) words remained OPEN at a 50,000-conflict cap.
* All **56** \(H=3\) words remained OPEN at a 50,000-conflict cap.
* A separate solver-direction experiment reached **1,788,293 conflicts** on \(H=1\) in about 90 seconds and remained UNKNOWN. The faster rate did not imply completion.
* The only tested representative for each of \(H=4,5,6\) was likewise OPEN at 50,000 conflicts; those single samples do not exhaust their classes.

Difficulty is strongly \(H\)-dependent. The upper-eight bound does not make every child easy: its literal height/count is not a magic decomposition of all 58 vertices. All 5,021 remaining local words can remove additional structure only when the other 42 vertices are searched/proved too.

## What was independently checked

* The independent \(H\le8\) archive audit remains valid: twelve original leaf refutations, bound reasoning, lower-endpoint proof, and byte-identical strengthened CNF.
* Local enumerations independently give **5,224** words with `1,10,56,270,907,1602,1465,710,180,22,1` by \(H\). The upper-eight condition excludes **203**, leaving **5,021**.
* The Lean cover proof (`.ultramath/smwzzcvej/m2/cover.lean`) **compiled successfully with no warnings**, and contains no `sorry` or `native_decide`. It establishes the 55-clause semantics, pairwise-leaf equivalence, exact cover and semantic composition lemma—not the full original CNF's UNSAT status.
* Four scoped audits were accepted: cube/composition obligations, Lean cover logic, solver measurements, and structural scope limits.

## Next required work

This needs a deliberately budgeted **multi-hour exact-case campaign**, not another indistinct timeout. The high-\(H\) cases make individual clauses accessible cheaply; the low-\(H\) tail is expensive. A complete proof needs every child of an exact cover of the entire parent and independent proof replay/export. There is no `COVER_READY` or verified original-parent result from this attempt.

Keep large child proofs and unfinished composition files under `.scratch/`, not in the result directory or production evidence archive. The two result files here are a handoff and a compact data receipt, not a claimed closure certificate.
