# Defects found in the K58 bundle, with minimal fixes

Everything here was reproduced against the handoff bundle; each item names the
file and the smallest change that removes the problem. None of them is a defect
in the mathematics — for that see [K58_CAMPAIGN_REVIEW.md](K58_CAMPAIGN_REVIEW.md).

## 1. The classification citation points at a file that disclaims completeness

`gluing.py`'s docstring says the U/T templates are "from Tatarevic,
arXiv:2610.36648v2, as encoded in
`formal/src/R4333Lean/CriticalTemplates.lean` at commit 6c3f2fd". That file
states: *"Completeness is deliberately not asserted here; that is the separate
certificate problem."* The completeness theorem is Theorem 2.1 of the paper,
attributed to Kalbfleisch–Stanton (K16) and Heinrich (K15); in the pinned
repository it is `CriticalCatalogues.k16CriticalCatalogue_complete` and
`k15CriticalCatalogue_complete`.

Fix: cite `CriticalCatalogues.lean` and Theorem 2.1, not `CriticalTemplates.lean`.

## 2. `import-legacy` cannot read 569 of the 752 campaign rows

`cover_evidence.recipe_from` does `recipe = {name: row[name] for name in RECIPE}`
with `RECIPE = ("tables", "total_critical", "full_root")`. 569 rows of
`historical/campaign.jsonl` predate `full_root`, so the documented migration path
raises `KeyError: 'full_root'` before it looks for a proof file. Reproduced on
case `5e6290f4b19c20722fb0c300c7aa8ff0b2969e2c2ba3191efb56275732742278`.

Fix: `row.get(name, False)` (which is what `audit_campaign.audit_receipt` already
does), or drop `full_root` from `RECIPE` and pass `False`.

## 3. `--require-cadical` counts producer-written receipts

`inspect_secondary` never runs CaDiCaL and never hashes a binary: it checks
`solver["name"] == "CaDiCaL"`, `len(solver["sha256"]) == 64`, and that the log
contains `s UNSATISFIABLE`. A `cadical.json` naming `/nonexistent/bin/cadical`
with hash `0x00…00` and a one-line log is counted as `CADICAL_UNSAT` even while a
real drat-trim replays the direct certificates.

Fix: record the SHA-256 of the executable actually invoked, and have
`--require-cadical` compare it with a binary path supplied by the auditor (or
drop the flag's claim).

## 4. A manifest hash certifies nothing on its own

`manifest` has no `--checker` option, and `inspect_case` without a checker only
checks that retained files hash-match the values the producer wrote. A two-byte
"certificate" plus a hand-written log containing `s VERIFIED` is reported as
CERTIFIED by `manifest` and accepted by `verify` when `--checker` is omitted —
and rejected as soon as a real checker is passed.

Fix: require `--checker` for `verify`, and either require one for `manifest` or
record in the manifest that no checking was performed. Reviewers should quote a
manifest hash only together with the output of
`verify --require-complete --checker <their own drat-trim>`.

## 5. The ledger does not pin the encoding per case

Each certificate stores its own `recipe` and `inspect_case` rebuilds the CNF from
it, so a release cannot enforce that every certificate proves a formula implied
by its case. Both recipes in use (first pass: arm threshold plus
`2M − 57`; retry: the full `H ≥ w`) are implied, so this batch is sound, but the
property is unchecked in general.

Fix: put the intended recipe in the ledger row and compare.

## 6. `support_tables` is called "optional redundant" and is not

The docstring says the constraints are redundant; they are not a local fact. The
family accepts 4,344 of 5,688 locally consistent four- and five-point supports
and rejects the 1,344 whose two-colouring is `C4 + 2K2`. That is justified only
by the K15/K16 classification (in U15/T15 every colour class of every vertex is
`C5` or `P4`), which the bundle does not mention here.

Fix: either say "implied by the classification", or run with `tables=False` —
which costs nothing measurable: five example certificates rebuild to identical
input hashes and stay UNSAT in under a second, 22 of 23 sampled cases are
unchanged, and one case is faster without the tables.
