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

**Confirmed against real evidence:** a proof restored from the owner's 11.4 GB
archive, with `full_root: false` supplied, replays successfully through this
path. The 569 rows are importable once the default is in place; what remains
missing is only the proof bytes.

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

## The empty-clause trap in `dense.marked_threshold`

`marked_threshold` ends with

```python
for limits, minimum in ((selectors, bound), (all_selectors, total), (root_selectors, root_goal)):
    if minimum > len(limits):
        return [[]]
```

so a requested charge larger than the number of available guards returns a
**single empty clause** — a formula that is UNSAT for no reason at all. A runner
that trusted the exit status would record a closure in milliseconds.

*Reproduced:* for `Family((15,14,14,14), ('T','-','-','-'), arm 0, mark 5,
size 15, '_T_', position 0)` with placement `(0,0,0)`, `bound = 15` gives 10,794
extra clauses and no empty clause (the correct case), while `bound = 16` and
`bound = 20` each give exactly `[[]]`.

It does not fire for any of the 113,179 frozen rows — the plan's charge never
exceeds the guard count there, and that has been swept under all four recipes.
The hazard is a hand-made row, a new profile, or an edited plan.

**Fix:** in `run_cover.py`, refuse to emit a case whose extra clauses contain an
empty clause (or whose charge exceeds the guard count), and treat that as an
error rather than an UNSAT. It is the same class of failure as the twin-lex
order that produced 381 void refutations: an over-constrained formula whose
refutation proves nothing.

## The global mixture cap in a three-arm instance

A three-arm instance built for the gluing question capped
`|N_0(a) ∩ (all arms)| <= 5`. Mixture (`|N_f(x) ∩ N_g(u)| <= 5`) holds **per
arm** — L1 is stated for a fixed pair of colours, and the three arms of a root are
three different colours — so the union can carry up to fifteen. In the
three-arm instance each arm point must have fourteen colour-0 partners spread
across the arms, so the global cap contradicts the branch by arithmetic alone: the
formula is UNSAT for no reason, and the "0.01 s gluing refutation" it produced was
an artefact.

*Reproduced:* a builder matching the published file's sizes exactly under the
global-cap reading gives 15,765 variables / 91,770 clauses for three arms and
9,521 / 48,664 for two; the per-arm build is 14,535 / 89,040, and with the same
pinned words it is UNKNOWN at 300 s.

**Fix:** state every cardinality bound with the arm it applies to and check the
sum against the coverage requirement before running. A bound that makes the sum
impossible is a defect, not a hard instance.
