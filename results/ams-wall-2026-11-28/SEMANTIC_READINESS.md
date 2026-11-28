# Semantic memory/readiness check before trying MCTS on the wall

Checked 2026-11-28 at repository HEAD `bb0544cfdc508c5e33de0855604ce90ee37978c8`.

## Confirmed again

* `lean/build.sh` passed (incremental, all public axiom lists unchanged).
* The native input-only negation binding in `K58/EncoderExtensions.lean` is the
  registered native theorem. The older `K58/AtLeast.lean` auxiliary-sign-renamed
  `satisfiable_atLeast` is not used anywhere else in `lean/` as though it were
  the native CNF shape. `legacy_atLeastCNF_not_native` documents the distinction.
* `bash .ultramath/smwzxq4fl/m3/reproduce.sh` passed again with python-sat
  1.9.dev22: exact native counter comparisons, conditional projection/BCP
  controls and all 168 actual gadgets. Status `PASS`, no DRAT/row-closure check.
* The m6 native/support validator passed again: a real contiguous 2,536-clause
  counter+support suffix with joint extension, 1,208 positive generic
  extensions, 128 exhaustive negative hypotheses, and 112 invalid-selector
  rejections. No full-parent assembly is claimed.
* Selected existing artifacts match their pinned identities:
  * ordinary wall parent `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`;
  * working CNF `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38`;
  * RUP/CAS prefix `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3`.
  These are byte-for-byte copies under `.scratch/duggan-followup-semantic-wall/`.

## Not established — the remaining semantic bridge

A frozen-row CNF UNSAT proof does not yet imply that no physical colouring
realises that row. The full assembly still must prove all of the following
against the exact emitted CNF:

1. host/triangle/one-colour semantics and every frozen unit's meaning;
2. physical criticality supplies each selected guard premise, including the
   inside-root-arm-degree threshold of 14 after the root edge is counted;
3. the guards selected to meet the marked/total-critical floors really witness
   `w(r) <= H(r)` (and the appropriate relaxation/recipe distinction);
4. actual P4/C5/critical-support geometry implies membership in every emitted
   `allowed_supports` catalogue, for all sizes/kinds, not just the checked sample;
5. selector/cardinality fresh-variable allocation is disjoint and total;
6. the final Lean formula is hash-identical to the emitted parent DIMACS.

The first-tier parent uses `tables=True,total_critical=True,full_root=False` and
is a relaxation of the semantic row. An UNSAT proof of the relaxation transfers;
a model or timeout proves nothing about the semantic row. No `native_decide` or
trusted solver status can replace this assembly.

## Consequence for this experiment

MCTS may be assessed on the exact wall parent and its decomposition may obtain
strict CNF proof receipts. A bounded timeout is OPEN. A leaf proof is scoped to
its parent plus cube. A whole-parent CNF UNSAT cover is only a **CNF-level**
candidate unless the bridge above is finished and checked. No colouring-level
row, profile or Ramsey closure will be asserted from the experiment without it.
