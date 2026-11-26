# One thousand model-supported third-word probes

Date: 2026-11-26.

## Question and answer

Can a small fresh solver batch close any of the new physical patterns?

**Not in this batch. All 1,000 exact parent-plus-word-cube cases remained
`OPEN`.** There were zero `UNSAT_BASE` results and zero physical `SAT_BASE`
results. No full wall row was closed and no Ramsey-number change follows.

## Exact test

`tools/adaptive_wall/pattern_wave_probe.py` uses the campaign's own
`word_wave.worker`/`run_native` pipeline on the original **first-tier K58
parent plus each selected fifteen-spoke physical cube**. Every case has its
own native receipt, query hash, parent hash, cap and conflict count. It is not
a three-color arm approximation.

Selection:

- 61 **full-arm model-supported third words** per largest size-14 pentagon,
  not `third_star.candidates()` (which contains 73 earlier pair-live patterns);
- 1,000 distinct `(original row, arm, word)` instances across **17 actual
  parents**;
- 5 profiles, with counts `15,14,14,14`: 244, `15,15,14,13`: 207,
  `16,14,14,13`: 183, `16,15,14,12`: 183, `16,16,14,11`: 183;
- eligible-profile round-robin selection with one largest pentagon arm per
  parent, preserving generator order;
- the previously completed 61-word wave on `05dd65df8f6e…` was excluded.

Settings: **5,000 conflict cap per case, two workers**, one eager proof pass,
and the campaign's bounded base-certification fallback (up to four times the
cap where required). The batch took **151.200367 seconds of coordinator wall time**. The receipt clock total, including overlapping solver work, was
**268.801 seconds**.

## Independent audit

`pattern-wave-1000-audit.json` independently rereads all 1,000 saved native
receipts and regenerates all 1,000 plain-parent and guided-query hashes:

| Status | Cases |
| --- | ---: |
| OPEN | **1,000** |
| UNSAT / closed physical cube | **0** |
| SAT witness / physical model | **0** |
| Pending augmented-base proof | **0** |
| Whole-row closures | **0** |
| Query hashes independently rebuilt | 1,000 |

Actual measured conflict sums were **5,000,623**, with cap values 5,000 for
each query. Nominal caps can be exceeded by solver counter behavior: **399**
receipts exceed 5,000, with a maximum of 5,006. These are retained as actual
work rather than being normalized. At a cap, OPEN is unresolved whether or
not the cap is reached, not a statement of impossibility or feasibility.

The closure validator was additionally exercised on a known locally refuted
word at cap 35,000. It reached `UNSAT_BASE` after **29,306 conflicts** and the
independent proof replay succeeded with `proof_sha256`
`944e7cc76ecab1287ac3c3157b770bf15986ee417e4781bbb63db9f1c4a8f13c`
(2,739,922 compressed bytes). The immutable control receipt is
`pattern-wave-closure-control.json`.

The primary receipt `pattern-wave-1000.json` contains every individual row,
arm, cube, parent/query hash, native status, conflict count and elapsed time.
Its SHA-256 is
`8c10e972d0edf3d6204b972f873880e433b8b8a888d87871da5820f8b407f44a`.
Receipt hashes and parent/CNF bindings are supplied, not an implicit full-row
proof. No proof or model was fabricated for the OPEN cases.

A separately selected known locally refuted third word **00210** was used as
a closure/control check, excluded from the 1,000-model-supported sample. Its
transferred proof was **430,058 bytes** and verified against its exact original
parent and physical cube with `lift.replay`. It demonstrates that the
original-parent refutation transfer works; it is not an `UNSAT_BASE` result in
the new batch and is not the whole parent's verdict.

## Relation to campaign reviews

Four independent audit directions in `smwy48onb` accepted the reusable
finite-rule machinery subject to its scope:

- all 616 two-word and 73 third-word local CNFs, all **668 local colorings**,
  and **21 local RUP refutations** were reproduced and checked;
- **all 24 physical original-parent-plus-cube RUP receipts** passed native
  checking (102,280,662 bytes);
- the headline **6,097,628 eliminated virtual cells** reproduces exactly, but
  is only **9.1125%** of the selected row-pattern cells, leaving 60,817,332;
- all 35 stock and 70 guided native attempts remained OPEN, with total actual
  conflicts **2,660,023 versus 2,660,049** and receipt times **171.948 versus
  190.431 seconds**. Guided time was **10.75% higher**, not a demonstrated gain;
- cached terminal receipts need their referenced artifacts reloaded, hashed
  and validated before unattended root closure is trusted; the full verifier
  catches these, the bare cached resume path does not;
- the inherited **179+326** contact counts remain log claims in this bundle,
  not an independently replayed new 505-proof manifest.

## Assessment

The work is promising as a compact, reproducible **conditional-lemma library**.
It is not yet a demonstrated successful whole-row search strategy. Correct
conditional UNSAT proofs do not imply parent UNSAT, a full-coloring witness,
or reduced solving time.

The next useful measurement should separate three effects without changing
split depth: original first-tier parent (A), same parent plus checked pair
batch (B), and B plus checked third refinement (C), at one common per-parent
conflict allocation. Current guided-vs-stock comparisons confound added rules
with binary splitting. Broad deeper splitting is not justified by this batch.
The 533,358 minimum-conditioned off-star exclusions must not be imported as
unconditional rules without their exact-minimum guards and complementary case.
